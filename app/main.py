from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, status
from pydantic import BaseModel, Field

app = FastAPI(title="Energy Data API")

# In-memory storage for now. Replaced by PostgreSQL in the next slice.
readings: list["Reading"] = []


class ReadingIn(BaseModel):
    device_id: str = Field(min_length=1)
    kwh: Annotated[float, Field(ge=0)]
    timestamp: datetime


class Reading(ReadingIn):
    pass


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/readings", status_code=status.HTTP_201_CREATED, response_model=Reading)
def create_reading(payload: ReadingIn) -> Reading:
    reading = Reading(**payload.model_dump())
    readings.append(reading)
    return reading


@app.get("/readings", response_model=list[Reading])
def list_readings() -> list[Reading]:
    return readings
