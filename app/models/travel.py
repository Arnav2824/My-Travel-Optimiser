from pydantic import BaseModel, model_validator
from typing import Optional
from enum import Enum
from datetime import datetime , time
from pydantic import BaseModel, model_validator
from typing import Optional

class TravelOption(BaseModel):
    origin: str
    destination: str

    mode: str
    operator: Optional[str] = None

    departure_time: str
    arrival_time: str

    duration_minutes: int
    price: float
    currency: str = "INR"

    transfers: int = 0

    source: Optional[str] = None

class TravelRequest(BaseModel):
    origin: str
    destination: str
    travel_date: datetime | None = None
    budget: Optional[float] = None

    cost_weight: float = 0.5
    time_weight: float = 0.5
    convenience_weight: float = 0.0
    travel_time_value: Optional[float] = None
    waiting_time_value: Optional[float] = None
    value_of_time: Optional[float] = None
    earliest_departure: datetime | None = None
    latest_departure: datetime | None = None
    latest_arrival: datetime | None = None
    
    max_transfers: Optional[int] = None

    @model_validator(mode="after")
    def validate_weights(self):
        total = (
            self.cost_weight
            + self.time_weight
            + self.convenience_weight
        )

        if abs(total - 1.0) > 0.001:
            raise ValueError(
                "cost_weight, time_weight, and "
                "convenience_weight must add up to 1.0"
            )

        if any(
            weight < 0
            for weight in [
                self.cost_weight,
                self.time_weight,
                self.convenience_weight
            ]
        ):
            raise ValueError("Weights cannot be negative")

        return self

class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    LIMITED = "limited"
    SOLD_OUT = "sold_out"
    UNKNOWN = "unknown"

class TravelLeg(BaseModel):
    origin: str
    destination: str

    mode: str
    operator: Optional[str] = None
    source: Optional[str] = None
    
    departure_time: datetime
    arrival_time: datetime
    last_updated: datetime | None = None
    duration_minutes: int
    price: float
    currency: str = "INR"

    transfers: int = 0
    availability: AvailabilityStatus = AvailabilityStatus.UNKNOWN

    @model_validator(mode="after")
    def validate_duration(self):
        actual_duration = int(
            (self.arrival_time - self.departure_time).total_seconds() / 60
        )

        if actual_duration != self.duration_minutes:
            raise ValueError(
                f"duration_minutes ({self.duration_minutes}) does not match "
                f"the actual travel time ({actual_duration} minutes)"
            )

        if self.arrival_time <= self.departure_time:
            raise ValueError(
                "arrival_time must be after departure_time"
            )

        return self

class Journey(BaseModel):
    origin: str
    destination: str

    legs: list[TravelLeg]
    score: float | None = None

    @property
    def total_price(self) -> float:
        return sum(leg.price for leg in self.legs)

    @property
    def total_duration_minutes(self) -> int:
        if not self.legs:
            return 0

        journey_start = self.legs[0].departure_time
        journey_end = self.legs[-1].arrival_time

        return int(
            (journey_end - journey_start).total_seconds() / 60
        )
    @property
    def total_travel_time_minutes(self) -> int:
        return sum(
        leg.duration_minutes
        for leg in self.legs
    )

    @property
    def total_waiting_time_minutes(self) -> int:
        if len(self.legs) <= 1:
            return 0

        waiting_time = 0

        for i in range(len(self.legs) - 1):
            current_leg = self.legs[i]
            next_leg = self.legs[i + 1]

            waiting_time += int(
            (
                next_leg.departure_time
                - current_leg.arrival_time
            ).total_seconds() / 60
        )

        return waiting_time

    @property
    def time_burden_minutes(self) -> float:
        return (
        self.total_travel_time_minutes
        + self.total_waiting_time_minutes
    )

    @property
    def total_transfers(self) -> int:
        return max(0, len(self.legs) - 1)

    @property
    def modes(self) -> list[str]:
        return [leg.mode for leg in self.legs]

    @model_validator(mode="after")
    def validate_legs(self):

        for i in range(len(self.legs) - 1):
            current_leg = self.legs[i]
            next_leg = self.legs[i + 1]

            if next_leg.departure_time < current_leg.arrival_time:
                raise ValueError(
                    "A journey leg cannot depart before "
                    "the previous leg arrives."
                )

        return self