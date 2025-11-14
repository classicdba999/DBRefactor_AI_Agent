# DBRefactor AI Agent - Agentic Framework Architecture

## Overview

This document describes the architecture of a flexible, modular agentic framework designed to facilitate database object discovery, dependency analysis, and automated migration from legacy to modern database systems.

## Core Philosophy

The framework is built on the following principles:

1. **Agent Autonomy**: Each agent is a self-contained unit with its own tools and capabilities
2. **Modularity**: Components can be added, removed, or replaced without affecting the entire system
3. **Tool-Based Actions**: Agents use tools to interact with databases, analyze code, and perform migrations
4. **Dependency Awareness**: The framework understands database object dependencies and respects them
5. **Workflow-Driven**: Complex migrations are broken down into orchestrated workflows

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                     │
│  - REST endpoints for migration management                  │
│  - WebSocket for real-time status updates                  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Workflow Orchestration Layer               │
│  - Migration workflow engine                                │
│  - Task scheduling and coordination                         │
│  - State management                                         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Agent Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ DB Discoverer│  │Schema Analyzer│ │Code Converter│     │
│  │    Agent     │  │    Agent      │  │    Agent     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Validator   │  │   Executor    │  │   Logger     │     │
│  │    Agent     │  │    Agent      │  │    Agent     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                       Tool Layer                            │
│  - Database connection tools                                │
│  - Query execution tools                                    │
│  - DDL extraction tools                                     │
│  - Dependency analysis tools                                │
│  - Code transformation tools                                │
│  - AI/LLM integration tools                                 │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Resource Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Source    │  │   Target    │  │ Application │        │
│  │  Database   │  │  Database   │  │  Database   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Agent Framework

#### Base Agent Class

All agents inherit from a base `Agent` class that provides:

```python
class Agent:
    """Base class for all agents in the framework"""

    def __init__(self, name: str, description: str, tools: List[Tool]):
        self.name = name
        self.description = description
        self.tools = tools
        self.memory = AgentMemory()
        self.logger = get_logger(name)

    async def execute(self, task: Task) -> AgentResult:
        """Execute a task using available tools"""
        pass

    def register_tool(self, tool: Tool):
        """Register a new tool for this agent"""
        pass

    def get_capabilities(self) -> List[str]:
        """Return list of capabilities based on available tools"""
        pass
```

#### Agent Registry

Central registry for all available agents:

```python
class AgentRegistry:
    """Registry for managing all agents in the system"""

    def register_agent(self, agent: Agent)
    def get_agent(self, name: str) -> Agent
    def list_agents(self) -> List[Agent]
    def discover_agents(self, capability: str) -> List[Agent]
```

### 2. Tool System

#### Tool Interface

```python
class Tool:
    """Base class for all tools that agents can use"""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        category: ToolCategory
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.category = category

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass

    def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters before execution"""
        pass
```

#### Tool Categories

- **Database Tools**: Connect, query, extract metadata
- **Analysis Tools**: Analyze dependencies, complexity, performance
- **Transformation Tools**: Convert SQL, refactor code, optimize queries
- **Validation Tools**: Verify syntax, check constraints, test compatibility
- **AI Tools**: LLM-powered code generation, translation, optimization

### 3. Specialized Agents

#### DB Discoverer Agent

**Purpose**: Discover database objects and their dependencies

**Tools**:
- `get_database_metadata`: Extract schema information
- `list_tables`: List all tables in a schema
- `list_views`: List all views
- `list_procedures`: List stored procedures
- `list_functions`: List functions
- `list_triggers`: List triggers
- `analyze_dependencies`: Build dependency graph
- `get_ddl`: Extract DDL for objects

**Capabilities**:
- Enumerate all database objects in a schema
- Build complete dependency graph (tables → views → procedures → triggers)
- Identify circular dependencies
- Categorize objects by type and complexity
- Export metadata for analysis

