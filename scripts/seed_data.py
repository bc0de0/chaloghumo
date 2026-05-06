import uuid
import logging
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from core.database import SessionLocal
from core.config import settings
from models.destination import Destination, RegionType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample Seed Data: 20+ Diverse Destinations
SEED_DATA = [
    {"name": "Santorini, Greece", "lat": 36.3932, "lng": 25.4615, "elevation": 300, "region_type": RegionType.COASTAL, "base_vibe": ["Romantic", "Sunset", "Whitewashed", "Aegean", "Caldera"]},
    {"name": "Zermatt, Switzerland", "lat": 46.0207, "lng": 7.7491, "elevation": 1608, "region_type": RegionType.ALPINE, "base_vibe": ["Skiing", "Matterhorn", "Luxury", "Alpine", "Car-free"]},
    {"name": "Kyoto, Japan", "lat": 35.0116, "lng": 135.7681, "elevation": 50, "region_type": RegionType.URBAN, "base_vibe": ["Temples", "Zen", "Tradition", "Cherry Blossom", "Geisha"]},
    {"name": "Tuscany, Italy", "lat": 43.7711, "lng": 11.2486, "elevation": 150, "region_type": RegionType.RURAL, "base_vibe": ["Vineyards", "Rolling Hills", "Gastronomy", "Renaissance", "Slow-life"]},
    {"name": "Wadi Rum, Jordan", "lat": 29.5735, "lng": 35.4210, "elevation": 1000, "region_type": RegionType.DESERT, "base_vibe": ["Mars-like", "Bedouin", "Stargazing", "Red Sand", "Ancient"]},
    {"name": "Reykjavik, Iceland", "lat": 64.1265, "lng": -21.8174, "elevation": 15, "region_type": RegionType.COASTAL, "base_vibe": ["Geothermal", "Northern Lights", "Quirky", "Glacial", "Viking"]},
    {"name": "Banff, Canada", "lat": 51.1784, "lng": -115.5708, "elevation": 1383, "region_type": RegionType.ALPINE, "base_vibe": ["Turquoise Lakes", "Rockies", "Wildlife", "Grandeur", "Hiking"]},
    {"name": "Marrakech, Morocco", "lat": 31.6295, "lng": -7.9811, "elevation": 466, "region_type": RegionType.URBAN, "base_vibe": ["Souks", "Spices", "Riad", "Vibrant", "History"]},
    {"name": "Cotswolds, UK", "lat": 51.8330, "lng": -1.8433, "elevation": 200, "region_type": RegionType.RURAL, "base_vibe": ["Stone Cottages", "Tea", "Quaint", "Greenery", "English Garden"]},
    {"name": "Sedona, USA", "lat": 34.8697, "lng": -111.7610, "elevation": 1311, "region_type": RegionType.DESERT, "base_vibe": ["Vortex", "Red Rocks", "Spiritual", "Artistic", "Hiking"]},
    {"name": "Amalfi Coast, Italy", "lat": 40.6333, "lng": 14.6029, "elevation": 0, "region_type": RegionType.COASTAL, "base_vibe": ["Cliffs", "Lemons", "Glamour", "Azure", "Vertical"]},
    {"name": "Chamonix, France", "lat": 45.9237, "lng": 6.8694, "elevation": 1035, "region_type": RegionType.ALPINE, "base_vibe": ["Mont Blanc", "Extreme Sports", "Mountaineering", "Cosmopolitan", "Peak"]},
    {"name": "Tokyo, Japan", "lat": 35.6762, "lng": 139.6503, "elevation": 40, "region_type": RegionType.URBAN, "base_vibe": ["Neon", "Cyberpunk", "Sushi", "Efficiency", "Futuristic"]},
    {"name": "Provençe, France", "lat": 43.9352, "lng": 6.0679, "elevation": 300, "region_type": RegionType.RURAL, "base_vibe": ["Lavender", "Sun-drenched", "Rosé", "Chic", "Cicadas"]},
    {"name": "Joshua Tree, USA", "lat": 34.1353, "lng": -116.3131, "elevation": 800, "region_type": RegionType.DESERT, "base_vibe": ["Alien Trees", "Music", "Desert Modernism", "Climbing", "Isolation"]},
    {"name": "Bora Bora, French Polynesia", "lat": -16.5004, "lng": -151.7415, "elevation": 0, "region_type": RegionType.COASTAL, "base_vibe": ["Overwater Bungalows", "Coral", "Paradise", "Exclusivity", "Lagoon"]},
    {"name": "Aspen, USA", "lat": 39.1911, "lng": -106.8175, "elevation": 2405, "region_type": RegionType.ALPINE, "base_vibe": ["Apres-ski", "Celebrity", "Powder", "Aspen Trees", "High-end"]},
    {"name": "New York City, USA", "lat": 40.7128, "lng": -74.0060, "elevation": 10, "region_type": RegionType.URBAN, "base_vibe": ["Skyscrapers", "Energy", "Culture", "Broadway", "Diversity"]},
    {"name": "Chianti, Italy", "lat": 43.4687, "lng": 11.2882, "elevation": 400, "region_type": RegionType.RURAL, "base_vibe": ["Wine", "Olive Groves", "Rustic", "Stone Villages", "Etruscan"]},
    {"name": "Death Valley, USA", "lat": 36.4606, "lng": -116.8656, "elevation": -86, "region_type": RegionType.DESERT, "base_vibe": ["Extreme", "Salt Flats", "Desolate", "Dunes", "Vastness"]}
]

def get_embedding(text: str):
    """
    Mock embedding generator for seeding.
    In a real production environment, this would call Gemini text-embedding-004.
    Generating 768 dimensions of pseudo-random data based on string hash.
    """
    import random
    random.seed(text)
    return [random.uniform(-1, 1) for _ in range(768)]

def seed_data():
    db: Session = SessionLocal()
    q_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    
    collection_name = "destinations"

    try:
        logger.info(f"Seeding {len(SEED_DATA)} destinations...")
        
        for data in SEED_DATA:
            # 1. Create SQL Record
            destination_id = uuid.uuid4()
            db_destination = Destination(
                id=destination_id,
                name=data["name"],
                lat=data["lat"],
                lng=data["lng"],
                elevation=data["elevation"],
                region_type=data["region_type"],
                base_vibe=data["base_vibe"],
                dynamic_state={} # Initial state empty
            )
            db.add(db_destination)
            
            # 2. Create Vector Point
            # We combine vibe tags into a single string for embedding
            vibe_text = ", ".join(data["base_vibe"])
            embedding = get_embedding(vibe_text)
            
            q_client.upsert(
                collection_name=collection_name,
                points=[
                    qmodels.PointStruct(
                        id=str(destination_id),
                        vector=embedding,
                        payload={
                            "name": data["name"],
                            "region_type": data["region_type"].value,
                            "elevation": data["elevation"],
                            "vibe_tags": data["base_vibe"]
                        }
                    )
                ]
            )
            
        db.commit()
        logger.info("Database and Vector Store seeding complete.")
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
