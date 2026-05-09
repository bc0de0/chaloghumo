import asyncio
import uuid
from services.vector_store import vector_service
from services.llm import intelligence_service

MINIMAL_CITIES = [
    {
        "name": "Paris",
        "country": "FR",
        "lat": 48.8566,
        "lng": 2.3522,
        "vibe_description": "Paris is a vibrant metropolis located in FR. It offers a temperate climate and is known for museums, architecture, foodie. With a luxury budget profile, it's perfect for travelers seeking history.",
        "budget_level": "Luxury",
        "climate_type": "Temperate",
        "safety_index": 0.85,
        "tags": ["museums", "architecture", "foodie", "history"]
    },
    {
        "name": "Bali",
        "country": "ID",
        "lat": -8.4095,
        "lng": 115.1889,
        "vibe_description": "Bali is a charming destination located in ID. It offers a tropical climate and is known for beach, surfing, sunset. With a mid-range budget profile, it's perfect for travelers seeking adventure.",
        "budget_level": "Mid-range",
        "climate_type": "Tropical",
        "safety_index": 0.90,
        "tags": ["beach", "surfing", "sunset", "adventure"]
    },
    {
        "name": "Tokyo",
        "country": "JP",
        "lat": 35.6762,
        "lng": 139.6503,
        "vibe_description": "Tokyo is a vibrant metropolis located in JP. It offers a temperate climate and is known for nightlife, shopping, food. With a luxury budget profile, it's perfect for travelers seeking culture.",
        "budget_level": "Luxury",
        "climate_type": "Temperate",
        "safety_index": 0.98,
        "tags": ["nightlife", "shopping", "food", "culture"]
    }
]

async def seed_minimal_data():
    print("Starting on-the-fly seeding for in-memory DB...", flush=True)
    try:
        for city in MINIMAL_CITIES:
            print(f"DEBUG: Seeding {city['name']}...", flush=True)
            city_str_id = f"{city['name']}_{city['country']}".lower()
            city_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, city_str_id))
            
            try:
                embedding = await intelligence_service.generate_embedding(city['vibe_description'])
                print(f"DEBUG: Embedding for {city['name']} generated.", flush=True)
            except Exception as e:
                print(f"DEBUG: Embedding for {city['name']} failed: {e}", flush=True)
                import random
                embedding = [random.uniform(-1, 1) for _ in range(384)]

            success = await vector_service.upsert_destination(
                destination_id=city_id,
                vector=embedding,
                payload=city
            )
            print(f"DEBUG: Upsert for {city['name']} success: {success}", flush=True)
        print("Seeding completed successfully.", flush=True)
    except Exception as e:
        print(f"CRITICAL: Seeding failed with error: {e}", flush=True)

