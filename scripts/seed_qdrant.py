import asyncio
from qdrant_client import QdrantClient
from qdrant_client.http import models
from services.llm import intelligence_service
import uuid

# Re-using the baseline data for consistency
DESTINATIONS = [
    {
        "iata_code": "CDG",
        "name": "Paris",
        "vibe_description": "A historic and romantic city with world-class museums, luxury shopping, and a sophisticated atmosphere.",
        "payload": {"budget": "Luxury", "safety": 0.85, "tags": ["culture", "history", "romantic"]}
    },
    {
        "iata_code": "TYO",
        "name": "Tokyo",
        "vibe_description": "A high-tech urban metropolis blending traditional temples with futuristic neon streets, exceptional food, and organized chaos.",
        "payload": {"budget": "Luxury", "safety": 0.98, "tags": ["technology", "food", "urban"]}
    },
    {
        "iata_code": "BKK",
        "name": "Bangkok",
        "vibe_description": "A vibrant tropical city known for ornate temples, bustling street food markets, and an energetic nightlife.",
        "payload": {"budget": "Budget", "safety": 0.75, "tags": ["street_food", "nightlife", "temples"]}
    },
    {
        "iata_code": "REK",
        "name": "Reykjavik",
        "vibe_description": "A quiet and clean arctic gateway to glaciers, hot springs, and breathtaking natural wonders under the northern lights.",
        "payload": {"budget": "Ultra-Luxury", "safety": 0.99, "tags": ["nature", "glaciers", "adventure"]}
    },
    {
        "iata_code": "DXB",
        "name": "Dubai",
        "vibe_description": "A desert oasis of modern architectural marvels, ultra-luxury shopping malls, and high-end artificial islands.",
        "payload": {"budget": "Luxury", "safety": 0.92, "tags": ["shopping", "luxury", "modern"]}
    }
]

async def seed_qdrant():
    print("--- Starting Qdrant Semantic Seeding ---")
    client = QdrantClient("localhost", port=6333)
    collection_name = "destinations"
    
    # 1. Re-initialize Collection
    print(f"Initializing collection: {collection_name}")
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
    )
    
    # 2. Generate and Upload Vectors
    points = []
    for dest in DESTINATIONS:
        print(f"Embedding {dest['name']}...")
        vector = await intelligence_service.generate_embedding(dest["vibe_description"])
        
        points.append(models.PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, dest["iata_code"])),
            vector=vector,
            payload={
                "iata_code": dest["iata_code"],
                "name": dest["name"],
                **dest["payload"]
            }
        ))
    
    client.upsert(collection_name=collection_name, points=points)
    print(f"Successfully seeded {len(points)} vectors to Qdrant.")

if __name__ == "__main__":
    asyncio.run(seed_qdrant())
