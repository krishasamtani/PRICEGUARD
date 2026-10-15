from typing import Optional
from pydantic import BaseModel, Field

class DecisionRecommendationResponse(BaseModel):
    commodity: str = Field(..., description="Target commodity")
    assessed_risk_level: str = Field(..., description="Current detected market risk tier")
    recommended_scenario: str = Field(..., description="Recommended policy intervention scenario")
    release_mt: int = Field(..., description="Optimal buffer stock liquidation volume (MT)")
    target_price: float = Field(..., description="Target equilibrium retail/wholesale price ₹/kg")
    expected_drop: float = Field(..., description="Expected price reduction ₹/kg")
    buffer_retained: int = Field(..., description="Remaining strategic buffer (MT)")
    estimated_budget_lakhs: float = Field(..., description="Estimated fiscal logistics cost in ₹ Lakhs")
    policymaker_rationale: str = Field(..., description="Strategic justification rationale for ministerial decision")
