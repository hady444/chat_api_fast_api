from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.chat import (
    MessageRequest, 
    MessageResponse, 
    EndSessionRequest, 
    EndSessionResponse,
    MessageRole
)
from app.api.dependencies import get_current_user
from app.services.session_service import session_service
from app.services.gemini_service import gemini_service
from typing import Optional

router = APIRouter()

@router.post("/message", response_model=MessageResponse)
async def send_message(
    request: MessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send a message to the AI chat"""
    try:
        # Get or create session
        if request.session_id:
            # Verify session exists
            session = await session_service.get_session(request.session_id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )
            if session.get("status") == "ended":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session has already ended"
                )
            session_id = request.session_id
            
            # Verify session belongs to the user
            if session.get("user_id") != request.user_id and request.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Session does not belong to this user"
                )
        else:
            # Create new session - user_id is required
            if not request.user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="user_id is required when creating a new session"
                )
            session_id = await session_service.create_session(
                user_id=request.user_id,
                user_info=request.user
            )
        
        # Add user message to session
        await session_service.add_message(
            session_id=session_id,
            role=MessageRole.USER,
            content=request.message,
            user_info=request.user
        )
        
        # Get conversation history
        history = await session_service.get_conversation_history(session_id)
        
        # Generate AI response
        ai_response = await gemini_service.generate_response(
            message=request.message,
            conversation_history=history[:-1],  # Exclude the current message
            user_info=request.user
        )
        
        # Add AI response to session
        await session_service.add_message(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=ai_response
        )
        
        return MessageResponse(
            reply=ai_response,
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in send_message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message"
        )

@router.post("/end", response_model=EndSessionResponse)
async def end_session(
    request: EndSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """End an ongoing session and trigger storage/cleanup"""
    try:
        # Check if session exists
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session.get("status") == "ended":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session has already ended"
            )
        
        # End the session
        success = await session_service.end_session(request.session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to end session"
            )
        
        return EndSessionResponse(status="ended")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in end_session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while ending the session"
        )

@router.get("/sessions/{user_id}")
async def get_user_sessions(
    user_id: str,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all sessions for a specific user"""
    try:
        sessions = await session_service.get_user_sessions(user_id, status)
        return {"sessions": sessions, "count": len(sessions)}
    except Exception as e:
        print(f"Error getting user sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching sessions"
        )