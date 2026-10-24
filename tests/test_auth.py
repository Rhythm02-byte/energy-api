import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import TEST_API_TOKEN

PAYLOAD = {"device_id": "meter-1", "kwh": 1.0, "timestamp": "2026-10-24T10:00:00Z"}


@pytest.fixture
def anonymous():
    return TestClient(app)


def test_health_check_needs_no_token(anonymous):
    response = anonymous.get("/health")

    assert response.status_code == 200


def test_post_reading_without_token_is_rejected(anonymous):
    response = anonymous.post("/readings", json=PAYLOAD)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_list_readings_without_token_is_rejected(anonymous):
    response = anonymous.get("/readings")

    assert response.status_code == 401


def test_wrong_token_is_rejected(anonymous):
    response = anonymous.post(
        "/readings", json=PAYLOAD, headers={"Authorization": "Bearer not-the-token"}
    )

    assert response.status_code == 401


def test_wrong_auth_scheme_is_rejected(anonymous):
    response = anonymous.get(
        "/readings", headers={"Authorization": f"Basic {TEST_API_TOKEN}"}
    )

    assert response.status_code == 401


def test_correct_token_is_accepted(anonymous):
    response = anonymous.post(
        "/readings", json=PAYLOAD, headers={"Authorization": f"Bearer {TEST_API_TOKEN}"}
    )

    assert response.status_code == 201


def test_every_token_is_rejected_when_api_token_is_not_configured(anonymous, monkeypatch):
    # Fail closed: a server with no configured token must refuse all writes.
    monkeypatch.delenv("API_TOKEN")

    response = anonymous.post(
        "/readings", json=PAYLOAD, headers={"Authorization": f"Bearer {TEST_API_TOKEN}"}
    )

    assert response.status_code == 401
