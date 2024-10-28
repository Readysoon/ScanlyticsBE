import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

'''with pytest.raises(Exception)'''

# base user data
@pytest.fixture
def user_data_login():
    return {
        "user_email": "ghhjadssddddsxdsdsassasfxcddddssddikddyssxdsccdddgdddhffhdf@inohm.com",
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

# Parameterized test cases using fixtures
@pytest.mark.parametrize("data_modifier,expected_status", [
    # Valid case - uses fixture data as is
    # (lambda x: x, 201),
    # Invalid email
    (lambda x: {**x, "user_email": "invalid_email"}, 422),
    # Missing user_name
    (lambda x: {k: v for k, v in x.items() if k != "user_name"}, 422),
    # Invalid role
    # (lambda x: {**x, "user_role": "invalid_role"}, 422),
    # Empty password
    # '''returns 201????'''
    # (lambda x: {**x, "user_password": ""}, 500),
])
def test_signup_validation(user_data_signup, data_modifier, expected_status):
    modified_data = data_modifier(user_data_signup)
    response = client.post("/auth/user_signup", json=modified_data)
    assert response.status_code == expected_status
    
# UserSignup with mail_verification disabled to return access token
# test has to be fixture because test cannot be repeated (user will already exist) and token is needed for next test
@pytest.fixture
def test_UserSignupService_fixture(user_data_signup):
    res = client.post("/auth/user_signup", json=user_data_signup)
    assert res.status_code == 201

    access_token = res.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

# verify with the token
def test_VerificationService(test_UserSignupService_fixture):
    token = test_UserSignupService_fixture["Authorization"].split(" ")[1]
    res = client.get(f"/auth/verify/{token}")
    assert res.status_code == 200

'''construction site'''
# Parameterized test cases using fixtures
@pytest.mark.parametrize("data_modifier,expected_status", [
    # Valid case - uses fixture data as is
    # (lambda x: x, 201),
    # Invalid email
    (lambda x: {**x, "user_email": "invalid_email"}, 422),
    # Missing user_name
    (lambda x: {k: v for k, v in x.items() if k != "user_name"}, 422),
    # Invalid role
    # (lambda x: {**x, "user_role": "invalid_role"}, 422),
    # Empty password
    # '''returns 201????'''
    # (lambda x: {**x, "user_password": ""}, 500),
])
def test_Login(user_data_login, data_modifier, expected_status):
    modified_data = data_modifier(user_data_signup)
    res = client.post("/auth/login", json=user_data_login)
    assert res.status_code == 200

@pytest.fixture
def test_Login_fixture(user_data_login):
    res = client.post("/auth/login", json=user_data_login)
    assert res.status_code == 200

    access_token = res.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

def test_Delete(test_Login_fixture):
    headers = test_Login_fixture
    print(headers)
    res = client.delete(f"/user/", headers=headers)
    print(res)
    assert res.status_code == 200
