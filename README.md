# DBRefactor AI Agent

An intelligent, agentic framework for database migration from legacy to modern systems. This framework provides a flexible, modular approach to discovering database objects, analyzing dependencies, and orchestrating complex migration workflows.

## Overview

DBRefactor AI Agent is built on an **agentic architecture** where specialized agents work together to handle different aspects of database migration:

- **DB Discoverer Agent**: Discovers database objects and builds dependency graphs
- **Schema Analyzer Agent**: Analyzes schema compatibility and migration complexity
- **Code Converter Agent**: Converts database code using AI-powered transformation
- **Dependency Resolver Agent**: Determines optimal migration order
- **Validator Agent**: Validates converted code and schema
- **Executor Agent**: Executes migration steps on target database
- **Logger Agent**: Tracks and reports migration progress

## Key Features

### Agentic Framework
- **Autonomous Agents**: Each agent is self-contained with its own tools and capabilities
- **Tool-Based Actions**: Agents use composable tools to perform operations
- **Modular Design**: Add, remove, or replace agents without affecting the system
- **Agent Registry**: Centralized management and discovery of agents

### Database Discovery
- Enumerate all database objects (tables, views, procedures, functions, triggers)
- Extract comprehensive metadata
- Build complete dependency graphs
- Identify circular dependencies
- Determine optimal migration order

### Workflow Orchestration
- Define complex multi-step workflows
- Automatic dependency resolution
- Parallel execution where possible
- Error handling and retry logic
- Pause/resume capability

### AI-Powered Conversion
- Context-aware SQL dialect transformation
- Procedural code conversion (PL/SQL → PL/pgSQL)
- Query optimization suggestions
- Learning from historical migrations

## Architecture

The framework is organized into distinct layers:

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │
├─────────────────────────────────────┤
│   Workflow Orchestration Layer      │
├─────────────────────────────────────┤
│          Agent Layer                │
│  (DB Discoverer, Converter, etc.)   │
├─────────────────────────────────────┤
│          Tool Layer                 │
│  (Database, Analysis, Transform)    │
├─────────────────────────────────────┤
│        Resource Layer               │
│  (Source, Target, App Databases)    │
└─────────────────────────────────────┘
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture documentation.

## Project Structure

```
DBRefactor_AI_Agent/
├── app/
│   ├── agents/              # Agent implementations
│   │   ├── base.py          # Base Agent class
│   │   ├── registry.py      # Agent Registry
│   │   └── db_discoverer.py # DB Discoverer Agent
│   ├── tools/               # Tool implementations
│   │   ├── base.py          # Base Tool class
│   │   └── database/        # Database tools
│   ├── workflow/            # Workflow engine
│   │   └── engine.py        # Workflow Engine
│   ├── models/              # Data models
│   ├── api/                 # API endpoints
│   ├── services/            # Business logic
│   └── config.py            # Configuration
├── tests/                   # Test suite
├── docs/                    # Documentation
├── ARCHITECTURE.md          # Architecture details
└── README.md               # This file
```

## Installation

### Prerequisites

- Python 3.10+
- Database drivers for your source and target databases
- (Optional) Redis for caching and task queue

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd DBRefactor_AI_Agent
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and API keys
   ```

5. **Start the FastAPI backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Start the Next.js UI** (in a separate terminal):
   ```bash
   cd ui
   npm install
   npm run dev
   ```

7. **Access the application**:
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs
   - **Web UI**: http://localhost:3000

## Quick Start

### 1. Initialize the Framework

```python
from app.agents.registry import AgentRegistry
from app.agents.db_discoverer import DBDiscovererAgent
from app.workflow.engine import WorkflowEngine

# Initialize registry and register agents
registry = AgentRegistry()
registry.register_agent(DBDiscovererAgent())

# Initialize workflow engine
engine = WorkflowEngine(registry)
```

### 2. Discover a Database Schema

```python
from app.agents.base import Task

# Create a discovery task
task = Task(
    id="discover_hr_schema",
    action="full_discovery",
    params={
        "connection": db_connection,
        "schema_name": "HR",
        "include_system_objects": False
    }
)

