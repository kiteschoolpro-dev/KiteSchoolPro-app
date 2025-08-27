from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Any
from datetime import datetime, timedelta
from models import (
    User, UserRole, DashboardStats, InstructorSchedule, 
    InstructorScheduleCreate, TimeSlot, SpotLocation
)
from auth import get_current_user_id
from database import get_database

router = APIRouter(prefix="/admin", tags=["admin"])

async def verify_admin_access(user_id: str):
    """Helper to verify admin access"""
    db = await get_database()
    user = await db.users.find_one({"id": user_id})
    if not user or user.get('role') not in ['admin', 'owner']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(user_id: str = Depends(get_current_user_id)):
    """Get dashboard statistics"""
    await verify_admin_access(user_id)
    db = await get_database()
    
    today = datetime.utcnow().date().isoformat()  # Convert to string
    month_start = today[:7] + "-01"  # Get YYYY-MM-01 format
    
    # Count today's bookings
    today_bookings = await db.bookings.count_documents({
        "booking_date": today.isoformat(),
        "status": {"$in": ["confirmed", "pending"]}
    })
    
    # Calculate month revenue
    month_payments = await db.payments.find({
        "status": "paid",
        "paid_at": {"$gte": month_start.isoformat()}
    }).to_list(1000)
    month_revenue = sum(p['amount'] for p in month_payments)
    
    # Count active instructors
    active_instructors = await db.users.count_documents({
        "role": "instructor",
        "is_active": True
    })
    
    # Count pending payments
    pending_payments = await db.payments.count_documents({
        "status": "pending"
    })
    
    return DashboardStats(
        total_bookings_today=today_bookings,
        total_revenue_month=month_revenue,
        active_instructors=active_instructors,
        pending_payments=pending_payments
    )

@router.get("/users", response_model=List[User])
async def get_all_users(user_id: str = Depends(get_current_user_id)):
    """Get all users"""
    await verify_admin_access(user_id)
    db = await get_database()
    
    users = await db.users.find({}).to_list(1000)
    # Remove sensitive data
    for user in users:
        user.pop('hashed_password', None)
    
    return [User(**user) for user in users]

@router.get("/instructors", response_model=List[User])
async def get_instructors(user_id: str = Depends(get_current_user_id)):
    """Get all instructors"""
    await verify_admin_access(user_id)
    db = await get_database()
    
    instructors = await db.users.find({
        "role": "instructor",
        "is_active": True
    }).to_list(1000)
    
    # Remove sensitive data
    for instructor in instructors:
        instructor.pop('hashed_password', None)
    
    return [User(**instructor) for instructor in instructors]

@router.post("/instructor-schedule")
async def create_instructor_schedule(
    schedule_data: InstructorScheduleCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create instructor schedule"""
    await verify_admin_access(user_id)
    db = await get_database()
    
    # Check if instructor exists
    instructor = await db.users.find_one({
        "id": schedule_data.instructor_id,
        "role": "instructor"
    })
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructor not found"
        )
    
    # Check if schedule already exists for this date/instructor/spot
    existing = await db.instructor_schedules.find_one({
        "instructor_id": schedule_data.instructor_id,
        "date": schedule_data.date.isoformat(),
        "spot": schedule_data.spot.value
    })
    
    if existing:
        # Update existing schedule
        await db.instructor_schedules.update_one(
            {"id": existing['id']},
            {"$set": {
                "available_slots": [slot.dict() for slot in schedule_data.available_slots],
                "is_available": True
            }}
        )
        return {"message": "Schedule updated", "schedule_id": existing['id']}
    else:
        # Create new schedule
        schedule = InstructorSchedule(**schedule_data.dict())
        await db.instructor_schedules.insert_one(schedule.dict())
        return {"message": "Schedule created", "schedule_id": schedule.id}

@router.get("/instructor-schedules/{instructor_id}")
async def get_instructor_schedules(
    instructor_id: str,
    start_date: str,
    end_date: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get instructor schedules for date range"""
    await verify_admin_access(user_id)
    db = await get_database()
    
    schedules = await db.instructor_schedules.find({
        "instructor_id": instructor_id,
        "date": {
            "$gte": start_date,
            "$lte": end_date
        }
    }).to_list(1000)
    
    return [InstructorSchedule(**schedule) for schedule in schedules]

@router.patch("/users/{target_user_id}/role")
async def update_user_role(
    target_user_id: str,
    new_role: UserRole,
    user_id: str = Depends(get_current_user_id)
):
    """Update user role"""
    user = await verify_admin_access(user_id)
    db = await get_database()
    
    # Only owners can promote to admin/owner
    if new_role in [UserRole.ADMIN, UserRole.OWNER] and user.get('role') != 'owner':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can assign admin/owner roles"
        )
    
    # Update user role
    result = await db.users.update_one(
        {"id": target_user_id},
        {"$set": {"role": new_role.value}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User role updated", "new_role": new_role.value}

@router.get("/bookings/today")
async def get_today_bookings(user_id: str = Depends(get_current_user_id)):
    """Get all bookings for today"""
    await verify_admin_access(user_id)
    db = await get_database()
    
    today = datetime.utcnow().date()
    bookings = await db.bookings.find({
        "booking_date": today.isoformat(),
        "status": {"$in": ["confirmed", "pending"]}
    }).to_list(1000)
    
    # Enrich with customer and instructor data
    enriched_bookings = []
    for booking_doc in bookings:
        customer = await db.users.find_one({"id": booking_doc['customer_id']})
        instructor = None
        if booking_doc.get('instructor_id'):
            instructor = await db.users.find_one({"id": booking_doc['instructor_id']})
        
        course = await db.courses.find_one({"id": booking_doc['course_id']})
        
        enriched_bookings.append({
            "booking": booking_doc,
            "customer": customer,
            "instructor": instructor,
            "course": course
        })
    
    return enriched_bookings