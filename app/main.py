from fastapi import FastAPI

from app.models.travel import TravelRequest, Journey
from app.models.api import OptimizeResponse

from app.services.data_manager import TravelDataManager
from app.services.travel_data import DummyTravelDataProvider
from app.services.optimization_service import OptimizationService


app = FastAPI(title="Travel Optimiser")


travel_data_manager = TravelDataManager(
    providers=[
        DummyTravelDataProvider(),
    ]
)


optimization_service = OptimizationService(
    travel_data_manager=travel_data_manager
)


def serialize_journey(journey: Journey) -> dict:
    return {
        "score": journey.score,
        "total_price": journey.total_price,
        "total_duration_minutes": journey.total_duration_minutes,
        "total_transfers": journey.total_transfers,
        "modes": journey.modes,
        "total_travel_time_minutes": (
            journey.total_travel_time_minutes
        ),
        "total_waiting_time_minutes": (
            journey.total_waiting_time_minutes
        ),
        "legs": [
            {
                "origin": leg.origin,
                "destination": leg.destination,
                "mode": leg.mode,
                "operator": leg.operator,
                "departure_time": leg.departure_time,
                "arrival_time": leg.arrival_time,
                "duration_minutes": leg.duration_minutes,
                "price": leg.price,
                "currency": leg.currency,
                "transfers": leg.transfers,
                "availability": leg.availability.value,
                "last_updated": leg.last_updated,
                "source": leg.source,
            }
            for leg in journey.legs
        ],
    }


@app.get("/")
def home():
    return {
        "message": "Travel Optimiser is alive!"
    }


@app.post(
    "/optimize",
    response_model=OptimizeResponse,
)
def optimize_travel(request: TravelRequest):

    result = optimization_service.optimize(request)

    recommendation = result.recommendation
    alternatives = result.alternatives

    return {
        "recommendation": (
            serialize_journey(recommendation)
            if recommendation is not None
            else None
        ),
        "explanation": result.explanation,
        "alternatives": [
            serialize_journey(journey)
            for journey in alternatives
        ],
    }