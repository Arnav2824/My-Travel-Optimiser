from datetime import datetime

from app.models.travel import Journey, TravelLeg, TravelRequest
from app.services.recommendation_explainer import (
    explain_recommendation,
)


def make_journey(
    price,
    departure,
    arrival,
):
    departure_time = datetime.fromisoformat(departure)
    arrival_time = datetime.fromisoformat(arrival)

    leg = TravelLeg(
        origin="A",
        destination="B",
        mode="test",
        operator="Test Operator",
        departure_time=departure_time,
        arrival_time=arrival_time,
        duration_minutes=int(
            (arrival_time - departure_time).total_seconds() / 60
        ),
        price=price,
    )

    return Journey(
        origin="A",
        destination="B",
        legs=[leg],
    )


def test_explanation_mentions_key_price_and_time_tradeoff():

    recommendation = make_journey(
        price=1200,
        departure="2026-08-29T15:00:00",
        arrival="2026-08-29T19:00:00",
    )

    cheap = make_journey(
        price=900,
        departure="2026-08-29T16:00:00",
        arrival="2026-08-29T20:30:00",
    )

    fast = make_journey(
        price=3000,
        departure="2026-08-29T18:00:00",
        arrival="2026-08-29T19:30:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=0.5,
        time_weight=0.5,
        convenience_weight=0.0,
    )

    explanation = explain_recommendation(
        recommendation=recommendation,
        alternatives=[cheap, fast],
        request=request,
    )

    assert "₹300" in explanation
    assert "30 minutes" in explanation
    assert "₹1800" in explanation
    assert "150 minutes" in explanation

def test_explanation_when_only_one_journey_exists():

    recommendation = make_journey(
        price=1200,
        departure="2026-08-29T15:00:00",
        arrival="2026-08-29T19:00:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=0.5,
        time_weight=0.5,
        convenience_weight=0.0,
    )

    explanation = explain_recommendation(
        recommendation=recommendation,
        alternatives=[],
        request=request,
    )

    assert explanation == (
        "Recommended because it is the only feasible journey."
    )


def test_explanation_mentions_budget_constraint():

    recommendation = make_journey(
        price=1200,
        departure="2026-08-29T15:00:00",
        arrival="2026-08-29T19:00:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        budget=1500,
        cost_weight=0.5,
        time_weight=0.5,
        convenience_weight=0.0,
    )

    explanation = explain_recommendation(
        recommendation=recommendation,
        alternatives=[],
        request=request,
    )

    assert "within your ₹1500 budget" in explanation