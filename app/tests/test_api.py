import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def get_test_token():
    """Get a test token from the API"""
    response = requests.post(f"{BASE_URL}/auth/generate-test-token")
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Failed to get test token. Make sure DEBUG=True in .env")
        return None

def test_chat_api():
    # Get test token
    token = get_test_token()
    if not token:
        print("No token available. Testing without authentication...")
        headers = {"Content-Type": "application/json"}
    else:
        print(f"Got test token: {token[:20]}...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    # Test 1: Create new chat session
    print("\n1. Testing new chat session...")
    response = requests.post(
        f"{BASE_URL}/chat/message",
        headers=headers,
        json={
            "message": "What diet should I follow?",
            "user_id": "123",
            "user": {
                "firstName": "John",
                "lastName": "Doe",
                "weight": 80,
                "weightGoal": 75,
                "height": 180,
                "fitnessLevel": "beginner",
                "fitnessGoal": "lose fat",
                "healthCondition": "diabetic",
                "allergy": "nuts"
            }
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        session_id = data["session_id"]
        print(f"✅ Success! Session ID: {session_id}")
        print(f"AI Reply: {data['reply'][:100]}...")
        
        # Test 2: Continue conversation
        print("\n2. Testing continue conversation...")
        response2 = requests.post(
            f"{BASE_URL}/chat/message",
            headers=headers,
            json={
                "message": "Can you suggest some exercises that are safe for diabetics?",
                "session_id": session_id
            }
        )
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ Success! Continued session: {data2['session_id']}")
            print(f"AI Reply: {data2['reply'][:100]}...")
            
            # Test 3: End session
            print("\n3. Testing end session...")
            response3 = requests.post(
                f"{BASE_URL}/chat/end",
                headers=headers,
                json={"session_id": session_id}
            )
            
            if response3.status_code == 200:
                print(f"✅ Success! Session ended: {response3.json()}")
            else:
                print(f"❌ Failed to end session: {response3.status_code} - {response3.text}")
        else:
            print(f"❌ Failed to continue conversation: {response2.status_code} - {response2.text}")
    else:
        print(f"❌ Failed to create session: {response.status_code} - {response.text}")

def test_health_check():
    print("\n4. Testing health check...")
    response = requests.get(f"{BASE_URL}/api/health")
    if response.status_code == 200:
        print(f"✅ Health check: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Health check failed: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Starting API tests...")
    print(f"Testing against: {BASE_URL}")
    test_health_check()
    test_chat_api()