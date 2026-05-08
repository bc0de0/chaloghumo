import asyncio
import csv
import io
import json
import os
import random
import uuid
from typing import List, Dict, Any

import httpx
from sqlalchemy.orm import Session
from qdrant_client.http import models

from core.database import SessionLocal, engine
from models.destination import Destination
from services.llm import llm_service
from services.vector_store import vector_service

CITY_DATA_URL = "https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_public.csv"
CHECKPOINT_FILE = "seed_checkpoint_optimum.json"
BATCH_SIZE = 50

# Metadata Maps
CLIMATE_MAP = {"AF": "Arid", "AS": "Tropical", "EU": "Temperate", "NA": "Temperate", "SA": "Tropical", "OC": "Tropical", "AN": "Polar"}
BUDGET_MAP = {"EU": "Luxury", "NA": "Luxury", "AS": "Mid-range", "SA": "Mid-range", "AF": "Budget", "OC": "Luxury"}
TAGS_POOL = {
    "Urban": ["nightlife", "shopping", "museums", "architecture", "foodie"],
    "Nature": ["hiking", "mountains", "forests", "wildlife", "national-park"],
    "Coastal": ["beach", "surfing", "diving", "seafood", "sunset"],
    "Historical": ["ruins", "temples", "castles", "heritage", "history"]
}

async def fetch_cities() -> List[Dict[str, Any]]:
    print(f"Fetching city data from {CITY_DATA_URL}...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(CITY_DATA_URL)
        response.raise_for_status()
        f = io.StringIO(response.text)
        reader = csv.DictReader(f, delimiter='^')
        cities = []
        for row in reader:
            if row.get('location_type') in ['C', 'CA', 'A']:
                pop = int(row.get('population') or "0")
                cities.append({
                    "name": row.get('asciiname') or row.get('name'),
                    "country": row.get('country_code'),
                    "lat": float(row.get('latitude') or 0.0),
                    "lng": float(row.get('longitude') or 0.0),
                    "iata": row.get('iata_code'),
                    "continent": row.get('continent_name'),
                    "population": pop
                })
        cities.sort(key=lambda x: x['population'], reverse=True)
        return cities

def synthesize_metadata(city: Dict[str, Any]) -> Dict[str, Any]:
    continent = city.get('continent', 'EU')
    cont_code = "EU"
    if "Africa" in continent: cont_code = "AF"
    elif "Asia" in continent: cont_code = "AS"
    elif "North America" in continent: cont_code = "NA"
    elif "South America" in continent: cont_code = "SA"
    elif "Oceania" in continent: cont_code = "OC"
    
    climate = CLIMATE_MAP.get(cont_code, "Temperate")
    budget = BUDGET_MAP.get(cont_code, "Mid-range")
    safety = round(random.uniform(0.6, 0.95), 2)
    
    tags = random.sample(TAGS_POOL["Urban"] if city['population'] > 1000000 else TAGS_POOL["Nature"] + TAGS_POOL["Coastal"], 3)
    if random.random() > 0.7: tags.extend(random.sample(TAGS_POOL["Historical"], 1))
    tags = list(set(tags))
    
    vibe = f"{city['name']} is a {'vibrant metropolis' if city['population'] > 1000000 else 'charming destination'} " \
           f"in {city['country']} with a {climate.lower()} climate and {', '.join(tags[:3])} vibes."
    
    return {"climate_type": climate, "budget_level": budget, "safety_index": safety, "tags": tags, "vibe_description": vibe}

async def process_batch(batch: List[Dict[str, Any]], completed_ids: set):
    tasks = []
    enriched_data = []
    
    for city in batch:
        city_str_id = city.get('iata') or f"{city['name']}_{city['country']}".replace(" ", "_").lower()
        city_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, city_str_id))
        if city_id in completed_ids: continue
        
        meta = synthesize_metadata(city)
        enriched_data.append((city_id, city, meta))
        tasks.append(llm_service.generate_embedding(meta['vibe_description']))
    
    if not tasks: return

    embeddings = await asyncio.gather(*tasks)
    
    # 1. Upsert to Qdrant (Batch)
    points = []
    for (city_id, city, meta), emb in zip(enriched_data, embeddings):
        payload = {**city, **meta}
        points.append(models.PointStruct(id=city_id, vector=emb, payload=payload))
    
    vector_service._ensure_collection()
    vector_service.client.upsert(collection_name=vector_service.collection_name, points=points)
    
    # 2. Upsert to Postgres (Batch)
    db: Session = SessionLocal()
    try:
        for (city_id, city, meta), _ in zip(enriched_data, embeddings):
            dest = Destination(
                id=uuid.UUID(city_id),
                name=city["name"],
                country=city["country"],
                latitude=city["lat"],
                longitude=city["lng"],
                vibe_description=meta["vibe_description"],
                budget_level=meta["budget_level"],
                climate_type=meta["climate_type"],
                safety_index=meta["safety_index"],
                tags=meta["tags"]
            )
            db.merge(dest) # Use merge to handle idempotency
        db.commit()
        for city_id, _, _ in enriched_data: completed_ids.add(city_id)
    except Exception as e:
        print(f"Postgres Error: {e}")
        db.rollback()
    finally:
        db.close()

async def main(limit: int = 2000):
    cities = await fetch_cities()
    completed_ids = set()
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f: completed_ids = set(json.load(f))
    
    for i in range(0, min(len(cities), limit), BATCH_SIZE):
        batch = cities[i : i + BATCH_SIZE]
        print(f"Processing batch {i//BATCH_SIZE + 1}...")
        await process_batch(batch, completed_ids)
        with open(CHECKPOINT_FILE, "w") as f: json.dump(list(completed_ids), f)
    
    print(f"Optimum seeding completed. {len(completed_ids)} cities total.")

if __name__ == "__main__":
    asyncio.run(main(limit=2000))
