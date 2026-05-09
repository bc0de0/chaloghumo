import json
from typing import Any

from services.llm import intelligence_service


class UniversalQueryBuilder:
    """
    The Sovereign Query Builder for ChaloGhumo.
    Translates triage plans into optimized database-specific queries and API specifications.
    Powered by google/gemma-3n-4b-it for high-precision synthesis.
    """

    def __init__(self):
        self.model = "meta-llama/Llama-3-70b-chat-hf"

    async def synthesize_queries(self, triage_plan: dict[str, Any]) -> dict[str, Any]:
        """
        Translates the intent plan into a multi-domain retrieval strategy.
        """
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
            temperature=0.1,
        )

        if not response:
            return self._get_fallback_queries(triage_plan)

        try:
            return intelligence_service.parse_json_output(response)
        except Exception:
            return self._get_fallback_queries(triage_plan)

    def _get_fallback_queries(self, triage: dict[str, Any]) -> dict[str, Any]:
        """
        Safe fallback logic if LLM synthesis fails.
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


query_builder = UniversalQueryBuilder()
