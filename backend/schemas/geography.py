from typing import List
from pydantic import BaseModel, Field

class MandiHub(BaseModel):
    mandi_name: str = Field(..., description="Wholesale market center name")
    state: str = Field(..., description="State code or name")
    latitude: float = Field(..., description="Geographical latitude")
    longitude: float = Field(..., description="Geographical longitude")
    spot_rate: float = Field(..., description="Current spot price ₹/kg")
    arrival_tonnes: float = Field(..., description="Daily arrival quantity in Tonnes")
    vulnerability_tier: str = Field(..., description="Vulnerability classification (LOW, MODERATE, HIGH)")

class GeographyResponse(BaseModel):
    commodity: str = Field(..., description="Analyzed commodity")
    mandis: List[MandiHub] = Field(..., description="List of primary reporting wholesale mandis")
    total_reporting_mandis: int = Field(..., description="Total active mandis")
    high_vulnerability_count: int = Field(..., description="Number of mandis in high vulnerability tier")
