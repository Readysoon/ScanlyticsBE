import pytest
from fastapi.testclient import TestClient

import os
os.environ["TESTING"] = "1"

from app.main import app

client = TestClient(app)

# base user data
@pytest.fixture
def user_data_login():
    return {
        "user_email": "ghhjasddasdasddfgssufdssssdddfas@inohm.com",
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


'''catch too long mails'''
@pytest.mark.parametrize("data_modifier,expected_status", [
    (lambda x: {**x, "user_email": "invalid_email"}, 422),
    (lambda x: {k: v for k, v in x.items() if k != "user_name"}, 422),
])
def test_signup_validation(user_data_signup, data_modifier, expected_status):
    modified_data = data_modifier(user_data_signup)
    response = client.post("/auth/user_signup", json=modified_data)
    assert response.status_code == expected_status


@pytest.fixture
def test_UserSignupService_fixture(user_data_signup):
    res = client.post("/auth/user_signup", json=user_data_signup)
    assert res.status_code == 201

    access_token = res.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_VerificationService(test_UserSignupService_fixture):
    token = test_UserSignupService_fixture["Authorization"].split(" ")[1]
    res = client.get(f"/auth/verify/{token}")
    assert res.status_code == 200


@pytest.mark.parametrize("data_modifier,expected_status", [
    (lambda x: {**x, "user_email": "invalid_email"}, 422),
    (lambda x: {**x, "user_password": ""}, 422),
    (lambda x: {k: v for k, v in x.items() if k != "user_name" and k != "user_password"}, 422),
])
def test_Login(user_data_login, data_modifier, expected_status):
    modified_data = data_modifier(user_data_login)
    response = client.post("/auth/user_signup", json=modified_data)
    assert response.status_code == expected_status


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
