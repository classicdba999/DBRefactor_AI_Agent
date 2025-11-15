"""
Workflow management endpoints.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.workflow.engine import (
    WorkflowEngine,
    Workflow,
    WorkflowStep,
    WorkflowContext,
    WorkflowStatus
)
from app.agents.registry import registry
from app.agents.base import Task

router = APIRouter()

# Global workflow engine
workflow_engine = WorkflowEngine(registry)


class WorkflowStepRequest(BaseModel):
    """Request model for a workflow step"""
    name: str
    description: str
    agent_name: str
    action: str
    params: Dict[str, Any] = {}
    dependencies: List[str] = []
    max_retries: int = 3


class WorkflowRequest(BaseModel):
    """Request model for creating a workflow"""
    name: str
    description: str
    steps: List[WorkflowStepRequest]
    context_data: Dict[str, Any] = {}


@router.post("/create")
async def create_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Create a new workflow"""
    workflow_id = str(uuid.uuid4())

    # Build workflow steps
    steps = []
    for idx, step_req in enumerate(request.steps):
        step = WorkflowStep(
            id=f"step_{idx + 1}",
            name=step_req.name,
            description=step_req.description,
            agent_name=step_req.agent_name,
            task=Task(
                id=f"task_{idx + 1}",
                action=step_req.action,
                params=step_req.params
            ),
            dependencies=step_req.dependencies,
            max_retries=step_req.max_retries
        )
        steps.append(step)

    # Create workflow
    workflow = Workflow(
        id=workflow_id,
        name=request.name,
        description=request.description,
        steps=steps,
        context=WorkflowContext(
            workflow_id=workflow_id,
            data=request.context_data
        )
    )

    # Register workflow
    workflow_engine.register_workflow(workflow)

    return {
        "workflow_id": workflow_id,
        "name": workflow.name,
        "total_steps": len(workflow.steps),
        "status": workflow.status.value
    }


@router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Execute a workflow"""
    workflow = workflow_engine.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")

    if workflow.status == WorkflowStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Workflow is already running")

    # Execute workflow in background
    background_tasks.add_task(workflow_engine.execute_workflow, workflow)

    return {
        "workflow_id": workflow_id,
        "status": "started",
        "message": "Workflow execution started in background"
    }


@router.get("/{workflow_id}/status")
async def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """Get workflow execution status"""
    workflow = workflow_engine.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")

    # Get step statuses
    step_statuses = []
    for step in workflow.steps:
        step_status = {
            "id": step.id,
            "name": step.name,
            "status": step.status.value,
            "agent": step.agent_name,
            "started_at": step.started_at.isoformat() if step.started_at else None,
            "completed_at": step.completed_at.isoformat() if step.completed_at else None,
            "retry_count": step.retry_count
        }
        if step.result:
            step_status["success"] = step.result.success
            step_status["execution_time_ms"] = step.result.execution_time_ms
            step_status["error"] = step.result.error

        step_statuses.append(step_status)

    return {
        "workflow_id": workflow.id,
        "name": workflow.name,
        "status": workflow.status.value,
        "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
        "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
        "error": workflow.error,
        "steps": step_statuses
    }


@router.get("/")
async def list_workflows() -> List[Dict[str, Any]]:
    """List all workflows"""
    workflows = workflow_engine.list_workflows()

    return [
        {
            "workflow_id": wf.id,
            "name": wf.name,
            "description": wf.description,
            "status": wf.status.value,
            "total_steps": len(wf.steps),
            "created_at": wf.created_at.isoformat()
        }
        for wf in workflows
    ]


@router.get("/stats")
async def get_workflow_stats() -> Dict[str, Any]:
    """Get workflow engine statistics"""
    return workflow_engine.get_engine_stats()
