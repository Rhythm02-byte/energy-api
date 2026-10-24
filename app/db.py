import os

import psycopg

DEFAULT_DATABASE_URL = "postgresql://localhost/energy_dev"

SCHEMA = """
CREATE TABLE IF NOT EXISTS readings (
    id SERIAL PRIMARY KEY,
    device_id TEXT NOT NULL,
    kwh DOUBLE PRECISION NOT NULL CHECK (kwh >= 0),
    recorded_at TIMESTAMPTZ NOT NULL
)
"""


def connect() -> psycopg.Connection:
    return psycopg.connect(os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL))
