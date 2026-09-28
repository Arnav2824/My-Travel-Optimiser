from app.models.travel import Journey, TravelRequest


def explain_recommendation(
    recommendation: Journey,
    alternatives: list[Journey],
    request: TravelRequest
) -> str:

    if not alternatives:
        constraint_reasons = []

        if request.budget is not None:
            if recommendation.total_price <= request.budget:
                constraint_reasons.append(
                    f"stays within your ₹{request.budget:.0f} budget"
            )

        if request.max_transfers is not None:
            if recommendation.total_transfers <= request.max_transfers:
                constraint_reasons.append(
                    f"stays within your limit of "
                    f"{request.max_transfers} transfers"
            )

        if request.latest_arrival is not None:
            if recommendation.legs[-1].arrival_time <= request.latest_arrival:
                constraint_reasons.append(
                    "arrives within your required time"
            )

        if constraint_reasons:
            if len(constraint_reasons) == 1:
                reason_text = constraint_reasons[0]
            else:
                reason_text = (
                    ", ".join(constraint_reasons[:-1])
                    + ", and "
                    + constraint_reasons[-1]
            )

            return f"Recommended because it {reason_text}."

        return "Recommended because it is the only feasible journey."

    next_best = alternatives[0]

    reasons = []
    additional_tradeoffs = []

    for alternative in alternatives[1:]:

        price_difference = (
            alternative.total_price
            - recommendation.total_price
        )

        travel_time_difference = (
            alternative.total_travel_time_minutes
            - recommendation.total_travel_time_minutes
        )

        if (
            travel_time_difference < 0
            and price_difference > 0
        ):
            additional_tradeoffs.append(
                f"a faster option saves "
                f"{abs(travel_time_difference)} minutes "
                f"but costs ₹{price_difference:.0f} more"
            )

    # ---------------------------------------------------------
    # Price comparison
    # ---------------------------------------------------------

    price_difference = (
        next_best.total_price - recommendation.total_price
    )

    if price_difference > 0:
        reasons.append(
            f"saves ₹{price_difference:.0f} compared with "
            f"the next-best option"
        )

    elif price_difference < 0:
        reasons.append(
            f"costs ₹{abs(price_difference):.0f} more than "
            f"the next-best option"
        )

    # ---------------------------------------------------------
    # Travel time comparison
    # ---------------------------------------------------------

    travel_time_difference = (
        recommendation.total_travel_time_minutes
        - next_best.total_travel_time_minutes
    )

    if travel_time_difference > 0:
        reasons.append(
            f"takes {travel_time_difference} additional minutes "
            f"of travel time"
        )

    elif travel_time_difference < 0:
        reasons.append(
            f"saves {abs(travel_time_difference)} minutes "
            f"of travel time"
        )

    # ---------------------------------------------------------
    # Waiting time comparison
    # ---------------------------------------------------------

    waiting_time_difference = (
        recommendation.total_waiting_time_minutes
        - next_best.total_waiting_time_minutes
    )

    if waiting_time_difference > 0:
        reasons.append(
            f"has {waiting_time_difference} additional minutes "
            f"of waiting time"
        )

    elif waiting_time_difference < 0:
        reasons.append(
            f"has {abs(waiting_time_difference)} fewer minutes "
            f"of waiting time"
        )

    # ---------------------------------------------------------
    # Overall journey duration
    # ---------------------------------------------------------

    duration_difference = (
        recommendation.total_duration_minutes
        - next_best.total_duration_minutes
    )

    if duration_difference > 0:
        reasons.append(
            f"takes {duration_difference} minutes longer overall"
        )

    elif duration_difference < 0:
        reasons.append(
            f"takes {abs(duration_difference)} minutes less overall"
        )

    # ---------------------------------------------------------
    # Transfers
    # ---------------------------------------------------------

    transfer_difference = (
        recommendation.total_transfers
        - next_best.total_transfers
    )

    if transfer_difference < 0:
        reasons.append(
            f"requires {abs(transfer_difference)} fewer transfers"
        )

    elif transfer_difference > 0:
        reasons.append(
            f"requires {transfer_difference} additional transfers"
        )

    # ---------------------------------------------------------
    # User constraints
    # ---------------------------------------------------------

    constraint_reasons = []

    if request.budget is not None:
        if recommendation.total_price <= request.budget:
            constraint_reasons.append(
                f"stays within your ₹{request.budget:.0f} budget"
            )

    if request.max_transfers is not None:
        if recommendation.total_transfers <= request.max_transfers:
            constraint_reasons.append(
                f"stays within your limit of "
                f"{request.max_transfers} transfers"
            )

    if request.latest_arrival is not None:
        if recommendation.legs[-1].arrival_time <= request.latest_arrival:
            constraint_reasons.append(
                "arrives within your required time"
            )

    # ---------------------------------------------------------
    # Build explanation
    # ---------------------------------------------------------

    all_reasons = (constraint_reasons
        + reasons
        + additional_tradeoffs
    )

    if not all_reasons:
        return (
            "Recommended because it provides the highest score "
            "among the feasible journeys."
        )

    if len(all_reasons) == 1:
        reason_text = all_reasons[0]

    elif len(all_reasons) == 2:
        reason_text = f"{all_reasons[0]} and {all_reasons[1]}"

    else:
        reason_text = (
            ", ".join(all_reasons[:-1])
            + ", and "
            + all_reasons[-1]
        )

    return f"Recommended because it {reason_text}."