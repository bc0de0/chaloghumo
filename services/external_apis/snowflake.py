"""
Snowflake Service Module for ChaloGhumo.

This module provides the analytical memory layer, interfacing with Snowflake's 
Medallion architecture (Gold Layer) to cross-reference real-time recommendations 
with historical traveler trends and predictive 'vibe' stability scores.
"""

import asyncio
from typing import Any, Dict, Optional

import snowflake.connector

from core.config import settings


class SnowflakeService:
    """
    Analytical Data Access Layer.
    
    Provides long-term memory and predictive signals by querying the 
    ANALYTICS_GOLD schema.
    """

    def __init__(self):
        """
        Initializes the Snowflake service.
        
        Checks for required credentials and sets the initial connection state to None.
        """
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
        Lazily establishes a connection to the Snowflake warehouse.
        
        Returns:
            A snowflake.connector.SnowflakeConnection object, or None if disabled/failed.
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
    ) -> Dict[str, Any]:
        """
        Validates a candidate destination against historical trend data.
        
        Args:
            dest_id: Unique identifier for the destination.
            mood: The semantic mood category to cross-reference.
            
        Returns:
            A dictionary containing seasonality insights and stability scores.
        """
        conn = self._get_connection()
        if not conn:
            return self._get_fallback_trend()

        try:
            # Snowflake SDK is synchronous; we run in executor to prevent 
            # event loop blocking during I/O.
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, self._execute_trend_query, dest_id, mood
            )
        except Exception as e:
            print(f"Snowflake Query Error (Trend): {e}")
            return self._get_fallback_trend()

    def _execute_trend_query(self, dest_id: str, mood: str) -> Dict[str, Any]:
        """Synchronous implementation of the trend analysis SQL query."""
        cursor = self._conn.cursor()
        try:
            # Query targets the Gold layer for aggregated predictive metrics.
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
        Retrieves the reliability index for a specific destination's 'vibe'.
        
        Args:
            dest_id: Destination to score.
            
        Returns:
            A float representing historical match reliability (0.0 - 1.0).
        """
        conn = self._get_connection()
        if not conn:
            return 0.75  # Standard baseline for unknown trends.

        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._execute_score_query, dest_id)
        except Exception:
            return 0.75

    def _execute_score_query(self, dest_id: str) -> float:
        """Synchronous implementation of the reliability score query."""
        cursor = self._conn.cursor()
        try:
            query = "SELECT reliability_score FROM ANALYTICS_GOLD.VIBE_RELIABILITY WHERE destination_id = %s"
            cursor.execute(query, (dest_id,))
            result = cursor.fetchone()
            return float(result[0]) if result else 0.75
        finally:
            cursor.close()

    def _get_fallback_trend(self) -> Dict[str, Any]:
        """Provides a safe baseline trend payload for cases where data is missing."""
        return {
            "is_trending": True,
            "historical_score": 0.8,
            "peak_season": "Year-round",
            "narrative": "Consistent historical performance for this mood category.",
        }


# Singleton service instance
snowflake_service = SnowflakeService()
