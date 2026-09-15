from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.models.travel import AvailabilityStatus


client = TestClient(app)


def test_optimize_returns_no_bookable_journeys_when_all_options_are_unavailable(
    monkeypatch,
):

    from app import main

    original_get_travel_legs = (
        main.travel_data_manager.get_travel_legs
    )

    def unavailable_legs(travel_date=None, mode=None):

        legs = original_get_travel_legs(
            travel_date=travel_date,
            mode=mode,
        )

        for leg in legs:
            leg.availability = AvailabilityStatus.SOLD_OUT

        return legs

    monkeypatch.setattr(
        main.travel_data_manager,
        "get_travel_legs",
        unavailable_legs,
    )

    response = client.post(
        "/optimize",
        json={
            "origin": "Jammu",
            "destination": "Mumbai",
            "cost_weight": 0.5,
            "time_weight": 0.5,
            "convenience_weight": 0.0,
            "travel_date": "2026-08-29T00:00:00",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["recommendation"] is None

    assert data["explanation"] == (
        "Travel options exist for this route, "
        "but there are currently no bookable journeys available."
    )

    assert data["alternatives"] == []

def test_optimize_returns_valid_journey_response():

    response = client.post(
        "/optimize",
        json={
            "origin": "Jammu",
            "destination": "Delhi",
            "cost_weight": 0.5,
            "time_weight": 0.5,
            "convenience_weight": 0.0,
            "travel_date": "2026-08-29T00:00:00",
        },
    )

    assert response.status_code == 200

    data = response.json()

    # Top-level response structure
    assert "recommendation" in data
    assert "explanation" in data
    assert "alternatives" in data

    # Recommendation exists
    recommendation = data["recommendation"]

    assert recommendation is not None

    # Journey-level fields
    assert "score" in recommendation
    assert "total_price" in recommendation
    assert "total_duration_minutes" in recommendation
    assert "total_transfers" in recommendation
    assert "modes" in recommendation
    assert "total_travel_time_minutes" in recommendation
    assert "total_waiting_time_minutes" in recommendation
    assert "legs" in recommendation

    # At least one leg should exist
    assert len(recommendation["legs"]) > 0

    # Leg-level fields
    leg = recommendation["legs"][0]

    assert "origin" in leg
    assert "destination" in leg
    assert "mode" in leg
    assert "operator" in leg
    assert "departure_time" in leg
    assert "arrival_time" in leg
    assert "duration_minutes" in leg
    assert "price" in leg
    assert "currency" in leg
    assert "transfers" in leg
    assert "availability" in leg
    assert "last_updated" in leg
    assert "source" in leg

    # Alternatives should follow the same journey structure
    for alternative in data["alternatives"]:
        assert "score" in alternative
        assert "total_price" in alternative
        assert "legs" in alternative

def test_optimize_returns_no_recommendation_when_constraints_match_nothing():

    response = client.post(
        "/optimize",
        json={
            "origin": "Jammu",
            "destination": "Delhi",
            "budget": 100,
            "cost_weight": 0.5,
            "time_weight": 0.5,
            "convenience_weight": 0.0,
            "travel_date": "2026-08-29T00:00:00",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["recommendation"] is None

    assert data["explanation"] == (
        "No journey matches your current requirements. "
        "Try increasing your budget, allowing more transfers, "
        "or expanding your departure window."
    )

    assert data["alternatives"] == []