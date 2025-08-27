from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from models import Course, CourseCreate, CourseType, SpotLocation
from auth import get_current_user_id
from database import get_database

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("/", response_model=List[Course])
async def get_courses():
    """Get all active courses"""
    db = await get_database()
    courses = await db.courses.find({"is_active": True}).to_list(1000)
    return [Course(**course) for course in courses]

@router.get("/{course_id}", response_model=Course)
async def get_course(course_id: str):
    """Get specific course by ID"""
    db = await get_database()
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return Course(**course)

@router.post("/", response_model=Course)
async def create_course(course_data: CourseCreate, user_id: str = Depends(get_current_user_id)):
    """Create new course (Admin only)"""
    db = await get_database()
    
    # Check user role (should be admin)
    user = await db.users.find_one({"id": user_id})
    if not user or user.get('role') not in ['admin', 'owner']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create courses"
        )
    
    course = Course(**course_data.dict())
    await db.courses.insert_one(course.dict())
    return course

@router.get("/by-type/{course_type}", response_model=List[Course])
async def get_courses_by_type(course_type: CourseType):
    """Get courses filtered by type"""
    db = await get_database()
    courses = await db.courses.find({
        "course_type": course_type.value,
        "is_active": True
    }).to_list(1000)
    return [Course(**course) for course in courses]

@router.get("/by-spot/{spot}", response_model=List[Course])
async def get_courses_by_spot(spot: SpotLocation):
    """Get courses available at specific spot"""
    db = await get_database()
    courses = await db.courses.find({
        "spots": {"$in": [spot.value]},
        "is_active": True
    }).to_list(1000)
    return [Course(**course) for course in courses]