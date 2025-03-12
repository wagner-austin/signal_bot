"""
validators.py
-------------
Utility module for CLI argument validation, plus phone validation.
"""

import re
from core.constants import ALLOWED_CLI_FLAGS, DANGEROUS_PATTERN
from core.exceptions import VolunteerError

# Precompile the dangerous pattern regex to improve performance
DANGEROUS_REGEX = re.compile(DANGEROUS_PATTERN)

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
    for arg in args:
        if arg.startswith("-") and arg not in ALLOWED_CLI_FLAGS:
            raise CLIValidationError(f"Disallowed flag detected: {arg}")
        if DANGEROUS_REGEX.search(arg):
            raise CLIValidationError(f"Potentially dangerous character detected in argument: {arg}")

# New phone validator (unified)
_PHONE_REGEX = re.compile(r'^\+?\d{7,15}$')

def validate_phone_number(phone: str) -> None:
    """
    validate_phone_number - Ensures phone meets the +digits with length 7-15 pattern.
    
    Args:
        phone (str): The phone number to validate.
    
    Raises:
        VolunteerError: If the phone is invalid or empty.
    """
    if not phone or not _PHONE_REGEX.match(phone):
        raise VolunteerError(f"Invalid phone number format. Provided: {phone}")

# End of core/validators.py