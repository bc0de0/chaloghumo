from fastapi import APIRouter

from api.v1.endpoints import health, recommendations

api_router = APIRouter()
api_router.include_router(
    recommendations.router, prefix="/recommendations", tags=["recommendations"]
)
api_router.include_router(health.router, prefix="/health", tags=["system"])
