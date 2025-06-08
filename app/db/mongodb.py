from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from typing import Optional

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.database = mongodb.client[settings.MONGODB_DB_NAME]
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        print("❌ Disconnected from MongoDB")

def get_database():
    return mongodb.database