"""
Agent management endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from app.agents.registry import registry
from app.agents.base import Task, AgentResult

router = APIRouter()


class TaskRequest(BaseModel):
    """Request model for executing a task"""
    action: str
    params: Dict[str, Any] = {}
    context: Dict[str, Any] = {}


class AgentInfo(BaseModel):
    """Agent information response"""
    name: str
    description: str
    version: str
    enabled: bool
    tools: List[str]
    capabilities: List[Dict[str, Any]]
    stats: Dict[str, Any]


@router.get("/")
async def list_agents() -> List[str]:
    """List all registered agent names"""
    return registry.list_agent_names()


@router.get("/info")
async def get_registry_info() -> Dict[str, Any]:
    """Get comprehensive registry information"""
    return registry.get_registry_info()


@router.get("/{agent_name}")
async def get_agent_info(agent_name: str) -> AgentInfo:
    """Get information about a specific agent"""
    agent = registry.get_agent(agent_name)

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    capabilities = [
        {
            "name": cap.name,
            "description": cap.description,
            "requires_tools": cap.requires_tools
        }
        for cap in agent.get_capabilities()
    ]

    return AgentInfo(
        name=agent.name,
        description=agent.description,
        version=agent.version,
        enabled=agent.enabled,
        tools=list(agent.tools.keys()),
        capabilities=capabilities,
        stats=agent.get_stats()
    )


@router.post("/{agent_name}/execute")
async def execute_agent_task(agent_name: str, task_request: TaskRequest) -> Dict[str, Any]:
    """Execute a task on a specific agent"""
    agent = registry.get_agent(agent_name)

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    if not agent.enabled:
        raise HTTPException(status_code=400, detail=f"Agent '{agent_name}' is disabled")

    # Create task
    task = Task(
        id=f"{agent_name}_{task_request.action}",
        action=task_request.action,
        params=task_request.params,
        context=task_request.context
    )

    # Execute task
    result = await agent.execute(task)

    return {
        "task_id": result.task_id,
        "success": result.success,
        "data": result.data,
        "error": result.error,
        "execution_time_ms": result.execution_time_ms,
        "tool_calls": result.tool_calls,
        "metadata": result.metadata
    }


@router.post("/{agent_name}/enable")
async def enable_agent(agent_name: str) -> Dict[str, str]:
    """Enable an agent"""
    success = registry.enable_agent(agent_name)

    if not success:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    return {"status": "enabled", "agent": agent_name}


@router.post("/{agent_name}/disable")
async def disable_agent(agent_name: str) -> Dict[str, str]:
    """Disable an agent"""
    success = registry.disable_agent(agent_name)

    if not success:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    return {"status": "disabled", "agent": agent_name}


@router.get("/{agent_name}/stats")
async def get_agent_stats(agent_name: str) -> Dict[str, Any]:
    """Get execution statistics for an agent"""
    agent = registry.get_agent(agent_name)

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    return agent.get_stats()


@router.post("/{agent_name}/stats/reset")
async def reset_agent_stats(agent_name: str) -> Dict[str, str]:
    """Reset execution statistics for an agent"""
    agent = registry.get_agent(agent_name)

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    agent.reset_stats()

    return {"status": "reset", "agent": agent_name}
