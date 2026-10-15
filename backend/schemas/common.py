from typing import Generic, TypeVar, Optional, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool = Field(True, description="Indicates if the request was successful")
    message: str = Field("Success", description="Status or error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC response timestamp")
    data: Optional[T] = Field(None, description="Payload data")

class HealthCheckResponse(BaseModel):
    status: str = Field("healthy", description="System health status")
    version: str = Field("1.0.0", description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    active_commodities: List[str]
    system_name: str

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
