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
CHECKPOINT_FILE = "seed_checkpoint_production.json"
BATCH_SIZE = 100
CONCURRENCY_LIMIT = 10

# Semaphores to control concurrent tasks
sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

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
                if pop > 500000: # Focus on major cities for relevant entries
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
        return cities[:1000] # Cap at 1000 most relevant cities

async def generate_embedding_with_sem(text: str):
    async with sem:
        return await llm_service.generate_embedding(text)

async def process_batch(batch: List[Dict[str, Any]], completed_ids: set):
    enriched_data = []
    embedding_tasks = []
    
    for city in batch:
        city_str_id = city.get('iata') or f"{city['name']}_{city['country']}".replace(" ", "_").lower()
        city_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, city_str_id))
        if city_id in completed_ids: continue
        
        # Simple synthesis
        vibe = f"{city['name']} ({city['country']}) is a major hub with {city['population']} people. Known for its urban density and hub status."
        meta = {
            "climate_type": "Temperate", 
            "budget_level": "Mid-range", 
            "safety_index": 0.8, 
            "tags": ["urban", "hub"],
            "vibe_description": vibe
        }
        enriched_data.append((city_id, city, meta))
        embedding_tasks.append(generate_embedding_with_sem(vibe))
    
    if not embedding_tasks: return

    print(f"Generating {len(embedding_tasks)} embeddings...")
    embeddings = await asyncio.gather(*embedding_tasks)
    
    # Batch Upsert to Qdrant
    points = []
    for (city_id, city, meta), emb in zip(enriched_data, embeddings):
        payload = {**city, **meta}
        points.append(models.PointStruct(id=city_id, vector=emb, payload=payload))
    
    vector_service._ensure_collection()
    vector_service.client.upsert(collection_name=vector_service.collection_name, points=points)
    
    # Batch Upsert to Postgres
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
            db.merge(dest)
        db.commit()
        for city_id, _, _ in enriched_data: completed_ids.add(city_id)
    except Exception as e:
        print(f"Postgres Error: {e}")
        db.rollback()
    finally:
        db.close()

async def main():
    cities = await fetch_cities()
    completed_ids = set()
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f: completed_ids = set(json.load(f))
    
    print(f"Starting seeding for {len(cities)} cities...")
    for i in range(0, len(cities), BATCH_SIZE):
        batch = cities[i : i + BATCH_SIZE]
        await process_batch(batch, completed_ids)
        with open(CHECKPOINT_FILE, "w") as f: json.dump(list(completed_ids), f)
        print(f"Progress: {len(completed_ids)}/{len(cities)}")
    
    print("Seeding completed.")

if __name__ == "__main__":
    from models.destination import Base
    Base.metadata.create_all(bind=engine)
    asyncio.run(main())
