import asyncio
import json
from functools import partial
from typing import Any

from sentence_transformers import SentenceTransformer

from core.config import settings


class IntelligenceService:
    """
    Core Intelligence Service for ChaloGhumo.
    Powered exclusively by Together AI for reasoning and SentenceTransformers for local vibes.
    """

    embedding_model: SentenceTransformer
    together_client: Any | None = None

    def __init__(self):
        # 1. Local Embedding Engine (all-MiniLM-L6-v2)
        # Optimized for travel 'vibes' and sub-100ms latency.
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        # 2. Together AI Client Initialization
        self._initialize_together()

    def _initialize_together(self):
        try:
            from together import Together

            if (
                settings.TOGETHER_API_KEY
                and settings.TOGETHER_API_KEY != "your_together_api_key_here"
            ):
                self.together_client = Together(api_key=settings.TOGETHER_API_KEY)
        except ImportError:
            print("Warning: 'together' library not found.")

    async def generate_embedding(self, text: str) -> list[float]:
        """
        Convert text into a 384-D vector locally.
        """
        try:
            # Synchronous call wrapped for async safety
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"Embedding Error: {e}")
            return [0.0] * 384

    async def get_reasoning(
        self,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str | None:
        """
        Primary inference method for Together AI models (Mixtral/Llama 3).
        """
        if not self.together_client:
            return None

        try:
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
        Safely extract and sanitize JSON from model outputs.
        """
        if not text:
            return None
        try:
            clean_text = text.replace("```json", "").replace("```", "").strip()
            # Handle Python-style booleans if the model slips up
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
        Filter for potential prompt injection or logic leakage.
        """
        forbidden = ["System Prompt", "Ignore previous", "Override"]
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


# Singleton Instance
intelligence_service = IntelligenceService()
