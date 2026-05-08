import asyncio
import json
import os
import httpx
import random
from typing import List, Dict, Any
from services.llm import llm_service
from services.vector_store import vector_service

import csv
import io

CITY_DATA_URL = "https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_public.csv"
CHECKPOINT_FILE = "seed_checkpoint.json"

# Heuristics for data enrichment
CLIMATE_MAP = {
    "AF": "Arid",
    "AS": "Tropical",
    "EU": "Temperate",
    "NA": "Temperate",
    "SA": "Tropical",
    "OC": "Tropical",
    "AN": "Polar"
}

BUDGET_MAP = {
    "EU": "Luxury",
    "NA": "Luxury",
    "AS": "Mid-range",
    "SA": "Mid-range",
    "AF": "Budget",
    "OC": "Luxury"
}

TAGS_POOL = {
    "Urban": ["nightlife", "shopping", "museums", "architecture", "foodie"],
    "Nature": ["hiking", "mountains", "forests", "wildlife", "national-park"],
    "Coastal": ["beach", "surfing", "diving", "seafood", "sunset"],
    "Historical": ["ruins", "temples", "castles", "heritage", "history"]
}

async def fetch_cities() -> List[Dict[str, Any]]:
    """
    Download and parse the opentraveldata POR dataset.
    Uses '^' as delimiter.
    """
    print(f"Fetching city data from {CITY_DATA_URL}...")
    async with httpx.AsyncClient() as client:
        # Large file, we'll stream or just read it if memory allows
        response = await client.get(CITY_DATA_URL)
        response.raise_for_status()
        
        f = io.StringIO(response.text)
        reader = csv.DictReader(f, delimiter='^')
        
        cities = []
        for row in reader:
            # location_type 'C' for City, 'H' for Heliport, 'A' for Airport, 'R' for Railway...
            # We want Cities and maybe some Airports that act as city hubs
            if row.get('location_type') in ['C', 'CA', 'A']:
                pop_str = row.get('population') or "0"
                pop = int(pop_str) if pop_str.isdigit() else 0
                
                cities.append({
                    "name": row.get('name') or row.get('asciiname'),
                    "country": row.get('country_code'),
                    "lat": float(row.get('latitude')) if row.get('latitude') else 0.0,
                    "lng": float(row.get('longitude')) if row.get('longitude') else 0.0,
                    "iata": row.get('iata_code'),
                    "continent": row.get('continent_name'),
                    "population": pop
                })
        
        # Sort by population to get major cities first
        cities.sort(key=lambda x: x['population'], reverse=True)
        return cities

def load_checkpoint() -> set:
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            try:
                return set(json.load(f))
            except:
                return set()
    return set()

def save_checkpoint(completed_ids: set):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(list(completed_ids), f)

def synthesize_metadata(city: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesize missing metadata for DestinationPayload.
    """
    continent = city.get('continent', 'EU')
    # Rough mapping of continent names to codes
    cont_code = "EU"
    if "Africa" in continent: cont_code = "AF"
    elif "Asia" in continent: cont_code = "AS"
    elif "North America" in continent: cont_code = "NA"
    elif "South America" in continent: cont_code = "SA"
    elif "Oceania" in continent: cont_code = "OC"
    elif "Antarctica" in continent: cont_code = "AN"

    climate = CLIMATE_MAP.get(cont_code, "Temperate")
    budget = BUDGET_MAP.get(cont_code, "Mid-range")
    
    # Randomize safety index around a baseline
    safety = round(random.uniform(0.6, 0.95), 2)
    
    # Assign tags based on population (Urban) or randomly
    tags = []
    if city['population'] > 1000000:
        tags.extend(random.sample(TAGS_POOL["Urban"], 3))
    else:
        # Mix of Nature and Coastal if population is smaller
        pool = TAGS_POOL["Nature"] + TAGS_POOL["Coastal"]
        tags.extend(random.sample(pool, 3))
        
    if random.random() > 0.7:
        tags.extend(random.sample(TAGS_POOL["Historical"], 2))
        
    tags = list(set(tags)) # Unique
    
    # Construct a more 'semantic' vibe description
    vibe = f"{city['name']} is a {'vibrant metropolis' if city['population'] > 1000000 else 'charming destination'} " \
           f"located in {city['country']}. It offers a {climate.lower()} climate and is known for {', '.join(tags[:3])}. " \
           f"With a {budget.lower()} budget profile, it's perfect for travelers seeking {tags[-1] if tags else 'adventure'}."
    
    return {
        "climate_type": climate,
        "budget_level": budget,
        "safety_index": safety,
        "tags": tags,
        "vibe_description": vibe
    }

async def seed_data(limit: int = 1000):
    """
    Main seeding logic.
    """
    cities_all = await fetch_cities()
    completed_ids = load_checkpoint()
    
    count = 0
    # Process only top N major cities for quality
    for city in cities_all:
        if count >= limit:
            break
            
        city_str_id = city.get('iata') or f"{city['name']}_{city['country']}".replace(" ", "_").lower()
        import uuid
        # Qdrant requires UUID or integer. Generate deterministic UUID from city string.
        city_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, city_str_id))

        if city_id in completed_ids:
            count += 1 # Still count as processed if we skip
            continue
            
        print(f"Processing {count+1}/{limit}: {city['name']}, {city['country']} (Pop: {city['population']})...")
        
        # Enrich metadata
        meta = synthesize_metadata(city)
        
        # 2. Generate embedding
        embedding = await llm_service.generate_embedding(meta['vibe_description'])
        
        # 3. Upsert to Qdrant
        payload = {
            "name": city["name"],
            "country": city["country"],
            "lat": city["lat"],
            "lng": city["lng"],
            "iata": city.get('iata'),
            "vibe_description": meta['vibe_description'],
            "budget_level": meta['budget_level'],
            "climate_type": meta['climate_type'],
            "safety_index": meta['safety_index'],
            "tags": meta['tags']
        }
        
        success = await vector_service.upsert_destination(
            destination_id=city_id,
            vector=embedding,
            payload=payload
        )
        
        if success:
            completed_ids.add(city_id)
            save_checkpoint(completed_ids)
            count += 1
        else:
            print(f"Failed to upsert {city['name']}")
            
    print(f"Seeding completed. {len(completed_ids)} cities total in DB.")

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    # Ensure Qdrant is ready
    asyncio.run(seed_data(limit=1000))
