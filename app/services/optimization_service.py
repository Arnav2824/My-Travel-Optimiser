from app.models.travel import TravelRequest
from app.models.api import OptimizationResult

from app.services.data_manager import TravelDataManager
from app.services.journey_generator import generate_journeys
from app.services.journey_optimiser import (
    filter_journeys,
    filter_dominated_journeys,
    rank_journeys,
    filter_available_journeys,
    filter_fresh_journeys,
)
from app.services.recommendation_explainer import (
    explain_recommendation,
)


class OptimizationService:

    def __init__(
        self,
        travel_data_manager: TravelDataManager,
    ):
        self.travel_data_manager = travel_data_manager

    def optimize(
        self,
        request: TravelRequest,
    ) -> OptimizationResult:

        # 1. Get travel data

        legs = self.travel_data_manager.get_travel_legs(
            travel_date=request.travel_date
        )

        if not legs:
            return OptimizationResult(
                recommendation=None,
                explanation=(
                    f"We don't currently have travel data for "
                    f"{request.origin} → {request.destination}."
                ),
                alternatives=[],
            )

        # 2. Generate possible journeys

        journeys = generate_journeys(
            legs=legs,
            origin=request.origin,
            destination=request.destination,
        )

        if not journeys:
            return OptimizationResult(
                recommendation=None,
                explanation=(
                    f"We don't currently have travel data for "
                    f"{request.origin} → {request.destination}."
                ),
                alternatives=[],
            )

        # 3. Remove unavailable and stale journeys

        journeys = filter_available_journeys(journeys)

        journeys = filter_fresh_journeys(journeys)

        if not journeys:
            return OptimizationResult(
                recommendation=None,
                explanation=(
                    "Travel options exist for this route, "
                    "but there are currently no bookable journeys available."
                ),
                alternatives=[],
            )

        # 4. Apply user constraints

        filtered_journeys = filter_journeys(
            journeys,
            request,
        )

        # 5. Remove dominated journeys

        non_dominated_journeys = filter_dominated_journeys(
            filtered_journeys
        )

        # 6. Rank according to user preferences

        ranked_journeys = rank_journeys(
            non_dominated_journeys,
            request,
        )

        # 7. Handle no feasible journey

        if not ranked_journeys:
            return OptimizationResult(
                recommendation=None,
                explanation=(
                    "No journey matches your current requirements. "
                    "Try increasing your budget, allowing more transfers, "
                    "or expanding your departure window."
                ),
                alternatives=[],
            )

        # 8. Select recommendation

        recommendation = ranked_journeys[0]
        alternatives = ranked_journeys[1:]

        # 9. Generate explanation

        explanation = explain_recommendation(
            recommendation=recommendation,
            alternatives=alternatives,
            request=request,
        )

        # 10. Return optimization result

        return OptimizationResult(
            recommendation=recommendation,
            explanation=explanation,
            alternatives=alternatives,
        )