from app.models.travel import (
    TravelLeg,
    Journey
)


def generate_journeys(
    legs: list[TravelLeg],
    origin: str,
    destination: str,
    max_legs: int = 4
) -> list[Journey]:

    journeys = []

    def build_journey(
        current_location: str,
        current_legs: list[TravelLeg]
    ):

        # We have reached the destination
        if current_location == destination:

            journeys.append(
                Journey(
                    origin=origin,
                    destination=destination,
                    legs=current_legs
                )
            )

            return

        # Prevent excessively complicated journeys
        if len(current_legs) >= max_legs:
            return

        for leg in legs:

            # The next leg must start
            # where the current journey ends
            if leg.origin != current_location:
                continue

            # Don't reuse the same leg
            if leg in current_legs:
                continue

            # If there are already legs,
            # make sure the timings work
            if current_legs:
                previous_leg = current_legs[-1]

                if leg.departure_time < previous_leg.arrival_time:
                    continue

            build_journey(
                leg.destination,
                current_legs + [leg]
            )

    build_journey(origin, [])

# Remove duplicate journeys
    unique_journeys = []
    seen = set()

    for journey in journeys:
        journey_key = tuple(
        (
            leg.origin,
            leg.destination,
            leg.mode,
            leg.operator,
            leg.departure_time,
            leg.arrival_time,
            leg.price
        )
        for leg in journey.legs
    )

        if journey_key not in seen:
            seen.add(journey_key)
            unique_journeys.append(journey)

    return unique_journeys      