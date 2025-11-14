"""
Example usage of the DBRefactor AI Agent framework.

This script demonstrates how to:
1. Initialize the framework
2. Register agents
3. Discover a database schema
4. Execute a workflow
"""

import asyncio
from datetime import datetime

from app.agents.registry import AgentRegistry
from app.agents.db_discoverer import DBDiscovererAgent
from app.agents.base import Task
from app.workflow.engine import (
    WorkflowEngine,
    Workflow,
    WorkflowStep,
    WorkflowContext
)


async def example_agent_usage():
    """Example: Using an agent directly"""
    print("=" * 60)
    print("Example 1: Using DB Discoverer Agent Directly")
    print("=" * 60)

    # Initialize agent registry
    registry = AgentRegistry()

    # Register the DB Discoverer agent
    db_discoverer = DBDiscovererAgent()
    registry.register_agent(db_discoverer)

    print(f"Registered agents: {registry.list_agent_names()}")

    # Create a discovery task
    # Note: In a real scenario, you would provide an actual database connection
    task = Task(
        id="discover_example_schema",
        action="discover_schema",
        params={
            "connection": None,  # Replace with actual connection
            "schema_name": "HR",
            "include_system_objects": False
        }
    )

    print(f"\nExecuting task: {task.action}")
    print(f"Schema: {task.params['schema_name']}")

    # Execute the task
    # Note: This will fail without a real connection, but demonstrates the API
    try:
        result = await db_discoverer.execute(task)

        if result.success:
            print(f"\n✓ Task completed successfully")
            print(f"Execution time: {result.execution_time_ms:.2f}ms")
            print(f"Tools used: {', '.join(result.tool_calls)}")
            print(f"\nDiscovered data:")
            print(result.data)
        else:
            print(f"\n✗ Task failed: {result.error}")

    except Exception as e:
        print(f"\n✗ Exception: {str(e)}")
        print("(This is expected without a real database connection)")

    # Show agent statistics
    print(f"\nAgent statistics:")
    print(registry.get_agent_stats())


async def example_workflow_usage():
    """Example: Using the workflow engine"""
    print("\n" + "=" * 60)
    print("Example 2: Using Workflow Engine")
    print("=" * 60)

    # Initialize components
    registry = AgentRegistry()
    registry.register_agent(DBDiscovererAgent())

    engine = WorkflowEngine(registry)

    # Define a multi-step workflow
    workflow = Workflow(
        id="example_migration_workflow",
        name="Example Migration Workflow",
        description="Demonstrates a multi-step migration workflow",
        steps=[
            WorkflowStep(
                id="step1_discover",
                name="Discover Schema",
                description="Discover all database objects",
                agent_name="db_discoverer",
                task=Task(
                    id="task1",
                    action="discover_schema",
                    params={
                        "connection": None,  # Replace with actual connection
                        "schema_name": "HR",
                        "include_system_objects": False
                    }
                ),
                dependencies=[],  # No dependencies - first step
                max_retries=2
            ),
            WorkflowStep(
                id="step2_analyze",
                name="Analyze Dependencies",
                description="Build dependency graph",
                agent_name="db_discoverer",
                task=Task(
                    id="task2",
                    action="analyze_dependencies",
                    params={
                        "connection": None,  # Replace with actual connection
                        "schema_name": "HR",
                        "object_list": None
                    }
                ),
                dependencies=["step1_discover"],  # Depends on step 1
                max_retries=2
            ),
            WorkflowStep(
                id="step3_full_discovery",
                name="Full Discovery",
                description="Complete discovery with DDL extraction",
                agent_name="db_discoverer",
                task=Task(
                    id="task3",
                    action="full_discovery",
                    params={
                        "connection": None,  # Replace with actual connection
                        "schema_name": "HR",
                        "include_system_objects": False
                    }
                ),
                dependencies=["step2_analyze"],  # Depends on step 2
                max_retries=2
            )
        ],
        context=WorkflowContext(
            workflow_id="example_migration_workflow",
            data={
                "source_database": "Oracle",
                "target_database": "PostgreSQL",
                "migration_type": "schema_only"
            }
        )
    )

    print(f"\nWorkflow: {workflow.name}")
    print(f"Total steps: {len(workflow.steps)}")
    print(f"\nExecution plan:")
    for i, step in enumerate(workflow.steps, 1):
        deps = f" (depends on: {', '.join(step.dependencies)})" if step.dependencies else ""
        print(f"  {i}. {step.name}{deps}")

    # Register event handlers
    def on_step_started(wf, step):
        print(f"\n→ Starting step: {step.name}")

    def on_step_completed(wf, step):
        print(f"  ✓ Completed step: {step.name} ({step.result.execution_time_ms:.2f}ms)")

    def on_step_failed(wf, step):
        print(f"  ✗ Failed step: {step.name}")

    engine.on('step_started', on_step_started)
    engine.on('step_completed', on_step_completed)
    engine.on('step_failed', on_step_failed)

    print(f"\n{'='*60}")
    print("Executing workflow...")
    print('='*60)

    # Execute the workflow
    try:
        result = await engine.execute_workflow(workflow)

        print(f"\n{'='*60}")
        print("Workflow Execution Summary")
        print('='*60)
        print(f"Status: {result.status.value}")
        print(f"Steps completed: {result.steps_completed}")
        print(f"Steps failed: {result.steps_failed}")
        print(f"Total execution time: {result.execution_time_ms:.2f}ms")

        if result.error:
            print(f"Error: {result.error}")

    except Exception as e:
        print(f"\n✗ Workflow execution failed: {str(e)}")
        print("(This is expected without a real database connection)")


