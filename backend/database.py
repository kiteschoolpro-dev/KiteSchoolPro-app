from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None

database = Database()

async def get_database():
    return database.db

async def connect_to_mongo():
    """Create database connection"""
    mongo_url = os.environ.get('MONGO_URL')
    database.client = AsyncIOMotorClient(mongo_url)
    database.db = database.client[os.environ.get('DB_NAME', 'kiteschool_pro')]

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()