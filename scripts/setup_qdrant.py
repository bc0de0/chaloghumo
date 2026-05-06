import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_qdrant():
    client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    
    collection_name = "destinations"
    
    # Check if collection exists
    collections = client.get_collections().collections
    exists = any(c.name == collection_name for c in collections)
    
    if exists:
        logger.info(f"Collection '{collection_name}' already exists. Re-initializing indexing strategy.")
        # For now, we won't delete to avoid data loss during development, 
        # but in a fresh setup, we could.
    else:
        logger.info(f"Creating collection '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=768, # Dimension for text-embedding-004
                distance=models.Distance.COSINE
            ),
            # Optimize for high-recall semantic search
            hnsw_config=models.HnswConfigDiff(
                m=16,
                ef_construct=100,
                full_scan_threshold=10000,
            )
        )
    
    # Create payload indices for common filters (Environmental & Societal Domains)
    # This allows Qdrant to perform efficient filtering before semantic search.
    
    logger.info("Setting up payload indices...")
    
    # 1. Region Type (Categorical filtering)
    client.create_payload_index(
        collection_name=collection_name,
        field_name="region_type",
        field_schema=models.PayloadSchemaType.KEYWORD,
    )
    
    # 2. Match Score / Reputation (Numeric filtering)
    client.create_payload_index(
        collection_name=collection_name,
        field_name="elevation",
        field_schema=models.PayloadSchemaType.FLOAT,
    )

    logger.info("Qdrant vector store initialization complete.")

if __name__ == "__main__":
    setup_qdrant()
