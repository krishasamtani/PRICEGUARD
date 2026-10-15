from fastapi import APIRouter, Query, HTTPException
from backend.schemas.common import ApiResponse
from backend.schemas.risk import RiskEvaluationResponse
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/risk", tags=["Risk Engine & Early Warning"])

@router.get("/evaluate", response_model=ApiResponse[RiskEvaluationResponse], summary="Market Spike Risk Assessment")
async def evaluate_risk(
    commodity: str = Query("Onion", description="Commodity name: Onion or Tur"),
    force_demo: bool = Query(False, description="Force synthetic demo stream")
):
    """
    Computes statistical price anomaly Z-scores, calibrated spike probabilities,
    and assigns official risk classification tiers (LOW, MODERATE, HIGH, CRITICAL).
    """
    try:
        risk_data = ml_service.evaluate_risk(commodity=commodity, force_demo=force_demo)
        return ApiResponse(
            success=True,
            message="Risk evaluation completed",
            data=RiskEvaluationResponse(**risk_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk evaluation error: {str(e)}")
