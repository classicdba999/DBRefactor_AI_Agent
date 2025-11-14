"""
Base Tool class for the DBRefactor AI Agent framework.

Tools are the primary way agents interact with databases, APIs,
and perform various operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import structlog


logger = structlog.get_logger(__name__)


class ToolCategory(str, Enum):
    """Categories of tools available in the system"""
    DATABASE = "database"
    ANALYSIS = "analysis"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    EXECUTION = "execution"
    AI = "ai"
    LOGGING = "logging"
    UTILITY = "utility"


class ToolParameter(BaseModel):
    """Definition of a tool parameter"""
    name: str
    description: str
    type: str  # e.g., "str", "int", "bool", "dict", "list"
    required: bool = True
    default: Optional[Any] = None
    validation_rules: Dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    """Result of a tool execution"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Tool(ABC):
    """
    Base class for all tools in the DBRefactor AI framework.

    Tools are reusable components that agents can use to perform
    specific operations like database queries, code transformation, etc.
    """

    def __init__(
        self,
        name: str,
        description: str,
        category: ToolCategory,
        parameters: Optional[List[ToolParameter]] = None
    ):
        """
        Initialize the tool.

        Args:
            name: Unique name for the tool
            description: Description of what the tool does
            category: Category this tool belongs to
            parameters: List of parameters this tool accepts
        """
        self.name = name
        self.description = description
        self.category = category
        self.parameters = parameters or []
        self.logger = structlog.get_logger(f"Tool.{name}")

        # Execution statistics
        self.stats = {
            'executions': 0,
            'successes': 0,
            'failures': 0,
            'total_execution_time_ms': 0.0
        }

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters.

        This is the main entry point for tool execution.
        Subclasses must implement this method.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            ToolResult with execution details
        """
        pass

    def validate_parameters(self, **kwargs) -> tuple[bool, Optional[str]]:
        """
        Validate parameters before execution.

        Args:
            **kwargs: Parameters to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required parameters
        required_params = {p.name for p in self.parameters if p.required}
        provided_params = set(kwargs.keys())

        missing_params = required_params - provided_params
        if missing_params:
            return False, f"Missing required parameters: {missing_params}"

        # Check parameter types
        for param in self.parameters:
            if param.name in kwargs:
                value = kwargs[param.name]
                expected_type = param.type

                # Basic type validation
                if not self._validate_type(value, expected_type):
                    return (
                        False,
                        f"Parameter '{param.name}' expected type '{expected_type}', "
                        f"got '{type(value).__name__}'"
                    )

                # Apply validation rules
                if param.validation_rules:
                    is_valid, error = self._apply_validation_rules(
                        param.name,
                        value,
                        param.validation_rules
                    )
                    if not is_valid:
                        return False, error

        return True, None

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate that value matches expected type"""
        type_mapping = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'dict': dict,
            'list': list,
            'any': object
        }

        expected_class = type_mapping.get(expected_type.lower())
        if expected_class is None:
            # Unknown type, skip validation
            return True

        return isinstance(value, expected_class)

    def _apply_validation_rules(
        self,
        param_name: str,
        value: Any,
        rules: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Apply validation rules to a parameter value"""
        # Min/Max validation for numbers
        if 'min' in rules and isinstance(value, (int, float)):
            if value < rules['min']:
                return False, f"Parameter '{param_name}' must be >= {rules['min']}"

        if 'max' in rules and isinstance(value, (int, float)):
            if value > rules['max']:
                return False, f"Parameter '{param_name}' must be <= {rules['max']}"

        # Min/Max length validation for strings and lists
        if 'min_length' in rules and isinstance(value, (str, list)):
            if len(value) < rules['min_length']:
                return (
                    False,
                    f"Parameter '{param_name}' length must be >= {rules['min_length']}"
                )

        if 'max_length' in rules and isinstance(value, (str, list)):
            if len(value) > rules['max_length']:
                return (
                    False,
                    f"Parameter '{param_name}' length must be <= {rules['max_length']}"
                )

        # Enum validation
        if 'enum' in rules:
            if value not in rules['enum']:
                return (
                    False,
                    f"Parameter '{param_name}' must be one of {rules['enum']}"
                )

        # Pattern validation for strings
        if 'pattern' in rules and isinstance(value, str):
            import re
            if not re.match(rules['pattern'], value):
                return (
                    False,
                    f"Parameter '{param_name}' does not match pattern {rules['pattern']}"
                )

        return True, None

    async def _safe_execute(self, **kwargs) -> ToolResult:
        """
        Execute tool with parameter validation and error handling.

        This method wraps the execute() method with validation,
        error handling, and statistics tracking.

        Args:
            **kwargs: Tool parameters

        Returns:
            ToolResult
        """
        start_time = datetime.utcnow()

        # Validate parameters
        is_valid, error_msg = self.validate_parameters(**kwargs)
        if not is_valid:
            self.stats['executions'] += 1
            self.stats['failures'] += 1
            return ToolResult(
                success=False,
                error=error_msg,
                execution_time_ms=0.0
            )

        try:
            # Execute the tool
            result = await self.execute(**kwargs)

            # Update statistics
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            result.execution_time_ms = execution_time

            self.stats['executions'] += 1
            if result.success:
                self.stats['successes'] += 1
            else:
                self.stats['failures'] += 1
            self.stats['total_execution_time_ms'] += execution_time

            return result

        except Exception as e:
            # Handle unexpected errors
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            self.stats['executions'] += 1
            self.stats['failures'] += 1
            self.stats['total_execution_time_ms'] += execution_time

            self.logger.error(
                "tool_execution_failed",
                tool=self.name,
                error=str(e),
                exc_info=True
            )

            return ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}",
                execution_time_ms=execution_time
            )

    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for tool parameters.

        Returns:
            Dictionary containing parameter schema
        """
        properties = {}
        required = []

        for param in self.parameters:
            param_schema = {
                'type': param.type,
                'description': param.description
            }

            if param.default is not None:
                param_schema['default'] = param.default

            if param.validation_rules:
                param_schema.update(param.validation_rules)

            properties[param.name] = param_schema

            if param.required:
                required.append(param.name)

        return {
            'type': 'object',
            'properties': properties,
            'required': required
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get tool execution statistics"""
        return {
            **self.stats,
            'success_rate': (
                self.stats['successes'] / self.stats['executions']
                if self.stats['executions'] > 0
                else 0.0
            ),
            'average_execution_time_ms': (
                self.stats['total_execution_time_ms'] / self.stats['executions']
                if self.stats['executions'] > 0
                else 0.0
            )
        }

    def reset_stats(self):
        """Reset execution statistics"""
        self.stats = {
            'executions': 0,
            'successes': 0,
            'failures': 0,
            'total_execution_time_ms': 0.0
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"name='{self.name}' "
            f"category={self.category.value}>"
        )


class ToolFactory:
    """Factory for creating and managing tools"""

    _tools: Dict[str, type] = {}

    @classmethod
    def register_tool_class(cls, tool_class: type):
        """Register a tool class for creation"""
        if not issubclass(tool_class, Tool):
            raise ValueError(f"{tool_class} must be a subclass of Tool")

        cls._tools[tool_class.__name__] = tool_class

    @classmethod
    def create_tool(cls, tool_class_name: str, **kwargs) -> Tool:
        """Create a tool instance"""
        if tool_class_name not in cls._tools:
            raise ValueError(f"Tool class '{tool_class_name}' not registered")

        tool_class = cls._tools[tool_class_name]
        return tool_class(**kwargs)

    @classmethod
    def list_tool_classes(cls) -> List[str]:
        """List all registered tool classes"""
        return list(cls._tools.keys())
