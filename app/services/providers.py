from abc import ABC, abstractmethod

from app.models.travel import TravelLeg


class TravelDataProvider(ABC):

    name: str = "unknown"
    priority: int = 100

    @abstractmethod
    def get_travel_legs(
        self,
        travel_date=None,
        mode=None,
    ) -> list[TravelLeg]:
        pass