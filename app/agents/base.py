"""
Base Agent class for the DBRefactor AI Agent framework.

All agents in the system inherit from this base class which provides
core functionality for tool management, task execution, and memory.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog
from pydantic import BaseModel, Field


logger = structlog.get_logger(__name__)


class AgentCapability(BaseModel):
    """Represents a capability that an agent has"""
    name: str
    description: str
    requires_tools: List[str] = Field(default_factory=list)


class Task(BaseModel):
    """Represents a task that an agent can execute"""
    id: str
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentResult(BaseModel):
    """Result of an agent's task execution"""
    task_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float
    tool_calls: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentMemory:
    """Memory system for agents to store and retrieve information"""

    def __init__(self):
        self.short_term: List[Dict[str, Any]] = []
        self.long_term: Dict[str, Any] = {}
        self.context_cache: Dict[str, Any] = {}

    def remember(self, event: Dict[str, Any]):
        """Store an event in short-term memory"""
        self.short_term.append({
            **event,
            'timestamp': datetime.utcnow()
        })
        # Keep only last 100 events in short-term memory
        if len(self.short_term) > 100:
            self.short_term = self.short_term[-100:]

    def recall(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on query"""
        # Simple implementation - can be enhanced with semantic search
        results = []
        for event in reversed(self.short_term):
            if query.lower() in str(event).lower():
                results.append(event)
                if len(results) >= limit:
                    break
        return results

    def learn_pattern(self, pattern_name: str, pattern_data: Any):
        """Store a learned pattern in long-term memory"""
        self.long_term[pattern_name] = {
            'data': pattern_data,
            'learned_at': datetime.utcnow()
        }

    def get_pattern(self, pattern_name: str) -> Optional[Any]:
        """Retrieve a learned pattern"""
        pattern = self.long_term.get(pattern_name)
        return pattern['data'] if pattern else None

    def cache_context(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Cache context information with TTL"""
        self.context_cache[key] = {
            'value': value,
            'expires_at': datetime.utcnow().timestamp() + ttl_seconds
        }

    def get_cached_context(self, key: str) -> Optional[Any]:
        """Retrieve cached context if not expired"""
        cached = self.context_cache.get(key)
        if cached and datetime.utcnow().timestamp() < cached['expires_at']:
            return cached['value']
        return None


class Agent(ABC):
    """
    Base class for all agents in the DBRefactor AI framework.

    Agents are autonomous units that can execute tasks using tools.
    Each agent has a specific purpose and set of capabilities.
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0"
    ):
        """
        Initialize the agent.

        Args:
            name: Unique name for the agent
            description: Description of what the agent does
            version: Version of the agent implementation
        """
        self.name = name
        self.description = description
        self.version = version
        self.tools: Dict[str, Any] = {}
        self.memory = AgentMemory()
        self.logger = structlog.get_logger(name)
        self.enabled = True

        # Track execution statistics
        self.stats = {
            'tasks_executed': 0,
            'tasks_succeeded': 0,
            'tasks_failed': 0,
            'total_execution_time_ms': 0.0
        }

    @abstractmethod
    async def execute(self, task: Task) -> AgentResult:
        """
        Execute a task using available tools.

        This is the main entry point for agent execution.
        Subclasses must implement this method.

        Args:
            task: The task to execute

        Returns:
            AgentResult with execution details
        """
        pass

    def register_tool(self, tool: Any):
        """
        Register a tool for this agent to use.

        Args:
            tool: Tool instance to register
        """
        self.tools[tool.name] = tool
        self.logger.info(
            "tool_registered",
            agent=self.name,
            tool=tool.name
        )

    def unregister_tool(self, tool_name: str):
        """
        Unregister a tool from this agent.

        Args:
            tool_name: Name of the tool to unregister
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            self.logger.info(
                "tool_unregistered",
                agent=self.name,
                tool=tool_name
            )

    def has_tool(self, tool_name: str) -> bool:
        """Check if agent has a specific tool"""
        return tool_name in self.tools

    def get_capabilities(self) -> List[AgentCapability]:
        """
        Return list of capabilities based on available tools.

        Returns:
            List of AgentCapability objects
        """
        capabilities = []
        for tool_name, tool in self.tools.items():
            capabilities.append(
                AgentCapability(
                    name=tool_name,
                    description=getattr(tool, 'description', ''),
                    requires_tools=[tool_name]
                )
            )
        return capabilities

    def can_handle(self, task: Task) -> bool:
        """
        Determine if this agent can handle a given task.

        Args:
            task: Task to evaluate

        Returns:
            True if agent can handle the task
        """
        # Default implementation - subclasses can override
        return task.action in self.tools

    async def _execute_tool(
        self,
        tool_name: str,
        **kwargs
    ) -> Any:
        """
        Execute a tool with given parameters.

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters to pass to the tool

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool is not registered
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not registered with {self.name}")

        tool = self.tools[tool_name]
        self.logger.debug(
            "executing_tool",
            agent=self.name,
            tool=tool_name,
            params=kwargs
        )

        result = await tool.execute(**kwargs)
        return result

    def update_stats(self, result: AgentResult):
        """Update agent execution statistics"""
        self.stats['tasks_executed'] += 1
        if result.success:
            self.stats['tasks_succeeded'] += 1
        else:
            self.stats['tasks_failed'] += 1
        self.stats['total_execution_time_ms'] += result.execution_time_ms

    def get_stats(self) -> Dict[str, Any]:
        """Get agent execution statistics"""
        return {
            **self.stats,
            'success_rate': (
                self.stats['tasks_succeeded'] / self.stats['tasks_executed']
                if self.stats['tasks_executed'] > 0
                else 0.0
            )
        }

    def reset_stats(self):
        """Reset execution statistics"""
        self.stats = {
            'tasks_executed': 0,
            'tasks_succeeded': 0,
            'tasks_failed': 0,
            'total_execution_time_ms': 0.0
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"name='{self.name}' "
            f"tools={len(self.tools)} "
            f"enabled={self.enabled}>"
        )
