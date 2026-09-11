from app.models.travel import TravelOption, TravelRequest


def filter_options(
    options: list[TravelOption],
    request: TravelRequest
) -> list[TravelOption]:

    feasible_options = []

    for option in options:

        # Budget is a hard constraint
        if request.budget is not None:
            if option.price > request.budget:
                continue

        # Maximum transfers is also a hard constraint
        if request.max_transfers is not None:
            if option.transfers > request.max_transfers:
                continue

        feasible_options.append(option)

    return feasible_options

def remove_dominated_options(
    options: list[TravelOption]
) -> list[TravelOption]:

    non_dominated = []

    for option in options:

        dominated = False

        for other in options:

            if option == other:
                continue

            cheaper_or_equal = other.price <= option.price
            faster_or_equal = (
                other.duration_minutes
                <= option.duration_minutes
            )
            more_convenient_or_equal = (
                other.transfers
                <= option.transfers
            )

            strictly_better = (
                other.price < option.price
                or other.duration_minutes
                < option.duration_minutes
                or other.transfers < option.transfers
            )

            if (
                cheaper_or_equal
                and faster_or_equal
                and more_convenient_or_equal
                and strictly_better
            ):
                dominated = True
                break

        if not dominated:
            non_dominated.append(option)

    return non_dominated


def calculate_scores(
    options: list[TravelOption],
    request: TravelRequest
) -> list[dict]:

    if not options:
        return []

    # Find the worst values among the available options.
    max_price = max(option.price for option in options)
    max_duration = max(
        option.duration_minutes for option in options
    )
    max_transfers = max(
        option.transfers for option in options
    )

    scored_options = []

    for option in options:

        # Lower price = better
        if max_price > 0:
            cost_score = 1 - (option.price / max_price)
        else:
            cost_score = 1

        # Lower duration = better
        if max_duration > 0:
            time_score = 1 - (
                option.duration_minutes / max_duration
            )
        else:
            time_score = 1

        # Lower transfers = better
        if max_transfers > 0:
            convenience_score = 1 - (
                option.transfers / max_transfers
            )
        else:
            convenience_score = 1

        overall_score = (
            cost_score * request.cost_weight
            + time_score * request.time_weight
            + convenience_score * request.convenience_weight
        )

        scored_options.append({
            "option": option,
            "score": round(overall_score, 4),
            "cost_score": round(cost_score, 4),
            "time_score": round(time_score, 4),
            "convenience_score": round(
                convenience_score, 4
            )
        })

    return sorted(
        scored_options,
        key=lambda x: x["score"],
        reverse=True
    )


def optimize(
    options: list[TravelOption],
    request: TravelRequest
) -> list[dict]:

    feasible_options = filter_options(
        options,
        request
    )

    non_dominated_options = remove_dominated_options(
        feasible_options
    )

    return calculate_scores(
        non_dominated_options,
        request
    )