from datetime import datetime
from app.models.travel import TravelLeg
from app.services.travel_data import DummyTravelDataProvider


def test_dummy_provider_returns_travel_legs():

    provider = DummyTravelDataProvider()

    legs = provider.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    assert len(legs) > 0

    assert all(
        hasattr(leg, "origin")
        and hasattr(leg, "destination")
        and hasattr(leg, "availability")
        and hasattr(leg, "last_updated")
        for leg in legs
    )

def test_dummy_provider_filters_by_mode():

    provider = DummyTravelDataProvider()

    legs = provider.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
        mode="flight",
    )

    assert len(legs) > 0

    assert all(
        leg.mode == "flight"
        for leg in legs
    )


def test_data_manager_combines_provider_results():

    from app.services.data_manager import TravelDataManager

    provider_1 = DummyTravelDataProvider()
    provider_2 = DummyTravelDataProvider()

    manager = TravelDataManager(
        providers=[
            provider_1,
            provider_2,
        ]
    )

    legs = manager.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    single_provider_legs = provider_1.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    assert len(legs) == len(single_provider_legs)

def test_data_manager_passes_mode_to_providers():

    from app.services.data_manager import TravelDataManager

    provider = DummyTravelDataProvider()

    manager = TravelDataManager(
        providers=[provider]
    )

    legs = manager.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
        mode="flight",
    )

    assert len(legs) > 0

    assert all(
        leg.mode == "flight"
        for leg in legs
    )

def test_data_manager_continues_when_provider_fails():

    from app.services.data_manager import TravelDataManager

    class FailingProvider:

        def get_travel_legs(
            self,
            travel_date=None,
            mode=None,
        ):
            raise RuntimeError("Provider failed")

    working_provider = DummyTravelDataProvider()

    manager = TravelDataManager(
        providers=[
            FailingProvider(),
            working_provider,
        ]
    )

    legs = manager.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    expected_legs = working_provider.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    assert len(legs) == len(expected_legs)

def test_data_manager_removes_duplicate_legs():

    from app.services.data_manager import TravelDataManager

    provider = DummyTravelDataProvider()

    manager = TravelDataManager(
        providers=[provider, provider]
    )

    legs = manager.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    expected_legs = provider.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    assert len(legs) == len(expected_legs)

def test_data_manager_keeps_different_legs():

    from app.services.data_manager import TravelDataManager

    provider_1 = DummyTravelDataProvider()
    provider_2 = DummyTravelDataProvider()

    manager = TravelDataManager(
        providers=[provider_1, provider_2]
    )

    legs_1 = provider_1.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    legs_2 = provider_2.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    # Modify one leg so it represents a genuinely different option.
    legs_2[0].price += 500

    class CustomProvider:

        def get_travel_legs(
            self,
            travel_date=None,
            mode=None,
        ):
            return legs_2

    manager = TravelDataManager(
        providers=[
            provider_1,
            CustomProvider(),
        ]
    )

    legs = manager.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    assert len(legs) == len(legs_1) + 1

def test_dummy_provider_sets_source():

    provider = DummyTravelDataProvider()

    legs = provider.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    assert len(legs) > 0

    assert all(
        leg.source == "dummy_provider"
        for leg in legs
    )

def test_data_manager_prefers_higher_priority_provider():

    from app.services.data_manager import TravelDataManager

    provider_1 = DummyTravelDataProvider()
    provider_2 = DummyTravelDataProvider()

    legs_1 = provider_1.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    legs_2 = provider_2.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    legs_1[0].source = "low_priority_provider"
    legs_2[0].source = "high_priority_provider"

    class ProviderOne:

        priority = 100

        def get_travel_legs(
            self,
            travel_date=None,
            mode=None,
        ):
            return legs_1

    class ProviderTwo:

        priority = 10

        def get_travel_legs(
            self,
            travel_date=None,
            mode=None,
        ):
            return legs_2

    manager = TravelDataManager(
        providers=[
            ProviderOne(),
            ProviderTwo(),
        ]
    )

    legs = manager.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    matching_legs = [
        leg
        for leg in legs
        if (
            leg.origin == legs_1[0].origin
            and leg.destination == legs_1[0].destination
            and leg.mode == legs_1[0].mode
            and leg.departure_time == legs_1[0].departure_time
            and leg.arrival_time == legs_1[0].arrival_time
        )
    ]

    assert len(matching_legs) == 1

    assert matching_legs[0].source == "high_priority_provider"

