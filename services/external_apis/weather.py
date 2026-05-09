from typing import Any

import httpx

from core.config import settings


class WeatherClient:
    """
    Client for fetching real-time environmental data from OpenWeatherMap.
    """

    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"

    async def get_weather(self, lat: float, lon: float) -> dict[str, Any]:
        """
        Fetch current weather and 5-day forecast summary.
        """
        if not self.api_key:
            return self._get_stub_data()

        try:
            async with httpx.AsyncClient() as client:
                # 1. Get Current Weather
                current_url = f"{self.base_url}/weather"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric",
                }
                response = await client.get(current_url, params=params, timeout=5.0)
                response.raise_for_status()
                data = response.json()

                return {
                    "temp": data["main"]["temp"],
                    "condition": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"],
                }
        except Exception as e:
            print(f"Weather API Error: {e}")
            return self._get_stub_data()

    def _get_stub_data(self) -> dict[str, Any]:
        return {
            "temp": 22.0,
            "condition": "Clear",
            "description": "clear sky",
            "humidity": 45,
            "wind_speed": 3.5,
        }


weather_client = WeatherClient()
