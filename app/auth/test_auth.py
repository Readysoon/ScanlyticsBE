import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db
from app.db.testdb import test_db

# Setup TestClient
client = TestClient(app)

app.dependency_overrides[get_db] = test_db

# base user data
@pytest.fixture
def user_data_login():
    return {
        "user_email": "gvghbjknmlkkkkkkkkkkkkkkkkkkhhjs@inohm.com",
        "user_password": "SecurePassword123"
    }

# base user data extended for UserSignup
@pytest.fixture
def user_data_signup(user_data_login):
    user_data = user_data_login.copy()
    user_data.update({
        "user_name": "John Doe",
        "user_role": "admin"
    })
    return user_data


def test_UserSignupService_fixture(user_data_signup):
    res = client.post("/auth/user_signup", json=user_data_signup)
    assert res.status_code == 201