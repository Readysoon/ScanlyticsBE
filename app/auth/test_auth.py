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
        "user_email": "test1@example.com",
        "user_password": "password123"
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

@pytest.fixture
def user_data_orga_signup(user_data_signup):
    return {
        **user_data_signup,
        "orga_address": "123 Main St",
        "orga_email": "org@example.com",
        "orga_name": "Test Organization"
    }


def test_check_mail_new_email():
    res = client.post("/auth/check_mail", json={"user_email": "new@example.com"})
    assert res.status_code == 200


def test_orga_signup(user_data_orga_signup):
    res = client.post("/auth/orga_signup", json=user_data_orga_signup)
    assert res.status_code == 201

@pytest.mark.parametrize("invalid_data,expected_status_code", [
    # Missing required fields
    ({"user_email": "test@example.com", "user_password": "pass123"}, 422),  # Missing name and role
    ({"user_name": "John", "user_email": "test@example.com"}, 422),  # Missing password and role
    
    # Invalid email formats
    ({"user_email": "invalid-email", "user_password": "pass123", "user_name": "John", "user_role": "admin"}, 422),
    ({"user_email": "@example.com", "user_password": "pass123", "user_name": "John", "user_role": "admin"}, 422),
    
    # Invalid password (assuming there's a minimum length requirement)
    ({"user_email": "test@example.com", "user_password": "123", "user_name": "John", "user_role": "admin"}, 422),
    
    # Invalid role
    ({"user_email": "test@example.com", "user_password": "pass123", "user_name": "John", "user_role": "superuser"}, 422),
    
    # Empty fields
    ({"user_email": "", "user_password": "pass123", "user_name": "John", "user_role": "admin"}, 422),
    ({"user_email": "test@example.com", "user_password": "", "user_name": "John", "user_role": "admin"}, 422),
    ({"user_email": "test@example.com", "user_password": "pass123", "user_name": "", "user_role": "admin"}, 422),
])
def test_OrgaSignup_invalid_data(invalid_data, expected_status_code):
    res = client.post("/auth/orga_signup", json=invalid_data)
    assert res.status_code == expected_status_code


def test_UserSignup(user_data_signup):
    res = client.post("/auth/user_signup", json=user_data_signup)
    assert res.status_code == 201

# Parametrized tests for signup failures
@pytest.mark.parametrize("invalid_data,expected_status_code", [
    # Missing required fields
    ({"user_email": "test@example.com", "user_password": "pass123"}, 422),  # Missing name and role
    ({"user_name": "John", "user_email": "test@example.com"}, 422),  # Missing password and role
    
    # Invalid email formats
    ({"user_email": "invalid-email", "user_password": "pass123", "user_name": "John", "user_role": "admin"}, 422),
    ({"user_email": "@example.com", "user_password": "pass123", "user_name": "John", "user_role": "admin"}, 422),
    
    # Invalid password (assuming there's a minimum length requirement)
    ({"user_email": "test@example.com", "user_password": "123", "user_name": "John", "user_role": "admin"}, 422),
    
    # Invalid role
    ({"user_email": "test@example.com", "user_password": "pass123", "user_name": "John", "user_role": "superuser"}, 422),
    
    # Empty fields
    ({"user_email": "", "user_password": "pass123", "user_name": "John", "user_role": "admin"}, 422),
    ({"user_email": "test@example.com", "user_password": "", "user_name": "John", "user_role": "admin"}, 422),
    ({"user_email": "test@example.com", "user_password": "pass123", "user_name": "", "user_role": "admin"}, 422),
])
def test_UserSignup_invalid_data(invalid_data, expected_status_code):
    res = client.post("/auth/user_signup", json=invalid_data)
    assert res.status_code == expected_status_code



def test_UserLogin(user_data_login): 
    res = client.post("/auth/login", json=user_data_login)
    assert res.status_code == 200

# Parametrized tests for login failures
@pytest.mark.parametrize("invalid_login,expected_status_code,expected_error", [
    # Missing fields
    ({"user_email": "test@example.com"}, 422, "Missing password"),
    ({"user_password": "password123"}, 422, "Missing email"),
    
    # Invalid credentials
    ({"user_email": "wrong@example.com", "user_password": "password123"}, 401, "Invalid credentials"),
    ({"user_email": "test1@example.com", "user_password": "wrongpassword"}, 401, "Invalid credentials"),
    
    # Invalid email format
    ({"user_email": "invalid-email", "user_password": "password123"}, 422, "Invalid email format"),
    
    # Empty fields
    ({"user_email": "", "user_password": "password123"}, 422, "Email cannot be empty"),
    ({"user_email": "test@example.com", "user_password": ""}, 422, "Password cannot be empty"),
])
def test_UserLogin_invalid_data(invalid_login, expected_status_code, expected_error):
    res = client.post("/auth/login", json=invalid_login)
    assert res.status_code == expected_status_code
    
    # If you're returning error messages in the response
    if res.status_code != 200:
        assert "detail" in res.json()
