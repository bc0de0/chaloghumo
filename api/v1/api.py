from fastapi import APIRouter

from api.v1.endpoints import recommendations, personas, destinations, ai, feedback

api_router = APIRouter()
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(personas.router, prefix="/personas", tags=["personas"])
api_router.include_router(destinations.router, prefix="/destinations", tags=["destinations"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
