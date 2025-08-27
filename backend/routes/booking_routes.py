from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Any
from datetime import datetime, timedelta
from models import (
    Booking, BookingCreate, BookingDetails, BookingStatus, 
    AvailabilityCheck, TimeSlot, SpotLocation, User, Course
)
from auth import get_current_user_id
from database import get_database

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/check-availability")
async def check_availability(availability: AvailabilityCheck):
    """Check if booking is available for given parameters"""
    db = await get_database()
    
    # Get course details
    course = await db.courses.find_one({"id": availability.course_id})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Find available instructors for that date/spot
    instructors = await db.users.find({
        "role": "instructor",
        "is_active": True
    }).to_list(1000)
    
    # Check instructor schedules
    available_slots = []
    for instructor in instructors:
        schedule = await db.instructor_schedules.find_one({
            "instructor_id": instructor['id'],
            "date": availability.booking_date,  # booking_date is already a string
            "spot": availability.spot.value,
            "is_available": True
        })
        
        if schedule:
            # Check for conflicts with existing bookings
            for slot in schedule.get('available_slots', []):
                existing_booking = await db.bookings.find_one({
                    "instructor_id": instructor['id'],
                    "booking_date": availability.booking_date.isoformat(),
                    "time_slot.start_time": slot['start_time'],
                    "status": {"$in": ["pending", "confirmed"]}
                })
                
                if not existing_booking:
                    available_slots.append({
                        "instructor_id": instructor['id'],
                        "instructor_name": f"{instructor['first_name']} {instructor['last_name']}",
                        "time_slot": slot,
                        "available": True
                    })
    
    return {
        "available": len(available_slots) > 0,
        "available_slots": available_slots,
        "course": course
    }

@router.post("/", response_model=Booking)
async def create_booking(booking_data: BookingCreate, user_id: str = Depends(get_current_user_id)):
    """Create a new booking"""
    db = await get_database()
    
    # Get customer info
    customer = await db.users.find_one({"id": user_id})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Get course details
    course = await db.courses.find_one({"id": booking_data.course_id})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Calculate pricing (basic for MVP)
    base_price = course['base_price']
    total_price = base_price * booking_data.number_of_students
    deposit_amount = total_price * 0.3  # 30% deposit
    
    # Find available instructor
    instructors = await db.users.find({
        "role": "instructor",
        "is_active": True
    }).to_list(1000)
    
    assigned_instructor = None
    for instructor in instructors:
        schedule = await db.instructor_schedules.find_one({
            "instructor_id": instructor['id'],
            "date": booking_data.booking_date.isoformat(),
            "spot": booking_data.spot.value,
            "is_available": True
        })
        
        if schedule:
            # Check if time slot is available
            slot_available = any(
                slot['start_time'] == booking_data.time_slot.start_time.isoformat()
                for slot in schedule.get('available_slots', [])
            )
            
            if slot_available:
                # Check for conflicts
                existing_booking = await db.bookings.find_one({
                    "instructor_id": instructor['id'],
                    "booking_date": booking_data.booking_date.isoformat(),
                    "time_slot.start_time": booking_data.time_slot.start_time.isoformat(),
                    "status": {"$in": ["pending", "confirmed"]}
                })
                
                if not existing_booking:
                    assigned_instructor = instructor['id']
                    break
    
    if not assigned_instructor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No instructor available for selected time slot"
        )
    
    # Create booking
    booking = Booking(
        customer_id=user_id,
        instructor_id=assigned_instructor,
        total_price=total_price,
        deposit_amount=deposit_amount,
        **booking_data.dict()
    )
    
    await db.bookings.insert_one(booking.dict())
    return booking

@router.get("/my-bookings", response_model=List[BookingDetails])
async def get_my_bookings(user_id: str = Depends(get_current_user_id)):
    """Get current user's bookings"""
    db = await get_database()
    
    # Get user to check role
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Query based on role
    if user['role'] == 'customer':
        bookings = await db.bookings.find({"customer_id": user_id}).to_list(1000)
    elif user['role'] == 'instructor':
        bookings = await db.bookings.find({"instructor_id": user_id}).to_list(1000)
    else:  # admin/owner
        bookings = await db.bookings.find({}).to_list(1000)
    
    # Enrich bookings with related data
    enriched_bookings = []
    for booking_doc in bookings:
        booking = Booking(**booking_doc)
        
        # Get course
        course_doc = await db.courses.find_one({"id": booking.course_id})
        course = Course(**course_doc) if course_doc else None
        
        # Get customer
        customer_doc = await db.users.find_one({"id": booking.customer_id})
        customer = User(**customer_doc) if customer_doc else None
        
        # Get instructor
        instructor = None
        if booking.instructor_id:
            instructor_doc = await db.users.find_one({"id": booking.instructor_id})
            instructor = User(**instructor_doc) if instructor_doc else None
        
        # Get payments
        payments = await db.payments.find({"booking_id": booking.id}).to_list(1000)
        
        enriched_bookings.append(BookingDetails(
            booking=booking,
            course=course,
            customer=customer,
            instructor=instructor,
            payments=payments
        ))
    
    return enriched_bookings

@router.get("/{booking_id}", response_model=BookingDetails)
async def get_booking(booking_id: str, user_id: str = Depends(get_current_user_id)):
    """Get specific booking details"""
    db = await get_database()
    
    booking_doc = await db.bookings.find_one({"id": booking_id})
    if not booking_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = Booking(**booking_doc)
    
    # Check access permissions
    user = await db.users.find_one({"id": user_id})
    if (user['role'] == 'customer' and booking.customer_id != user_id) or \
       (user['role'] == 'instructor' and booking.instructor_id != user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get related data
    course_doc = await db.courses.find_one({"id": booking.course_id})
    course = Course(**course_doc) if course_doc else None
    
    customer_doc = await db.users.find_one({"id": booking.customer_id})
    customer = User(**customer_doc) if customer_doc else None
    
    instructor = None
    if booking.instructor_id:
        instructor_doc = await db.users.find_one({"id": booking.instructor_id})
        instructor = User(**instructor_doc) if instructor_doc else None
    
    payments = await db.payments.find({"booking_id": booking.id}).to_list(1000)
    
    return BookingDetails(
        booking=booking,
        course=course,
        customer=customer,
        instructor=instructor,
        payments=payments
    )

@router.patch("/{booking_id}/status")
async def update_booking_status(
    booking_id: str, 
    status: BookingStatus,
    user_id: str = Depends(get_current_user_id)
):
    """Update booking status"""
    db = await get_database()
    
    # Check permissions (admin, instructor, or customer can cancel their own)
    user = await db.users.find_one({"id": user_id})
    booking = await db.bookings.find_one({"id": booking_id})
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if user['role'] not in ['admin', 'owner'] and \
       user['id'] not in [booking['customer_id'], booking.get('instructor_id')]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update status
    await db.bookings.update_one(
        {"id": booking_id},
        {"$set": {
            "status": status.value,
            "updated_at": datetime.utcnow().isoformat()
        }}
    )
    
    return {"message": "Booking status updated", "new_status": status.value}