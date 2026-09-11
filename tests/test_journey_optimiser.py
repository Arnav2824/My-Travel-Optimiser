from datetime import datetime, timedelta

import pytest

from app.models.travel import (
    TravelLeg,
    Journey,
    TravelRequest,
    AvailabilityStatus,
)
from app.services.journey_optimiser import (
    filter_available_journeys,
    filter_fresh_journeys,
    filter_dominated_journeys,
    filter_journeys,
    rank_journeys,
)



# =========================================================
# HELPERS
# =========================================================

def make_leg(
    origin,
    destination,
    departure,
    arrival,
    price,
    mode="test",
    operator="Test Operator",
):
    departure_time = datetime.fromisoformat(departure)
    arrival_time = datetime.fromisoformat(arrival)

    duration = int(
        (arrival_time - departure_time).total_seconds() / 60
    )

    return TravelLeg(
        origin=origin,
        destination=destination,
        mode=mode,
        operator=operator,
        departure_time=departure_time,
        arrival_time=arrival_time,
        duration_minutes=duration,
        price=price,
    )


def make_direct_journey(
    price,
    departure,
    arrival,
    transfers=0,
):
    leg = make_leg(
        origin="A",
        destination="B",
        departure=departure,
        arrival=arrival,
        price=price,
    )

    return Journey(
        origin="A",
        destination="B",
        legs=[leg],
    )


# =========================================================
# FILTER TESTS
# =========================================================

def test_budget_filter_removes_expensive_journeys():

    journeys = [
        make_direct_journey(
            price=5000,
            departure="2026-08-29T10:00:00",
            arrival="2026-08-29T12:00:00",
        ),
        make_direct_journey(
            price=10000,
            departure="2026-08-29T10:00:00",
            arrival="2026-08-29T12:00:00",
        ),
    ]

    request = TravelRequest(
        origin="A",
        destination="B",
        budget=6000,
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
    )

    result = filter_journeys(journeys, request)

    assert len(result) == 1
    assert result[0].total_price == 5000


