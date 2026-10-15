import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError

from backend.config import settings
from backend.services.ml_service import ml_service
from backend.schemas.common import ErrorResponse

# Import all routers
from backend.routers.health import router as health_router
from backend.routers.data import router as data_router
from backend.routers.forecast import router as forecast_router
from backend.routers.risk import router as risk_router
from backend.routers.explainability import router as explain_router
from backend.routers.geography import router as geo_router
from backend.routers.simulation import router as sim_router
from backend.routers.decision import router as decision_router
from backend.routers.replay import router as replay_router
from backend.routers.report import router as report_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PRICEGUARD")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager. Pre-warms the XGBoost ML models and data pipelines on startup.
    """
    logger.info("🛡️ Starting PRICEGUARD Decision Support API...")
    try:
        # Pre-warm Onion models in background
        logger.info("⚡ Pre-warming feature pipelines and ML models for Onion...")
        ml_service.get_trained_models(commodity="Onion")
        logger.info("✅ ML Cache initialized successfully.")
    except Exception as e:
        logger.warning(f"⚠️ Model pre-warming encountered an issue (will re-attempt on demand): {e}")
    yield
    logger.info("🛡️ PRICEGUARD Decision Support API shutdown.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Timing Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time-Sec"] = f"{process_time:.4f}"
    return response

# Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            success=False,
            message="Invalid request parameters",
            error_detail=str(exc.errors())
        ).model_dump(mode="json")
    )

# Generic Exception Handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            message="Internal server error",
            error_detail=str(exc)
        ).model_dump(mode="json")
    )

# Include Routers under /api/v1
api_v1 = settings.API_V1_STR
app.include_router(health_router, prefix=api_v1)
app.include_router(data_router, prefix=api_v1)
app.include_router(forecast_router, prefix=api_v1)
app.include_router(risk_router, prefix=api_v1)
app.include_router(explain_router, prefix=api_v1)
app.include_router(geo_router, prefix=api_v1)
app.include_router(sim_router, prefix=api_v1)
app.include_router(decision_router, prefix=api_v1)
app.include_router(replay_router, prefix=api_v1)
app.include_router(report_router, prefix=api_v1)

@app.get("/", summary="Root Redirect to Swagger Documentation", include_in_schema=False)
async def root():
    """Redirects base path to interactive Swagger API documentation."""
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
