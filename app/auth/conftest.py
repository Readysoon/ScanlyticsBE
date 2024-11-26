from app.main import app
from fastapi.testclient import TestClient
from app.db.database import get_db
from app.db.testdb import test_db

# Setup TestClient
client = TestClient(app)

app.dependency_overrides[get_db] = test_db