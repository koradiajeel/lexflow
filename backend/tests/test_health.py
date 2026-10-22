"""The /health check Render uses, and CORS origins coming from settings."""
from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_local_frontend_is_allowed_by_cors():
    with TestClient(app) as client:
        res = client.options(
            "/health",
            headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
        )
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_unknown_website_is_not_allowed_by_cors():
    with TestClient(app) as client:
        res = client.options(
            "/health",
            headers={"Origin": "https://evil.example.com", "Access-Control-Request-Method": "GET"},
        )
    assert "access-control-allow-origin" not in res.headers
