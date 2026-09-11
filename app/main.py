from fastapi import FastAPI
from app.services.data_manager import TravelDataManager
from app.models.travel import TravelRequest
from app.services.travel_data import DummyTravelDataProvider
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


app = FastAPI(title="Travel Optimiser")

travel_data_manager = TravelDataManager(
    providers=[
        DummyTravelDataProvider(),
    ]
)


@app.get("/")
def home():
    return {
        "message": "Travel Optimiser is alive!"
    }


@app.post("/optimize")
def optimize_travel(request: TravelRequest):

    # ---------------------------------------------------------
    # 1. Get travel data
    # ---------------------------------------------------------

    legs = travel_data_manager.get_travel_legs(
        travel_date=request.travel_date
    )

    if not legs:
        return {
            "recommendation": None,
            "explanation": (
                f"We don't currently have travel data for "
                f"{request.origin} → {request.destination}."
            ),
            "alternatives": [],
        }

    # ---------------------------------------------------------
    # 2. Generate possible journeys
    # ---------------------------------------------------------

    journeys = generate_journeys(
        legs=legs,
        origin=request.origin,
        destination=request.destination,
    )

    if not journeys:
        return {
            "recommendation": None,
            "explanation": (
                f"We don't currently have travel data for "
                f"{request.origin} → {request.destination}."
            ),
            "alternatives": [],
        }

    # ---------------------------------------------------------
    # 3. Remove unavailable and stale journeys
    # ---------------------------------------------------------

    journeys = filter_available_journeys(
        journeys
    )

    journeys = filter_fresh_journeys(
        journeys
    )

    if not journeys:
        return {
            "recommendation": None,
            "explanation": (
                "Travel options exist for this route, "
                "but there are currently no bookable journeys available."
            ),
            "alternatives": [],
        }

    # ---------------------------------------------------------
    # 4. Apply user constraints
    # ---------------------------------------------------------

    filtered_journeys = filter_journeys(
        journeys,
        request,
    )

    # ---------------------------------------------------------
    # 5. Remove dominated journeys
    # ---------------------------------------------------------

    non_dominated_journeys = filter_dominated_journeys(
        filtered_journeys
    )

    # ---------------------------------------------------------
    # 6. Rank according to user preferences
    # ---------------------------------------------------------

    ranked_journeys = rank_journeys(
        non_dominated_journeys,
        request,
    )

    # ---------------------------------------------------------
    # 7. Handle no feasible journey
    # ---------------------------------------------------------

    if not ranked_journeys:
        return {
            "recommendation": None,
            "explanation": (
                "No journey matches your current requirements. "
                "Try increasing your budget, allowing more transfers, "
                "or expanding your departure window."
            ),
            "alternatives": [],
        }

    # ---------------------------------------------------------
    # 8. Select recommendation
    # ---------------------------------------------------------

    recommendation = ranked_journeys[0]
    alternatives = ranked_journeys[1:]

    # ---------------------------------------------------------
    # 9. Generate explanation
    # ---------------------------------------------------------

    explanation = explain_recommendation(
        recommendation=recommendation,
        alternatives=alternatives,
        request=request,
    )

    # ---------------------------------------------------------
    # 10. Build API response
    # ---------------------------------------------------------

    return {
        "recommendation": {
            "score": recommendation.score,
            "total_price": recommendation.total_price,
            "total_duration_minutes": (
                recommendation.total_duration_minutes
            ),
            "total_transfers": recommendation.total_transfers,
            "modes": recommendation.modes,
            "total_travel_time_minutes": (
                recommendation.total_travel_time_minutes
            ),
            "total_waiting_time_minutes": (
                recommendation.total_waiting_time_minutes
            ),
        },

        "explanation": explanation,

        "alternatives": [
            {
                "score": journey.score,
                "total_price": journey.total_price,
                "total_duration_minutes": (
                    journey.total_duration_minutes
                ),
                "total_transfers": journey.total_transfers,
                "modes": journey.modes,
                "total_travel_time_minutes": (
                    journey.total_travel_time_minutes
                ),
                "total_waiting_time_minutes": (
                    journey.total_waiting_time_minutes
                ),
            }
            for journey in alternatives
        ],
    }