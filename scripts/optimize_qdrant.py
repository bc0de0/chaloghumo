from qdrant_client import QdrantClient
from qdrant_client.http import models

def optimize_qdrant():
    print("--- Starting Qdrant Collection Optimization ---")
    client = QdrantClient("localhost", port=6333)
    collection_name = "destinations"
    
    # 1. Update HNSW Parameters for High Performance
    # m: Max number of edges per node (higher = more accurate, slower indexing)
    # ef_construct: Candidate list size during index construction
    print("Tuning HNSW indexing parameters...")
    client.update_collection(
        collection_name=collection_name,
        optimizer_config=models.OptimizersConfigDiff(
            indexing_threshold=10000, # Start indexing after 10k points
            memmap_threshold=20000    # Use mmap for large collections
        ),
        hnsw_config=models.HnswConfigDiff(
            m=16,
            ef_construct=100,
            full_scan_threshold=1000 # Use full scan for very small searches
        )
    )
    
    # 2. Create Payload Indices
    # Accelerates the "Relational Pruning" if we filter inside Qdrant
    print("Creating payload indices for budget and tags...")
    client.create_payload_index(
        collection_name=collection_name,
        field_name="budget",
        field_schema=models.PayloadSchemaType.KEYWORD
    )
    
    client.create_payload_index(
        collection_name=collection_name,
        field_name="tags",
        field_schema=models.PayloadSchemaType.KEYWORD
    )
    
    print("Qdrant collection optimized and ready for production.")

if __name__ == "__main__":
    optimize_qdrant()
