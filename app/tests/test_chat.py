import pytest
from httpx import AsyncClient
from ..main import app
from app.core.security import create_access_token

TEST_USER_ID = "test_user_123"

@pytest.fixture
def auth_token():
    """Create a test authentication token"""
    return create_access_token({"sub": "test_user", "userId": TEST_USER_ID})

@pytest.mark.asyncio
async def test_send_message_new_session_with_user_id(auth_token):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/chat/message",
            json={
                "message": "What diet should I follow?",
                "user_id": TEST_USER_ID,
                "user": {
                    "firstName": "John",
                    "fitnessGoal": "lose fat",
                    "healthCondition": "diabetic"
                }
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "session_id" in data
        assert data["session_id"] is not None

@pytest.mark.asyncio
async def test_send_message_new_session_without_user_id(auth_token):
    """Test that creating a session without user_id fails"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/chat/message",
            json={
                "message": "Hello",
                # Missing user_id
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
        assert "user_id is required" in response.json()["detail"]

@pytest.mark.asyncio
async def test_send_message_existing_session(auth_token):
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First message to create session with user_id
        response1 = await client.post(
            "/chat/message",
            json={
                "message": "Hello",
                "user_id": TEST_USER_ID
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        session_id = response1.json()["session_id"]
        
        # Second message with session_id (no user_id needed)
        response2 = await client.post(
            "/chat/message",
            json={
                "message": "What exercises should I do?",
                "session_id": session_id
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response2.status_code == 200
        data = response2.json()
        assert data["session_id"] == session_id

@pytest.mark.asyncio
async def test_get_user_sessions(auth_token):
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a session first
        await client.post(
            "/chat/message",
            json={
                "message": "Hello",
                "user_id": TEST_USER_ID
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Get user sessions
        response = await client.get(
            f"/chat/sessions/{TEST_USER_ID}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "count" in data
        assert data["count"] >= 0