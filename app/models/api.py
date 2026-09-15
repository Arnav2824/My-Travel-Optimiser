from datetime import datetime
from typing import Optional
from app.models.travel import Journey

from pydantic import BaseModel

from app.models.travel import AvailabilityStatus


class JourneyLegResponse(BaseModel):
    origin: str
    destination: str

    mode: str
    operator: Optional[str] = None

    departure_time: datetime
    arrival_time: datetime

    duration_minutes: int
    price: float
    currency: str = "INR"

    transfers: int = 0

    availability: AvailabilityStatus
    last_updated: Optional[datetime] = None

    source: Optional[str] = None


class JourneyResponse(BaseModel):
    score: Optional[float] = None

    total_price: float
    total_duration_minutes: int
    total_transfers: int

    modes: list[str]

    total_travel_time_minutes: int
    total_waiting_time_minutes: int

    legs: list[JourneyLegResponse]

class OptimizationResult(BaseModel):
    recommendation: Optional[Journey] = None
    explanation: str
    alternatives: list[Journey]


class OptimizeResponse(BaseModel):
    recommendation: Optional[JourneyResponse] = None

    explanation: str

    alternatives: list[JourneyResponse]