from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class HorizonInterval(BaseModel):
    horizon_days: int = Field(..., description="Forecast horizon in days (e.g. 7 or 14)")
    point_forecast: float = Field(..., description="Point estimate of future price in ₹/kg")
    lower_bound: float = Field(..., description="Lower bound of conformal prediction interval in ₹/kg")
    upper_bound: float = Field(..., description="Upper bound of conformal prediction interval in ₹/kg")
    interval_width: float = Field(..., description="Total interval spread in ₹/kg")
    coverage_guarantee: str = Field("90%", description="Statistically calibrated coverage percentage")

class HorizonMetric(BaseModel):
    MAE: float = Field(..., description="Mean Absolute Error in ₹/kg")
    RMSE: float = Field(..., description="Root Mean Squared Error in ₹/kg")
    sMAPE: float = Field(..., description="Symmetric Mean Absolute Percentage Error (%)")

class PriceDataPoint(BaseModel):
    date: str = Field(..., description="Date string YYYY-MM-DD")
    price_per_kg: float = Field(..., description="Price in ₹/kg")
    arrival_qty: Optional[float] = Field(None, description="Arrivals in Quintals/MT")

class ForecastResponse(BaseModel):
    commodity: str = Field(..., description="Analyzed commodity (Onion or Tur)")
    current_price: float = Field(..., description="Latest recorded spot price in ₹/kg")
    recent_7d_mean: float = Field(..., description="7-day rolling average spot price in ₹/kg")
    recent_7d_std: float = Field(..., description="7-day rolling standard deviation in ₹/kg")
    recent_arrivals: float = Field(..., description="Latest recorded daily arrival quantity")
    is_demo: bool = Field(..., description="True if using synthetic demo stream")
    as_of_date: str = Field(..., description="Latest date of record")
    intervals: Dict[int, HorizonInterval] = Field(..., description="Conformal forecast intervals keyed by horizon")
    metrics: Dict[int, HorizonMetric] = Field(..., description="Validation metrics keyed by horizon")
    recent_history: List[PriceDataPoint] = Field(default_factory=list, description="Recent 60 days price history")
