import pytest
import os
from jose import jwt
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app

from app.error.errorHelper import ErrorStack
from .authHelper import CreateAccessTokenHelper, VerifyAccessTokenHelper, GetCurrentUserIDHelper


client = TestClient(app)

@pytest.fixture
def mock_user_id():
    return {"sub": "User:⟨abc123⟩"}  # Simulating Surreal DB ID format

def test_CreateAccessTokenHelper(mock_user_id):
    error_stack = ErrorStack()
    token = CreateAccessTokenHelper(mock_user_id, error_stack)
    
    # Decode and verify token
    decoded = jwt.decode(
        token, 
        os.getenv("secret_key"), 
        algorithms=["HS256"]
    )
    
    assert decoded['sub'] == "abc123"  # ID was extracted correctly
    assert isinstance(decoded['exp'], int)  # Expiration was set
    assert datetime.fromtimestamp(decoded['exp'], tz=timezone.utc) > datetime.now(timezone.utc)


def test_VerifyAccessTokenHelper():
    # Create a valid token
    error_stack = ErrorStack()
    test_data = {"sub": "User:⟨test123⟩"}
    token = CreateAccessTokenHelper(test_data, error_stack)
    
    # Verify token
    user_id = VerifyAccessTokenHelper(token, error_stack)
    assert user_id == "test123"

@pytest.fixture
def user_data_login():
    return {
        "user_email": "test1@example.com",
        "user_password": "password123"
    }

@pytest.fixture
def test_UserLogin_fixture(user_data_login): 
    res = client.post("/auth/login", json=user_data_login)

    return {
        'access_token': res.json()[1]['access_token'],
        'token_type': res.json()[1]['token_type']
    }

from unittest.mock import Mock, AsyncMock

@pytest.fixture
def mock_db():
    db = Mock()
    db.query = AsyncMock()
    return db

@pytest.fixture
def mock_oauth2_scheme():
    return "mock_token"

@pytest.fixture
def mock_verify_token(monkeypatch):
    def mock_verify(*args, **kwargs):
        return "test_user_id"
    # Update the path to match your actual project structure
    monkeypatch.setattr("app.auth.authHelper.VerifyAccessTokenHelper", mock_verify)
    return mock_verify

@pytest.mark.asyncio
async def test_get_current_user_id_success(mock_db, mock_oauth2_scheme, mock_verify_token):
    # Arrange
    mock_db.query.return_value = [{
        'result': [{
            'id': 'User:test_user_id'
        }]
    }]

    # Act
    result = await GetCurrentUserIDHelper(mock_oauth2_scheme, mock_db)

    # Assert
    assert result == 'User:test_user_id'
    mock_db.query.assert_called_once()
    assert "test_user_id" in mock_db.query.call_args[0][1]['user_id']