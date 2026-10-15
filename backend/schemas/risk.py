from typing import Optional
from pydantic import BaseModel, Field

class RiskEvaluationResponse(BaseModel):
    commodity: str = Field(..., description="Target commodity")
    risk_level: str = Field(..., description="Risk tier: LOW, MODERATE, HIGH, or CRITICAL")
    z_score: float = Field(..., description="Statistical price anomaly Z-score")
    spike_probability: float = Field(..., description="Calibrated price surge probability (%)")
    badge_color: str = Field(..., description="Color indicator for dashboard (green, yellow, orange, red)")
    action_summary: str = Field(..., description="Actionable early warning directive for policymakers")
    current_price: float = Field(..., description="Current spot price ₹/kg")
    forecast_price_7d: float = Field(..., description="7-day point forecast ₹/kg")
    upper_bound_7d: float = Field(..., description="7-day upper conformal boundary ₹/kg")
    recent_mean_7d: float = Field(..., description="Recent 7-day average baseline price ₹/kg")
