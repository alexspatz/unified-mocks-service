from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Union
import uvicorn

from models import (
    PaymentRequest, PaymentResponse,
    FiscalRequest, FiscalSuccessResponse, FiscalFailureResponse,
    KDSRequest, KDSSuccessResponse, KDSFailureResponse,
    ConfigUpdateRequest, LogEntry, ServiceConfig
)
from mocks import handle_payment_request, handle_fiscal_request, handle_kds_request
from storage import storage
from telegram_bot import start_bot, stop_bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    print("🚀 Starting Unified Mocks Service...")
    await start_bot()
    print("✅ Service started")

    yield

    # Shutdown
    print("🛑 Stopping Unified Mocks Service...")
    await stop_bot()
    print("✅ Service stopped")


app = FastAPI(
    title="Unified Mocks Service",
    description="Mock service for Payment Edge, Fiscal Edge, and KDS with Telegram management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Unified Mocks Service",
        "version": "1.0.0",
        "endpoints": {
            "payment": "/mocks/payment",
            "fiscal": "/mocks/fiscal",
            "kds": "/mocks/kds",
            "config": "/mocks/config",
            "logs": "/mocks/logs"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


# Payment Mock Endpoint
@app.post("/mocks/payment", response_model=PaymentResponse)
async def payment_mock(request: PaymentRequest):
    """
    Payment Edge Mock Endpoint

    Simulates payment terminal behavior with configurable responses.
    """
    try:
        response = await handle_payment_request(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Fiscal Mock Endpoint
@app.post("/mocks/fiscal", response_model=Union[FiscalSuccessResponse, FiscalFailureResponse])
async def fiscal_mock(request: FiscalRequest):
    """
    Fiscal Edge Mock Endpoint

    Simulates fiscal printer behavior with configurable responses.
    """
    try:
        response = await handle_fiscal_request(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# KDS Mock Endpoint
@app.post("/mocks/kds", response_model=Union[KDSSuccessResponse, KDSFailureResponse])
async def kds_mock(request: KDSRequest):
    """
    KDS (Kitchen Display System) Mock Endpoint

    Simulates kitchen display system behavior with configurable responses.
    """
    try:
        response = await handle_kds_request(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Configuration Endpoints
@app.get("/mocks/config")
async def get_config():
    """
    Get current configuration for all services
    """
    configs = storage.get_all_configs()
    return {
        service: {
            "mode": config.mode.value,
            "timeout_seconds": config.timeout_seconds,
            "default_response": config.default_response,
            "sequence_config": config.sequence_config.dict() if config.sequence_config else None
        }
        for service, config in configs.items()
    }


@app.post("/mocks/config")
async def update_config(request: ConfigUpdateRequest):
    """
    Update configuration for services
    """
    updated = []

    if request.payment:
        storage.update_config("payment", request.payment)
        updated.append("payment")

    if request.fiscal:
        storage.update_config("fiscal", request.fiscal)
        updated.append("fiscal")

    if request.kds:
        storage.update_config("kds", request.kds)
        updated.append("kds")

    return {
        "status": "ok",
        "updated": updated,
        "message": f"Configuration updated for: {', '.join(updated)}"
    }


# Logs Endpoint
@app.get("/mocks/logs")
async def get_logs(limit: int = 100):
    """
    Get recent logs

    Parameters:
    - limit: Maximum number of logs to return (default: 100, max: 1000)
    """
    limit = min(limit, 1000)
    logs = storage.get_logs(limit)

    return {
        "logs": [log.dict() for log in logs]
    }


# Service-specific status endpoints
@app.get("/mocks/payment/status")
async def payment_status():
    """Get Payment service status"""
    config = storage.get_config("payment")
    return {
        "service": "payment",
        "mode": config.mode.value,
        "timeout_seconds": config.timeout_seconds,
        "default_response": config.default_response
    }


@app.get("/mocks/fiscal/status")
async def fiscal_status():
    """Get Fiscal service status"""
    config = storage.get_config("fiscal")
    return {
        "service": "fiscal",
        "mode": config.mode.value,
        "timeout_seconds": config.timeout_seconds,
        "default_response": config.default_response
    }


@app.get("/mocks/kds/status")
async def kds_status():
    """Get KDS service status"""
    config = storage.get_config("kds")
    return {
        "service": "kds",
        "mode": config.mode.value,
        "timeout_seconds": config.timeout_seconds,
        "default_response": config.default_response
    }


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
