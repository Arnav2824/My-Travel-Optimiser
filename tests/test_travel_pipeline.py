from datetime import datetime

from app.models.travel import TravelRequest
from app.services.travel_data import get_all_travel_legs
from app.services.journey_generator import generate_journeys
from app.services.journey_optimiser import (
    filter_dominated_journeys,
    filter_journeys,
    rank_journeys,
    filter_available_journeys,
    filter_fresh_journeys,
)


def run_pipeline(request: TravelRequest):
    """
    Runs the same core decision pipeline used by the application.
    """

    legs = get_all_travel_legs(
        travel_date=request.travel_date
    )

    journeys = generate_journeys(
        legs=legs,
        origin=request.origin,
        destination=request.destination,
    )

    journeys = filter_available_journeys(
        journeys,
    )

    journeys = filter_fresh_journeys(
        journeys,
    )

    journeys = filter_journeys(
        journeys,
        request,
    )

    journeys = filter_dominated_journeys(
        journeys,
    )

    journeys = rank_journeys(
        journeys,
        request,
    )

    return journeys


# =========================================================
# BASIC END-TO-END TEST
# =========================================================

def test_jammu_to_mumbai_pipeline_finds_journeys():

    request = TravelRequest(
        origin="Jammu",
        destination="Mumbai",
        budget=12000,
        cost_weight=0.5,
        time_weight=0.3,
        convenience_weight=0.2,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
        earliest_departure=datetime.fromisoformat(
            "2026-08-29T14:00:00"
        ),
        latest_departure=datetime.fromisoformat(
            "2026-08-29T17:00:00"
        ),
        max_transfers=3,
    )

    journeys = run_pipeline(request)

    assert len(journeys) > 0


# =========================================================
# RECOMMENDATION MUST SATISFY CONSTRAINTS
# =========================================================

def test_recommendation_respects_budget():

    request = TravelRequest(
        origin="Jammu",
        destination="Mumbai",
        budget=6000,
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
    )

    journeys = run_pipeline(request)

    assert len(journeys) > 0

    recommendation = journeys[0]

    assert recommendation.total_price <= 6000


def test_recommendation_respects_transfer_limit():

    request = TravelRequest(
        origin="Jammu",
        destination="Mumbai",
        max_transfers=1,
        cost_weight=0.5,
        time_weight=0.5,
        convenience_weight=0.0,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
    )

    journeys = run_pipeline(request)

    assert len(journeys) > 0

    for journey in journeys:
        assert journey.total_transfers <= 1


# =========================================================
# DEPARTURE / ARRIVAL CONSTRAINTS
# =========================================================

def test_recommendation_respects_departure_window():

    earliest = datetime.fromisoformat(
        "2026-08-29T14:00:00"
    )

    latest = datetime.fromisoformat(
        "2026-08-29T17:00:00"
    )

    request = TravelRequest(
        origin="Jammu",
        destination="Mumbai",
        cost_weight=0.5,
        time_weight=0.5,
        convenience_weight=0.0,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
        earliest_departure=earliest,
        latest_departure=latest,
    )

    journeys = run_pipeline(request)

    assert len(journeys) > 0

    for journey in journeys:

        departure = journey.legs[0].departure_time

        assert departure >= earliest
        assert departure <= latest


def test_recommendation_respects_latest_arrival():

    latest_arrival = datetime.fromisoformat(
        "2026-08-30T12:00:00"
    )

    request = TravelRequest(
        origin="Jammu",
        destination="Mumbai",
        cost_weight=0.5,
        time_weight=0.5,
        convenience_weight=0.0,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
        latest_arrival=latest_arrival,
    )

    journeys = run_pipeline(request)

    assert len(journeys) > 0

    for journey in journeys:

        arrival = journey.legs[-1].arrival_time

        assert arrival <= latest_arrival


# =========================================================
# JOURNEY INTEGRITY
# =========================================================

def test_generated_journeys_are_temporally_valid():

    request = TravelRequest(
        origin="Jammu",
        destination="Mumbai",
        cost_weight=0.5,
        time_weight=0.5,
        convenience_weight=0.0,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
    )

    journeys = run_pipeline(request)

    assert len(journeys) > 0

    for journey in journeys:

        for i in range(len(journey.legs) - 1):

            current_leg = journey.legs[i]
            next_leg = journey.legs[i + 1]

            assert (
                next_leg.departure_time
                >= current_leg.arrival_time
            )


def test_generated_journeys_start_and_end_correctly():

    request = TravelRequest(
        origin="Jammu",
        destination="Mumbai",
        cost_weight=0.5,
        time_weight=0.5,
        convenience_weight=0.0,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
    )

    journeys = run_pipeline(request)

    assert len(journeys) > 0

    for journey in journeys:

        assert journey.legs[0].origin == "Jammu"
        assert journey.legs[-1].destination == "Mumbai"


# =========================================================
# RANKING INTEGRITY
# =========================================================

def test_ranked_journeys_are_sorted_by_score():

    request = TravelRequest(
        origin="Jammu",
        destination="Mumbai",
        cost_weight=0.5,
        time_weight=0.5,
        convenience_weight=0.0,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
    )

    journeys = run_pipeline(request)

    assert len(journeys) > 0

    scores = [
        journey.score
        for journey in journeys
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_best_journey_has_highest_score():

    request = TravelRequest(
        origin="Jammu",
        destination="Mumbai",
        cost_weight=0.5,
        time_weight=0.5,
        convenience_weight=0.0,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
    )

    journeys = run_pipeline(request)

    assert len(journeys) > 0

    recommendation = journeys[0]

    assert recommendation.score == max(
        journey.score
        for journey in journeys
    )


# =========================================================
# DIFFERENT USER PREFERENCES
# =========================================================

def test_cost_focused_user_gets_low_cost_option():

    request = TravelRequest(
        origin="Jammu",
        destination="Mumbai",
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
    )

    journeys = run_pipeline(request)

    assert len(journeys) > 0

    recommendation = journeys[0]

    assert recommendation.total_price == min(
        journey.total_price
        for journey in journeys
    )


def test_time_focused_user_gets_fast_option():

    request = TravelRequest(
        origin="Jammu",
        destination="Mumbai",
        cost_weight=0.0,
        time_weight=1.0,
        convenience_weight=0.0,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
    )

    journeys = run_pipeline(request)

    assert len(journeys) > 0

    recommendation = journeys[0]

    assert recommendation.total_duration_minutes == min(
        journey.total_duration_minutes
        for journey in journeys
    )


def test_convenience_focused_user_gets_low_transfer_option():

    request = TravelRequest(
        origin="Jammu",
        destination="Mumbai",
        cost_weight=0.0,
        time_weight=0.0,
        convenience_weight=1.0,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
    )

    journeys = run_pipeline(request)

    assert len(journeys) > 0

    recommendation = journeys[0]

    assert recommendation.total_transfers == min(
        journey.total_transfers
        for journey in journeys
    )


# =========================================================
# EXTREME VALUE-OF-TIME TEST
# =========================================================

def test_extremely_high_value_of_time_prefers_fast_journey():

    request = TravelRequest(
        origin="Jammu",
        destination="Mumbai",
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
        travel_time_value=10000,
        waiting_time_value=10000,
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
    )

    journeys = run_pipeline(request)

    assert len(journeys) > 0

    recommendation = journeys[0]

    assert recommendation.total_duration_minutes == min(
        journey.total_duration_minutes
        for journey in journeys
    )