import asyncio

from sqlalchemy import text

from core.database import SessionLocal

# Baseline Destination Data for Sprint 4
DESTINATIONS = [
    {
        "iata_code": "CDG",
        "name": "Paris",
        "country": "France",
        "budget_level": "Luxury",
        "safety_index": 0.85,
        "climate_type": "Temperate",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "tags": ["culture", "history", "romantic", "museums"],
    },
    {
        "iata_code": "TYO",
        "name": "Tokyo",
        "country": "Japan",
        "budget_level": "Luxury",
        "safety_index": 0.98,
        "climate_type": "Temperate",
        "latitude": 35.6895,
        "longitude": 139.6917,
        "tags": ["technology", "food", "urban", "clean"],
    },
    {
        "iata_code": "BKK",
        "name": "Bangkok",
        "country": "Thailand",
        "budget_level": "Budget",
        "safety_index": 0.75,
        "climate_type": "Tropical",
        "latitude": 13.7563,
        "longitude": 100.5018,
        "tags": ["street_food", "nightlife", "temples", "affordable"],
    },
    {
        "iata_code": "REK",
        "name": "Reykjavik",
        "country": "Iceland",
        "budget_level": "Ultra-Luxury",
        "safety_index": 0.99,
        "climate_type": "Arctic",
        "latitude": 64.1466,
        "longitude": -21.9426,
        "tags": ["nature", "glaciers", "adventure", "quiet"],
    },
    {
        "iata_code": "DXB",
        "name": "Dubai",
        "country": "UAE",
        "budget_level": "Luxury",
        "safety_index": 0.92,
        "climate_type": "Desert",
        "latitude": 25.2048,
        "longitude": 55.2708,
        "tags": ["shopping", "luxury", "modern", "desert"],
    },
]


async def seed_postgres():
    print("--- Starting Postgres Baseline Seeding ---")
    db = SessionLocal()

    try:
        for dest in DESTINATIONS:
            # Idempotent Upsert logic
            query = text("""
                INSERT INTO destinations (iata_code, name, country, budget_level, safety_index, climate_type, latitude, longitude, tags)
                VALUES (:iata, :name, :country, :budget, :safety, :climate, :lat, :lon, CAST(:tags AS JSONB))
                ON CONFLICT (iata_code) DO UPDATE SET
                    budget_level = EXCLUDED.budget_level,
                    safety_index = EXCLUDED.safety_index,
                    climate_type = EXCLUDED.climate_type,
                    tags = EXCLUDED.tags,
                    updated_at = now();
            """)

            import json

            db.execute(
                query,
                {
                    "iata": dest["iata_code"],
                    "name": dest["name"],
                    "country": dest["country"],
                    "budget": dest["budget_level"],
                    "safety": dest["safety_index"],
                    "climate": dest["climate_type"],
                    "lat": dest["latitude"],
                    "lon": dest["longitude"],
                    "tags": json.dumps(dest["tags"]),
                },
            )

        db.commit()
        print(f"Successfully seeded {len(DESTINATIONS)} destinations.")

    except Exception as e:
        print(f"Seeding Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(seed_postgres())
