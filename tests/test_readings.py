from fastapi.testclient import TestClient

from app.main import app, readings

client = TestClient(app)


def setup_function():
    readings.clear()


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


def test_list_readings_returns_everything_posted():
    client.post("/readings", json={"device_id": "meter-1", "kwh": 1.0, "timestamp": "2026-10-24T10:00:00Z"})
    client.post("/readings", json={"device_id": "meter-2", "kwh": 2.0, "timestamp": "2026-10-24T10:05:00Z"})

    response = client.get("/readings")

    assert response.status_code == 200
    assert [r["device_id"] for r in response.json()] == ["meter-1", "meter-2"]


def test_negative_kwh_is_rejected():
    payload = {"device_id": "meter-1", "kwh": -0.5, "timestamp": "2026-10-24T10:00:00Z"}

    response = client.post("/readings", json=payload)

    assert response.status_code == 422


def test_missing_device_id_is_rejected():
    payload = {"kwh": 1.0, "timestamp": "2026-10-24T10:00:00Z"}

    response = client.post("/readings", json=payload)

    assert response.status_code == 422
