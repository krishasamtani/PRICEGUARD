from fastapi import APIRouter, Query, Body, HTTPException, Response
from backend.schemas.common import ApiResponse
from backend.schemas.report import ReportRequest, ReportResponse
from backend.services.ml_service import ml_service
from datetime import datetime

router = APIRouter(prefix="/report", tags=["Executive Situation Briefing"])

@router.get("/briefing", response_model=ApiResponse[ReportResponse], summary="Generate Executive Situation Report (GET)")
async def generate_briefing_get(
    commodity: str = Query("Onion", description="Target commodity"),
    buffer_stock_available: float = Query(50000.0, description="Buffer reserves available (MT)"),
    force_demo: bool = Query(False, description="Force synthetic demo stream")
):
    """Generates an official Department of Consumer Affairs situation briefing memo."""
    try:
        rep_data = ml_service.generate_report(
            commodity=commodity,
            buffer_stock_available=buffer_stock_available,
            force_demo=force_demo
        )
        return ApiResponse(
            success=True,
            message="Executive briefing generated",
            data=ReportResponse(**rep_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")

@router.post("/briefing", response_model=ApiResponse[ReportResponse], summary="Generate Executive Situation Report (POST)")
async def generate_briefing_post(
    req: ReportRequest = Body(...)
):
    """Generates an official Department of Consumer Affairs situation briefing memo from JSON body."""
    try:
        rep_data = ml_service.generate_report(
            commodity=req.commodity,
            buffer_stock_available=req.buffer_stock_available
        )
        return ApiResponse(
            success=True,
            message="Executive briefing generated",
            data=ReportResponse(**rep_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")

@router.get("/download", summary="Download Executive Briefing as .txt file")
async def download_briefing_txt(
    commodity: str = Query("Onion", description="Target commodity"),
    buffer_stock_available: float = Query(50000.0, description="Buffer reserves (MT)"),
    force_demo: bool = Query(False, description="Force synthetic demo stream")
):
    """Generates and streams the situation report directly as a downloadable plain-text briefing attachment."""
    try:
        rep_data = ml_service.generate_report(
            commodity=commodity,
            buffer_stock_available=buffer_stock_available,
            force_demo=force_demo
        )
        filename = f"PRICEGUARD_Briefing_{commodity}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        return Response(
            content=rep_data["report_text"],
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report download error: {str(e)}")
