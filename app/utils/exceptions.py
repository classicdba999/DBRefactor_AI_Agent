"""
Custom exceptions for DBRefactor AI Agent.
"""


class DBRefactorException(Exception):
    """Base exception for all DBRefactor errors"""
    pass


class ConfigurationError(DBRefactorException):
    """Raised when configuration is invalid"""
    pass


class AgentNotFoundError(DBRefactorException):
    """Raised when an agent is not found in the registry"""
    pass


class AgentExecutionError(DBRefactorException):
    """Raised when an agent fails to execute a task"""
    pass


class ToolExecutionError(DBRefactorException):
    """Raised when a tool fails to execute"""
    pass


class WorkflowExecutionError(DBRefactorException):
    """Raised when a workflow fails"""
    pass


class DatabaseConnectionError(DBRefactorException):
    """Raised when database connection fails"""
    pass


class DependencyError(DBRefactorException):
    """Raised when dependency resolution fails"""
    pass


class ValidationError(DBRefactorException):
    """Raised when validation fails"""
    pass
