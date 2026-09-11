from datetime import datetime

from app.models.travel import TravelLeg
from app.services.journey_generator import generate_journeys
from app.services.travel_data import get_all_travel_legs


# =========================================================
# HELPERS
# =========================================================

def make_leg(
    origin,
    destination,
    departure,
    arrival,
    price=1000,
    mode="test",
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
        operator="Test Operator",
        departure_time=departure_time,
        arrival_time=arrival_time,
        duration_minutes=duration,
        price=price,
    )


# =========================================================
# BASIC ROUTE GENERATION
# =========================================================

def test_generator_finds_direct_journey():

    legs = [
        make_leg(
            "A",
            "B",
            "2026-08-29T10:00:00",
            "2026-08-29T12:00:00",
        )
    ]

    journeys = generate_journeys(
        legs,
        "A",
        "B",
    )

    assert len(journeys) == 1

    journey = journeys[0]

    assert journey.origin == "A"
    assert journey.destination == "B"
    assert len(journey.legs) == 1


def test_generator_finds_multi_leg_journey():

    legs = [
        make_leg(
            "A",
            "C",
            "2026-08-29T10:00:00",
            "2026-08-29T12:00:00",
        ),
        make_leg(
            "C",
            "B",
            "2026-08-29T13:00:00",
            "2026-08-29T15:00:00",
        ),
    ]

    journeys = generate_journeys(
        legs,
        "A",
        "B",
    )

    assert len(journeys) == 1

    assert len(journeys[0].legs) == 2


# =========================================================
# TIMING VALIDATION
# =========================================================

def test_generator_rejects_impossible_connection():

    legs = [
        make_leg(
            "A",
            "C",
            "2026-08-29T10:00:00",
            "2026-08-29T15:00:00",
        ),
        make_leg(
            "C",
            "B",
            "2026-08-29T14:00:00",
            "2026-08-29T16:00:00",
        ),
    ]

    journeys = generate_journeys(
        legs,
        "A",
        "B",
    )

    assert len(journeys) == 0


def test_generator_allows_exact_connection():

    legs = [
        make_leg(
            "A",
            "C",
            "2026-08-29T10:00:00",
            "2026-08-29T12:00:00",
        ),
        make_leg(
            "C",
            "B",
            "2026-08-29T12:00:00",
            "2026-08-29T14:00:00",
        ),
    ]

    journeys = generate_journeys(
        legs,
        "A",
        "B",
    )

    assert len(journeys) == 1


def test_generator_allows_overnight_connection():

    legs = [
        make_leg(
            "A",
            "C",
            "2026-08-29T22:00:00",
            "2026-08-30T02:00:00",
        ),
        make_leg(
            "C",
            "B",
            "2026-08-30T03:00:00",
            "2026-08-30T06:00:00",
        ),
    ]

    journeys = generate_journeys(
        legs,
        "A",
        "B",
    )

    assert len(journeys) == 1


# =========================================================
# MAX LEGS
# =========================================================

def test_max_legs_is_respected():

    legs = [
        make_leg(
            "A",
            "B",
            "2026-08-29T08:00:00",
            "2026-08-29T09:00:00",
        ),
        make_leg(
            "B",
            "C",
            "2026-08-29T10:00:00",
            "2026-08-29T11:00:00",
        ),
        make_leg(
            "C",
            "D",
            "2026-08-29T12:00:00",
            "2026-08-29T13:00:00",
        ),
        make_leg(
            "D",
            "E",
            "2026-08-29T14:00:00",
            "2026-08-29T15:00:00",
        ),
    ]

    journeys = generate_journeys(
        legs,
        "A",
        "E",
        max_legs=3,
    )

    assert len(journeys) == 0


def test_four_leg_journey_allowed_when_max_legs_is_four():

    legs = [
        make_leg(
            "A",
            "B",
            "2026-08-29T08:00:00",
            "2026-08-29T09:00:00",
        ),
        make_leg(
            "B",
            "C",
            "2026-08-29T10:00:00",
            "2026-08-29T11:00:00",
        ),
        make_leg(
            "C",
            "D",
            "2026-08-29T12:00:00",
            "2026-08-29T13:00:00",
        ),
        make_leg(
            "D",
            "E",
            "2026-08-29T14:00:00",
            "2026-08-29T15:00:00",
        ),
    ]

    journeys = generate_journeys(
        legs,
        "A",
        "E",
        max_legs=4,
    )

    assert len(journeys) == 1
    assert len(journeys[0].legs) == 4


# =========================================================
# LEG REUSE / CYCLES
# =========================================================

def test_same_leg_cannot_be_reused():

    legs = [
        make_leg(
            "A",
            "B",
            "2026-08-29T08:00:00",
            "2026-08-29T09:00:00",
        ),
        make_leg(
            "B",
            "A",
            "2026-08-29T10:00:00",
            "2026-08-29T11:00:00",
        ),
    ]

    journeys = generate_journeys(
        legs,
        "A",
        "B",
        max_legs=4,
    )

    assert len(journeys) == 1

    assert len(journeys[0].legs) == 1


