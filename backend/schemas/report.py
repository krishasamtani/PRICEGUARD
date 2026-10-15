from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ReportRequest(BaseModel):
    commodity: str = Field("Onion", description="Commodity name")
    buffer_stock_available: float = Field(50000.0, description="Available buffer reserves (MT)")

class ReportResponse(BaseModel):
    commodity: str
    generated_at: str
    report_text: str = Field(..., description="Full-text official Situation Report brief")
    risk_level: str
    recommended_action: str
