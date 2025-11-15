"""
Validation utilities for configuration and data.
"""

from typing import List, Optional
import re


def validate_required_env_vars(required_vars: List[str], settings: dict) -> List[str]:
    """
    Validate that required environment variables are set.

    Args:
        required_vars: List of required variable names
        settings: Settings dictionary

    Returns:
        List of missing variables
    """
    missing = []
    for var in required_vars:
        value = settings.get(var)
        if not value or value == "":
            missing.append(var)
    return missing


def validate_port(port: int) -> bool:
    """
    Validate port number.

    Args:
        port: Port number to validate

    Returns:
        True if valid, False otherwise
    """
    return 1 <= port <= 65535


def validate_host(host: str) -> bool:
    """
    Validate host address (IP or hostname).

    Args:
        host: Host address to validate

    Returns:
        True if valid, False otherwise
    """
    if not host:
        return False

    # Allow localhost and 0.0.0.0
    if host in ['localhost', '0.0.0.0', '127.0.0.1']:
        return True

    # Basic hostname/IP validation
    hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]{0,61}[a-zA-Z0-9])?$'
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'

    return bool(re.match(hostname_pattern, host) or re.match(ip_pattern, host))


def validate_log_level(level: str) -> bool:
    """
    Validate log level.

    Args:
        level: Log level to validate

    Returns:
        True if valid, False otherwise
    """
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    return level.upper() in valid_levels
