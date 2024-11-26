import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

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



@pytest.fixture
def test_UserLogin_fixture(user_data_login): 
    res = client.post("/auth/login", json=user_data_login)

    return {
        'access_token': res.json()[1]['access_token'],
        'token_type': res.json()[1]['token_type']
    }

def test_update_password(test_UserLogin_fixture):
    new_password = {"user_password": "newpassword123"}
    
    res = client.patch(
        "/auth/password",
        json=new_password,
        headers={
            "Authorization": f"{test_UserLogin_fixture['token_type']} {test_UserLogin_fixture['access_token']}"
        }
    )

    assert res.status_code == 200

    old_password = {"user_password": "password123"}
    
    res = client.patch(
        "/auth/password",
        json=old_password,
        headers={
            "Authorization": f"{test_UserLogin_fixture['token_type']} {test_UserLogin_fixture['access_token']}"
        }
    )
    
    assert res.status_code == 200


@pytest.mark.parametrize("password,expected_status", [
    ({"user_password": ""}, 422),  # Empty
    ({"user_password": "123"}, 422),  # Too short
    ("invalid_json", 422),  # Invalid JSON
    ({"wrong_key": "password123"}, 422),  # Wrong key
    (None, 422)  # None
])
def test_update_password_invalid(test_UserLogin_fixture, password, expected_status):
    res = client.patch(
        "/auth/password",
        json=password,
        headers={
            "Authorization": f"{test_UserLogin_fixture['token_type']} {test_UserLogin_fixture['access_token']}"
        }
    )
    assert res.status_code == expected_status


def test_validate(test_UserLogin_fixture):
    res = client.post(
        "/auth/validate",
        headers={
            "Authorization": f"{test_UserLogin_fixture['token_type']} {test_UserLogin_fixture['access_token']}"
        }
    )
    assert res.status_code == 200


def test_verify(test_UserLogin_fixture):
    res = client.get(
        f"/auth/verify/{test_UserLogin_fixture['access_token']}"
    )
    assert res.status_code == 200