async def example_agent_registry():
    """Example: Agent registry features"""
    print("\n" + "=" * 60)
    print("Example 3: Agent Registry Features")
    print("=" * 60)

    registry = AgentRegistry()

    # Register multiple agents
    db_discoverer = DBDiscovererAgent()
    registry.register_agent(db_discoverer)

    print(f"\nRegistered agents: {len(registry)}")
    print(f"Agent names: {registry.list_agent_names()}")

    # Get registry information
    info = registry.get_registry_info()
    print(f"\nRegistry info:")
    print(f"  Total agents: {info['total_agents']}")
    print(f"  Enabled agents: {info['enabled_agents']}")
    print(f"  Total tools: {info['total_tools']}")
    print(f"  Capabilities: {info['capabilities']}")

    # Get specific agent
    agent = registry.get_agent("db_discoverer")
    if agent:
        print(f"\nAgent: {agent.name}")
        print(f"  Description: {agent.description}")
        print(f"  Version: {agent.version}")
        print(f"  Tools: {len(agent.tools)}")
        print(f"  Enabled: {agent.enabled}")

        capabilities = agent.get_capabilities()
        print(f"  Capabilities:")
        for cap in capabilities:
            print(f"    - {cap.name}: {cap.description}")

    # Find agent for a task
    task = Task(
        id="test_task",
        action="discover_schema",
        params={}
    )

    suitable_agent = registry.find_agent_for_task(task)
    if suitable_agent:
        print(f"\nAgent for task '{task.action}': {suitable_agent.name}")


async def main():
    """Run all examples"""
    print("\n" + "🤖" * 30)
    print("DBRefactor AI Agent Framework - Usage Examples")
    print("🤖" * 30 + "\n")

    # Example 1: Direct agent usage
    await example_agent_usage()

    # Example 2: Workflow usage
    await example_workflow_usage()

    # Example 3: Agent registry
    await example_agent_registry()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Set up your database connections in .env")
    print("2. Create custom agents for your specific needs")
    print("3. Define workflows for your migration tasks")
    print("4. Integrate with the REST API for production use")
    print("\nSee README.md and ARCHITECTURE.md for more information.")


if __name__ == "__main__":
    asyncio.run(main())
