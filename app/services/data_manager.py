from app.models.travel import TravelLeg
from app.services.providers import TravelDataProvider


class TravelDataManager:

    def __init__(self, providers: list[TravelDataProvider]):
        self.providers = providers

    def get_travel_legs(
        self,
        travel_date=None,
        mode=None,
) -> list[TravelLeg]:

        all_legs = []

        for provider in self.providers:

            try:
                legs = provider.get_travel_legs(
                travel_date=travel_date,
                mode=mode,
            )

                valid_legs = [
                    leg
                    for leg in legs
                    if isinstance(leg, TravelLeg)
            ]

                all_legs.extend(
                    (provider, leg)
                    for leg in valid_legs
            )

            except Exception as exc:
                print(
                    f"Travel provider failed: "
                    f"{provider.__class__.__name__}: {exc}"
            )
                continue

        return self._remove_duplicates(all_legs)

    def _remove_duplicates(
        self,
        provider_legs,
    ) -> list[TravelLeg]:

        unique_legs = {}

        for provider, leg in provider_legs:

            key = (
                leg.origin,
                leg.destination,
                leg.mode,
                leg.operator,
                leg.departure_time,
                leg.arrival_time,
                leg.price,
                leg.currency,
            )

            if key not in unique_legs:
                unique_legs[key] = (
                    provider,
                    leg,
                )

            else:
                existing_provider, existing_leg = (
                    unique_legs[key]
                )

                if getattr(provider, "priority", 100) < getattr(existing_provider,"priority",100,):
                    unique_legs[key] = (
                        provider,
                        leg,
                    )

        return [
            leg
            for provider, leg in unique_legs.values()
        ]