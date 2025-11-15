"""
Agent Registry for managing all agents in the system.

The registry provides centralized agent management, discovery,
and lifecycle control.
"""

from typing import Dict, List, Optional, Set
from collections import defaultdict
import structlog

from app.agents.base import Agent, Task, AgentCapability


logger = structlog.get_logger(__name__)


class AgentRegistry:
    """
    Central registry for managing all agents in the system.

    The registry allows:
    - Registration and unregistration of agents
    - Discovery of agents by name or capability
    - Agent lifecycle management
    - Load balancing across multiple instances of the same agent type
    """

    _instance = None

    def __new__(cls):
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the registry"""
        if self._initialized:
            return

        self.agents: Dict[str, Agent] = {}
        self.agent_by_capability: Dict[str, Set[str]] = defaultdict(set)
        self.logger = structlog.get_logger("AgentRegistry")
        self._initialized = True

    def register_agent(self, agent: Agent) -> bool:
        """
        Register an agent with the registry.

        Args:
            agent: Agent instance to register

        Returns:
            True if registration successful, False if agent already exists

        Raises:
            ValueError: If agent name is invalid or duplicate
        """
        if not agent.name:
            raise ValueError("Agent name cannot be empty")

        if agent.name in self.agents:
            self.logger.warning(
                "agent_already_registered",
                agent_name=agent.name
            )
            return False

        self.agents[agent.name] = agent

        # Index by capabilities
        for capability in agent.get_capabilities():
            self.agent_by_capability[capability.name].add(agent.name)

        self.logger.info(
            "agent_registered",
            agent_name=agent.name,
            capabilities=len(agent.get_capabilities()),
            tools=len(agent.tools)
        )

        return True

    def unregister_agent(self, agent_name: str) -> bool:
        """
        Unregister an agent from the registry.

        Args:
            agent_name: Name of the agent to unregister

        Returns:
            True if unregistration successful, False if agent not found
        """
        if agent_name not in self.agents:
            self.logger.warning(
                "agent_not_found",
                agent_name=agent_name
            )
            return False

        agent = self.agents[agent_name]

        # Remove from capability index
        for capability in agent.get_capabilities():
            self.agent_by_capability[capability.name].discard(agent_name)

        del self.agents[agent_name]

        self.logger.info(
            "agent_unregistered",
            agent_name=agent_name
        )

        return True

    def get_agent(self, name: str) -> Optional[Agent]:
        """
        Get an agent by name.

        Args:
            name: Name of the agent

        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(name)

    def list_agents(self) -> List[Agent]:
        """
        List all registered agents.

        Returns:
            List of all agent instances
        """
        return list(self.agents.values())

    def list_agent_names(self) -> List[str]:
        """
        List all registered agent names.

        Returns:
            List of agent names
        """
        return list(self.agents.keys())

    def discover_agents(
        self,
        capability: str,
        enabled_only: bool = True
    ) -> List[Agent]:
        """
        Discover agents that have a specific capability.

        Args:
            capability: Capability name to search for
            enabled_only: Only return enabled agents

        Returns:
            List of agents with the specified capability
        """
        agent_names = self.agent_by_capability.get(capability, set())
        agents = [self.agents[name] for name in agent_names if name in self.agents]

        if enabled_only:
            agents = [agent for agent in agents if agent.enabled]

        return agents

    def find_agent_for_task(self, task: Task) -> Optional[Agent]:
        """
        Find the best agent to handle a specific task.

        Args:
            task: Task to find an agent for

        Returns:
            Best matching agent or None if no suitable agent found
        """
        # First, try to find agents that can handle the task
        capable_agents = [
            agent for agent in self.agents.values()
            if agent.enabled and agent.can_handle(task)
        ]

        if not capable_agents:
            self.logger.warning(
                "no_capable_agent_found",
                task_action=task.action
            )
            return None

        # Select agent with best success rate
        if len(capable_agents) == 1:
            return capable_agents[0]

        # Return agent with highest success rate
        best_agent = max(
            capable_agents,
            key=lambda a: a.get_stats()['success_rate']
        )

        return best_agent

    def get_agent_stats(self) -> Dict[str, Dict]:
        """
        Get statistics for all agents.

        Returns:
            Dictionary mapping agent names to their stats
        """
        return {
            name: agent.get_stats()
            for name, agent in self.agents.items()
        }

    def enable_agent(self, agent_name: str) -> bool:
        """
        Enable an agent.

        Args:
            agent_name: Name of the agent to enable

        Returns:
            True if successful, False if agent not found
        """
        agent = self.get_agent(agent_name)
        if agent:
            agent.enabled = True
            self.logger.info("agent_enabled", agent_name=agent_name)
            return True
        return False

    def disable_agent(self, agent_name: str) -> bool:
        """
        Disable an agent.

        Args:
            agent_name: Name of the agent to disable

        Returns:
            True if successful, False if agent not found
        """
        agent = self.get_agent(agent_name)
        if agent:
            agent.enabled = False
            self.logger.info("agent_disabled", agent_name=agent_name)
            return True
        return False

    def get_registry_info(self) -> Dict:
        """
        Get information about the registry.

        Returns:
            Dictionary with registry statistics
        """
        enabled_agents = sum(1 for agent in self.agents.values() if agent.enabled)
        total_tools = sum(len(agent.tools) for agent in self.agents.values())

        return {
            'total_agents': len(self.agents),
            'enabled_agents': enabled_agents,
            'disabled_agents': len(self.agents) - enabled_agents,
            'total_tools': total_tools,
            'capabilities': len(self.agent_by_capability),
            'agents': {
                name: {
                    'enabled': agent.enabled,
                    'tools': len(agent.tools),
                    'stats': agent.get_stats()
                }
                for name, agent in self.agents.items()
            }
        }

    def reset_all_stats(self):
        """Reset statistics for all agents"""
        for agent in self.agents.values():
            agent.reset_stats()
        self.logger.info("all_agent_stats_reset")

    def __len__(self) -> int:
        """Return number of registered agents"""
        return len(self.agents)

    def __contains__(self, agent_name: str) -> bool:
        """Check if an agent is registered"""
        return agent_name in self.agents

    def __repr__(self) -> str:
        return (
            f"<AgentRegistry "
            f"agents={len(self.agents)} "
            f"enabled={sum(1 for a in self.agents.values() if a.enabled)}>"
        )


# Global registry instance
registry = AgentRegistry()
