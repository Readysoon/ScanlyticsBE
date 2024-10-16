from fastapi.testclient import TestClient

from scanlyticsbe.app.main import app

client = TestClient(app)

def test_user_signup():
    user_data = {
        "user_email": "test63@example.com",
        "user_password": "password123",
        "user_name": "John Doe",
        "user_role": "user"
    }
    response = client.post("/auth/user_signup", json=user_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()