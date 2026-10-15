from fastapi import APIRouter, Query, HTTPException
from backend.schemas.common import ApiResponse
from backend.schemas.geography import GeographyResponse
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/geography", tags=["Geographic Intelligence"])

@router.get("/mandis", response_model=ApiResponse[GeographyResponse], summary="Geographic Mandi Spatial Matrix")
async def get_mandi_geography(
    commodity: str = Query("Onion", description="Commodity name: Onion or Tur"),
    force_demo: bool = Query(False, description="Force synthetic demo stream")
):
    """
    Returns geographical coordinates, arrival volumes, spot rates, and vulnerability
    classifications across primary Indian wholesale mandis (Lasalgaon, Azadpur, Latur, etc.).
    """
    try:
        geo_data = ml_service.get_geography(commodity=commodity, force_demo=force_demo)
        return ApiResponse(
            success=True,
            message="Geographic mandi matrix retrieved",
            data=GeographyResponse(**geo_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geography engine error: {str(e)}")
