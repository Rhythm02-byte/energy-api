import pytest
from fastapi.testclient import TestClient

from app import grid
from app.main import app

RAW = {
    "unix_seconds": [1795275900, 1795276800, 1795277700],  # last slot has no data yet
    "production_types": [
        {"name": "Solar", "data": [120.0, None]},  # newest slot not filled in yet
        {"name": "Wind onshore", "data": [19000.0, 19800.0]},
        {"name": "Wind offshore", "data": [8000.0, 8500.0]},
        {"name": "Fossil gas", "data": [11000.0, 11400.0]},
        {"name": "Fossil hard coal", "data": [3600.0, 3600.0]},
        {"name": "Fossil brown coal / lignite", "data": [6400.0, 6400.0]},
        {"name": "Geothermal", "data": [13.0, 13.0]},
        {"name": "Cross border electricity trading", "data": [-3000.0, -3040.0]},
        {"name": "Load", "data": [58000.0, 58100.0, None]},
        {"name": "Renewable share of generation", "data": [60.0, 60.3]},
    ],
}


@pytest.fixture(autouse=True)
def fresh_cache():
    grid._cache.update(at=0.0, value=None)
    yield
    grid._cache.update(at=0.0, value=None)


def test_summarize_groups_sources_and_skips_totals():
    result = grid.summarize(RAW)

    assert result["sources_mw"] == {
        "Wind": 28300.0,
        "Gas": 11400.0,
        "Coal": 10000.0,
        "Solar": 120.0,
        "Other": 13.0,
    }
    assert list(result["sources_mw"]) == ["Wind", "Gas", "Coal", "Solar", "Other"]
    assert result["renewable_share"] == 60.3
    assert result["load_mw"] == 58100.0
    assert result["time"] == "2026-11-21T16:00:00+00:00"


def test_grid_endpoint_needs_no_token(monkeypatch):
    monkeypatch.setattr(grid, "fetch_public_power", lambda: RAW)

    response = TestClient(app).get("/grid")

    assert response.status_code == 200
    assert response.json()["renewable_share"] == 60.3


def test_grid_endpoint_caches_the_upstream_call(monkeypatch):
    calls = []
    monkeypatch.setattr(grid, "fetch_public_power", lambda: calls.append(1) or RAW)
    client = TestClient(app)

    client.get("/grid")
    client.get("/grid")

    assert len(calls) == 1


def test_grid_endpoint_returns_502_when_upstream_fails(monkeypatch):
    def boom():
        raise OSError("network down")

    monkeypatch.setattr(grid, "fetch_public_power", boom)

    response = TestClient(app).get("/grid")

    assert response.status_code == 502
