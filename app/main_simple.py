"""Simplified FastAPI application for testing."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Multi-Service Automation Platform (Mid-Level)")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Multi-Service Automation Platform")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready Multi-Service Automation Platform with FastAPI - Mid-Level Features",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with version information."""
    return {
        "message": "Multi-Service Automation Platform",
        "version": settings.app_version,
        "status": "running",
        "api_version": "v2",
        "supported_versions": ["v1", "v2"],
        "features": [
            "FastAPI Backend",
            "Slack Integration",
            "Telegram Integration", 
            "Google Sheets Integration",
            "JWT Authentication",
            "Role-Based Access Control (RBAC)",
            "Rate Limiting",
            "Redis Caching",
            "WebSocket Support",
            "Background Jobs (Celery)",
            "API Versioning",
            "Monitoring & Metrics",
            "Admin Panel",
            "Docker Support"
        ],
        "endpoints": {
            "api_docs": "/docs",
            "health": "/health",
            "admin": "/api/v1/admin",
            "auth": "/api/v1/auth",
            "messages": "/api/v1/messages",
            "sheets": "/api/v1/sheets",
            "websocket": "/api/v1/ws/connect"
        }
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2025-09-10T03:48:00Z",
        "version": settings.app_version,
        "services": {
            "database": {"status": "healthy", "response_time": 0.001},
            "redis": {"status": "healthy", "response_time": 0.001},
            "external": {
                "slack": {"status": "configured", "response_time": 0.001},
                "telegram": {"status": "configured", "response_time": 0.001},
                "google_sheets": {"status": "configured", "response_time": 0.001}
            }
        },
        "system": {
            "platform": "Linux",
            "python_version": "3.13",
            "cpu_percent": 15.2,
            "memory_percent": 45.8,
            "disk_percent": 23.1
        }
    }


@app.get("/metrics")
async def get_metrics():
    """Get application metrics."""
    return {
        "metrics": {
            "requests_total": 1250,
            "response_time_avg": 0.125,
            "error_rate": 0.02,
            "active_users": 45
        },
        "timestamp": "2025-09-10T03:48:00Z"
    }


@app.get("/api/v1/admin/stats/overview")
async def get_system_overview():
    """Get system overview statistics."""
    return {
        "users": {
            "total": 150,
            "active": 120,
            "verified": 100,
            "recent_registrations": 25
        },
        "services": {
            "slack": 80,
            "telegram": 75,
            "google_sheets": 60
        },
        "sessions": 45,
        "metrics": {
            "requests_total": 1250,
            "response_time_avg": 0.125,
            "error_rate": 0.02
        }
    }


@app.get("/api/v1/admin/users")
async def list_users(page: int = 1, size: int = 20):
    """List users with pagination."""
    return {
        "users": [
            {
                "id": 1,
                "email": "user1@example.com",
                "username": "user1",
                "is_active": True,
                "created_at": "2025-09-01T10:00:00Z"
            },
            {
                "id": 2,
                "email": "user2@example.com", 
                "username": "user2",
                "is_active": True,
                "created_at": "2025-09-02T10:00:00Z"
            }
        ],
        "total": 150,
        "page": page,
        "size": size,
        "pages": 8
    }


@app.post("/api/v1/messages/send")
async def send_unified_message():
    """Send unified message to multiple services."""
    return {
        "success": True,
        "message": "Message sent successfully",
        "services": ["slack", "telegram"],
        "total_sent": 2,
        "total_failed": 0,
        "results": [
            {"service": "slack", "success": True, "message_id": "slack-123"},
            {"service": "telegram", "success": True, "message_id": "telegram-456"}
        ]
    }


@app.post("/api/v1/sheets/append")
async def append_to_sheet():
    """Append data to Google Sheet."""
    return {
        "success": True,
        "message": "Data appended to Google Sheet successfully",
        "updated_cells": 3,
        "updated_range": "Sheet1!A1:C1"
    }


@app.post("/api/v1/auth/login")
async def login():
    """Login user and return access token."""
    return {
        "access_token": "demo-jwt-token-12345",
        "token_type": "bearer",
        "expires_in": 1800
    }


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "ValidationError",
                "message": "Validation failed",
                "status_code": 422,
                "details": {"validation_errors": []}
            }
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "Internal server error",
                "status_code": 500
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_simple:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
