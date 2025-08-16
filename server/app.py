"""FastAPI application for MCP Demo Project."""

import os
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import __version__
from .api import mcp_servers, tutorials


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="MCP Demo Project",
        description="Comprehensive MCP demonstration from beginner to expert",
        version=__version__,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Set up templates directory
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    os.makedirs(templates_dir, exist_ok=True)
    templates = Jinja2Templates(directory=templates_dir)
    
    # Set up static files directory
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Include API routers
    app.include_router(tutorials.router, prefix="/api/tutorials", tags=["tutorials"])
    app.include_router(mcp_servers.router, prefix="/api/servers", tags=["servers"])
    
    # Root endpoint
    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "title": "MCP Demo Project", "version": __version__}
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": __version__}
    
    # Error handlers
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception):
        """Handle 404 errors."""
        return JSONResponse(
            status_code=404,
            content={"detail": "The requested resource was not found."},
        )
    
    @app.exception_handler(500)
    async def server_error_handler(request: Request, exc: Exception):
        """Handle 500 errors."""
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred."},
        )
    
    return app


# Create the application instance
app = create_app()