import asyncio
import json
from typing import Any

import redis.asyncio as redis

from core.config import settings
from services.external_apis.events import events_client
from services.external_apis.safety import safety_client
from services.external_apis.travel import travel_client
from services.external_apis.weather import weather_client


class SignalService:
    """
    Service for retrieving and refreshing real-time Environmental and Societal signals.
    Orchestrates ingestion from external APIs into the Redis cache.
    """

    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
        )

    async def get_environmental_state(
        self, destination_id: str, lat: float | None = None, lng: float | None = None
    ) -> dict[str, Any]:
        """
        Fetch cached weather data. If missing and coords provided, refresh.
        """
        data = await self.redis.get(f"signal:env:{destination_id}")
        if data:
            return json.loads(data)

        if lat and lng:
            weather_data = await weather_client.get_weather(lat, lng)
            await self.redis.set(
                f"signal:env:{destination_id}", json.dumps(weather_data), ex=3600
            )
            return weather_data

        return weather_client._get_stub_data()

    async def get_societal_state(
        self, destination_id: str, lat: float | None = None, lng: float | None = None
    ) -> dict[str, Any]:
        """
        Fetch cached societal data (Safety/Events).
        """
        data = await self.redis.get(f"signal:soc:{destination_id}")
        if data:
            return json.loads(data)

        if lat and lng:
            await self.refresh_signals(destination_id, lat, lng)
            new_data = await self.redis.get(f"signal:soc:{destination_id}")
            return (
                json.loads(new_data)
                if new_data
                else {"safety": {}, "events": [], "crowd_density": 0.5}
            )

        return {"safety": {"safety_index": 0.8}, "events": [], "crowd_density": 0.5}

    async def refresh_signals(self, destination_id: str, lat: float, lng: float):
        """
        Parallel fetch from all external APIs and update Redis.
        """
        tasks = [
            weather_client.get_weather(lat, lng),
            safety_client.get_safety_score(lat, lng),
            events_client.get_nearby_events(lat, lng),
        ]

        weather_data, safety_data, events_data = await asyncio.gather(*tasks)

        # Update cache
        await self.redis.set(
            f"signal:env:{destination_id}", json.dumps(weather_data), ex=3600
        )

        soc_data = {"safety": safety_data, "events": events_data, "crowd_density": 0.4}
        await self.redis.set(
            f"signal:soc:{destination_id}", json.dumps(soc_data), ex=3600
        )

    async def get_travel_availability(
        self, destination_id: str, iata: str | None = None
    ) -> dict[str, Any]:
        """
        Check flight and hotel availability for a destination.
        """
        flights = await travel_client.get_flight_availability(iata or "Unknown")
        hotels = await travel_client.get_hotel_baseline("Unknown")
        return {"flights": flights, "hotels": hotels}


signal_service = SignalService()
