# Energy Data API

A REST API that receives and serves energy-meter readings from smart-home devices.

## Status

Slice 1: health check, create and list readings, in-memory storage, validation tests.

Planned next: PostgreSQL storage, token authentication, Docker run, GitHub Actions CI.

## Run locally

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/uvicorn app.main:app --reload
```

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
