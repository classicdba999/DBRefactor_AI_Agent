"""
FastAPI main application file.

This module sets up the FastAPI application with all routes,
middleware, and WebSocket support.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import structlog
from typing import List
import json
import os

from app.config import settings
from app.agents.registry import registry
from app.agents.db_discoverer import DBDiscovererAgent
from app.workflow.engine import WorkflowEngine

logger = structlog.get_logger(__name__)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("websocket_connected", total_connections=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("websocket_disconnected", total_connections=len(self.active_connections))

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("broadcast_failed", error=str(e))


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("application_starting", app_name=settings.app.app_name)

    # Initialize and register agents
    registry.register_agent(DBDiscovererAgent())

    logger.info(
        "agents_registered",
        total_agents=len(registry),
        agents=registry.list_agent_names()
    )

    yield

    # Shutdown
    logger.info("application_shutting_down")


# Create FastAPI app
app = FastAPI(
    title=settings.app.app_name,
    version=settings.app.app_version,
    description="Agentic framework for database migration",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.api.v1 import agents, discovery, workflow, health

# Include routers
app.include_router(health.router, prefix=f"{settings.app.api_prefix}", tags=["health"])
app.include_router(agents.router, prefix=f"{settings.app.api_prefix}/agents", tags=["agents"])
app.include_router(discovery.router, prefix=f"{settings.app.api_prefix}/discovery", tags=["discovery"])
app.include_router(workflow.router, prefix=f"{settings.app.api_prefix}/workflows", tags=["workflows"])


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError as e:
                logger.warning("invalid_json_received", error=str(e), data=data[:100])
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                continue

            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif message.get("type") == "subscribe":
                # Client subscribes to specific events
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": message.get("channel")
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("websocket_error", error=str(e))
        manager.disconnect(websocket)


# Serve static files (React build)
# Use absolute path for better Docker compatibility
ui_dist_path = os.environ.get(
    "UI_DIST_PATH",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ui", "dist"))
)

if os.path.exists(ui_dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(ui_dist_path, "assets")), name="assets")

    @app.get("/")
    async def serve_ui():
        """Serve the React UI"""
        return FileResponse(os.path.join(ui_dist_path, "index.html"))

    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        """Catch-all route for React Router"""
        # Don't catch API routes or WebSocket
        if full_path.startswith("api") or full_path.startswith("/api") or full_path.startswith("ws"):
            return {"error": "Not found"}

        file_path = os.path.join(ui_dist_path, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)

        return FileResponse(os.path.join(ui_dist_path, "index.html"))
else:
    logger.warning("ui_dist_not_found", path=ui_dist_path)


@app.get("/api/v1/info")
async def get_app_info():
    """Get application information"""
    return {
        "name": settings.app.app_name,
        "version": settings.app.app_version,
        "environment": settings.app.environment,
        "debug": settings.app.debug
    }


# Export manager for use in routes
__all__ = ["app", "manager"]