# Get the DB Discoverer agent
agent = registry.get_agent("db_discoverer")

# Execute discovery
result = await agent.execute(task)

if result.success:
    discovery_data = result.data
    print(f"Discovered {discovery_data['discovery_summary']['total_objects']} objects")
    print(f"Migration order: {discovery_data['dependency_analysis']['creation_order']}")
```

### 3. Create a Migration Workflow

```python
from app.workflow.engine import Workflow, WorkflowStep, WorkflowContext

# Define workflow
workflow = Workflow(
    id="migrate_hr_schema",
    name="HR Schema Migration",
    description="Migrate HR schema from Oracle to PostgreSQL",
    steps=[
        WorkflowStep(
            id="step1",
            name="Discover Schema",
            description="Discover all objects and dependencies",
            agent_name="db_discoverer",
            task=Task(
                id="task1",
                action="full_discovery",
                params={"schema_name": "HR", "connection": source_conn}
            )
        ),
        WorkflowStep(
            id="step2",
            name="Convert Code",
            description="Convert database code",
            agent_name="code_converter",
            task=Task(
                id="task2",
                action="convert_schema",
                params={"schema_name": "HR"}
            ),
            dependencies=["step1"]  # Depends on discovery
        ),
        # Add more steps...
    ],
    context=WorkflowContext(workflow_id="migrate_hr_schema")
)

# Execute workflow
result = await engine.execute_workflow(workflow)
```

## Creating Custom Agents

You can extend the framework by creating custom agents:

```python
from app.agents.base import Agent, Task, AgentResult

class MyCustomAgent(Agent):
    def __init__(self):
        super().__init__(
            name="my_custom_agent",
            description="Does something custom",
            version="1.0.0"
        )

        # Register tools this agent will use
        self.register_tool(MyCustomTool())

    async def execute(self, task: Task) -> AgentResult:
        # Implement custom logic
        result = await self._execute_tool('my_custom_tool', **task.params)

        return AgentResult(
            task_id=task.id,
            success=True,
            data=result,
            execution_time_ms=0.0,
            tool_calls=['my_custom_tool']
        )

# Register with the registry
registry.register_agent(MyCustomAgent())
```

## Creating Custom Tools

Tools are reusable components that agents use:

```python
from app.tools.base import Tool, ToolCategory, ToolParameter, ToolResult

class MyCustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_custom_tool",
            description="Performs a custom operation",
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(
                    name="input_data",
                    description="Input data to process",
                    type="str",
                    required=True
                )
            ]
        )

    async def execute(self, **kwargs) -> ToolResult:
        input_data = kwargs.get('input_data')

        # Implement tool logic
        output = f"Processed: {input_data}"

        return ToolResult(
            success=True,
            data={'output': output},
            execution_time_ms=0.0
        )
```

## Configuration

The framework uses environment variables for configuration. Create a `.env` file:

```env
# Source Database (Oracle)
SOURCE_DB_HOST=localhost
SOURCE_DB_PORT=1521
SOURCE_DB_NAME=ORCL
SOURCE_DB_USER=hr
SOURCE_DB_PASSWORD=password

# Target Database (PostgreSQL)
TARGET_DB_HOST=localhost
TARGET_DB_PORT=5432
TARGET_DB_NAME=hr_migrated
TARGET_DB_USER=postgres
TARGET_DB_PASSWORD=password

# AI Configuration
GEMINI_API_KEY=your-gemini-api-key

# Application
DEBUG=False
LOG_LEVEL=INFO
```

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py
```

## API Documentation

The framework includes a FastAPI-based REST API. Once running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

[Add your license here]

## Roadmap

- [ ] Complete implementation of all agents
- [ ] Add support for more database systems (MySQL, SQL Server, etc.)
- [ ] Implement data migration capabilities
- [ ] Add web-based dashboard
- [ ] Machine learning for conversion pattern optimization
- [ ] Plugin system for custom extensions
- [ ] Multi-tenant support

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

Built with:
- FastAPI
- LangGraph
- SQLAlchemy
- Google Gemini
- And many other open-source projects
