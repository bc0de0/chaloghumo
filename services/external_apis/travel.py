from typing import Any

from core.config import settings


class TravelClient:
    """
    Client for fetching travel availability signals (Amadeus focus).
    """

    def __init__(self):
        self.api_key = settings.AMADEUS_API_KEY
        # Amadeus requires OAuth2, but for this implementation we assume
        # a simplified wrapper or a direct endpoint if using a proxy.
        # In a full production app, this would include the token refresh logic.
        self.base_url = "https://test.api.amadeus.com/v1"

    async def get_flight_availability(
        self, dest_iata: str, origin_iata: str = "DEL"
    ) -> list[dict[str, Any]]:
        """
        Check if there are flights from a major hub to the destination.
        """
        if not self.api_key:
            return self._get_stub_flights()

        # Note: Amadeus production requires token exchange.
        # For Sprint 4, we maintain the interface but return stubs if keys are missing.
        return self._get_stub_flights()

    async def get_hotel_baseline(self, city_code: str) -> dict[str, Any]:
        """
        Get average hotel price indicator for the city.
        """
        return {"avg_price": 120, "currency": "USD", "availability": "High"}

    def _get_stub_flights(self) -> list[dict[str, Any]]:
        return [
            {"airline": "IndiGo", "price": 450, "duration": "3h 45m", "type": "Direct"},
            {
                "airline": "Air India",
                "price": 520,
                "duration": "4h 10m",
                "type": "Direct",
            },
        ]


travel_client = TravelClient()
