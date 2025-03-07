"""
tests/core/test_validators.py - Tests for the CLI argument validation functions in core/validators.py.
Ensures that allowed CLI flags pass validation and disallowed flags or dangerous characters raise errors.
"""

import pytest
from core.validators import validate_cli_args, CLIValidationError

def test_validate_cli_args_valid():
    # Valid arguments should not raise an error.
    args = ["send", "--message-from-stdin"]
    # Should pass without error.
    validate_cli_args(args)

def test_validate_cli_args_invalid_flag():
    # A flag not in ALLOWED_CLI_FLAGS should trigger a CLIValidationError.
    args = ["-x"]
    with pytest.raises(CLIValidationError) as excinfo:
        validate_cli_args(args)
    assert "Disallowed flag" in str(excinfo.value)

def test_validate_cli_args_dangerous_character():
    # An argument containing dangerous characters should trigger a CLIValidationError.
    args = ["send", "test;rm -rf /"]
    with pytest.raises(CLIValidationError) as excinfo:
        validate_cli_args(args)
    assert "Potentially dangerous character" in str(excinfo.value)

# End of tests/core/test_validators.py