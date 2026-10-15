from fastapi import APIRouter, Query, HTTPException
from backend.schemas.common import ApiResponse
from backend.schemas.forecast import ForecastResponse
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/forecast", tags=["Multi-Horizon Forecasting"])

@router.get("", response_model=ApiResponse[ForecastResponse], summary="Multi-Horizon Price Forecast with Conformal CI")
async def get_forecast(
    commodity: str = Query("Onion", description="Commodity name: Onion or Tur"),
    force_demo: bool = Query(False, description="Force synthetic demo data stream")
):
    """
    Generates multi-horizon (7-day & 14-day) price forecasts using XGBoost models
    calibrated with Inductive Split Conformal Prediction (MAPIE) for rigorous 90% confidence bounds.
    """
    try:
        forecast_data = ml_service.get_full_forecast(commodity=commodity, force_demo=force_demo)
        return ApiResponse(
            success=True,
            message=f"Forecast computed successfully for {commodity}",
            data=ForecastResponse(**forecast_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting engine error: {str(e)}")
