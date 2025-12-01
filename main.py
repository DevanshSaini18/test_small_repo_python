from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from time import time
import logging

from app.routes import router as api_router
from app.database import Base, engine, get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enterprise Todo Platform",
    version="2.0.0",
    description="Production-ready SaaS todo platform with multi-tenancy, RBAC, analytics, and webhooks",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing and logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and track response time."""
    start_time = time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    process_time = int((time() - start_time) * 1000)  # in milliseconds
    
    # Add custom header
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time}ms"
    )
    
    # TODO: Log to database for analytics
    # This would require extracting org_id from auth token
    # log_usage(db, org_id, request.url.path, request.method, response.status_code, process_time)
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(api_router, prefix="/api/v1", tags=["API"])

@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Enterprise Todo Platform API",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