def test_cycles_do_not_create_infinite_routes():

    legs = [
        make_leg(
            "A",
            "B",
            "2026-08-29T08:00:00",
            "2026-08-29T09:00:00",
        ),
        make_leg(
            "B",
            "C",
            "2026-08-29T10:00:00",
            "2026-08-29T11:00:00",
        ),
        make_leg(
            "C",
            "A",
            "2026-08-29T12:00:00",
            "2026-08-29T13:00:00",
        ),
        make_leg(
            "A",
            "B",
            "2026-08-29T14:00:00",
            "2026-08-29T15:00:00",
        ),
    ]

    journeys = generate_journeys(
        legs,
        "A",
        "B",
        max_legs=4,
    )

    assert len(journeys) >= 1

    for journey in journeys:
        assert len(journey.legs) <= 4


# =========================================================
# DUPLICATE ROUTES
# =========================================================

def test_duplicate_journeys_are_removed():

    leg_a = make_leg(
        "A",
        "B",
        "2026-08-29T10:00:00",
        "2026-08-29T12:00:00",
        price=5000,
    )

    leg_b = make_leg(
        "A",
        "B",
        "2026-08-29T10:00:00",
        "2026-08-29T12:00:00",
        price=5000,
    )

    journeys = generate_journeys(
        [leg_a, leg_b],
        "A",
        "B",
    )

    assert len(journeys) == 1


# =========================================================
# NO ROUTE
# =========================================================

def test_generator_returns_empty_when_no_route_exists():

    legs = [
        make_leg(
            "A",
            "C",
            "2026-08-29T10:00:00",
            "2026-08-29T12:00:00",
        ),
        make_leg(
            "D",
            "B",
            "2026-08-29T13:00:00",
            "2026-08-29T15:00:00",
        ),
    ]

    journeys = generate_journeys(
        legs,
        "A",
        "B",
    )

    assert journeys == []


# =========================================================
# ACTUAL TRAVEL NETWORK
# =========================================================

def test_real_network_generates_jammu_mumbai_routes():

    legs = get_all_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    journeys = generate_journeys(
        legs,
        "Jammu",
        "Mumbai",
    )

    assert len(journeys) > 0


def test_real_network_has_multiple_jammu_mumbai_options():

    legs = get_all_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    journeys = generate_journeys(
        legs,
        "Jammu",
        "Mumbai",
    )

    assert len(journeys) > 1


# =========================================================
# ACTUAL NETWORK JOURNEY INTEGRITY
# =========================================================

def test_real_network_journeys_have_valid_connections():

    legs = get_all_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    journeys = generate_journeys(
        legs,
        "Jammu",
        "Mumbai",
    )

    for journey in journeys:

        for i in range(len(journey.legs) - 1):

            current_leg = journey.legs[i]
            next_leg = journey.legs[i + 1]

            assert (
                next_leg.departure_time
                >= current_leg.arrival_time
            )


def test_real_network_journeys_do_not_exceed_four_legs():

    legs = get_all_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    journeys = generate_journeys(
        legs,
        "Jammu",
        "Mumbai",
    )

    for journey in journeys:
        assert len(journey.legs) <= 4


def test_real_network_journeys_start_at_jammu_and_end_at_mumbai():

    legs = get_all_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    journeys = generate_journeys(
        legs,
        "Jammu",
        "Mumbai",
    )

    for journey in journeys:

        assert journey.legs[0].origin == "Jammu"
        assert journey.legs[-1].destination == "Mumbai"


# =========================================================
# JOURNEY CALCULATION INTEGRITY
# =========================================================

def test_generated_journey_price_matches_legs():

    legs = [
        make_leg(
            "A",
            "C",
            "2026-08-29T10:00:00",
            "2026-08-29T12:00:00",
            price=2000,
        ),
        make_leg(
            "C",
            "B",
            "2026-08-29T13:00:00",
            "2026-08-29T15:00:00",
            price=3000,
        ),
    ]

    journeys = generate_journeys(
        legs,
        "A",
        "B",
    )

    assert journeys[0].total_price == 5000


def test_generated_journey_waiting_time_is_correct():

    legs = [
        make_leg(
            "A",
            "C",
            "2026-08-29T10:00:00",
            "2026-08-29T12:00:00",
        ),
        make_leg(
            "C",
            "B",
            "2026-08-29T13:30:00",
            "2026-08-29T15:00:00",
        ),
    ]

    journeys = generate_journeys(
        legs,
        "A",
        "B",
    )

    assert journeys[0].total_waiting_time_minutes == 90


def test_generated_journey_transfer_count_is_correct():

    legs = [
        make_leg(
            "A",
            "C",
            "2026-08-29T10:00:00",
            "2026-08-29T12:00:00",
        ),
        make_leg(
            "C",
            "D",
            "2026-08-29T13:00:00",
            "2026-08-29T14:00:00",
        ),
        make_leg(
            "D",
            "B",
            "2026-08-29T15:00:00",
            "2026-08-29T16:00:00",
        ),
    ]

    journeys = generate_journeys(
        legs,
        "A",
        "B",
    )

    assert journeys[0].total_transfers == 2