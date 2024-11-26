import pytest
from fastapi.testclient import TestClient
from app.main import app

# Setup TestClient
client = TestClient(app)

@pytest.fixture
def user_data_login():
    return {
        "user_email": "test1@example.com",
        "user_password": "password123"
    }


def test_UserLogin(user_data_login): 
    res = client.post("/auth/login", json=user_data_login)
    assert res.status_code == 200


@pytest.fixture
def test_UserLogin_fixture(user_data_login): 
    res = client.post("/auth/login", json=user_data_login)

    return {
        'access_token': res.json()[1]['access_token'],
        'token_type': res.json()[1]['token_type']
    }


def test_delete_user(test_UserLogin_fixture):
    headers = {
        "Authorization": f"{test_UserLogin_fixture['token_type']} {test_UserLogin_fixture['access_token']}"
    }
    response = client.delete(
        "/user/",
        headers=headers
    )
    assert response.status_code == 200