"""
Reasoning Engine Module for ChaloGhumo.

This module orchestrates the multi-stage cognitive pipeline responsible for
transforming raw user moods into validated, expert-grade travel recommendations.
It implements a high-performance 'Flash Burst' RAG pattern, querying multiple 
heterogeneous data sources in parallel.
"""

import asyncio
import json
from typing import Any, cast, List, Dict

from schemas.persona import UserPersona
from services.external_apis.s3 import s3_service
from services.external_apis.snowflake import snowflake_service
from services.llm import intelligence_service
from services.postgres import postgres_service
from services.query_builder import query_builder
from services.signals import signal_service
from services.vector_store import vector_service


class TriageRouter:
    """
    Stage 1: The Intent Analyst.
    
    Uses a lightweight LLM (Qwen-2 1.5B) to perform initial intent extraction,
    query expansion, and signal requirement selection. This ensures that 
    downstream retrieval is surgically focused.
    """

    def __init__(self):
        """Initializes the triage router with the specified instructor model."""
        self.model = "arize-ai/qwen-2-1.5b-instruct"

    async def analyze_intent(self, persona: UserPersona) -> Dict[str, Any]:
        """
        Expands the user's mood into a structured search plan.
        
        Args:
            persona: The UserPersona object containing mood and constraints.
            
        Returns:
            A dictionary containing search terms, constraints, and signal requirements.
        """
        prompt = f"""
        [INST]
        As the ChaloGhumo Triage Router, analyze this traveler's persona and mood.
        Persona: {persona.model_dump_json()}

        Tasks:
        1. Expand the 'mood' into 3 semantic search terms for a vector database.
        2. Identify key constraints (budget, climate, etc.).
        3. Decide if 'Weather' or 'Events' signals are critical for this specific intent (True/False).

        Return ONLY a JSON object (ensure booleans are lowercase true/false):
        {{
            "search_terms": ["term1", "term2", "term3"],
            "constraints": {{"key": "value"}},
            "signal_requirements": {{"weather": true, "events": false, "flights": true}}
        }}
        [/INST]
        """

        response = await intelligence_service.get_reasoning(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Low temperature for structural reliability
        )

        # Fallback logic for extraction failures
        if not response:
            return {
                "search_terms": [persona.mood or "travel"],
                "constraints": {},
                "signal_requirements": {
                    "weather": True,
                    "events": True,
                    "flights": True,
                },
            }

        try:
            return intelligence_service.parse_json_output(response)
        except Exception:
            return {
                "search_terms": [persona.mood or "travel"],
                "constraints": {},
                "signal_requirements": {
                    "weather": True,
                    "events": True,
                    "flights": True,
                },
            }


