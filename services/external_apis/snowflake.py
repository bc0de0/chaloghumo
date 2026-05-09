import asyncio
from typing import Any

import snowflake.connector

from core.config import settings


class SnowflakeService:
    """
    Service for historical trend analysis and long-term memory.
    Interfaces with the ANALYTICS_GOLD schema for predictive traveler signals.
    """

    def __init__(self):
        self.enabled = all(
            [
                settings.SNOWFLAKE_ACCOUNT,
                settings.SNOWFLAKE_USER,
                settings.SNOWFLAKE_PASSWORD,
            ]
        )
        self._conn = None

    def _get_connection(self):
        """
        Lazily establishes a connection to Snowflake.
        """
        if not self.enabled:
            return None

        if self._conn is None:
            try:
                self._conn = snowflake.connector.connect(
                    user=settings.SNOWFLAKE_USER,
                    password=settings.SNOWFLAKE_PASSWORD,
                    account=settings.SNOWFLAKE_ACCOUNT,
                    warehouse=settings.SNOWFLAKE_WAREHOUSE,
                    database=settings.SNOWFLAKE_DATABASE,
                    schema=settings.SNOWFLAKE_SCHEMA or "ANALYTICS_GOLD",
                )
            except Exception as e:
                print(f"Snowflake Connection Error: {e}")
                return None
        return self._conn

    async def validate_destination_trend(
        self, dest_id: str, mood: str
    ) -> dict[str, Any]:
        """
        Cross-references a real-time recommendation against historical trend data.
        Returns a 'vibe_stability' score and seasonality insights.
        """
        conn = self._get_connection()
        if not conn:
            return self._get_fallback_trend()

        try:
            # We run the query in an executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, self._execute_trend_query, dest_id, mood
            )
        except Exception as e:
            print(f"Snowflake Query Error (Trend): {e}")
            return self._get_fallback_trend()

    def _execute_trend_query(self, dest_id: str, mood: str) -> dict[str, Any]:
        """
        Synchronous execution of the trend analysis SQL.
        """
        cursor = self._conn.cursor()
        try:
            # SQL targeting the ANALYTICS_GOLD layer
            query = """
                SELECT 
                    vibe_stability_index,
                    peak_season,
                    historical_match_rate,
                    trend_narrative
                FROM ANALYTICS_GOLD.DESTINATION_TRENDS
                WHERE destination_id = %s AND mood_category = %s
                LIMIT 1
            """
            cursor.execute(query, (dest_id, mood))
            result = cursor.fetchone()

            if result:
                return {
                    "is_trending": result[2] > 0.7,
                    "historical_score": float(result[0]),
                    "peak_season": result[1],
                    "narrative": result[3],
                }
            return self._get_fallback_trend()
        finally:
            cursor.close()

    async def get_predictive_vibe_score(self, dest_id: str) -> float:
        """
        Retrieves the historical reliability score for a destination's semantic 'vibe'.
        """
        conn = self._get_connection()
        if not conn:
            return 0.75  # Standard baseline

        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._execute_score_query, dest_id)
        except Exception:
            return 0.75

    def _execute_score_query(self, dest_id: str) -> float:
        cursor = self._conn.cursor()
        try:
            query = "SELECT reliability_score FROM ANALYTICS_GOLD.VIBE_RELIABILITY WHERE destination_id = %s"
            cursor.execute(query, (dest_id,))
            result = cursor.fetchone()
            return float(result[0]) if result else 0.75
        finally:
            cursor.close()

    def _get_fallback_trend(self) -> dict[str, Any]:
        return {
            "is_trending": True,
            "historical_score": 0.8,
            "peak_season": "Year-round",
            "narrative": "Consistent historical performance for this mood category.",
        }


snowflake_service = SnowflakeService()
