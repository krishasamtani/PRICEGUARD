from fastapi import APIRouter, Query, Body, HTTPException
from typing import Optional
from backend.schemas.common import ApiResponse
from backend.schemas.simulation import SimulationRequest, SimulationResponse
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/simulation", tags=["What-If Buffer Simulator"])

@router.post("/buffer-intervention", response_model=ApiResponse[SimulationResponse], summary="Simulate Buffer Stock Liquidation (POST)")
async def simulate_buffer_post(
    req: SimulationRequest = Body(...)
):
    """
    Simulates market price equilibrium under varying buffer stock liquidation quotas (5k, 10k, 20k MT)
    based on calibrated supply-price elasticities and logistics costs.
    """
    try:
        sim_data = ml_service.simulate_buffer(
            commodity=req.commodity,
            buffer_stock_available=req.buffer_stock_available,
            elasticity=req.elasticity,
            holding_cost=req.holding_cost_per_mt,
            transport_cost=req.transport_cost_per_mt,
            override_current_price=req.override_current_price,
            override_forecast_price=req.override_forecast_price,
            override_daily_arrivals=req.override_daily_arrivals
        )
        return ApiResponse(
            success=True,
            message="Buffer simulation computed successfully",
            data=SimulationResponse(**sim_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

@router.get("/buffer-intervention", response_model=ApiResponse[SimulationResponse], summary="Simulate Buffer Stock Liquidation (GET)")
async def simulate_buffer_get(
    commodity: str = Query("Onion", description="Commodity name"),
    buffer_stock_available: float = Query(50000.0, description="Available buffer in MT"),
    elasticity: float = Query(-0.18, description="Supply elasticity coefficient"),
    force_demo: bool = Query(False, description="Force demo stream")
):
    """Convenience GET endpoint to execute buffer intervention sensitivity simulation."""
    try:
        sim_data = ml_service.simulate_buffer(
            commodity=commodity,
            buffer_stock_available=buffer_stock_available,
            elasticity=elasticity,
            force_demo=force_demo
        )
        return ApiResponse(
            success=True,
            message="Buffer simulation computed successfully",
            data=SimulationResponse(**sim_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")
