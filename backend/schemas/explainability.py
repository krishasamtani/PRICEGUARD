from typing import List
from pydantic import BaseModel, Field

class SHAPFactor(BaseModel):
    feature: str = Field(..., description="Feature variable name")
    impact: float = Field(..., description="Local SHAP value contribution in ₹/kg")
    abs_impact: float = Field(..., description="Magnitude of factor importance")
    actual_value: float = Field(..., description="Current observed raw value of feature")
    policy_driver: str = Field(..., description="Human-translated economic policy narrative")

class ExplainabilityResponse(BaseModel):
    commodity: str = Field(..., description="Analyzed commodity")
    horizon: int = Field(7, description="Forecast horizon analyzed (days)")
    scientific_guardrail: str = Field(
        "Feature attributions represent model associations and relative weight contributions, not counterfactual physical causation.",
        description="Methodological disclaimer"
    )
    top_drivers: List[SHAPFactor] = Field(..., description="Ranked top driving economic factors")