**Example Usage**:
```python
discoverer = AgentRegistry.get_agent("db_discoverer")
result = await discoverer.execute(
    task=Task(
        action="discover_schema",
        params={"schema_name": "HR", "include_dependencies": True}
    )
)
# Returns: DatabaseSchema with all objects and dependency graph
```

#### Schema Analyzer Agent

**Purpose**: Analyze schema compatibility and migration complexity

**Tools**:
- `compare_schemas`: Compare source and target schemas
- `identify_incompatibilities`: Find incompatible features
- `estimate_complexity`: Calculate migration complexity score
- `suggest_alternatives`: Recommend target alternatives for source features
- `analyze_data_types`: Map data types between systems

#### Code Converter Agent

**Purpose**: Convert database code from legacy to modern syntax

**Tools**:
- `convert_sql`: Transform SQL dialect
- `convert_plsql_to_plpgsql`: Convert procedural code
- `optimize_query`: Apply query optimization
- `refactor_code`: Improve code structure
- `ai_transform`: Use LLM for complex transformations

**Features**:
- Context-aware conversion using historical migrations
- AI-powered transformation for complex logic
- Preservation of business logic integrity
- Optimization suggestions during conversion

#### Dependency Resolver Agent

**Purpose**: Determine optimal migration order

**Tools**:
- `build_dependency_graph`: Create directed acyclic graph (DAG)
- `topological_sort`: Determine creation order
- `detect_circular_dependencies`: Identify problematic dependencies
- `suggest_dependency_breaks`: Recommend ways to break circular deps

**Output**: Ordered list of objects to migrate that respects all dependencies

#### Validator Agent

**Purpose**: Validate converted code and schema

**Tools**:
- `validate_syntax`: Check SQL syntax
- `validate_semantics`: Verify logical correctness
- `dry_run_execution`: Test without committing
- `compare_results`: Compare source vs target output
- `verify_constraints`: Ensure constraints are preserved

#### Executor Agent

**Purpose**: Execute migration steps on target database

**Tools**:
- `execute_ddl`: Run DDL statements
- `execute_dml`: Run DML statements
- `manage_transactions`: Handle transaction boundaries
- `rollback_migration`: Revert changes if needed
- `verify_execution`: Confirm successful execution

#### Logger Agent

**Purpose**: Track and report migration progress

**Tools**:
- `log_event`: Record migration events
- `generate_report`: Create migration summary
- `track_metrics`: Collect performance metrics
- `alert_on_failure`: Send notifications for failures

### 4. Workflow Engine

The workflow engine orchestrates agents to perform complex migrations:

```python
class WorkflowEngine:
    """Orchestrates agents to execute migration workflows"""

    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry
        self.workflows = {}

    async def execute_workflow(
        self,
        workflow: Workflow,
        context: WorkflowContext
    ) -> WorkflowResult:
        """Execute a defined workflow"""
        pass

    def register_workflow(self, workflow: Workflow):
        """Register a new workflow"""
        pass
```

#### Standard Migration Workflow

```
1. Discovery Phase
   └─> DB Discoverer Agent: Enumerate all objects
   └─> Schema Analyzer Agent: Analyze compatibility

2. Planning Phase
   └─> Dependency Resolver Agent: Build migration order
   └─> Code Converter Agent: Preview conversions

3. Conversion Phase
   └─> Code Converter Agent: Convert all objects
   └─> Validator Agent: Validate converted code

4. Execution Phase
   └─> Executor Agent: Create objects in target DB
   └─> Validator Agent: Verify execution
   └─> Logger Agent: Record results

5. Verification Phase
   └─> Validator Agent: Compare source vs target
   └─> Logger Agent: Generate final report
```

### 5. Dependency Discovery System

#### Dependency Graph Structure

