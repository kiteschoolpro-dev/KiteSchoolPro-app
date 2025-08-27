"""
Initial data seeding for KiteSchool Pro
"""
import asyncio
from datetime import datetime, date, time, timedelta
from database import connect_to_mongo, get_database, close_mongo_connection
from models import Course, CourseType, SpotLocation, User, UserRole, InstructorSchedule, TimeSlot
from auth import get_password_hash

async def seed_courses():
    """Seed initial courses"""
    db = await get_database()
    
    # Check if courses already exist
    existing_courses = await db.courses.count_documents({})
    if existing_courses > 0:
        print("Courses already seeded, skipping...")
        return
    
    courses = [
        Course(
            name="Private Kitesurfing Lesson",
            course_type=CourseType.PRIVATE_KITESURF,
            description="One-on-one kitesurfing instruction. Perfect for beginners or advanced riders wanting personalized attention. Includes all equipment and safety briefing.",
            duration_hours=2.0,
            max_students=1,
            base_price=120.0,
            spots=[SpotLocation.SYLT, SpotLocation.ROMO],
            skill_level_required="beginner",
            equipment_included=["kite", "board", "harness", "wetsuit", "helmet"]
        ),
        Course(
            name="Semi-Private Kitesurfing Lesson", 
            course_type=CourseType.SEMI_PRIVATE_KITESURF,
            description="2-student kitesurfing lesson. Great for couples or friends who want to learn together while still getting personal attention.",
            duration_hours=2.5,
            max_students=2,
            base_price=85.0,
            spots=[SpotLocation.SYLT, SpotLocation.ROMO],
            skill_level_required="beginner",
            equipment_included=["kite", "board", "harness", "wetsuit", "helmet"]
        ),
        Course(
            name="E-Foil Coaching Session",
            course_type=CourseType.EFOIL_COACHING,
            description="Electric foil board coaching with experienced instructor. Learn the art of flying above water with our premium e-foil equipment.",
            duration_hours=1.5,
            max_students=1,
            base_price=150.0,
            spots=[SpotLocation.SYLT, SpotLocation.ROMO],
            skill_level_required="intermediate",
            equipment_included=["efoil_board", "safety_gear", "wetsuit"]
        ),
        Course(
            name="E-Foil Test Session",
            course_type=CourseType.EFOIL_TEST,
            description="Try e-foiling for the first time! 45-minute introductory session to experience the thrill of electric foil boarding.",
            duration_hours=0.75,
            max_students=1,
            base_price=89.0,
            spots=[SpotLocation.SYLT, SpotLocation.ROMO],
            skill_level_required="beginner",
            equipment_included=["efoil_board", "safety_gear", "wetsuit"]
        )
    ]
    
    for course in courses:
        await db.courses.insert_one(course.model_dump())
        print(f"✓ Added course: {course.name}")

async def seed_admin_user():
    """Seed initial admin user"""
    db = await get_database()
    
    # Check if admin exists
    existing_admin = await db.users.find_one({"role": "owner"})
    if existing_admin:
        print("Admin user already exists, skipping...")
        return
    
    admin = User(
        email="admin@kiteschoolpro.com",
        first_name="Admin", 
        last_name="User",
        role=UserRole.OWNER,
        phone="+49123456789",
        language_preference="en"
    )
    
    admin_doc = admin.model_dump()
    admin_doc['hashed_password'] = get_password_hash("kiteschool123")
    
    await db.users.insert_one(admin_doc)
    print(f"✓ Added admin user: {admin.email}")

async def seed_instructor():
    """Seed sample instructor"""
    db = await get_database()
    
    # Check if instructor exists
    existing_instructor = await db.users.find_one({"role": "instructor"})
    if existing_instructor:
        print("Instructor already exists, skipping...")
        return
    
    instructor = User(
        email="instructor@kiteschoolpro.com",
        first_name="Max",
        last_name="Mueller", 
        role=UserRole.INSTRUCTOR,
        phone="+49987654321",
        language_preference="de"
    )
    
    instructor_doc = instructor.model_dump()
    instructor_doc['hashed_password'] = get_password_hash("instructor123")
    
    await db.users.insert_one(instructor_doc)
    print(f"✓ Added instructor: {instructor.first_name} {instructor.last_name}")
    
    # Add some sample schedules for next 7 days
    today = date.today()
    for i in range(7):
        schedule_date = today + timedelta(days=i)
        
        # Morning slots
        morning_slots = [
            TimeSlot(start_time="09:00", end_time="11:00"),
            TimeSlot(start_time="11:30", end_time="13:30")
        ]
        
        # Afternoon slots  
        afternoon_slots = [
            TimeSlot(start_time="14:00", end_time="16:00"),
            TimeSlot(start_time="16:30", end_time="18:30")
        ]
        
        # Create schedules for both spots
        for spot in [SpotLocation.SYLT, SpotLocation.ROMO]:
            schedule = InstructorSchedule(
                instructor_id=instructor.id,
                date=schedule_date,
                available_slots=morning_slots + afternoon_slots,
                spot=spot
            )
            
            schedule_doc = schedule.model_dump()
            schedule_doc['date'] = schedule_date.isoformat()  # Convert date to string
            await db.instructor_schedules.insert_one(schedule_doc)
    
    print(f"✓ Added 14 instructor schedules (7 days × 2 spots)")

async def seed_demo_customer():
    """Seed demo customer for testing"""
    db = await get_database()
    
    # Check if demo customer exists
    existing_customer = await db.users.find_one({"email": "demo@customer.com"})
    if existing_customer:
        print("Demo customer already exists, skipping...")
        return
    
    customer = User(
        email="demo@customer.com",
        first_name="Demo",
        last_name="Customer",
        role=UserRole.CUSTOMER,
        phone="+49555123456", 
        language_preference="en"
    )
    
    customer_doc = customer.model_dump()
    customer_doc['hashed_password'] = get_password_hash("demo123")
    
    await db.users.insert_one(customer_doc)
    print(f"✓ Added demo customer: {customer.email}")

async def main():
    """Run all seeding functions"""
    print("🌱 Starting KiteSchool Pro data seeding...")
    
    await connect_to_mongo()
    
    await seed_courses()
    await seed_admin_user()
    await seed_instructor()
    await seed_demo_customer()
    
    await close_mongo_connection()
    
    print("✅ Data seeding completed!")
    print("\n📋 Test Credentials:")
    print("Admin: admin@kiteschoolpro.com / kiteschool123")
    print("Instructor: instructor@kiteschoolpro.com / instructor123") 
    print("Customer: demo@customer.com / demo123")

if __name__ == "__main__":
    asyncio.run(main())