def test_max_transfer_filter_removes_complex_journeys():

    direct = make_direct_journey(
        price=5000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    leg1 = make_leg(
        "A",
        "C",
        "2026-08-29T10:00:00",
        "2026-08-29T12:00:00",
        2000,
    )

    leg2 = make_leg(
        "C",
        "B",
        "2026-08-29T13:00:00",
        "2026-08-29T15:00:00",
        2000,
    )

    two_leg = Journey(
        origin="A",
        destination="B",
        legs=[leg1, leg2],
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        max_transfers=0,
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
    )

    result = filter_journeys(
        [direct, two_leg],
        request,
    )

    assert len(result) == 1
    assert result[0].total_transfers == 0


def test_earliest_departure_filter():

    journeys = [
        make_direct_journey(
            5000,
            "2026-08-29T09:00:00",
            "2026-08-29T11:00:00",
        ),
        make_direct_journey(
            6000,
            "2026-08-29T15:00:00",
            "2026-08-29T17:00:00",
        ),
    ]

    request = TravelRequest(
        origin="A",
        destination="B",
        earliest_departure=datetime.fromisoformat(
            "2026-08-29T12:00:00"
        ),
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
    )

    result = filter_journeys(journeys, request)

    assert len(result) == 1
    assert result[0].total_price == 6000


def test_latest_departure_filter():

    journeys = [
        make_direct_journey(
            5000,
            "2026-08-29T09:00:00",
            "2026-08-29T11:00:00",
        ),
        make_direct_journey(
            6000,
            "2026-08-29T15:00:00",
            "2026-08-29T17:00:00",
        ),
    ]

    request = TravelRequest(
        origin="A",
        destination="B",
        latest_departure=datetime.fromisoformat(
            "2026-08-29T12:00:00"
        ),
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
    )

    result = filter_journeys(journeys, request)

    assert len(result) == 1
    assert result[0].total_price == 5000


def test_latest_arrival_filter():

    journeys = [
        make_direct_journey(
            5000,
            "2026-08-29T09:00:00",
            "2026-08-29T11:00:00",
        ),
        make_direct_journey(
            6000,
            "2026-08-29T12:00:00",
            "2026-08-29T18:00:00",
        ),
    ]

    request = TravelRequest(
        origin="A",
        destination="B",
        latest_arrival=datetime.fromisoformat(
            "2026-08-29T12:00:00"
        ),
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
    )

    result = filter_journeys(journeys, request)

    assert len(result) == 1
    assert result[0].total_price == 5000


# =========================================================
# DOMINANCE TESTS
# =========================================================

def test_dominated_journey_is_removed():

    best = make_direct_journey(
        price=5000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    dominated = make_direct_journey(
        price=7000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T14:00:00",
    )

    result = filter_dominated_journeys(
        [best, dominated]
    )

    assert len(result) == 1
    assert result[0].total_price == 5000


def test_pareto_optimal_journeys_are_preserved():

    cheap = make_direct_journey(
        price=4000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T18:00:00",
    )

    fast = make_direct_journey(
        price=9000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    result = filter_dominated_journeys(
        [cheap, fast]
    )

    assert len(result) == 2


# =========================================================
# BASIC RANKING TESTS
# =========================================================

def test_cost_weight_prefers_cheaper_journey():

    cheap = make_direct_journey(
        price=4000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T18:00:00",
    )

    expensive = make_direct_journey(
        price=9000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
    )

    result = rank_journeys(
        [cheap, expensive],
        request,
    )

    assert result[0].total_price == 4000


def test_time_weight_prefers_faster_journey():

    cheap = make_direct_journey(
        price=4000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T18:00:00",
    )

    fast = make_direct_journey(
        price=9000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=0.0,
        time_weight=1.0,
        convenience_weight=0.0,
    )

    result = rank_journeys(
        [cheap, fast],
        request,
    )

    assert result[0].total_price == 9000


# =========================================================
# VALUE OF TIME TESTS
# =========================================================

def test_high_value_of_time_prefers_faster_journey():

    cheap = make_direct_journey(
        price=4000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T18:00:00",
    )

    fast = make_direct_journey(
        price=9000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
        value_of_time=1000,
    )

    result = rank_journeys(
        [cheap, fast],
        request,
    )

    assert result[0].total_price == 9000


def test_zero_value_of_time_prefers_cheaper_journey():

    cheap = make_direct_journey(
        price=4000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T18:00:00",
    )

    fast = make_direct_journey(
        price=9000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
        value_of_time=0,
    )

    result = rank_journeys(
        [cheap, fast],
        request,
    )

    assert result[0].total_price == 4000


# =========================================================
# SEPARATE TRAVEL / WAITING VALUE
# =========================================================

def test_travel_time_value_affects_ranking():

    cheap_slow = make_direct_journey(
        price=4000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T18:00:00",
    )

    expensive_fast = make_direct_journey(
        price=9000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
        travel_time_value=1000,
    )

    result = rank_journeys(
        [cheap_slow, expensive_fast],
        request,
    )

    assert result[0].total_price == 9000


def test_waiting_time_value_affects_ranking():

    low_wait = Journey(
        origin="A",
        destination="B",
        legs=[
            make_leg(
                "A",
                "C",
                "2026-08-29T10:00:00",
                "2026-08-29T12:00:00",
                3000,
            ),
            make_leg(
                "C",
                "B",
                "2026-08-29T12:30:00",
                "2026-08-29T14:30:00",
                3000,
            ),
        ],
    )

    high_wait = Journey(
        origin="A",
        destination="B",
        legs=[
            make_leg(
                "A",
                "C",
                "2026-08-29T10:00:00",
                "2026-08-29T12:00:00",
                2500,
            ),
            make_leg(
                "C",
                "B",
                "2026-08-29T16:30:00",
                "2026-08-29T18:30:00",
                2500,
            ),
        ],
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
        travel_time_value=100,
        waiting_time_value=2000,
    )

    result = rank_journeys(
        [low_wait, high_wait],
        request,
    )

    assert result[0] is low_wait


# =========================================================
# EDGE CASES
# =========================================================

def test_empty_journey_list_returns_empty():

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
    )

    assert rank_journeys([], request) == []


def test_empty_dominance_input_returns_empty():

    assert filter_dominated_journeys([]) == []


def test_empty_filter_input_returns_empty():

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
    )

    assert filter_journeys([], request) == []


def test_equal_journeys_are_not_considered_dominated():

    journey_a = make_direct_journey(
        price=5000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    journey_b = make_direct_journey(
        price=5000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    result = filter_dominated_journeys(
        [journey_a, journey_b]
    )

    assert len(result) == 2


# =========================================================
# REQUEST VALIDATION TESTS
# =========================================================

def test_weights_must_sum_to_one():

    with pytest.raises(ValueError):

        TravelRequest(
            origin="A",
            destination="B",
            cost_weight=0.5,
            time_weight=0.5,
            convenience_weight=0.5,
        )


def test_negative_weights_are_rejected():

    with pytest.raises(ValueError):

        TravelRequest(
            origin="A",
            destination="B",
            cost_weight=-0.1,
            time_weight=0.6,
            convenience_weight=0.5,
        )

def test_dominance_does_not_remove_journey_with_better_travel_time_but_more_waiting():

    # Journey A:
    # Cheaper/equal price
    # Less actual travel time
    # More waiting
    journey_a = Journey(
        origin="A",
        destination="B",
        legs=[
            make_leg(
                "A",
                "C",
                "2026-08-29T10:00:00",
                "2026-08-29T15:00:00",
                price=2500,
            ),
            make_leg(
                "C",
                "B",
                "2026-08-29T18:00:00",
                "2026-08-29T20:00:00",
                price=2500,
            ),
        ],
    )

    # Journey B:
    # Same price
    # More actual travel time
    # No waiting
    journey_b = Journey(
        origin="A",
        destination="B",
        legs=[
            make_leg(
                "A",
                "C",
                "2026-08-29T10:00:00",
                "2026-08-29T16:00:00",
                price=2500,
            ),
            make_leg(
                "C",
                "B",
                "2026-08-29T16:00:00",
                "2026-08-29T18:00:00",
                price=2500,
            ),
        ],
    )

    result = filter_dominated_journeys(
        [journey_a, journey_b]
    )

    # Neither journey should dominate the other:
    #
    # A:
    #   travel = 420 min
    #   waiting = 180 min
    #   total duration = 600 min
    #
    # B:
    #   travel = 480 min
    #   waiting = 0 min
    #   total duration = 480 min
    #
    # B has lower total duration,
    # but A has lower actual travel time.
    #
    # Therefore both should remain Pareto-optimal.

    assert len(result) == 2

# =========================================================
# BOUNDARY / ADVERSARIAL TESTS
# =========================================================

def test_budget_filter_allows_journey_exactly_at_budget():

    journey = make_direct_journey(
        price=5000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        budget=5000,
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
    )

    result = filter_journeys([journey], request)

    assert len(result) == 1
    assert result[0].total_price == 5000


def test_earliest_departure_allows_exact_boundary():

    journey = make_direct_journey(
        price=5000,
        departure="2026-08-29T12:00:00",
        arrival="2026-08-29T14:00:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        earliest_departure=datetime.fromisoformat(
            "2026-08-29T12:00:00"
        ),
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
    )

    result = filter_journeys([journey], request)

    assert len(result) == 1


def test_latest_departure_allows_exact_boundary():

    journey = make_direct_journey(
        price=5000,
        departure="2026-08-29T12:00:00",
        arrival="2026-08-29T14:00:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        latest_departure=datetime.fromisoformat(
            "2026-08-29T12:00:00"
        ),
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
    )

    result = filter_journeys([journey], request)

    assert len(result) == 1


def test_latest_arrival_allows_exact_boundary():

    journey = make_direct_journey(
        price=5000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        latest_arrival=datetime.fromisoformat(
            "2026-08-29T12:00:00"
        ),
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
    )

    result = filter_journeys([journey], request)

    assert len(result) == 1


def test_zero_transfer_journey_beats_multi_transfer_when_convenience_is_maximized():

    direct = make_direct_journey(
        price=5000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    leg1 = make_leg(
        "A",
        "C",
        "2026-08-29T10:00:00",
        "2026-08-29T11:00:00",
        2500,
    )

    leg2 = make_leg(
        "C",
        "B",
        "2026-08-29T11:30:00",
        "2026-08-29T12:00:00",
        2500,
    )

    multi_leg = Journey(
        origin="A",
        destination="B",
        legs=[leg1, leg2],
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=0.0,
        time_weight=0.0,
        convenience_weight=1.0,
    )

    result = rank_journeys(
        [direct, multi_leg],
        request,
    )

    assert result[0] is direct


def test_single_journey_gets_full_score():

    journey = make_direct_journey(
        price=5000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T12:00:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
    )

    result = rank_journeys([journey], request)

    assert len(result) == 1
    assert result[0].score == 1.0


def test_extreme_travel_time_value_can_overcome_large_price_difference():

    cheap = make_direct_journey(
        price=1000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T20:00:00",
    )

    fast = make_direct_journey(
        price=10000,
        departure="2026-08-29T10:00:00",
        arrival="2026-08-29T11:00:00",
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
        travel_time_value=2000,
    )

    result = rank_journeys(
        [cheap, fast],
        request,
    )

    assert result[0] is fast


def test_extreme_waiting_time_value_prefers_low_waiting_journey():

    low_wait = Journey(
        origin="A",
        destination="B",
        legs=[
            make_leg(
                "A",
                "C",
                "2026-08-29T10:00:00",
                "2026-08-29T12:00:00",
                5000,
            ),
            make_leg(
                "C",
                "B",
                "2026-08-29T12:30:00",
                "2026-08-29T14:30:00",
                5000,
            ),
        ],
    )

    high_wait = Journey(
        origin="A",
        destination="B",
        legs=[
            make_leg(
                "A",
                "C",
                "2026-08-29T10:00:00",
                "2026-08-29T12:00:00",
                4500,
            ),
            make_leg(
                "C",
                "B",
                "2026-08-29T18:30:00",
                "2026-08-29T20:30:00",
                4500,
            ),
        ],
    )

    request = TravelRequest(
        origin="A",
        destination="B",
        cost_weight=1.0,
        time_weight=0.0,
        convenience_weight=0.0,
        travel_time_value=0,
        waiting_time_value=5000,
    )

    result = rank_journeys(
        [low_wait, high_wait],
        request,
    )

    assert result[0] is low_wait

def test_available_journey_survives():
    leg = make_leg(
            "A",
            "B",
            "2026-08-29T10:00:00",
            "2026-08-29T12:00:00",
            5000,
    )
    leg.availability = AvailabilityStatus.AVAILABLE

    journey = Journey(
        origin="A",
        destination="B",
        legs=[leg],
    )

    result = filter_available_journeys([journey])

    assert result == [journey]


def test_sold_out_journey_is_removed():
    leg = make_leg(
        "A",
        "B",
        "2026-08-29T10:00:00",
        "2026-08-29T12:00:00",
        5000,
    )
    leg.availability = AvailabilityStatus.SOLD_OUT

    journey = Journey(
        origin="A",
        destination="B",
        legs=[leg],
    )

    result = filter_available_journeys([journey])

    assert result == []


def test_journey_removed_if_one_leg_is_sold_out():
    first_leg = make_leg(
        "A",
        "C",
        "2026-08-29T10:00:00",
        "2026-08-29T12:00:00",
        5000,
    )
    first_leg.availability = AvailabilityStatus.AVAILABLE

    second_leg = make_leg(
        "C",
        "B",
        "2026-08-29T13:00:00",
        "2026-08-29T15:00:00",
        5000,
    )
    second_leg.availability = AvailabilityStatus.SOLD_OUT

    journey = Journey(
        origin="A",
        destination="B",
        legs=[first_leg, second_leg],
    )

    result = filter_available_journeys([journey])

    assert result == []


def test_limited_availability_journey_survives():
    leg = make_leg(
        "A",
        "B",
        "2026-08-29T10:00:00",
        "2026-08-29T12:00:00",
        5000,
    )
    leg.availability = AvailabilityStatus.LIMITED

    journey = Journey(
        origin="A",
        destination="B",
        legs=[leg],
    )

    result = filter_available_journeys([journey])

    assert result == [journey]


def test_unknown_availability_journey_is_removed():
    leg = make_leg(
        "A",
        "B",
        "2026-08-29T10:00:00",
        "2026-08-29T12:00:00",
        5000,
    )
    leg.availability = AvailabilityStatus.UNKNOWN

    journey = Journey(
        origin="A",
        destination="B",
        legs=[leg],
    )

    result = filter_available_journeys([journey])

    assert result == []


def test_empty_journey_list_returns_empty():
    result = filter_available_journeys([])

    assert result == []


def test_fresh_journey_survives():
    leg = make_leg(
        "Jammu",
        "Delhi",
        "2026-08-29T10:00:00",
        "2026-08-29T11:00:00",
        3000,
    )
    leg.last_updated = datetime.now()

    journey = Journey(
        origin="Jammu",
        destination="Delhi",
        legs=[leg],
    )

    result = filter_fresh_journeys([journey])

    assert result == [journey]


def test_stale_journey_is_removed():
    leg = make_leg(
        "Jammu",
        "Delhi",
        "2026-08-29T10:00:00",
        "2026-08-29T11:00:00",
        3000,
    )
    leg.last_updated = datetime.now() - timedelta(minutes=31)

    journey = Journey(
        origin="Jammu",
        destination="Delhi",
        legs=[leg],
    )

    result = filter_fresh_journeys([journey])

    assert result == []


def test_journey_with_missing_timestamp_is_removed():
    leg = make_leg(
        "Jammu",
        "Delhi",
        "2026-08-29T10:00:00",
        "2026-08-29T11:00:00",
        3000,
    )
    leg.last_updated = None

    journey = Journey(
        origin="Jammu",
        destination="Delhi",
        legs=[leg],
    )

    result = filter_fresh_journeys([journey])

    assert result == []


def test_journey_removed_if_one_leg_is_stale():
    leg1 = make_leg(
        "Jammu",
        "Delhi",
        "2026-08-29T10:00:00",
        "2026-08-29T11:00:00",
        3000,
    )
    leg2 = make_leg(
        "Delhi",
        "Mumbai",
        "2026-08-29T13:00:00",
        "2026-08-29T15:00:00",
        5000,
    )

    leg1.last_updated = datetime.now()
    leg2.last_updated = datetime.now() - timedelta(minutes=31)

    journey = Journey(
        origin="Jammu",
        destination="Mumbai",
        legs=[leg1, leg2],
    )

    result = filter_fresh_journeys([journey])

    assert result == []
