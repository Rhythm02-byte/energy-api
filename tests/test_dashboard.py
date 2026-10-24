from fastapi.testclient import TestClient

from app.main import app


def test_dashboard_page_is_served_as_html():
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Energy Dashboard" in response.text


def test_dashboard_page_needs_no_token():
    # The page itself is public. Its data requests still need the token.
    response = TestClient(app).get("/")

    assert response.status_code == 200
