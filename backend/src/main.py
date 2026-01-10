"""
FastAPI application instance for CryptoTracker Pro

Constitution Principles:
- I: Security-First (CORS configuration)
- II: Type Safety (type hints)
- III: API Reliability (health checks)
- VI: Error Resilience (global error handling)
- VII: Clean Architecture (separation of concerns)
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events

    Handles:
    - Redis connection pool initialization
    - External API client setup
    - Graceful shutdown cleanup
    """
    # Startup: Initialize resources
    # TODO: Initialize Redis connection pool
    # TODO: Initialize API clients
    print('🚀 CryptoTracker Pro API starting up...')

    yield

    # Shutdown: Cleanup resources
    # TODO: Close Redis connections
    # TODO: Close HTTP client sessions
    print('👋 CryptoTracker Pro API shutting down...')


# Create FastAPI application instance
app = FastAPI(
    title='CryptoTracker Pro API',
    description='Real-time cryptocurrency price tracking API',
    version='1.0.0',
    lifespan=lifespan,
    # OpenAPI documentation
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/api/v1/openapi.json',
)

# CORS middleware configuration (Constitution Principle I: Security-First)
# Allow frontend to communicate with backend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',  # Vite dev server
        'http://localhost:5174',  # Alternative Vite port
        'http://127.0.0.1:5173',
        'http://127.0.0.1:5174',
    ],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['*'],
    expose_headers=['X-Cache-Hit', 'X-Last-Updated', 'X-Data-Source'],
)


# Global exception handler for unhandled errors (Constitution Principle VI)
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """
    Catch-all exception handler to prevent server crashes
    Returns user-friendly error messages (FR-019)
    """
    return JSONResponse(
        status_code=500,
        content={
            'message': 'An unexpected error occurred. Please try again later.',
            'code': 'INTERNAL_SERVER_ERROR',
            'timestamp': '2026-01-10T00:00:00Z',  # TODO: Use actual timestamp
        },
    )


# Root endpoint
@app.get('/')
async def root() -> dict[str, str]:
    """Root endpoint with API information"""
    return {
        'name': 'CryptoTracker Pro API',
        'version': '1.0.0',
        'docs': '/docs',
        'health': '/api/v1/health',
    }


# TODO: Register API routes
# from src.api.routes import health, cryptocurrencies
# app.include_router(health.router, prefix='/api/v1', tags=['health'])
# app.include_router(cryptocurrencies.router, prefix='/api/v1', tags=['cryptocurrencies'])
