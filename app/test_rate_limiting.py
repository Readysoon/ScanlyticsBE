from fastapi.testclient import TestClient
from app.main import app


# Setup TestClient
client = TestClient(app)

# (rate limiting is set for 30 per minute)
def test_rate_limiting():
    for n in range(29):
        res = client.get("/")
        # print(f"{n}: res.status_code: {res.status_code}")
        if n == 29:
            assert res.status_code == 429