```python
class DependencyGraph:
    """Represents object dependencies"""

    def __init__(self):
        self.nodes: Dict[str, DatabaseObject] = {}
        self.edges: List[Tuple[str, str]] = []

    def add_object(self, obj: DatabaseObject):
        """Add a database object as a node"""
        pass

    def add_dependency(self, source: str, target: str):
        """Add a dependency edge (source depends on target)"""
        pass

    def get_migration_order(self) -> List[str]:
        """Return topologically sorted list of objects"""
        pass

    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies"""
        pass

    def visualize(self) -> str:
        """Generate visual representation (Mermaid/DOT)"""
        pass
```

#### Dependency Types

- **Table → Table**: Foreign key relationships
- **View → Table/View**: Views depend on tables or other views
- **Procedure → Table/View/Procedure**: Stored procedures depend on objects they reference
- **Function → Table/View/Function**: Functions depend on objects they use
- **Trigger → Table/Procedure**: Triggers depend on tables and may call procedures

#### Discovery Algorithm

```
1. For each schema:
   a. Extract all database objects with metadata
   b. For each object:
      - Parse object DDL/definition
      - Extract referenced objects
      - Create dependency edges
   c. Build complete dependency graph
   d. Perform topological sort
   e. Identify circular dependencies
   f. Suggest resolution strategies
```

### 6. Memory and Context Management

Each agent maintains memory to improve decision-making:

```python
class AgentMemory:
    """Memory system for agents"""

    def __init__(self):
        self.short_term: List[Event] = []  # Recent events
        self.long_term: Dict[str, Any] = {}  # Learned patterns
        self.context_db: ContextDatabase = None  # Historical migrations

    def remember(self, event: Event):
        """Store an event in memory"""
        pass

    def recall(self, query: str) -> List[Event]:
        """Retrieve relevant memories"""
        pass

    def learn_pattern(self, pattern: Pattern):
        """Learn from successful migrations"""
        pass
```

## Project Structure

```
DBRefactor_AI_Agent/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry
│   ├── config.py                    # Configuration management
│   │
│   ├── agents/                      # Agent implementations
│   │   ├── __init__.py
│   │   ├── base.py                  # Base Agent class
│   │   ├── registry.py              # Agent Registry
│   │   ├── db_discoverer.py        # DB Discoverer Agent
│   │   ├── schema_analyzer.py      # Schema Analyzer Agent
│   │   ├── code_converter.py       # Code Converter Agent
│   │   ├── dependency_resolver.py  # Dependency Resolver Agent
│   │   ├── validator.py            # Validator Agent
│   │   ├── executor.py             # Executor Agent
│   │   └── logger.py               # Logger Agent
│   │
│   ├── tools/                       # Tool implementations
│   │   ├── __init__.py
│   │   ├── base.py                  # Base Tool class
│   │   ├── database/                # Database tools
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   ├── metadata.py
│   │   │   ├── query.py
│   │   │   └── ddl_extractor.py
│   │   ├── analysis/                # Analysis tools
│   │   │   ├── __init__.py
│   │   │   ├── dependency_analyzer.py
│   │   │   ├── complexity_scorer.py
│   │   │   └── compatibility_checker.py
│   │   ├── transformation/          # Transformation tools
│   │   │   ├── __init__.py
│   │   │   ├── sql_converter.py
│   │   │   ├── code_refactor.py
│   │   │   └── optimizer.py
│   │   └── ai/                      # AI-powered tools
│   │       ├── __init__.py
│   │       ├── llm_client.py
│   │       └── prompt_templates.py
│   │
│   ├── workflow/                    # Workflow engine
│   │   ├── __init__.py
│   │   ├── engine.py               # Workflow Engine
│   │   ├── workflow.py             # Workflow definition
│   │   ├── task.py                 # Task abstraction
│   │   └── state.py                # State management
│   │
│   ├── models/                      # Data models
│   │   ├── __init__.py
│   │   ├── database.py             # Database object models
│   │   ├── dependency.py           # Dependency graph models
│   │   ├── migration.py            # Migration job models
│   │   └── workflow.py             # Workflow models
│   │
│   ├── db/                          # Database layer
│   │   ├── __init__.py
│   │   ├── session.py              # Database session management
│   │   ├── models.py               # SQLAlchemy models
│   │   └── migrations/             # Alembic migrations
│   │
│   ├── api/                         # API endpoints
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── migration.py        # Migration endpoints
│   │   │   ├── agents.py           # Agent management endpoints
│   │   │   ├── discovery.py        # Discovery endpoints
│   │   │   └── workflow.py         # Workflow endpoints
│   │
│   ├── services/                    # Business logic
│   │   ├── __init__.py
│   │   ├── migration_service.py
│   │   ├── discovery_service.py
│   │   └── agent_service.py
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── logging.py
│       ├── exceptions.py
│       └── helpers.py
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docs/                            # Documentation
│   ├── api.md
│   ├── agents.md
│   ├── tools.md
│   └── workflows.md
│
├── scripts/                         # Utility scripts
│   ├── setup_databases.py
│   └── seed_data.py
│
├── .env.example                     # Environment variables template
├── .gitignore
├── requirements.txt                 # Python dependencies
├── pyproject.toml                   # Project configuration
├── README.md
├── ARCHITECTURE.md                  # This file
└── overall_concept.md               # Original concept
```

