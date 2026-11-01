from fastapi.testclient import TestClient

from app.main import app


def test_health_reports_ok_when_database_is_reachable():
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_returns_503_when_database_is_unreachable(monkeypatch):
    # Port 1 has no server listening, so the connection is refused straight away.
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost:1/energy_missing")

    response = TestClient(app).get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "unreachable"}


def test_health_needs_no_token():
    # Monitoring tools call this without credentials, so it must stay open.
    response = TestClient(app).get("/health")

    assert response.status_code == 200
