"""
Signal Service Module for ChaloGhumo.

This module provides a unified interface for retrieving real-time environmental,
societal, and availability signals. It implements an aggressive caching strategy
using Redis to ensure sub-100ms response times for repeat queries.
"""

import asyncio
import json
from typing import Any, Dict, Optional

import redis.asyncio as redis

from core.config import settings
from services.external_apis.events import events_client
from services.external_apis.safety import safety_client
from services.external_apis.travel import travel_client
from services.external_apis.weather import weather_client


class SignalService:
    """
    Orchestrator for real-time external signals.
    
    Responsible for fetching, normalizing, and caching data from disparate 
    external APIs (Weather, Ticketmaster, Amadeus, etc.).
    """

    def __init__(self):
        """Initializes the async Redis client for signal persistence."""
        self.redis = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
        )

    async def get_environmental_state(
        self, destination_id: str, lat: Optional[float] = None, lng: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Retrieves the environmental state (weather) for a destination.
        
        Args:
            destination_id: Unique identifier for the destination.
            lat: Latitude (optional, used for refresh).
            lng: Longitude (optional, used for refresh).
            
        Returns:
            A dictionary containing current weather conditions and forecasts.
        """
        # 1. Check Cache
        data = await self.redis.get(f"signal:env:{destination_id}")
        if data:
            return json.loads(data)

        # 2. Refresh if missing and coordinates are available
        if lat and lng:
            weather_data = await weather_client.get_weather(lat, lng)
            await self.redis.set(
                f"signal:env:{destination_id}", json.dumps(weather_data), ex=3600
            )
            return weather_data

        # 3. Fallback to stubs for development/unknown locations
        return weather_client._get_stub_data()

    async def get_societal_state(
        self, destination_id: str, lat: Optional[float] = None, lng: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Retrieves the societal state (safety, events, crowds) for a destination.
        
        Args:
            destination_id: Unique identifier for the destination.
            lat: Latitude.
            lng: Longitude.
            
        Returns:
            A dictionary containing safety scores and nearby events.
        """
        # 1. Check Cache
        data = await self.redis.get(f"signal:soc:{destination_id}")
        if data:
            return json.loads(data)

        # 2. Trigger parallel refresh if missing
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
        Performs a full parallelized refresh of all external API signals.
        
        Updates both environmental and societal caches simultaneously.
        
        Args:
            destination_id: Destination to refresh.
            lat: Latitude.
            lng: Longitude.
        """
        tasks = [
            weather_client.get_weather(lat, lng),
            safety_client.get_safety_score(lat, lng),
            events_client.get_nearby_events(lat, lng),
        ]

        # Execute all API calls in parallel
        weather_data, safety_data, events_data = await asyncio.gather(*tasks)

        # Update Redis with 1-hour TTL
        await self.redis.set(
            f"signal:env:{destination_id}", json.dumps(weather_data), ex=3600
        )

        soc_data = {"safety": safety_data, "events": events_data, "crowd_density": 0.4}
        await self.redis.set(
            f"signal:soc:{destination_id}", json.dumps(soc_data), ex=3600
        )

    async def get_travel_availability(
        self, destination_id: str, iata: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Checks real-time flight and hotel availability via Amadeus.
        
        Args:
            destination_id: Destination identifier.
            iata: IATA code for the target airport.
            
        Returns:
            Dictionary containing availability status and pricing baselines.
        """
        # Note: These are high-latency calls, usually triggered late in the reasoning chain.
        flights = await travel_client.get_flight_availability(iata or "Unknown")
        hotels = await travel_client.get_hotel_baseline("Unknown")
        return {"flights": flights, "hotels": hotels}


# Singleton service instance
signal_service = SignalService()
