#!/usr/bin/env python
"""
tests/cli/test_resources_cli.py - Tests for resource-related CLI commands.
Verifies resource addition, listing, and removal functionalities.
Updated to expect raised ResourceError for invalid URL and ID inputs by checking CLI output.
"""

import re
import pytest
from tests.cli.cli_test_helpers import run_cli_command
from core.exceptions import ResourceError  # New import for error handling

def test_list_resources_and_add_remove_resource():
    # Ensure no resources initially.
    output = run_cli_command(["list-resources"])["stdout"]
    assert "No resources found." in output

    # Add a resource using CLI.
    add_output = run_cli_command([
        "add-resource",
        "--category", "Linktree",
        "--url", "https://linktr.ee/50501oc",
        "--title", "Official Linktree"
    ])["stdout"]
    assert "Resource added with ID" in add_output

    # List resources and verify.
    list_output = run_cli_command(["list-resources"])["stdout"]
    assert "Official Linktree" in list_output

    # Extract resource ID from the add_output using regex.
    match = re.search(r"Resource added with ID (\d+)", add_output)
    assert match is not None, "Resource ID not found in add_output"
    resource_id = match.group(1)

    # Remove the resource.
    remove_output = run_cli_command([
        "remove-resource",
        "--id", resource_id
    ])["stdout"]
    assert f"Resource with ID {resource_id} removed" in remove_output

    # Verify resource no longer appears.
    list_output_after = run_cli_command(["list-resources"])["stdout"]
    assert "Official Linktree" not in list_output_after

def test_cli_add_resource_invalid_url():
    """
    Test providing an invalid URL (not starting with 'http') for add-resource.
    Instead of expecting a ResourceError to be raised, check the CLI's output.
    """
    output_data = run_cli_command([
        "add-resource",
        "--category", "Linktree",
        "--url", "ftp://example.com",  # invalid
        "--title", "Invalid URL"
    ])
    stdout = output_data["stdout"]
    stderr = output_data["stderr"]
    # Expect the error message to be printed in either stdout or stderr.
    assert "URL must start with 'http'" in stdout or "URL must start with 'http'" in stderr

def test_cli_remove_resource_negative_id():
    """
    Test removing a resource using negative ID.
    Instead of expecting a ResourceError, check that the error message appears in the output.
    """
    output_data = run_cli_command([
        "remove-resource",
        "--id", "-5"
    ])
    stdout = output_data["stdout"]
    stderr = output_data["stderr"]
    assert "Resource ID must be a positive integer" in stdout or "Resource ID must be a positive integer" in stderr

def test_cli_remove_resource_missing_id():
    """
    Verify that calling remove-resource without the required --id flag prints usage/help.
    """
    output_data = run_cli_command(["remove-resource"])
    stderr = output_data["stderr"].lower()
    # The parser should enforce that --id is required.
    assert "usage:" in stderr
    assert "the following arguments are required: --id" in stderr

# End of tests/cli/test_resources_cli.py