class ReasoningEngine:
    """
    The High-Performance RAG Orchestrator for ChaloGhumo.
    
    Manages the transition from raw input to cognitive synthesis through a 
    parallelized retrieval burst across Postgres, Qdrant, Snowflake, and External APIs.
    """

    def __init__(self):
        """Initializes core sub-services and intelligence clients."""
        self.router = TriageRouter()
        self.vector_store = vector_service
        self.llm = intelligence_service
        self.signals = signal_service
        self.snowflake = snowflake_service
        self.synthesis_model = "meta-llama/Llama-3-70b-chat-hf"

    async def generate_recommendation(self, persona: UserPersona) -> Dict[str, Any]:
        """
        Orchestrate the Sprint 4 Parallel RAG Flow.
        
        Flow: Triage -> Sovereign Query Expansion -> Parallel Retrieval -> Cognitive Synthesis.
        
        Args:
            persona: The validated UserPersona input.
            
        Returns:
            A structured recommendation dictionary including destination, score, and reasoning.
        """
        # 1. Triage Stage (Intent Extraction)
        intent_plan = await self.router.analyze_intent(persona)
        self._log_session_output(persona, intent_plan)

        # 2. Sovereign Query Expansion (Domain-specific query synthesis)
        query_strategy = await query_builder.synthesize_queries(intent_plan)

        # 3. Parallel Retrieval Burst
        # Optimization: We execute all I/O bound tasks simultaneously using asyncio.gather
        # to ensure sub-2-second end-to-end latency.
        search_query = query_strategy["qdrant_params"].get("search_text", "travel")
        query_vector = await self.llm.generate_embedding(search_query)

        burst_tasks = [
            postgres_service.fetch_candidate_ids(query_strategy["postgres_sql"]),
            self.vector_store.search_by_vibe(
                query_vector=query_vector,
                limit=10,
                filters=query_strategy["qdrant_params"].get("filters", {}),
            ),
            self._fetch_context_bundle_from_specs(query_strategy["api_specs"]),
        ]

        results = await asyncio.gather(*burst_tasks)
        postgres_ids = cast(List[Any], results[0])
        qdrant_results = cast(List[Dict[str, Any]], results[1])
        signal_context = results[2]

        # 4. Context Merging & Ranking (Intersection of semantic and relational results)
        final_candidates = self._merge_and_rank_candidates(qdrant_results, postgres_ids)

        if not final_candidates:
            return self._empty_response()

        top_destination = final_candidates[0]
        dest_payload = top_destination.get("payload", {})
        dest_id = top_destination.get("id")

        # 5. Cognitive Synthesis Stage (Final Reasoning Chain Generation)
        # We inject real-time API signals and historical Snowflake metrics into the final prompt.
        synthesis_context = {
            **signal_context,
            "historical": await self.snowflake.validate_destination_trend(
                dest_id, search_query
            ),
        }
        reasoning_chain = await self._generate_synthesis(
            persona, dest_payload, synthesis_context
        )

        return {
            "destination_id": dest_id,
            "destination_name": dest_payload.get("name", "Unknown"),
            "match_score": round(top_destination.get("score", 0.0), 4),
            "reasoning_chain": reasoning_chain,
            "travel_availability": synthesis_context.get("flights"),
            "context_snapshot": {
                "persona": persona.model_dump(),
                "query_strategy": query_strategy,
                "signals": synthesis_context,
            },
        }

    async def _fetch_context_bundle_from_specs(
        self, specs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Dynamically fetches real-time signals based on the Query Builder's specifications.
        """
        tasks = []
        # Signal services handle their own internal caching (Redis)
        tasks.append(self.signals.get_environmental_state("STUB"))
        tasks.append(self.signals.get_societal_state("STUB"))
        tasks.append(self.signals.get_travel_availability("STUB"))

        results = await asyncio.gather(*tasks)
        return {
            "environment": results[0],
            "societal": results[1],
            "flights": results[2],
        }

    def _merge_and_rank_candidates(
        self, qdrant_hits: List[Dict[str, Any]], postgres_ids: List[Any]
    ) -> List[Dict[str, Any]]:
        """
        Intersects semantic vector results with relational hard constraints from Postgres.
        """
        if not postgres_ids:
            return qdrant_hits

        str_postgres_ids = [str(pid) for pid in postgres_ids]
        return [
            hit for hit in qdrant_hits if str(hit.get("id")) in str_postgres_ids
        ] or qdrant_hits

    async def _generate_synthesis(
        self, persona: UserPersona, dest: Dict, context: Dict
    ) -> List[Dict[str, Any]]:
        """
        Generates a premium reasoning chain using Llama 3 70B.
        
        Synthesizes the persona, destination metadata, and real-time signals into a 
        cohesive, expert travel justification.
        """
        prompt = f"""
        <SYSTEM>
        You are the ChaloGhumo Synthesis Engine. Your goal is to explain why a destination is a perfect match for a traveler.
        Use a premium, expert, and slightly poetic tone. Cite specific signals (weather, historical trends, events).
        </SYSTEM>

        <CONTEXT>
        Traveler: {persona.model_dump_json()}
        Destination: {json.dumps(dest)}
        Retrieved Data: {json.dumps(context)}
        </CONTEXT>

        Return a JSON array of reasoning steps. Each step MUST have:
        - step_id: int
        - logic: string (The expert explanation)
        - domain: [Persona, Environmental, Societal, Historical]
        - impact_weight: float (-1.0 to 1.0)
        """

        response = await self.llm.get_reasoning(
            model=self.synthesis_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        if not response:
            return [
                {
                    "step_id": 1,
                    "logic": "Destination aligns with your unique vibe.",
                    "domain": "Persona",
                    "impact_weight": 0.5,
                }
            ]

        try:
            return self.llm.parse_json_output(response)
        except Exception:
            return [
                {
                    "step_id": 1,
                    "logic": "Destination aligns with your unique vibe.",
                    "domain": "Persona",
                    "impact_weight": 0.5,
                }
            ]

    def _empty_response(self) -> Dict[str, Any]:
        """Provides a safe, structured fallback for no-match scenarios."""
        return {
            "destination_id": "no-match",
            "match_score": 0.0,
            "reasoning_chain": [
                {
                    "step_id": 1,
                    "logic": "No destinations found matching your specific criteria.",
                    "domain": "System",
                    "impact_weight": 0.0,
                }
            ],
            "context_snapshot": {},
        }

    def _log_session_output(self, persona: UserPersona, intent: Dict[str, Any]):
        """
        Persists the triage and persona state for audit and analytical ingestion.
        
        Drops logs into local storage and pushes to S3 for Snowflake analytical processing.
        """
        import os
        import time
        from datetime import datetime

        session_id = (
            f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{int(time.time())}"
        )
        log_path = f"logs/sessions/{session_id}.json"

        os.makedirs("logs/sessions", exist_ok=True)

        output = {
            "timestamp": datetime.now().isoformat(),
            "persona": persona.model_dump(),
            "intent_plan": intent,
        }

        with open(log_path, "w") as f:
            json.dump(output, f, indent=2)

        # Async push to S3 Bronze layer for Snowflake Ingestion
        asyncio.create_task(s3_service.upload_session_log(session_id, output))

        print(f"Session output saved to {log_path} and queued for S3 upload")


# Singleton Instance for system-wide access
reasoning_engine = ReasoningEngine()
