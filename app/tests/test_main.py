import pytest
from fastapi.testclient import TestClient
from surrealdb import Surreal
from app.main import app
from app.db.database import get_db


# Test database configuration
TEST_SURREAL_URL = "ws://localhost:8004/rpc"
TEST_DB_NAME = "test_db"
TEST_NAMESPACE = "test_namespace"

# Setup TestClient
client = TestClient(app)


async def test_db():
    """Fixture to set up and tear down test database"""
    db = Surreal(TEST_SURREAL_URL)
    await db.connect()
    await db.signin({"user": "test", "pass": "test"})
    await db.use(TEST_NAMESPACE, TEST_DB_NAME)
    
    yield db
    
    # Cleanup after tests
    await db.query(f"REMOVE DATABASE {TEST_DB_NAME}")
    await db.close()


def test_landing_page():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"


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

