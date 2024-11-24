from fastapi.testclient import TestClient
from app.main import app


# Setup TestClient
client = TestClient(app)

def test_landing_page():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"

