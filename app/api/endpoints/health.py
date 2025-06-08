from fastapi import APIRouter
from app.db.mongodb import mongodb
from app.db.redis import redis_client

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "services": {
            "api": "up",
            "mongodb": "down",
            "redis": "down"
        }
    }
    
    # Check MongoDB
    try:
        if mongodb.client:
            await mongodb.client.admin.command('ping')
            health_status["services"]["mongodb"] = "up"
    except:
        pass
    
    # Check Redis
    try:
        if redis_client.redis:
            await redis_client.redis.ping()
            health_status["services"]["redis"] = "up"
    except:
        pass
    
    # Set overall status
    if any(status == "down" for status in health_status["services"].values()):
        health_status["status"] = "degraded"
    
    return health_status