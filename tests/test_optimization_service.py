from datetime import datetime

from app.models.travel import TravelRequest
from app.services.data_manager import TravelDataManager
from app.services.optimization_service import OptimizationService
from app.services.travel_data import DummyTravelDataProvider


def create_service():
    data_manager = TravelDataManager(
        providers=[
            DummyTravelDataProvider(),
        ]
    )

    return OptimizationService(
        travel_data_manager=data_manager
    )


def create_request(
    origin="Jammu",
    destination="Delhi",
    budget=None,
):
    return TravelRequest(
        origin=origin,
        destination=destination,
        budget=budget,
        cost_weight=0.5,
        time_weight=0.5,
        convenience_weight=0.0,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
    )


def test_optimization_service_returns_recommendation():

    service = create_service()
    request = create_request()

    result = service.optimize(request)

    assert result.recommendation is not None
    assert result.alternatives is not None
    assert isinstance(result.alternatives, list)


def test_optimization_service_returns_journey_objects():

    service = create_service()
    request = create_request()

    result = service.optimize(request)

    recommendation = result.recommendation

    assert recommendation is not None
    assert recommendation.origin == "Jammu"
    assert recommendation.destination == "Delhi"
    assert len(recommendation.legs) > 0


def test_optimization_service_respects_budget():

    service = create_service()
    request = create_request(
        budget=100
    )

    result = service.optimize(request)

    assert result.recommendation is None
    assert result.alternatives == []


def test_optimization_service_handles_unknown_route():

    service = create_service()

    request = create_request(
        origin="Jammu",
        destination="London",
    )

    result = service.optimize(request)

    assert result.recommendation is None
    assert result.alternatives == []

    assert result.explanation == (
        "We don't currently have travel data for "
        "Jammu → London."
    )