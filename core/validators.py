"""
core/validators.py - Utility module for CLI argument validation.
Centralizes security/validation checks for CLI arguments.
"""

import re
from core.constants import ALLOWED_CLI_FLAGS, DANGEROUS_PATTERN

class CLIValidationError(Exception):
    """
    CLIValidationError - Exception raised for CLI argument validation errors.
    """
    pass

def validate_cli_args(args):
    """
    validate_cli_args - Validates CLI arguments against allowed flags and dangerous characters.
    
    Args:
        args (list): List of CLI arguments.
        
    Raises:
        CLIValidationError: If any argument is invalid.
    """
    dangerous_pattern = re.compile(DANGEROUS_PATTERN)
    for arg in args:
        if arg.startswith("-") and arg not in ALLOWED_CLI_FLAGS:
            raise CLIValidationError(f"Disallowed flag detected: {arg}")
        if dangerous_pattern.search(arg):
            raise CLIValidationError(f"Potentially dangerous character detected in argument: {arg}")

# End of core/validators.py