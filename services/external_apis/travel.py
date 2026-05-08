from typing import List, Dict, Any
import random

class TravelAvailabilityClient:
    """
    Client for checking flight and hotel availability.
    Currently stubbed for Sprint 3.
    """
    async def get_flight_availability(self, destination_iata: str) -> Dict[str, Any]:
        """
        Check if flights are available to a destination and estimate cost.
        """
        # Mock response
        has_flights = random.random() > 0.1
        return {
            "available": has_flights,
            "min_price": random.randint(300, 1500) if has_flights else 0,
            "currency": "USD",
            "frequency": "Daily" if has_flights else "None",
            "provider": "Mock-Amadeus-v1"
        }

    async def get_hotel_baseline(self, destination_name: str) -> Dict[str, Any]:
        """
        Get baseline hotel pricing for a destination.
        """
        return {
            "avg_nightly_rate": random.randint(80, 500),
            "currency": "USD",
            "occupancy_trend": "Medium",
            "provider": "Mock-Booking-v1"
        }

travel_client = TravelAvailabilityClient()
