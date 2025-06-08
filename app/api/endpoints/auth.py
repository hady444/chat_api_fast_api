from fastapi import APIRouter, HTTPException
from datetime import timedelta
from app.core.security import create_access_token
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/generate-test-token", response_model=TokenResponse)
async def generate_test_token():
    """Generate a test token for development purposes"""
    if not settings.DEBUG:
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available in debug mode"
        )
    
    # Create a test token with 24 hours expiration
    access_token_expires = timedelta(hours=24)
    test_user_data = {
        "sub": "test_user",
        "userId": "test_123"
    }
    access_token = create_access_token(
        data=test_user_data, 
        expires_delta=access_token_expires
    )
    
    return TokenResponse(access_token=access_token)