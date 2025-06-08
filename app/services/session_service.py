from typing import Optional, Dict, List
import uuid
from datetime import datetime
from app.db.redis import redis_client
from app.db.mongodb import get_database
from app.schemas.chat import ChatSession, Message, MessageRole, UserInfo
from app.core.config import settings

class SessionService:
    def __init__(self):
        self.collection_name = "chat_sessions"
    
    async def create_session(self, user_id: str, user_info: Optional[UserInfo] = None) -> str:
        """Create a new chat session with required user_id"""
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "user_id": user_id,  # Now required
            "messages": [],
            "user": user_info.dict() if user_info else None,
            "started_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        await redis_client.set_session(session_id, session_data)
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session from Redis"""
        return await redis_client.get_session(session_id)
    
    async def get_user_sessions(self, user_id: str, status: Optional[str] = None) -> List[Dict]:
        """Get all sessions for a user from MongoDB"""
        db = get_database()
        collection = db[self.collection_name]
        
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        
        cursor = collection.find(query).sort("started_at", -1)
        sessions = []
        async for session in cursor:
            session["_id"] = str(session["_id"])
            sessions.append(session)
        
        return sessions
    
    async def add_message(
        self, 
        session_id: str, 
        role: MessageRole, 
        content: str,
        user_info: Optional[UserInfo] = None
    ):
        """Add a message to the session"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "user": user_info.dict() if user_info and role == MessageRole.USER else None
        }
        
        session["messages"].append(message)
        
        # Update user info if provided
        if user_info and role == MessageRole.USER:
            session["user"] = user_info.dict()
        
        await redis_client.set_session(session_id, session)
        return session
    
    async def end_session(self, session_id: str) -> bool:
        """End a session and move it to MongoDB"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        # Update session status
        session["ended_at"] = datetime.utcnow().isoformat()
        session["status"] = "ended"
        
        # Save to MongoDB
        db = get_database()
        collection = db[self.collection_name]
        await collection.insert_one(session)
        
        # Remove from Redis
        await redis_client.delete_session(session_id)
        
        return True
    
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session"""
        session = await self.get_session(session_id)
        if not session:
            return []
        
        return [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in session.get("messages", [])
        ]

session_service = SessionService()