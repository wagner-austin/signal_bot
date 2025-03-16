#!/usr/bin/env python
"""
core/validators.py
------------------
Utility module for CLI argument validation, plus phone validation.
Ensures phone meets a +digits pattern, or else raises an error.

CHANGES:
 - Updated 'Invalid phone number format' message to exactly match test expectations.
"""

import re
from plugins.constants import ALLOWED_CLI_FLAGS, DANGEROUS_PATTERN
from core.exceptions import VolunteerError

# Precompile the dangerous pattern regex
DANGEROUS_REGEX = re.compile(DANGEROUS_PATTERN)

class CLIValidationError(Exception):
    """
    CLIValidationError - Exception raised for CLI argument validation errors.
    """
    pass

def validate_cli_args(args):
    """
    validate_cli_args - Validates CLI arguments against allowed flags and dangerous characters.
    """
    for arg in args:
        if arg.startswith("-") and arg not in ALLOWED_CLI_FLAGS:
            raise CLIValidationError(f"Disallowed flag detected: {arg}")
        if DANGEROUS_REGEX.search(arg):
            raise CLIValidationError(f"Potentially dangerous character detected in argument: {arg}")

# Phone validation
_PHONE_REGEX = re.compile(r'^\+?\d{7,15}$')

def validate_phone_number(phone: str) -> None:
    """
    validate_phone_number - Ensures phone meets the +digits pattern with length 7-15.
    Raises VolunteerError if invalid.
    """
    if not phone or not _PHONE_REGEX.match(phone):
        # Test expects "invalid phone number format" substring
        raise VolunteerError("Invalid phone number format")

# End of validators.py