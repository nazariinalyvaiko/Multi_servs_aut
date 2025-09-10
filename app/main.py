"""Main FastAPI application with mid-level features."""

import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.core.database import create_tables
from app.core.exceptions import (
    BaseAPIException, ValidationError, AuthenticationError,
    AuthorizationError, NotFoundError, ConflictError,
    RateLimitError, ServiceUnavailableError, ExternalServiceError,
    create_error_response, handle_validation_error
)
from app.core.monitoring import RequestMetrics, HealthChecker, APIAnalytics
from app.core.versioning import version_manager
from app.api.v1 import auth, messages, sheets, websocket, admin
from services.slack_service import SlackService
from services.telegram_service import TelegramService

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
    create_tables()
    
    # Set up webhooks
    try:
        telegram_service = TelegramService()
        webhook_result = await telegram_service.set_webhook(settings.telegram_webhook_url)
        if webhook_result["success"]:
            logger.info("Telegram webhook set successfully")
        else:
            logger.warning(f"Failed to set Telegram webhook: {webhook_result['error']}")
    except Exception as e:
        logger.error(f"Error setting up webhooks: {str(e)}")
    
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

# Add request metrics middleware
app.add_middleware(RequestMetrics)

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")
app.include_router(sheets.router, prefix="/api/v1")
app.include_router(websocket.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def track_api_usage(request: Request, call_next):
    """Track API usage for analytics."""
    start_time = time.time()
    
    # Get user ID if available
    user_id = getattr(request.state, 'user_id', None)
    
    response = await call_next(request)
    
    # Calculate metrics
    duration = time.time() - start_time
    status_code = response.status_code
    
    # Track usage
    await APIAnalytics.track_api_usage(
        user_id=user_id,
        endpoint=request.url.path,
        method=request.method,
        status_code=status_code,
        response_time=duration,
        request_size=len(request.body) if hasattr(request, 'body') else 0
    )
    
    return response


@app.get("/")
async def root():
    """Root endpoint with version information."""
    return {
        "message": "Multi-Service Automation Platform",
        "version": settings.app_version,
        "status": "running",
        "api_version": version_manager.get_current_version(),
        "supported_versions": version_manager.get_supported_versions(),
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
    health_checker = HealthChecker()
    
    # Check all services
    db_health = await health_checker.check_database()
    redis_health = await health_checker.check_redis()
    external_health = await health_checker.check_external_services()
    system_info = await health_checker.get_system_info()
    
    # Determine overall status
    all_healthy = all([
        db_health["status"] == "healthy",
        redis_health["status"] == "healthy"
    ])
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "timestamp": time.time(),
        "version": settings.app_version,
        "services": {
            "database": db_health,
            "redis": redis_health,
            "external": external_health
        },
        "system": system_info
    }


@app.get("/metrics")
async def get_metrics():
    """Get application metrics."""
    from app.core.monitoring import metrics
    return {
        "metrics": metrics.get_metrics(),
        "timestamp": time.time()
    }


# Webhook handlers
@app.post("/api/v1/slack/webhook")
async def slack_webhook(request: Request):
    """Handle Slack webhook events."""
    try:
        # Get headers
        timestamp = request.headers.get("X-Slack-Request-Timestamp")
        signature = request.headers.get("X-Slack-Signature")
        
        # Get body
        body = await request.body()
        
        # Verify webhook
        slack_service = SlackService()
        if not slack_service.verify_webhook(timestamp, body.decode(), signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Slack signature"
            )
        
        # Process webhook data
        data = await request.json()
        
        # Handle different event types
        if data.get("type") == "url_verification":
            return {"challenge": data.get("challenge")}
        
        # Process message events
        if data.get("type") == "event_callback":
            event = data.get("event", {})
            if event.get("type") == "message" and not event.get("bot_id"):
                # Handle incoming message
                logger.info(f"Received Slack message: {event.get('text', '')}")
                # Here you could process the message, store it, etc.
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing Slack webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook"
        )


@app.post("/api/v1/telegram/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook events."""
    try:
        # Get webhook data
        data = await request.json()
        
        # Verify webhook
        telegram_service = TelegramService()
        if not telegram_service.verify_webhook(data):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Telegram webhook data"
            )
        
        # Process message
        message = data.get("message", {})
        if message:
            text = message.get("text", "")
            chat_id = message.get("chat", {}).get("id")
            user = message.get("from", {})
            
            logger.info(f"Received Telegram message from {user.get('username', 'unknown')}: {text}")
            # Here you could process the message, store it, etc.
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook"
        )


# Exception handlers
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """Handle custom API exceptions."""
    return create_error_response(exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return handle_validation_error(exc)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "status_code": exc.status_code
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
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