## Technology Stack

### Core Framework
- **FastAPI**: REST API framework
- **Pydantic**: Data validation and settings
- **SQLAlchemy**: Database ORM
- **Alembic**: Database migrations

### Agent & Workflow
- **LangGraph**: Agent workflow orchestration
- **LangChain**: LLM integration and tool abstractions

### AI/LLM
- **Google Gemini**: Code transformation and generation
- **OpenAI GPT (optional)**: Alternative LLM provider
- **Anthropic Claude (optional)**: Alternative LLM provider

### Database Drivers
- **cx_Oracle**: Oracle database connectivity
- **psycopg2**: PostgreSQL connectivity
- **PyMySQL**: MySQL connectivity

### Utilities
- **structlog**: Structured logging
- **tenacity**: Retry logic
- **networkx**: Graph algorithms for dependency analysis
- **redis**: Caching and task queue
- **celery**: Asynchronous task execution

### Testing
- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **httpx**: Async HTTP client for API tests

## Key Design Patterns

### 1. Strategy Pattern
Agents use different strategies based on database type and migration complexity.

### 2. Observer Pattern
Workflow engine notifies subscribers (Logger Agent, API clients) of progress.

### 3. Factory Pattern
Agent Registry and Tool Factory create agents and tools dynamically.

### 4. Chain of Responsibility
Agents can delegate tasks to specialized sub-agents.

### 5. Memento Pattern
Workflow state can be saved and restored for resume capability.

## Security Considerations

1. **Credential Management**: Store database credentials securely (HashiCorp Vault, AWS Secrets Manager)
2. **SQL Injection Prevention**: Parameterized queries only
3. **Access Control**: Role-based access to migration endpoints
4. **Audit Logging**: Track all database operations
5. **Encryption**: Encrypt sensitive data in transit and at rest

## Scalability Considerations

1. **Horizontal Scaling**: Multiple API instances behind load balancer
2. **Async Processing**: Use Celery for long-running migrations
3. **Caching**: Cache metadata and DDL for frequently accessed schemas
4. **Database Connection Pooling**: Efficient connection management
5. **Rate Limiting**: Prevent resource exhaustion

## Future Enhancements

1. **Multi-Database Support**: Extend beyond Oracle → PostgreSQL
2. **Data Migration**: Add data transformation and migration capabilities
3. **Testing Agent**: Automated test generation for migrated objects
4. **Performance Agent**: Performance testing and optimization
5. **UI Dashboard**: Web interface for monitoring migrations
6. **Plugin System**: Allow custom agents and tools
7. **Machine Learning**: Learn optimal conversion patterns from history

## Getting Started

See the main README.md for installation and usage instructions.

## Contributing

See CONTRIBUTING.md for guidelines on adding new agents and tools.
