from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from backend.schemas.common import ApiResponse
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/data", tags=["Market Data & Ingestion"])

@router.get("/summary", response_model=ApiResponse[Dict[str, Any]], summary="Market Data Summary")
async def get_data_summary(
    commodity: str = Query("Onion", description="Commodity name: Onion or Tur"),
    force_demo: bool = Query(False, description="Force synthetic demo stream")
):
    """Returns dataset summary statistics, date range, and current market baseline."""
    try:
        feat_df, is_demo = ml_service.get_pipeline_data(commodity=commodity, force_demo=force_demo)
        
        start_date = feat_df['date'].min().strftime('%Y-%m-%d')
        end_date = feat_df['date'].max().strftime('%Y-%m-%d')
        total_days = len(feat_df)
        
        latest_row = feat_df.iloc[-1]
        
        return ApiResponse(
            success=True,
            message="Data summary retrieved successfully",
            data={
                "commodity": commodity,
                "is_demo_stream": is_demo,
                "total_records": total_days,
                "start_date": start_date,
                "end_date": end_date,
                "latest_spot_price": round(float(latest_row['price_per_kg']), 2),
                "latest_arrivals": round(float(latest_row['arrival_qty']), 2),
                "rolling_7d_mean": round(float(latest_row['price_roll_mean_7']), 2),
                "rolling_7d_std": round(float(latest_row['price_roll_std_7']), 2),
                "recent_rainfall_mm": round(float(latest_row.get('rainfall_7d_mm', 0.0)), 2)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load data summary: {str(e)}")

@router.get("/history", response_model=ApiResponse[List[Dict[str, Any]]], summary="Historical Time Series")
async def get_price_history(
    commodity: str = Query("Onion", description="Commodity name: Onion or Tur"),
    days: int = Query(60, ge=7, le=365, description="Number of historical days to return"),
    force_demo: bool = Query(False, description="Force synthetic demo stream")
):
    """Retrieves cleaned historical time series including spot price, arrivals, and weather indicators."""
    try:
        feat_df, is_demo = ml_service.get_pipeline_data(commodity=commodity, force_demo=force_demo)
        history_df = feat_df.tail(days)
        
        records = []
        for _, row in history_df.iterrows():
            rec = {
                "date": row['date'].strftime('%Y-%m-%d'),
                "price_per_kg": round(float(row['price_per_kg']), 2),
                "arrival_qty": round(float(row['arrival_qty']), 2),
                "price_roll_mean_7": round(float(row['price_roll_mean_7']), 2),
                "rainfall_7d_mm": round(float(row.get('rainfall_7d_mm', 0.0)), 2)
            }
            records.append(rec)
            
        return ApiResponse(
            success=True,
            message=f"Retrieved past {len(records)} records for {commodity}",
            data=records
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")
