import os

import psycopg
import pytest

from app.db import SCHEMA

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://localhost/energy_test")


@pytest.fixture(autouse=True)
def clean_database(monkeypatch):
    # Point the app at the test database and start every test with an empty table.
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        conn.execute(SCHEMA)
        conn.execute("TRUNCATE readings RESTART IDENTITY")
    yield
