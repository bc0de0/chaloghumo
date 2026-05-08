from typing import Any, List, Dict
from schemas.persona import UserPersona
from services.vector_store import vector_service
from services.llm import llm_service
from services.signals import signal_service

class ReasoningEngine:
    """
    The core synthesis engine for ChaloGhumo.
    Orchestrates the multi-domain recommendation flow.
    """
    
    def __init__(self):
        self.vector_store = vector_service
        self.llm = llm_service
        self.signals = signal_service

    async def generate_recommendation(self, persona: UserPersona) -> Dict[str, Any]:
        """
        Orchestrate the V1 Baseline Recommendation Flow.
        """
        # 1. Extraction: Parse constraints from the persona
        filters = self._parse_constraints(persona)
        
        # 2. Semantic Alignment: Rank candidates via Qdrant based on Mood/Vibe + Filters
        ranked_candidates = await self._align_semantics(persona, filters)
        
        # 3. Contextual Weighting: Incorporate real-time signals
        weighted_candidates = await self._apply_contextual_weights(ranked_candidates)
        
        # 4. Synthesis: Generate final narrative via Gemini
        top_destination = weighted_candidates[0] if weighted_candidates else None
        
        if not top_destination:
            return self._empty_response()

        # Extract data from payload
        payload = top_destination.get("payload", {})
        dest_name = payload.get("name", "Unknown")
        dest_id = top_destination.get("id")

        # Fetch latest signals for the top destination
        env_state = await self.signals.get_environmental_state(dest_id)
        soc_state = await self.signals.get_societal_state(dest_id)
        travel_state = await self.signals.get_travel_availability(dest_id, iata=payload.get("iata"))

        reasoning_chain = await self.llm.generate_reasoning_chain(
            persona_context=persona.model_dump(),
            destination_context=payload,
            environmental_signals=env_state or {},
        )

        return {
            "destination_id": dest_id,
            "destination_name": dest_name,
            "match_score": round(top_destination.get("score", 0.0), 4),
            "reasoning_chain": reasoning_chain,
            "travel_availability": travel_state,
            "context_snapshot": {
                "persona": persona.model_dump(),
                "environment": env_state or {},
                "societal": soc_state or {},
                "events": soc_state.get("events", []) if soc_state else []
            }
        }

    def _parse_constraints(self, persona: UserPersona) -> Dict[str, Any]:
        """
        Parse string-based constraints into Qdrant filter structure.
        Example: ["budget: Luxury", "climate: Tropical"]
        """
        must_filters = []
        for constraint in persona.constraints:
            if ":" in constraint:
                key, value = [s.strip() for s in constraint.split(":", 1)]
                if key == "budget":
                    must_filters.append({"key": "budget_level", "match": {"value": value}})
                elif key == "climate":
                    must_filters.append({"key": "climate_type", "match": {"value": value}})
        
        return {"must": must_filters} if must_filters else {}

    async def _align_semantics(self, persona: UserPersona, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Logic for Vector-based similarity search with hard filters.
        """
        # Convert the user's mood/vibe into a vector
        query_vector = await self.llm.generate_embedding(persona.mood or "travel")
        
        # Search the vector store with filters
        results = await self.vector_store.search_by_vibe(
            query_vector=query_vector, 
            limit=10,
            filters=filters
        )
        
        return results

    async def _apply_contextual_weights(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Logic for adjusting scores based on real-time Environmental/Societal signals.
        Implements 'Environmental Determinism' by penalizing unsafe or incompatible states.
        """
        for cand in candidates:
            env = await self.signals.get_environmental_state(cand["id"])
            if env and env.get("conditions") == "Extreme":
                cand["score"] *= 0.1 # Severe penalty for safety invariant violation
            
            soc = await self.signals.get_societal_state(cand["id"])
            if soc and soc.get("crowd_density", 0) > 0.8:
                cand["score"] *= 0.7 # Penalty for high crowding (Crowding Paradox)
                
        return sorted(candidates, key=lambda x: x["score"], reverse=True)

    def _empty_response(self) -> Dict[str, Any]:
        return {
            "destination_id": "no-match",
            "match_score": 0.0,
            "reasoning_chain": [
                {
                    "step_id": 1,
                    "logic": "Unable to find a destination matching your constraints.",
                    "domain": "System",
                    "impact_weight": 0.0
                }
            ],
            "context_snapshot": {}
        }

reasoning_engine = ReasoningEngine()
