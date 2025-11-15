"""
Database discovery endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.agents.registry import registry
from app.agents.base import Task

router = APIRouter()


class DiscoveryRequest(BaseModel):
    """Request model for database discovery"""
    schema_name: str
    include_system_objects: bool = False
    connection_params: Optional[Dict[str, Any]] = None


@router.post("/discover")
async def discover_schema(request: DiscoveryRequest) -> Dict[str, Any]:
    """Discover all objects in a database schema"""
    agent = registry.get_agent("db_discoverer")

    if not agent:
        raise HTTPException(status_code=500, detail="DB Discoverer agent not available")

    task = Task(
        id=f"discover_{request.schema_name}",
        action="discover_schema",
        params={
            "schema_name": request.schema_name,
            "include_system_objects": request.include_system_objects,
            "connection": request.connection_params
        }
    )

    result = await agent.execute(task)

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return result.data


@router.post("/analyze-dependencies")
async def analyze_dependencies(request: DiscoveryRequest) -> Dict[str, Any]:
    """Analyze dependencies between database objects"""
    agent = registry.get_agent("db_discoverer")

    if not agent:
        raise HTTPException(status_code=500, detail="DB Discoverer agent not available")

    task = Task(
        id=f"analyze_deps_{request.schema_name}",
        action="analyze_dependencies",
        params={
            "schema_name": request.schema_name,
            "connection": request.connection_params,
            "object_list": None
        }
    )

    result = await agent.execute(task)

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return result.data


@router.post("/full-discovery")
async def full_discovery(request: DiscoveryRequest) -> Dict[str, Any]:
    """Perform complete discovery with metadata, dependencies, and DDL"""
    agent = registry.get_agent("db_discoverer")

    if not agent:
        raise HTTPException(status_code=500, detail="DB Discoverer agent not available")

    task = Task(
        id=f"full_discovery_{request.schema_name}",
        action="full_discovery",
        params={
            "schema_name": request.schema_name,
            "include_system_objects": request.include_system_objects,
            "connection": request.connection_params
        }
    )

    result = await agent.execute(task)

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return result.data
