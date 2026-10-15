from typing import Optional, Union
from pydantic import BaseModel, Field

class ReplayRequest(BaseModel):
    commodity: str = Field("Onion", description="Commodity to backtest (Onion or Tur)")
    replay_date: str = Field(..., description="Historical cutoff date in YYYY-MM-DD format")
    horizon: int = Field(7, description="Forecast horizon days to backtest")

class ReplayResponse(BaseModel):
    commodity: str
    replay_date: str
    as_of_price: float = Field(..., description="Observed spot price on the replay date ₹/kg")
    point_forecast: float = Field(..., description="Unbiased 7-day future price prediction ₹/kg")
    interval_lower: float = Field(..., description="Lower 90% conformal bound ₹/kg")
    interval_upper: float = Field(..., description="Upper 90% conformal bound ₹/kg")
    spike_probability: float = Field(..., description="Spike probability score calculated on cutoff date (%)")
    risk_level: str = Field(..., description="Historical risk assessment classification")
    actual_realized_price: Optional[float] = Field(None, description="Actual realized market price at T+H ₹/kg")
    was_accurate: bool = Field(..., description="True if realized price was contained within conformal prediction interval")
