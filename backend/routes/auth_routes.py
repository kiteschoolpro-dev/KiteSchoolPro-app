from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from models import User, UserCreate, UserLogin, UserRole
from auth import verify_password, get_password_hash, create_access_token, get_current_user_id
from database import get_database

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register")
async def register(user_data: UserCreate):
    db = await get_database()
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict()
    del user_dict['password']
    
    user = User(**user_dict)
    user_doc = user.dict()
    user_doc['hashed_password'] = hashed_password
    
    await db.users.insert_one(user_doc)
    
    # Create access token
    access_token_expires = timedelta(minutes=30 * 24)  # 30 days
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role
        }
    }

@router.post("/login")
async def login(login_data: UserLogin):
    db = await get_database()
    
    # Find user
    user_doc = await db.users.find_one({"email": login_data.email})
    if not user_doc or not verify_password(login_data.password, user_doc.get('hashed_password', '')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user_doc.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30 * 24)  # 30 days
    access_token = create_access_token(
        data={"sub": user_doc['id'], "role": user_doc['role']}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_doc['id'],
            "email": user_doc['email'],
            "first_name": user_doc['first_name'],
            "last_name": user_doc['last_name'],
            "role": user_doc['role']
        }
    }

@router.get("/me")
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    db = await get_database()
    
    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Remove sensitive data and non-serializable fields
    user_doc.pop('hashed_password', None)
    user_doc.pop('_id', None)  # Remove MongoDB ObjectId
    
    # Convert datetime to string if present
    if 'created_at' in user_doc and hasattr(user_doc['created_at'], 'isoformat'):
        user_doc['created_at'] = user_doc['created_at'].isoformat()
    
    return user_doc