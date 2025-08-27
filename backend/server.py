from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
from pathlib import Path

# Import our modules
from database import connect_to_mongo, close_mongo_connection
from routes.auth_routes import router as auth_router
from routes.course_routes import router as course_router  
from routes.booking_routes import router as booking_router
from routes.payment_routes import router as payment_router
from routes.admin_routes import router as admin_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

# Create the main app
app = FastAPI(
    title="KiteSchool Pro API",
    description="Watersports School Management Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "KiteSchool Pro API is running!", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "kiteschool-pro-api"}

# Include all route modules
api_router.include_router(auth_router)
api_router.include_router(course_router)
api_router.include_router(booking_router)
api_router.include_router(payment_router)
api_router.include_router(admin_router)

# Include the main API router in the app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
