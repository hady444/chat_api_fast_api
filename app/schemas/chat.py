from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserInfo(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    weight: Optional[float] = None
    weightGoal: Optional[float] = None
    height: Optional[float] = None
    job: Optional[str] = None
    fitnessLevel: Optional[str] = None
    fitnessGoal: Optional[str] = None
    healthCondition: Optional[str] = None
    allergy: Optional[str] = None

class MessageRequest(BaseModel):
    message: str
    user: Optional[UserInfo] = None
    session_id: Optional[str] = Field(None, alias="session_id")
    user_id: Optional[str] = Field(None, description="User ID - required for new sessions")
    
    class Config:
        populate_by_name = True

class MessageResponse(BaseModel):
    reply: str
    session_id: str

class EndSessionRequest(BaseModel):
    session_id: str

class EndSessionResponse(BaseModel):
    status: str

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user: Optional[UserInfo] = None

class ChatSession(BaseModel):
    session_id: str
    user_id: str  # Now required
    messages: List[Message] = []
    user: Optional[UserInfo] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    status: str = "active"