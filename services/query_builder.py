"""
Query Builder Module for ChaloGhumo.

This module provides the 'Universal Query Builder', a specialized intelligence
layer that translates structured triage plans into optimized, domain-specific 
query payloads for multiple data sources.
"""

import json
from typing import Any, Dict

from services.llm import intelligence_service


class UniversalQueryBuilder:
    """
    Sovereign Query Architect.
    
    Uses a high-parameter LLM (Llama-3-70B) to perform precision synthesis of
    SQL queries, vector search parameters, and external API specifications.
    """

    def __init__(self):
        """Initializes the architect with the Llama-3-70B model for high precision."""
        self.model = "meta-llama/Llama-3-70b-chat-hf"

    async def synthesize_queries(self, triage_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translates a triage intent plan into a multi-domain retrieval strategy.
        
        Args:
            triage_plan: The structured output from the TriageRouter.
            
        Returns:
            A multi-key dictionary containing:
            - postgres_sql: Filtered relational query.
            - qdrant_params: Vector search parameters.
            - api_specs: Requirements and params for real-time APIs.
        """
        # The prompt enforces a strict JSON schema for the multi-domain payload.
        prompt = f"""
        <SYSTEM>
        You are the ChaloGhumo Query Architect. Your task is to translate a Triage Intent Plan into specific query payloads.
        You must output ONLY a JSON object with the following structure:
        {{
            "postgres_sql": "A safe, read-only SQL SELECT statement for destination IDs based on constraints",
            "qdrant_params": {{
                "search_text": "The optimized semantic search string",
                "filters": {{"must": [{{ "key": "...", "match": {{ "value": "..." }} }}]}}
            }},
            "api_specs": {{
                "weather": {{ "required": bool, "params": {{ "location": "..." }} }},
                "events": {{ "required": bool, "params": {{ "category": "..." }} }}
            }}
        }}
        </SYSTEM>

        <TRIAGE_PLAN>
        {json.dumps(triage_plan)}
        </TRIAGE_PLAN>

        Generate the optimal retrieval strategy. Ensure SQL targets the 'destinations' table.
        """

        response = await intelligence_service.get_reasoning(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Critical: Low temperature for structural consistency.
        )

        if not response:
            return self._get_fallback_queries(triage_plan)

        try:
            return intelligence_service.parse_json_output(response)
        except Exception:
            return self._get_fallback_queries(triage_plan)

    def _get_fallback_queries(self, triage: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provides a conservative retrieval strategy if the LLM fails to synthesize.
        
        Defaults to a simple semantic search and a limited relational scan.
        """
        search_terms = " ".join(triage.get("search_terms", ["travel"]))
        return {
            "postgres_sql": "SELECT id FROM destinations LIMIT 20",
            "qdrant_params": {"search_text": search_terms, "filters": {}},
            "api_specs": {
                "weather": {"required": True, "params": {}},
                "events": {"required": True, "params": {}},
            },
        }


# Singleton architect instance
query_builder = UniversalQueryBuilder()
