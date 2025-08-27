from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time
from enum import Enum
import uuid

# Enums
class UserRole(str, Enum):
    CUSTOMER = "customer"
    INSTRUCTOR = "instructor" 
    ADMIN = "admin"
    OWNER = "owner"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    PARTIAL = "partial"
    REFUNDED = "refunded"
    FAILED = "failed"

class CourseType(str, Enum):
    PRIVATE_KITESURF = "private_kitesurf"
    SEMI_PRIVATE_KITESURF = "semi_private_kitesurf"
    EFOIL_COACHING = "efoil_coaching"
    EFOIL_TEST = "efoil_test"

class SpotLocation(str, Enum):
    SYLT = "sylt"
    ROMO = "romo"

# Base Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole
    language_preference: str = "en"  # en, de, dk
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    language_preference: str = "en"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Course Models
class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    course_type: CourseType
    description: str
    duration_hours: float
    max_students: int
    base_price: float  # EUR
    spots: List[SpotLocation]
    skill_level_required: str = "beginner"  # beginner, intermediate, advanced
    equipment_included: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class CourseCreate(BaseModel):
    name: str
    course_type: CourseType
    description: str
    duration_hours: float
    max_students: int
    base_price: float
    spots: List[SpotLocation]
    skill_level_required: str = "beginner"
    equipment_included: List[str] = []

# Booking Models
class TimeSlot(BaseModel):
    start_time: str  # Store as string (HH:MM format)
    end_time: str    # Store as string (HH:MM format)

class Booking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    course_id: str
    instructor_id: Optional[str] = None
    booking_date: str  # Store as ISO date string (YYYY-MM-DD)
    time_slot: TimeSlot
    spot: SpotLocation
    number_of_students: int
    student_names: List[str] = []
    student_details: Dict[str, Any] = {}  # weights, experience, special requirements
    total_price: float
    deposit_amount: float
    status: BookingStatus = BookingStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BookingCreate(BaseModel):
    course_id: str
    booking_date: str  # Store as ISO date string (YYYY-MM-DD)
    time_slot: TimeSlot
    spot: SpotLocation
    number_of_students: int
    student_names: List[str] = []
    student_details: Dict[str, Any] = {}
    notes: Optional[str] = None

class AvailabilityCheck(BaseModel):
    course_id: str
    booking_date: str  # Store as ISO date string (YYYY-MM-DD)
    spot: SpotLocation
    number_of_students: int

# Payment Models
class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_id: str
    stripe_payment_intent_id: Optional[str] = None
    amount: float
    currency: str = "EUR"
    payment_type: str  # "deposit", "balance", "full"
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None

class PaymentCreate(BaseModel):
    booking_id: str
    amount: float
    currency: str = "EUR"
    payment_type: str

# Schedule Models  
class InstructorSchedule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    instructor_id: str
    date: date
    available_slots: List[TimeSlot]
    spot: SpotLocation
    is_available: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InstructorScheduleCreate(BaseModel):
    instructor_id: str
    date: date
    available_slots: List[TimeSlot]
    spot: SpotLocation

# Response Models
class BookingDetails(BaseModel):
    booking: Booking
    course: Course
    customer: User
    instructor: Optional[User] = None
    payments: List[Payment] = []

class DashboardStats(BaseModel):
    total_bookings_today: int
    total_revenue_month: float
    active_instructors: int
    pending_payments: int