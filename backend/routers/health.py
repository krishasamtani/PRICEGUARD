from fastapi import APIRouter
from datetime import datetime
from backend.schemas.common import HealthCheckResponse, ApiResponse
from backend.config import settings

router = APIRouter(tags=["System & Health"])

@router.get("/health", response_model=HealthCheckResponse, summary="System Health Check")
async def health_check():
    """Returns the operational status and metadata of the PRICEGUARD backend."""
    return HealthCheckResponse(
        status="healthy",
        version=settings.VERSION,
        timestamp=datetime.utcnow(),
        active_commodities=settings.COMMODITIES,
        system_name=settings.PROJECT_NAME
    )

@router.get("/metadata", response_model=ApiResponse[dict], summary="System Metadata & Configurations")
async def get_metadata():
    """Returns runtime parameters, default horizons, conformal confidence levels, and commodity settings."""
    return ApiResponse(
        success=True,
        message="System metadata retrieved successfully",
        data={
            "app_name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "commodities": settings.COMMODITIES,
            "supported_horizons": settings.HORIZONS,
            "conformal_confidence_level": settings.CONFIDENCE_LEVEL,
            "alpha": settings.ALPHA,
            "default_simulation": {
                "buffer_stock_mt": settings.DEFAULT_BUFFER_STOCK,
                "elasticity": settings.DEFAULT_ELASTICITY,
                "holding_cost_per_mt": settings.HOLDING_COST_PER_MT,
                "logistics_cost_per_mt": settings.LOGISTICS_COST_PER_MT
            }
        }
    )
