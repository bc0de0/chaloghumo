from typing import Any

import httpx

from core.config import settings


class EventsClient:
    """
    Client for fetching hyper-local events from Ticketmaster.
    """

    def __init__(self):
        self.api_key = settings.TICKETMASTER_API_KEY
        self.base_url = "https://app.ticketmaster.com/discovery/v2"

    async def get_nearby_events(
        self, lat: float, lon: float, radius: int = 50
    ) -> list[dict[str, Any]]:
        """
        Fetch upcoming events within a specific radius (km).
        """
        if not self.api_key:
            return self._get_stub_data()

        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/events.json"
                params = {
                    "latlong": f"{lat},{lon}",
                    "radius": radius,
                    "unit": "km",
                    "apikey": self.api_key,
                    "size": 5,
                    "sort": "date,asc",
                }
                response = await client.get(url, params=params, timeout=5.0)
                response.raise_for_status()
                data = response.json()

                events = []
                if "_embedded" in data:
                    for event in data["_embedded"]["events"]:
                        events.append(
                            {
                                "name": event["name"],
                                "type": event["classifications"][0]["segment"]["name"]
                                if "classifications" in event
                                else "Event",
                                "start_date": event["dates"]["start"]["localDate"],
                                "url": event["url"],
                            }
                        )
                return events
        except Exception as e:
            print(f"Events API Error: {e}")
            return self._get_stub_data()

    def _get_stub_data(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "Local Cultural Festival",
                "type": "Arts",
                "start_date": "2026-06-15",
                "url": "#",
            },
            {
                "name": "Summer Concert Series",
                "type": "Music",
                "start_date": "2026-06-20",
                "url": "#",
            },
        ]


events_client = EventsClient()
