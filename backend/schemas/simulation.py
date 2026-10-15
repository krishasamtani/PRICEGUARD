from typing import List, Optional
from pydantic import BaseModel, Field

class SimulationRequest(BaseModel):
    commodity: str = Field("Onion", description="Target commodity")
    buffer_stock_available: float = Field(50000.0, ge=1000.0, le=500000.0, description="Total government buffer stock available in MT")
    elasticity: float = Field(-0.18, ge=-0.90, le=-0.01, description="Price elasticity of supply coefficient")
    holding_cost_per_mt: float = Field(450.0, ge=0.0, description="Monthly holding cost per MT (₹)")
    transport_cost_per_mt: float = Field(850.0, ge=0.0, description="Logistics transport cost per MT (₹)")
    override_current_price: Optional[float] = Field(None, description="Optional override for spot rate ₹/kg")
    override_forecast_price: Optional[float] = Field(None, description="Optional override for baseline forecast ₹/kg")
    override_daily_arrivals: Optional[float] = Field(None, description="Optional override for daily arrival volume")

class ScenarioOutcome(BaseModel):
    scenario: str = Field(..., description="Scenario identifier name")
    release_volume_mt: int = Field(..., description="Intervention release volume in Metric Tonnes")
    simulated_price: float = Field(..., description="Projected post-intervention equilibrium rate ₹/kg")
    price_reduction: float = Field(..., description="Absolute price relief achieved in ₹/kg")
    buffer_remaining_mt: int = Field(..., description="Residual buffer reserves after liquidation (MT)")
    intervention_cost_lakhs: float = Field(..., description="Fiscal implementation cost in ₹ Lakhs")
    market_risk_post_release: str = Field(..., description="Projected residual risk tier (LOW, MODERATE, HIGH)")

class SimulationResponse(BaseModel):
    commodity: str
    baseline_spot_price: float
    baseline_forecast_price: float
    available_buffer_mt: float
    elasticity_applied: float
    scenarios: List[ScenarioOutcome]
