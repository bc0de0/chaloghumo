"""
Vector Store Service Module for ChaloGhumo.

This module provides the semantic retrieval layer, utilizing Qdrant to perform
high-dimensional similarity searches based on destination 'vibes'. It handles 
collection management, schema-validated upserts, and semantic ranking.
"""

from typing import Any, Dict, List, Optional, Union

from qdrant_client import QdrantClient
from qdrant_client.http import models

from core.config import settings
from schemas.destination import DestinationPayload


class VectorService:
    """
    Semantic Data Access Layer.
    
    Interfaces with the Qdrant vector database to store and retrieve destinations
    based on high-dimensional semantic embeddings (384-D).
    """

    def __init__(self):
        """Initializes the Qdrant client and defines collection parameters."""
        self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.collection_name = "destinations"
        self.vector_size = 384  # Matches 'all-MiniLM-L6-v2' output dimensions.

    def _ensure_collection(self):
        """
        Idempotent check to ensure the target collection is provisioned correctly.
        
        Configures Cosine Similarity and HNSW indexing for high-performance 
        retrieval at scale.
        """
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size, distance=models.Distance.COSINE
                ),
                hnsw_config=models.HnswConfigDiff(
                    m=32, ef_construct=128, full_scan_threshold=10000
                ),
            )

    async def upsert_destination(
        self, destination_id: str, vector: List[float], payload: Dict[str, Any]
    ) -> bool:
        """
        Synchronizes a destination's semantic representation with the vector store.
        
        Args:
            destination_id: Unique identifier for the destination.
            vector: 384-D embedding vector.
            payload: Metadata dictionary (must conform to DestinationPayload).
            
        Returns:
            True if upsert was successful, False otherwise.
        """
        self._ensure_collection()
        try:
            # Enforce schema validation before storage to prevent index pollution.
            validated_payload = DestinationPayload(**payload)

            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=destination_id,
                        vector=vector,
                        payload=validated_payload.model_dump(),
                    )
                ],
            )
            return True
        except Exception as e:
            print(f"Error upserting to Qdrant: {e}")
            return False

    async def search_by_vibe(
        self,
        query_vector: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Performs a semantic similarity search based on a high-dimensional query.
        
        Args:
            query_vector: The embedding of the user's mood or intent.
            limit: Maximum number of results to return.
            filters: Optional Qdrant-native filters to apply during search.
            
        Returns:
            A list of hits including IDs, semantic scores, and payloads.
        """
        self._ensure_collection()
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=models.Filter(**filters) if filters else None,
                limit=limit,
            )
            return [
                {"id": hit.id, "score": hit.score, "payload": hit.payload}
                for hit in search_result
            ]
        except Exception as e:
            print(f"Error searching Qdrant: {e}")
            return []

    async def get_destination_vector(self, destination_id: str) -> Optional[List[float]]:
        """
        Retrieves the semantic vector for a specific destination.
        
        Args:
            destination_id: Target destination ID.
            
        Returns:
            The 384-D vector list, or None if not found.
        """
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[destination_id],
                with_vectors=True,
            )
            if result and result[0].vector is not None:
                vector = result[0].vector
                if isinstance(vector, list):
                    return cast(List[float], vector)
            return None
        except Exception as e:
            print(f"Error retrieving vector from Qdrant: {e}")
            return None

    async def delete_destination(self, destination_id: str) -> bool:
        """Removes a destination from the vector store."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[destination_id]),
            )
            return True
        except Exception as e:
            print(f"Error deleting from Qdrant: {e}")
            return False


# Singleton service instance
vector_service = VectorService()
