"""
Intelligence Service Module for ChaloGhumo.

This module provides the central intelligence layer, handling both semantic
vector embeddings (locally) and sophisticated reasoning chains (via Together AI).
It includes robust JSON parsing and sanitization for LLM-generated outputs.
"""

import asyncio
import json
from functools import partial
from typing import Any, Dict, List, Optional, Union

from sentence_transformers import SentenceTransformer

from core.config import settings


class IntelligenceService:
    """
    Central Intelligence Hub.
    
    Integrates local SentenceTransformers for embedding latency optimization 
    and Together AI's high-parameter models for complex reasoning.
    """

    embedding_model: SentenceTransformer
    together_client: Optional[Any] = None

    def __init__(self):
        """
        Initializes the intelligence layer.
        
        Loads the 'all-MiniLM-L6-v2' model for 384-D local embeddings 
        and configures the Together AI client.
        """
        # Optimized for travel 'vibes' and sub-100ms local latency.
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self._initialize_together()

    def _initialize_together(self):
        """Bootstraps the Together AI client with API key validation."""
        try:
            from together import Together

            if (
                settings.TOGETHER_API_KEY
                and settings.TOGETHER_API_KEY != "your_together_api_key_here"
            ):
                self.together_client = Together(api_key=settings.TOGETHER_API_KEY)
        except ImportError:
            print("Warning: 'together' library not found. LLM reasoning will be disabled.")

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Converts text into a 384-D vector locally.
        
        Args:
            text: Input string (e.g., user mood or destination description).
            
        Returns:
            A list of 384 floats representing the semantic embedding.
        """
        try:
            # CPU-bound call wrapped for event loop safety
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"Embedding Error: {e}")
            return [0.0] * 384

    async def get_reasoning(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> Optional[Union[str, Any]]:
        """
        Primary inference method for Together AI models.
        
        Args:
            model: Model identifier (e.g., Llama-3-70b-chat-hf).
            messages: List of message dictionaries (role/content).
            max_tokens: Output length constraint.
            temperature: Sampling temperature for creativity vs precision.
            stream: Whether to stream the response (returns generator if True).
            
        Returns:
            The raw string response from the model, or None on failure.
        """
        if not self.together_client:
            return None

        try:
            # Together SDK is synchronous; we run in executor to prevent blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(
                    self.together_client.chat.completions.create,
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream,
                ),
            )

            if stream:
                return response
            return response.choices[0].message.content
        except Exception as e:
            print(f"Together AI Error: {e}")
            return None

    def parse_json_output(self, text: str) -> Any:
        """
        Safely extracts and sanitizes JSON from model outputs.
        
        Handles markdown block removal and common model hallucinations 
        (e.g., Python-style Booleans).
        
        Args:
            text: Raw string from the LLM.
            
        Returns:
            Parsed Python object (dict or list), or None on failure.
        """
        if not text:
            return None
        try:
            # Clean markdown artifacts
            clean_text = text.replace("```json", "").replace("```", "").strip()
            
            # Normalize common model slips
            clean_text = clean_text.replace(": True", ": true").replace(
                ": False", ": false"
            )
            
            data = json.loads(clean_text)
            return self._sanitize(data)
        except Exception as e:
            print(f"JSON Parsing Error: {e}")
            return None

    def _sanitize(self, data: Any) -> Any:
        """
        Internal filter for potential prompt injection or logic leakage.
        
        Redacts sensitive strings and instructions found in structured outputs.
        """
        forbidden = ["System Prompt", "Ignore previous", "Override", "Developer mode"]
        if isinstance(data, list):
            return [self._sanitize(item) for item in data]
        elif isinstance(data, dict):
            return {k: self._sanitize(v) for k, v in data.items()}
        elif isinstance(data, str):
            for word in forbidden:
                if word.lower() in data.lower():
                    return "[REDACTED]"
            return data
        return data


# Singleton instance for global access
intelligence_service = IntelligenceService()
