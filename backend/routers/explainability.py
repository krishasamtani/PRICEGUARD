from fastapi import APIRouter, Query, HTTPException
from backend.schemas.common import ApiResponse
from backend.schemas.explainability import ExplainabilityResponse
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/explain", tags=["Explainable AI (TreeSHAP)"])

@router.get("", response_model=ApiResponse[ExplainabilityResponse], summary="Explainable AI Factor Attributions")
async def explain_forecast(
    commodity: str = Query("Onion", description="Commodity name: Onion or Tur"),
    horizon: int = Query(7, description="Forecast horizon days (e.g. 7 or 14)"),
    top_k: int = Query(4, ge=1, le=10, description="Number of top driving factors to return"),
    force_demo: bool = Query(False, description="Force synthetic demo stream")
):
    """
    Deconstructs the forecast using TreeSHAP to quantify the exact economic factor
    contributions (arrivals, historical momentum, weather deficits) into human-readable policy narratives.
    """
    try:
        explain_data = ml_service.get_explainability(
            commodity=commodity,
            horizon=horizon,
            top_k=top_k,
            force_demo=force_demo
        )
        return ApiResponse(
            success=True,
            message="Explainability factors computed successfully",
            data=ExplainabilityResponse(**explain_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explainability engine error: {str(e)}")
