"""
DB Discoverer Agent - Discovers database objects and their dependencies.

This agent is responsible for:
- Enumerating all database objects in a schema
- Building dependency graphs
- Identifying migration order
- Categorizing objects by type and complexity
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import structlog

from app.agents.base import Agent, Task, AgentResult
from app.tools.database.metadata import (
    GetDatabaseMetadataTool,
    AnalyzeDependenciesTool,
    GetDDLTool
)


logger = structlog.get_logger(__name__)


class DBDiscovererAgent(Agent):
    """
    Agent specialized in discovering and analyzing database objects.

    This agent can:
    1. Enumerate all objects in a database schema
    2. Extract metadata for each object
    3. Build dependency graphs
    4. Determine optimal migration order
    5. Identify circular dependencies
    6. Extract DDL for all objects
    """

    def __init__(self):
        super().__init__(
            name="db_discoverer",
            description="Discovers database objects and analyzes dependencies",
            version="1.0.0"
        )

        # Register tools
        self.register_tool(GetDatabaseMetadataTool())
        self.register_tool(AnalyzeDependenciesTool())
        self.register_tool(GetDDLTool())

    async def execute(self, task: Task) -> AgentResult:
        """
        Execute a discovery task.

        Supported actions:
        - discover_schema: Enumerate all objects in a schema
        - analyze_dependencies: Build dependency graph
        - get_ddl: Extract DDL for objects
        - full_discovery: Complete discovery with dependencies and DDL

        Args:
            task: Task to execute

        Returns:
            AgentResult with discovery data
        """
        start_time = datetime.utcnow()
        tool_calls = []

        try:
            action = task.action
            params = task.params

            if action == "discover_schema":
                result_data = await self._discover_schema(params, tool_calls)
            elif action == "analyze_dependencies":
                result_data = await self._analyze_dependencies(params, tool_calls)
            elif action == "get_ddl":
                result_data = await self._get_ddl(params, tool_calls)
            elif action == "full_discovery":
                result_data = await self._full_discovery(params, tool_calls)
            else:
                raise ValueError(f"Unknown action: {action}")

            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            result = AgentResult(
                task_id=task.id,
                success=True,
                data=result_data,
                execution_time_ms=execution_time,
                tool_calls=tool_calls
            )

            self.update_stats(result)
            return result

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            self.logger.error(
                "discovery_failed",
                task_id=task.id,
                action=task.action,
                error=str(e),
                exc_info=True
            )

            result = AgentResult(
                task_id=task.id,
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
                tool_calls=tool_calls
            )

            self.update_stats(result)
            return result

    async def _discover_schema(
        self,
        params: Dict[str, Any],
        tool_calls: List[str]
    ) -> Dict[str, Any]:
        """Discover all objects in a schema"""
        connection = params.get('connection')
        schema_name = params.get('schema_name')
        include_system_objects = params.get('include_system_objects', False)

        self.logger.info(
            "discovering_schema",
            schema_name=schema_name
        )

        # Use metadata tool to get all objects
        tool_calls.append('get_database_metadata')
        metadata_result = await self._execute_tool(
            'get_database_metadata',
            connection=connection,
            schema_name=schema_name,
            include_system_objects=include_system_objects
        )

        if not metadata_result.success:
            raise RuntimeError(f"Metadata extraction failed: {metadata_result.error}")

        metadata = metadata_result.data

        # Store in memory for future reference
        self.memory.cache_context(
            f"schema_metadata:{schema_name}",
            metadata,
            ttl_seconds=3600
        )

        # Categorize objects by complexity
        categorized_objects = self._categorize_objects(metadata)

        return {
            'schema_name': schema_name,
            'metadata': metadata,
            'categorized_objects': categorized_objects,
            'discovery_timestamp': datetime.utcnow().isoformat()
        }

    async def _analyze_dependencies(
        self,
        params: Dict[str, Any],
        tool_calls: List[str]
    ) -> Dict[str, Any]:
        """Analyze dependencies between objects"""
        connection = params.get('connection')
        schema_name = params.get('schema_name')
        object_list = params.get('object_list')

        self.logger.info(
            "analyzing_dependencies",
            schema_name=schema_name,
            object_count=len(object_list) if object_list else 'all'
        )

        # Use dependency analysis tool
        tool_calls.append('analyze_dependencies')
        dep_result = await self._execute_tool(
            'analyze_dependencies',
            connection=connection,
            schema_name=schema_name,
            object_list=object_list
        )

        if not dep_result.success:
            raise RuntimeError(f"Dependency analysis failed: {dep_result.error}")

        dep_data = dep_result.data

        # Store dependency graph in memory
        self.memory.cache_context(
            f"dependency_graph:{schema_name}",
            dep_data['dependency_graph'],
            ttl_seconds=3600
        )

        # Generate migration recommendations
        recommendations = self._generate_migration_recommendations(dep_data)

        return {
            'schema_name': schema_name,
            'dependency_analysis': dep_data,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }

    async def _get_ddl(
        self,
        params: Dict[str, Any],
        tool_calls: List[str]
    ) -> Dict[str, Any]:
        """Extract DDL for database objects"""
        connection = params.get('connection')
        schema_name = params.get('schema_name')
        object_type = params.get('object_type')
        object_name = params.get('object_name')

        self.logger.info(
            "extracting_ddl",
            schema_name=schema_name,
            object_type=object_type,
            object_name=object_name
        )

        # Use DDL extraction tool
        tool_calls.append('get_ddl')
        ddl_result = await self._execute_tool(
            'get_ddl',
            connection=connection,
            object_type=object_type,
            object_name=object_name,
            schema_name=schema_name
        )

        if not ddl_result.success:
            raise RuntimeError(f"DDL extraction failed: {ddl_result.error}")

        return ddl_result.data

    async def _full_discovery(
        self,
        params: Dict[str, Any],
        tool_calls: List[str]
    ) -> Dict[str, Any]:
        """
        Perform full discovery: metadata + dependencies + DDL

        This is the most comprehensive discovery action that
        gathers all information needed for migration planning.
        """
        connection = params.get('connection')
        schema_name = params.get('schema_name')
        include_system_objects = params.get('include_system_objects', False)

        self.logger.info(
            "performing_full_discovery",
            schema_name=schema_name
        )

        # Step 1: Discover schema
        schema_discovery = await self._discover_schema(
            {
                'connection': connection,
                'schema_name': schema_name,
                'include_system_objects': include_system_objects
            },
            tool_calls
        )

        # Step 2: Analyze dependencies
        dependency_analysis = await self._analyze_dependencies(
            {
                'connection': connection,
                'schema_name': schema_name,
                'object_list': None  # Analyze all objects
            },
            tool_calls
        )

        # Step 3: Extract DDL for all objects (using creation order)
        creation_order = dependency_analysis['dependency_analysis']['creation_order']
        ddl_by_object = {}

        for obj_ref in creation_order:
            # Parse object reference (format: "type:schema.name")
            try:
                obj_type, obj_full_name = obj_ref.split(':', 1)
                schema, obj_name = obj_full_name.split('.', 1)

                ddl_data = await self._get_ddl(
                    {
                        'connection': connection,
                        'object_type': obj_type,
                        'object_name': obj_name,
                        'schema_name': schema
                    },
                    tool_calls
                )

                ddl_by_object[obj_ref] = ddl_data['ddl']

            except Exception as e:
                self.logger.warning(
                    "ddl_extraction_failed_for_object",
                    object_ref=obj_ref,
                    error=str(e)
                )
                ddl_by_object[obj_ref] = f"-- Failed to extract DDL: {str(e)}"

        # Compile complete discovery report
        full_report = {
            'schema_name': schema_name,
            'discovery_summary': {
                **schema_discovery['metadata']['summary'],
                'has_circular_dependencies': dependency_analysis['dependency_analysis']['has_circular_dependencies'],
                'total_dependencies': dependency_analysis['dependency_analysis']['total_dependencies']
            },
            'metadata': schema_discovery['metadata'],
            'categorized_objects': schema_discovery['categorized_objects'],
            'dependency_analysis': dependency_analysis['dependency_analysis'],
            'migration_recommendations': dependency_analysis['recommendations'],
            'ddl_by_object': ddl_by_object,
            'discovery_timestamp': datetime.utcnow().isoformat()
        }

        # Store complete report in memory
        self.memory.cache_context(
            f"full_discovery:{schema_name}",
            full_report,
            ttl_seconds=7200  # 2 hours
        )

        return full_report

    def _categorize_objects(self, metadata: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Categorize objects by complexity and type.

        Categories:
        - simple: Tables with no dependencies
        - moderate: Views, simple procedures
        - complex: Procedures with dependencies, triggers
        - very_complex: Complex procedures, circular dependencies
        """
        categorized = {
            'simple': [],
            'moderate': [],
            'complex': [],
            'very_complex': []
        }

        # Categorize tables
        for table in metadata.get('tables', []):
            # Simple heuristic - can be enhanced
            if table.get('has_foreign_keys', False):
                categorized['moderate'].append(f"TABLE:{table['name']}")
            else:
                categorized['simple'].append(f"TABLE:{table['name']}")

        # Categorize views
        for view in metadata.get('views', []):
            categorized['moderate'].append(f"VIEW:{view['name']}")

        # Categorize procedures
        for proc in metadata.get('procedures', []):
            # Heuristic based on line count or complexity
            lines = proc.get('line_count', 0)
            if lines > 100:
                categorized['complex'].append(f"PROCEDURE:{proc['name']}")
            else:
                categorized['moderate'].append(f"PROCEDURE:{proc['name']}")

        # Categorize functions
        for func in metadata.get('functions', []):
            categorized['moderate'].append(f"FUNCTION:{func['name']}")

        # Categorize triggers (usually complex)
        for trigger in metadata.get('triggers', []):
            categorized['complex'].append(f"TRIGGER:{trigger['name']}")

        return categorized

    def _generate_migration_recommendations(
        self,
        dependency_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate recommendations for migration based on dependency analysis.

        Returns recommendations for:
        - Migration order
        - Circular dependency resolution
        - Risk assessment
        - Estimated complexity
        """
        recommendations = {
            'migration_strategy': 'sequential',  # or 'batched'
            'recommended_order': dependency_data['creation_order'],
            'risk_level': 'low',  # low, medium, high
            'warnings': [],
            'suggestions': []
        }

        # Check for circular dependencies
        if dependency_data['has_circular_dependencies']:
            recommendations['risk_level'] = 'high'
            recommendations['warnings'].append(
                "Circular dependencies detected. Manual intervention may be required."
            )
            recommendations['suggestions'].append(
                "Consider breaking circular dependencies by creating objects without "
                "constraints first, then adding constraints in a second pass."
            )

        # Assess complexity based on number of objects
        total_objects = dependency_data['total_objects']
        if total_objects > 100:
            recommendations['migration_strategy'] = 'batched'
            recommendations['suggestions'].append(
                f"Large number of objects ({total_objects}). "
                "Consider migrating in batches to manage risk."
            )

        # Check dependency depth
        if dependency_data['total_dependencies'] > total_objects * 2:
            recommendations['risk_level'] = 'medium' if recommendations['risk_level'] == 'low' else 'high'
            recommendations['warnings'].append(
                "High dependency ratio detected. Migration may be complex."
            )

        return recommendations

    def can_handle(self, task: Task) -> bool:
        """Check if this agent can handle the task"""
        supported_actions = {
            'discover_schema',
            'analyze_dependencies',
            'get_ddl',
            'full_discovery'
        }
        return task.action in supported_actions
