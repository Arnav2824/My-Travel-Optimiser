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