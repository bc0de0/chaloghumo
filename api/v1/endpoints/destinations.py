from typing import Any, List
from fastapi import APIRouter, HTTPException
from schemas.destination import Destination, DestinationCreate

router = APIRouter()

# Mock storage for initial setup
db_destinations = []

@router.get("/", response_model=List[Destination])
def read_destinations() -> Any:
    """
    Retrieve all destinations.
    """
    return db_destinations

@router.post("/", response_model=Destination)
def create_destination(destination_in: DestinationCreate) -> Any:
    """
    Add a new destination to the catalog.
    """
    new_dest = {
        **destination_in.model_dump(),
        "id": f"d-{len(db_destinations) + 1}",
        "coordinates": {"lat": 0.0, "lng": 0.0},
        "metadata": {}
    }
    db_destinations.append(new_dest)
    return new_dest

@router.get("/{destination_id}", response_model=Destination)
def read_destination(destination_id: str) -> Any:
    """
    Get destination details by ID.
    """
    dest = next((d for d in db_destinations if d["id"] == destination_id), None)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    return dest
