import psycopg
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import TEST_API_TOKEN, TEST_DATABASE_URL

AUTH_HEADERS = {"Authorization": f"Bearer {TEST_API_TOKEN}"}
client = TestClient(app, headers=AUTH_HEADERS)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_reading_returns_201_and_the_stored_reading():
    payload = {
        "device_id": "meter-1",
        "kwh": 1.25,
        "timestamp": "2026-10-24T10:00:00Z",
    }

    response = client.post("/readings", json=payload)

    assert response.status_code == 201
    assert response.json()["device_id"] == "meter-1"
    assert response.json()["kwh"] == 1.25


def test_create_reading_is_saved_in_postgres():
    client.post("/readings", json={"device_id": "meter-1", "kwh": 1.25, "timestamp": "2026-10-24T10:00:00Z"})

    with psycopg.connect(TEST_DATABASE_URL) as conn:
        rows = conn.execute("SELECT device_id, kwh FROM readings").fetchall()

    assert rows == [("meter-1", 1.25)]


def test_list_readings_returns_everything_posted():
    client.post("/readings", json={"device_id": "meter-1", "kwh": 1.0, "timestamp": "2026-10-24T10:00:00Z"})
    client.post("/readings", json={"device_id": "meter-2", "kwh": 2.0, "timestamp": "2026-10-24T10:05:00Z"})

    response = client.get("/readings")

    assert response.status_code == 200
    assert [r["device_id"] for r in response.json()] == ["meter-1", "meter-2"]


def test_list_readings_survives_a_new_app_client():
    # A fresh client has no in-memory state; the rows must come from Postgres.
    client.post("/readings", json={"device_id": "meter-1", "kwh": 1.0, "timestamp": "2026-10-24T10:00:00Z"})

    response = TestClient(app, headers=AUTH_HEADERS).get("/readings")

    assert [r["device_id"] for r in response.json()] == ["meter-1"]


def test_negative_kwh_is_rejected():
    payload = {"device_id": "meter-1", "kwh": -0.5, "timestamp": "2026-10-24T10:00:00Z"}

    response = client.post("/readings", json=payload)

    assert response.status_code == 422


def test_missing_device_id_is_rejected():
    payload = {"kwh": 1.0, "timestamp": "2026-10-24T10:00:00Z"}

    response = client.post("/readings", json=payload)

    assert response.status_code == 422