def test_data_manager_continues_when_one_provider_fails():

    from app.services.data_manager import TravelDataManager

    working_provider = DummyTravelDataProvider()

    class FailingProvider:

        priority = 10

        def get_travel_legs(
            self,
            travel_date=None,
            mode=None,
        ):
            raise RuntimeError("Provider unavailable")

    manager = TravelDataManager(
        providers=[
            FailingProvider(),
            working_provider,
        ]
    )

    legs = manager.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    expected_legs = working_provider.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    assert len(legs) == len(expected_legs)

def test_data_manager_ignores_invalid_provider_output():

    from app.services.data_manager import TravelDataManager

    working_provider = DummyTravelDataProvider()

    class BadProvider:

        priority = 10

        def get_travel_legs(
            self,
            travel_date=None,
            mode=None,
        ):
            return [
                "this is not a TravelLeg",
                None,
                123,
            ]

    manager = TravelDataManager(
        providers=[
            BadProvider(),
            working_provider,
        ]
    )

    legs = manager.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    expected_legs = working_provider.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    assert len(legs) == len(expected_legs)

    assert all(
        isinstance(leg, TravelLeg)
        for leg in legs
    )

def test_data_manager_continues_when_provider_returns_no_legs():

    from app.services.data_manager import TravelDataManager

    working_provider = DummyTravelDataProvider()

    class EmptyProvider:

        priority = 10

        def get_travel_legs(
            self,
            travel_date=None,
            mode=None,
        ):
            return []

    manager = TravelDataManager(
        providers=[
            EmptyProvider(),
            working_provider,
        ]
    )

    legs = manager.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    expected_legs = working_provider.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        )
    )

    assert len(legs) == len(expected_legs)

def test_data_manager_pipeline_removes_stale_provider_journeys():

    from app.services.data_manager import TravelDataManager
    from app.services.journey_generator import generate_journeys
    from app.services.journey_optimiser import filter_fresh_journeys

    class StaleProvider:

        priority = 10

        def get_travel_legs(
            self,
            travel_date=None,
            mode=None,
        ):
            legs = DummyTravelDataProvider().get_travel_legs(
                travel_date=travel_date
            )

            for leg in legs:
                leg.last_updated = datetime.fromisoformat(
                    "2026-08-20T00:00:00"
                )

            return legs

    manager = TravelDataManager(
        providers=[
            StaleProvider(),
        ]
    )

    request_date = datetime.fromisoformat(
        "2026-08-29T00:00:00"
    )

    legs = manager.get_travel_legs(
        travel_date=request_date
    )

    journeys = generate_journeys(
        legs=legs,
        origin="Jammu",
        destination="Mumbai",
    )

    fresh_journeys = filter_fresh_journeys(
        journeys
    )

    assert fresh_journeys == []

def test_data_manager_filters_by_mode():

    from app.services.data_manager import TravelDataManager

    class MixedProvider:

        priority = 10

        def get_travel_legs(
            self,
            travel_date=None,
            mode=None,
        ):
            legs = DummyTravelDataProvider().get_travel_legs(
                travel_date=travel_date
            )

            if mode is not None:
                legs = [
                    leg
                    for leg in legs
                    if leg.mode == mode
                ]

            return legs

    manager = TravelDataManager(
        providers=[
            MixedProvider(),
        ]
    )

    legs = manager.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
        mode="flight",
    )

    assert len(legs) > 0

    assert all(
        leg.mode == "flight"
        for leg in legs
    )

def test_data_manager_passes_mode_filter_to_all_providers():

    from app.services.data_manager import TravelDataManager

    provider_1 = DummyTravelDataProvider()
    provider_2 = DummyTravelDataProvider()

    manager = TravelDataManager(
        providers=[
            provider_1,
            provider_2,
        ]
    )

    legs = manager.get_travel_legs(
        travel_date=datetime.fromisoformat(
            "2026-08-29T00:00:00"
        ),
        mode="flight",
    )

    assert len(legs) > 0

    assert all(
        leg.mode == "flight"
        for leg in legs
    )