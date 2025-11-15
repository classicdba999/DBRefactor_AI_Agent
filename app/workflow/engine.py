"""
Workflow Engine for orchestrating agent-based migration workflows.

The engine manages the execution of complex workflows that involve
multiple agents working together to complete migration tasks.
"""

from typing import Any, Dict, List, Optional, Callable
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import structlog
import asyncio

from app.agents.registry import AgentRegistry
from app.agents.base import Task, AgentResult


logger = structlog.get_logger(__name__)


class WorkflowStatus(str, Enum):
    """Status of a workflow execution"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepStatus(str, Enum):
    """Status of a workflow step"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep(BaseModel):
    """Represents a single step in a workflow"""
    id: str
    name: str
    description: str
    agent_name: str
    task: Task
    dependencies: List[str] = Field(default_factory=list)
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    result: Optional[AgentResult] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3


class WorkflowContext(BaseModel):
    """Context shared across workflow steps"""
    workflow_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Workflow(BaseModel):
    """Defines a workflow of agent tasks"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    context: WorkflowContext
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class WorkflowResult(BaseModel):
    """Result of a workflow execution"""
    workflow_id: str
    status: WorkflowStatus
    steps_completed: int
    steps_failed: int
    steps_skipped: int
    execution_time_ms: float
    results: Dict[str, AgentResult] = Field(default_factory=dict)
    error: Optional[str] = None
    context: WorkflowContext


class WorkflowEngine:
    """
    Orchestrates agents to execute migration workflows.

    The engine:
    - Manages workflow lifecycle
    - Coordinates agent execution
    - Handles dependencies between steps
    - Provides error handling and retries
    - Supports pause/resume functionality
    """

    def __init__(self, agent_registry: Optional[AgentRegistry] = None):
        """
        Initialize the workflow engine.

        Args:
            agent_registry: Registry of available agents
        """
        self.agent_registry = agent_registry or AgentRegistry()
        self.workflows: Dict[str, Workflow] = {}
        self.logger = structlog.get_logger("WorkflowEngine")
        self.event_handlers: Dict[str, List[Callable]] = {
            'workflow_started': [],
            'workflow_completed': [],
            'workflow_failed': [],
            'step_started': [],
            'step_completed': [],
            'step_failed': []
        }

    async def execute_workflow(
        self,
        workflow: Workflow
    ) -> WorkflowResult:
        """
        Execute a workflow.

        Args:
            workflow: Workflow to execute

        Returns:
            WorkflowResult with execution details
        """
        start_time = datetime.utcnow()
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = start_time

        self.workflows[workflow.id] = workflow
        self.logger.info(
            "workflow_started",
            workflow_id=workflow.id,
            workflow_name=workflow.name,
            total_steps=len(workflow.steps)
        )

        await self._emit_event('workflow_started', workflow)

        try:
            # Execute steps in dependency order
            await self._execute_steps(workflow)

            # Check if all steps completed successfully
            failed_steps = [
                step for step in workflow.steps
                if step.status == WorkflowStepStatus.FAILED
            ]

            if failed_steps:
                workflow.status = WorkflowStatus.FAILED
                workflow.error = f"{len(failed_steps)} steps failed"
                await self._emit_event('workflow_failed', workflow)
            else:
                workflow.status = WorkflowStatus.COMPLETED
                await self._emit_event('workflow_completed', workflow)

            workflow.completed_at = datetime.utcnow()

            # Build result
            result = self._build_workflow_result(workflow, start_time)

            self.logger.info(
                "workflow_completed",
                workflow_id=workflow.id,
                status=workflow.status.value,
                execution_time_ms=result.execution_time_ms
            )

            return result

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(e)
            workflow.completed_at = datetime.utcnow()

            self.logger.error(
                "workflow_execution_failed",
                workflow_id=workflow.id,
                error=str(e),
                exc_info=True
            )

            await self._emit_event('workflow_failed', workflow)

            return self._build_workflow_result(workflow, start_time)

    async def _execute_steps(self, workflow: Workflow):
        """Execute workflow steps in dependency order"""
        completed_steps = set()
        pending_steps = {step.id: step for step in workflow.steps}

        while pending_steps:
            # Find steps ready to execute (dependencies satisfied)
            ready_steps = [
                step for step in pending_steps.values()
                if all(dep in completed_steps for dep in step.dependencies)
            ]

            if not ready_steps:
                # No steps ready - check for circular dependencies
                remaining = list(pending_steps.keys())
                raise RuntimeError(
                    f"Circular dependency or missing dependencies detected. "
                    f"Remaining steps: {remaining}"
                )

            # Execute ready steps in parallel
            tasks = [
                self._execute_step(workflow, step)
                for step in ready_steps
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for step, result in zip(ready_steps, results):
                if isinstance(result, Exception):
                    step.status = WorkflowStepStatus.FAILED
                    self.logger.error(
                        "step_execution_exception",
                        workflow_id=workflow.id,
                        step_id=step.id,
                        error=str(result)
                    )
                else:
                    completed_steps.add(step.id)

                # Remove from pending
                pending_steps.pop(step.id, None)

    async def _execute_step(
        self,
        workflow: Workflow,
        step: WorkflowStep
    ) -> AgentResult:
        """Execute a single workflow step"""
        step.status = WorkflowStepStatus.RUNNING
        step.started_at = datetime.utcnow()

        self.logger.info(
            "step_started",
            workflow_id=workflow.id,
            step_id=step.id,
            step_name=step.name,
            agent=step.agent_name
        )

        await self._emit_event('step_started', workflow, step)

        # Get the agent
        agent = self.agent_registry.get_agent(step.agent_name)
        if not agent:
            raise ValueError(f"Agent '{step.agent_name}' not found")

        # Execute with retry logic
        last_error = None
        for attempt in range(step.max_retries + 1):
            try:
                # Add workflow context to task
                step.task.context.update({
                    'workflow_id': workflow.id,
                    'workflow_context': workflow.context.data
                })

                # Execute the agent task
                result = await agent.execute(step.task)

                if result.success:
                    step.status = WorkflowStepStatus.COMPLETED
                    step.result = result
                    step.completed_at = datetime.utcnow()

                    # Update workflow context with result data
                    if result.data:
                        workflow.context.data[f"step_{step.id}_result"] = result.data

                    self.logger.info(
                        "step_completed",
                        workflow_id=workflow.id,
                        step_id=step.id,
                        execution_time_ms=result.execution_time_ms
                    )

                    await self._emit_event('step_completed', workflow, step)
                    return result
                else:
                    last_error = result.error
                    if attempt < step.max_retries:
                        step.retry_count += 1
                        self.logger.warning(
                            "step_failed_retrying",
                            workflow_id=workflow.id,
                            step_id=step.id,
                            attempt=attempt + 1,
                            max_retries=step.max_retries,
                            error=result.error
                        )
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise RuntimeError(result.error)

            except Exception as e:
                last_error = str(e)
                if attempt < step.max_retries:
                    step.retry_count += 1
                    self.logger.warning(
                        "step_exception_retrying",
                        workflow_id=workflow.id,
                        step_id=step.id,
                        attempt=attempt + 1,
                        max_retries=step.max_retries,
                        error=str(e)
                    )
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise

        # All retries exhausted
        step.status = WorkflowStepStatus.FAILED
        step.completed_at = datetime.utcnow()

        self.logger.error(
            "step_failed",
            workflow_id=workflow.id,
            step_id=step.id,
            error=last_error
        )

        await self._emit_event('step_failed', workflow, step)

        raise RuntimeError(f"Step failed after {step.max_retries} retries: {last_error}")

    def _build_workflow_result(
        self,
        workflow: Workflow,
        start_time: datetime
    ) -> WorkflowResult:
        """Build workflow result from workflow state"""
        execution_time = (
            (workflow.completed_at or datetime.utcnow()) - start_time
        ).total_seconds() * 1000

        steps_completed = sum(
            1 for step in workflow.steps
            if step.status == WorkflowStepStatus.COMPLETED
        )
        steps_failed = sum(
            1 for step in workflow.steps
            if step.status == WorkflowStepStatus.FAILED
        )
        steps_skipped = sum(
            1 for step in workflow.steps
            if step.status == WorkflowStepStatus.SKIPPED
        )

        results = {
            step.id: step.result
            for step in workflow.steps
            if step.result is not None
        }

        return WorkflowResult(
            workflow_id=workflow.id,
            status=workflow.status,
            steps_completed=steps_completed,
            steps_failed=steps_failed,
            steps_skipped=steps_skipped,
            execution_time_ms=execution_time,
            results=results,
            error=workflow.error,
            context=workflow.context
        )

    def register_workflow(self, workflow: Workflow):
        """Register a workflow definition for later execution"""
        self.workflows[workflow.id] = workflow
        self.logger.info(
            "workflow_registered",
            workflow_id=workflow.id,
            workflow_name=workflow.name
        )

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID"""
        return self.workflows.get(workflow_id)

    def list_workflows(self) -> List[Workflow]:
        """List all registered workflows"""
        return list(self.workflows.values())

    def on(self, event: str, handler: Callable):
        """Register an event handler"""
        if event in self.event_handlers:
            self.event_handlers[event].append(handler)
        else:
            raise ValueError(f"Unknown event: {event}")

    async def _emit_event(self, event: str, *args):
        """Emit an event to all registered handlers"""
        for handler in self.event_handlers.get(event, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(*args)
                else:
                    handler(*args)
            except Exception as e:
                self.logger.error(
                    "event_handler_failed",
                    event=event,
                    error=str(e),
                    exc_info=True
                )

    def get_engine_stats(self) -> Dict[str, Any]:
        """Get workflow engine statistics"""
        return {
            'total_workflows': len(self.workflows),
            'running_workflows': sum(
                1 for w in self.workflows.values()
                if w.status == WorkflowStatus.RUNNING
            ),
            'completed_workflows': sum(
                1 for w in self.workflows.values()
                if w.status == WorkflowStatus.COMPLETED
            ),
            'failed_workflows': sum(
                1 for w in self.workflows.values()
                if w.status == WorkflowStatus.FAILED
            )
        }
