from fastapi import APIRouter, Query, Body, HTTPException
from backend.schemas.common import ApiResponse
from backend.schemas.replay import ReplayRequest, ReplayResponse
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/replay", tags=["Historical Crisis Replay & Validation"])

@router.post("/crisis", response_model=ApiResponse[ReplayResponse], summary="Execute Historical Crisis Replay (POST)")
async def replay_crisis_post(
    req: ReplayRequest = Body(...)
):
    """
    Backtests predictive performance by masking future data before a chosen historical cutoff date
    and validating if the realized price falls within the 90% conformal prediction interval.
    """
    try:
        rep_data = ml_service.replay_crisis(
            commodity=req.commodity,
            replay_date=req.replay_date,
            horizon=req.horizon
        )
        return ApiResponse(
            success=True,
            message=f"Historical crisis replay executed for {req.replay_date}",
            data=ReplayResponse(**rep_data)
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crisis replay failed: {str(e)}")

@router.get("/crisis", response_model=ApiResponse[ReplayResponse], summary="Execute Historical Crisis Replay (GET)")
async def replay_crisis_get(
    commodity: str = Query("Onion", description="Commodity name: Onion or Tur"),
    replay_date: str = Query("2026-01-20", description="Historical date in YYYY-MM-DD"),
    horizon: int = Query(7, description="Forecast horizon days"),
    force_demo: bool = Query(False, description="Force demo stream")
):
    """Convenience GET endpoint for historical backtest replay."""
    try:
        rep_data = ml_service.replay_crisis(
            commodity=commodity,
            replay_date=replay_date,
            horizon=horizon,
            force_demo=force_demo
        )
        return ApiResponse(
            success=True,
            message=f"Historical crisis replay executed for {replay_date}",
            data=ReplayResponse(**rep_data)
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crisis replay failed: {str(e)}")
