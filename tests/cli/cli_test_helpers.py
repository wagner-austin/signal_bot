#!/usr/bin/env python
"""
tests/cli/cli_test_helpers.py - Helper functions for CLI tests.
Provides a unified helper to simulate command-line invocations of cli_tools.py.
"""

import sys
import io

def run_cli_command(command_args):
    """
    run_cli_command - Helper function to simulate command-line invocation of cli_tools.py.
    
    Args:
        command_args (list): List of command arguments.
    
    Returns:
        str: Captured output from running the command.
    """
    original_argv = sys.argv
    original_stdout = sys.stdout
    try:
        sys.argv = ["cli_tools.py"] + command_args
        captured_output = io.StringIO()
        sys.stdout = captured_output
        from cli_tools import main as cli_main
        try:
            cli_main()
        except SystemExit:
            pass
        return captured_output.getvalue()
    finally:
        sys.argv = original_argv
        sys.stdout = original_stdout

# End of tests/cli/cli_test_helpers.py