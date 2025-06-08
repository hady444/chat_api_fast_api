import redis.asyncio as redis
from app.core.config import settings
import json
from typing import Optional

class RedisClient:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        self.redis = await redis.from_url(settings.REDIS_URL, decode_responses=True)
        print("✅ Connected to Redis")
    
    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            print("❌ Disconnected from Redis")
    
    async def set_session(self, session_id: str, data: dict, ttl: int = settings.REDIS_TTL):
        await self.redis.setex(
            f"session:{session_id}",
            ttl,
            json.dumps(data)
        )
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        data = await self.redis.get(f"session:{session_id}")
        return json.loads(data) if data else None
    
    async def delete_session(self, session_id: str):
        await self.redis.delete(f"session:{session_id}")
    
    async def exists(self, session_id: str) -> bool:
        return await self.redis.exists(f"session:{session_id}") > 0

redis_client = RedisClient()