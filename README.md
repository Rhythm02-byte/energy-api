# Energy Data API

A REST API that receives and serves energy-meter readings from smart-home devices.

## Status

Slice 2: health check, create and list readings, stored in PostgreSQL, validation tests.

Planned next: token authentication, Docker run, GitHub Actions CI.

## Set up PostgreSQL

Create two databases, one for running the app and one for tests:

```bash
createdb energy_dev
createdb energy_test
```

The app reads `DATABASE_URL` (default `postgresql://localhost/energy_dev`).
Tests read `TEST_DATABASE_URL` (default `postgresql://localhost/energy_test`) and empty the table before each test, so never point it at real data.

## Run locally

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/uvicorn app.main:app --reload
```

The table is created on startup if it does not exist.

Interactive docs: http://127.0.0.1:8000/docs

## Test

```bash
./.venv/bin/python -m pytest -q
```

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Health check |
| POST | `/readings` | Store a reading (`device_id`, `kwh` ≥ 0, `timestamp`) |
| GET | `/readings` | List all stored readings |

## How this was built

Built with Claude Code as an AI pair programmer. I planned the slices, chose the stack, reviewed the code, and ran the tests and the server myself.
