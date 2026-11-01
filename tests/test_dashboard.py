import re

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


def _page() -> str:
    return TestClient(app).get("/").text


def test_dashboard_script_only_uses_elements_that_exist():
    # Every element the script looks up by id must be on the page, or the dashboard breaks silently.
    page = _page()
    looked_up = set(re.findall(r'\$\("([A-Za-z-]+)"\)', page))

    assert looked_up, "expected the script to look up elements"
    for element_id in looked_up:
        assert f'id="{element_id}"' in page, f"missing element: {element_id}"


def test_dashboard_shows_the_three_stats_and_the_chart():
    page = _page()

    for element_id in ("stat-count", "stat-kwh", "stat-devices", "chart", "chart-empty", "rows"):
        assert f'id="{element_id}"' in page


def test_dashboard_reading_form_has_required_fields():
    page = _page()

    for field in ("device-id", "kwh", "timestamp"):
        tag = re.search(rf'<input id="{field}"[^>]*>', page)
        assert tag, f"missing input: {field}"
        assert "required" in tag.group(0)


def test_dashboard_sends_the_token_and_reads_readings():
    page = _page()

    assert 'Authorization' in page and 'Bearer' in page
    assert 'api("/readings")' in page
    assert 'api("/readings", { method: "POST"' in page
