from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import stripe
import os
from models import Payment, PaymentCreate, PaymentStatus, Booking
from auth import get_current_user_id
from database import get_database

# Configure Stripe (using test keys for development)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_...")

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/create-payment-intent")
async def create_payment_intent(payment_data: PaymentCreate, user_id: str = Depends(get_current_user_id)):
    """Create Stripe payment intent for a booking"""
    db = await get_database()
    
    # Get booking
    booking_doc = await db.bookings.find_one({"id": payment_data.booking_id})
    if not booking_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = Booking(**booking_doc)
    
    # Check if user owns this booking or is admin
    user = await db.users.find_one({"id": user_id})
    if user['role'] not in ['admin', 'owner'] and booking.customer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(payment_data.amount * 100),  # Convert to cents
            currency=payment_data.currency.lower(),
            metadata={
                "booking_id": payment_data.booking_id,
                "customer_id": booking.customer_id,
                "payment_type": payment_data.payment_type
            }
        )
        
        # Save payment record
        payment = Payment(
            booking_id=payment_data.booking_id,
            stripe_payment_intent_id=intent.id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            payment_type=payment_data.payment_type,
            status=PaymentStatus.PENDING
        )
        
        await db.payments.insert_one(payment.dict())
        
        return {
            "client_secret": intent.client_secret,
            "payment_id": payment.id,
            "amount": payment_data.amount
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment processing error: {str(e)}"
        )

@router.post("/confirm-payment/{payment_id}")
async def confirm_payment(payment_id: str, user_id: str = Depends(get_current_user_id)):
    """Confirm payment success and update booking status"""
    db = await get_database()
    
    # Get payment
    payment_doc = await db.payments.find_one({"id": payment_id})
    if not payment_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    payment = Payment(**payment_doc)
    
    # Get booking to verify ownership
    booking_doc = await db.bookings.find_one({"id": payment.booking_id})
    if not booking_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = Booking(**booking_doc)
    
    # Check permissions
    user = await db.users.find_one({"id": user_id})
    if user['role'] not in ['admin', 'owner'] and booking.customer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Verify payment with Stripe
        if payment.stripe_payment_intent_id:
            intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
            
            if intent.status == 'succeeded':
                # Update payment status
                await db.payments.update_one(
                    {"id": payment_id},
                    {"$set": {
                        "status": PaymentStatus.PAID.value,
                        "paid_at": datetime.utcnow().isoformat()
                    }}
                )
                
                # Update booking payment status
                total_paid = 0
                all_payments = await db.payments.find({"booking_id": payment.booking_id}).to_list(1000)
                for p in all_payments:
                    if p.get('status') == PaymentStatus.PAID.value:
                        total_paid += p['amount']
                
                # Determine booking payment status
                if total_paid >= booking.total_price:
                    payment_status = "paid"
                    booking_status = "confirmed"
                elif total_paid >= booking.deposit_amount:
                    payment_status = "partial"
                    booking_status = "confirmed"
                else:
                    payment_status = "pending"
                    booking_status = "pending"
                
                await db.bookings.update_one(
                    {"id": payment.booking_id},
                    {"$set": {
                        "payment_status": payment_status,
                        "status": booking_status
                    }}
                )
                
                return {"message": "Payment confirmed", "status": "success"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment not completed"
                )
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment verification error: {str(e)}"
        )

@router.get("/booking/{booking_id}", response_model=List[Payment])
async def get_booking_payments(booking_id: str, user_id: str = Depends(get_current_user_id)):
    """Get all payments for a booking"""
    db = await get_database()
    
    # Get booking to verify ownership
    booking_doc = await db.bookings.find_one({"id": booking_id})
    if not booking_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = Booking(**booking_doc)
    
    # Check permissions
    user = await db.users.find_one({"id": user_id})
    if user['role'] not in ['admin', 'owner'] and booking.customer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    payments = await db.payments.find({"booking_id": booking_id}).to_list(1000)
    return [Payment(**payment) for payment in payments]

from datetime import datetime