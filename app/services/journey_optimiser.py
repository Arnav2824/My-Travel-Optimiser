from app.models.travel import (
    Journey,
    TravelRequest,
    AvailabilityStatus,
)
from datetime import datetime, timedelta


def filter_available_journeys(
    journeys: list[Journey]
) -> list[Journey]:

    if not journeys:
        return []

    available_journeys = []

    for journey in journeys:
        if all(
            leg.availability in (
                AvailabilityStatus.AVAILABLE,
                AvailabilityStatus.LIMITED,
            )
            for leg in journey.legs
        ):
            available_journeys.append(journey)

    return available_journeys

def filter_fresh_journeys(
    journeys: list[Journey],
    max_age_minutes: int = 30,
) -> list[Journey]:

    if not journeys:
        return []

    now = datetime.now()
    max_age = timedelta(minutes=max_age_minutes)

    fresh_journeys = []

    for journey in journeys:
        if all(
            leg.last_updated is not None
            and now - leg.last_updated <= max_age
            for leg in journey.legs
        ):
            fresh_journeys.append(journey)

    return fresh_journeys

def rank_journeys(
    journeys: list[Journey],
    request: TravelRequest
) -> list[Journey]:

    if not journeys:
        return []

    # --------------------------------------------------
    # EFFECTIVE COST
    # --------------------------------------------------

    def effective_cost(journey: Journey) -> float:

        travel_cost = journey.total_price

        # --------------------------------------------------
        # TRAVEL TIME COST
        # --------------------------------------------------

        if request.travel_time_value is not None:
            travel_time_cost = (
                journey.total_travel_time_minutes / 60
            ) * request.travel_time_value

        elif request.value_of_time is not None:
            # Backward compatibility with the old model.
            travel_time_cost = (
                journey.total_travel_time_minutes / 60
            ) * request.value_of_time

        else:
            travel_time_cost = 0

        # --------------------------------------------------
        # WAITING TIME COST
        # --------------------------------------------------

        if request.waiting_time_value is not None:
            waiting_time_cost = (
                journey.total_waiting_time_minutes / 60
            ) * request.waiting_time_value

        elif request.value_of_time is not None:
            # Backward compatibility with the old model.
            waiting_time_cost = (
                journey.total_waiting_time_minutes / 60
            ) * request.value_of_time

        else:
            waiting_time_cost = 0

        return (
            travel_cost
            + travel_time_cost
            + waiting_time_cost
        )

    effective_costs = {
        id(journey): effective_cost(journey)
        for journey in journeys
    }

    min_effective_cost = min(effective_costs.values())
    max_effective_cost = max(effective_costs.values())

    # --------------------------------------------------
    # SCORE
    # --------------------------------------------------

    def score(journey: Journey) -> float:

        current_cost = effective_costs[id(journey)]

        # ----------------------------------------------
        # COST SCORE
        # ----------------------------------------------

        if max_effective_cost > min_effective_cost:
            cost_score = (
                max_effective_cost - current_cost
            ) / (
                max_effective_cost - min_effective_cost
            )
        else:
            cost_score = 1.0

        # ----------------------------------------------
        # TIME SCORE
        # ----------------------------------------------

        min_duration = min(
            j.total_duration_minutes
            for j in journeys
        )

        max_duration = max(
            j.total_duration_minutes
            for j in journeys
        )

        if max_duration > min_duration:
            time_score = (
                max_duration
                - journey.total_duration_minutes
            ) / (
                max_duration - min_duration
            )
        else:
            time_score = 1.0

        # ----------------------------------------------
        # CONVENIENCE SCORE
        # ----------------------------------------------

        min_transfers = min(
            j.total_transfers
            for j in journeys
        )

        max_transfers = max(
            j.total_transfers
            for j in journeys
        )

        if max_transfers > min_transfers:
            convenience_score = (
                max_transfers
                - journey.total_transfers
            ) / (
                max_transfers - min_transfers
            )
        else:
            convenience_score = 1.0

        # ----------------------------------------------
        # FINAL SCORE
        # ----------------------------------------------

        # If the user has explicitly assigned a monetary
        # value to travel or waiting time, those costs are
        # already incorporated into effective_cost.
        # Therefore, do not apply time_weight separately.
        if (
            request.value_of_time is not None
            or request.travel_time_value is not None
            or request.waiting_time_value is not None
        ):

            economic_weight_total = (
                request.cost_weight
                + request.convenience_weight
            )

            # Cost + convenience
            if economic_weight_total > 0:
                return (
                    (
                        request.cost_weight
                        / economic_weight_total
                    ) * cost_score
                    +
                    (
                        request.convenience_weight
                        / economic_weight_total
                    ) * convenience_score
                )

            # If neither cost nor convenience has weight,
            # optimize purely on effective cost.
            return cost_score

        # Normal model when no explicit value of time exists.
        return (
            request.cost_weight * cost_score
            + request.time_weight * time_score
            + request.convenience_weight * convenience_score
        )

    # --------------------------------------------------
    # APPLY SCORES
    # --------------------------------------------------

    for journey in journeys:
        journey.score = score(journey)

    return sorted(
        journeys,
        key=lambda journey: journey.score,
        reverse=True
    )


def filter_journeys(
    journeys: list[Journey],
    request: TravelRequest
) -> list[Journey]:

    filtered_journeys = []

    for journey in journeys:

        # ----------------------------------------------
        # BUDGET
        # ----------------------------------------------

        if request.budget is not None:
            if journey.total_price > request.budget:
                continue

        # ----------------------------------------------
        # MAX TRANSFERS
        # ----------------------------------------------

        if request.max_transfers is not None:
            if journey.total_transfers > request.max_transfers:
                continue

        # ----------------------------------------------
        # EARLIEST DEPARTURE
        # ----------------------------------------------

        if request.earliest_departure is not None:
            if (
                journey.legs[0].departure_time
                < request.earliest_departure
            ):
                continue

        # ----------------------------------------------
        # LATEST DEPARTURE
        # ----------------------------------------------

        if request.latest_departure is not None:
            if (
                journey.legs[0].departure_time
                > request.latest_departure
            ):
                continue

        # ----------------------------------------------
        # LATEST ARRIVAL
        # ----------------------------------------------

        if request.latest_arrival is not None:
            if (
                journey.legs[-1].arrival_time
                > request.latest_arrival
            ):
                continue

        filtered_journeys.append(journey)

    return filtered_journeys


def filter_dominated_journeys(
    journeys: list[Journey]
) -> list[Journey]:

    if not journeys:
        return []

    non_dominated_journeys = []

    for journey in journeys:
        dominated = False

        for other in journeys:
            if journey is other:
                continue

            no_worse_cost = (
                other.total_price
                <= journey.total_price
            )

            no_worse_travel_time = (
                other.total_travel_time_minutes
                <= journey.total_travel_time_minutes
            )

            no_worse_waiting_time = (
                other.total_waiting_time_minutes
                <= journey.total_waiting_time_minutes
            )

            no_worse_convenience = (
                other.total_transfers
                <= journey.total_transfers
            )

            strictly_better = (
                other.total_price
                < journey.total_price
                or
                other.total_travel_time_minutes
                < journey.total_travel_time_minutes
                or
                other.total_waiting_time_minutes
                < journey.total_waiting_time_minutes
                or
                other.total_transfers
                < journey.total_transfers
            )

            if (
                no_worse_cost
                and no_worse_travel_time
                and no_worse_waiting_time
                and no_worse_convenience
                and strictly_better
            ):
                dominated = True
                break

        if not dominated:
            non_dominated_journeys.append(journey)

    return non_dominated_journeys