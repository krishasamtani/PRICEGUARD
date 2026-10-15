from fastapi import APIRouter, Query, HTTPException
from backend.schemas.common import ApiResponse
from backend.schemas.decision import DecisionRecommendationResponse
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/decision", tags=["Policy Decision Support"])

@router.get("/recommend", response_model=ApiResponse[DecisionRecommendationResponse], summary="Optimal Policy Intervention Recommendation")
async def recommend_optimal_policy(
    commodity: str = Query("Onion", description="Commodity name: Onion or Tur"),
    buffer_stock_available: float = Query(50000.0, description="Current buffer stock available in MT"),
    elasticity: float = Query(-0.18, description="Supply price elasticity coefficient"),
    force_demo: bool = Query(False, description="Force synthetic demo stream")
):
    """
    Evaluates optimal market intervention trade-offs between price stabilization,
    buffer conservation, and fiscal expenditure to formulate policy guidance.
    """
    try:
        decision_data = ml_service.recommend_decision(
            commodity=commodity,
            buffer_stock_available=buffer_stock_available,
            elasticity=elasticity,
            force_demo=force_demo
        )
        return ApiResponse(
            success=True,
            message="Optimal policy evaluated successfully",
            data=DecisionRecommendationResponse(**decision_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision engine error: {str(e)}")
