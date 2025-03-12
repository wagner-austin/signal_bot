#!/usr/bin/env python
"""
tests/cli/test_resources_cli.py - Tests for resource-related CLI commands.
Verifies resource addition, listing, and removal functionalities using the unified resources_manager.
Ensures that CLI commands delegate to managers.resources_manager.list_all_resources and removes legacy DB logic.
"""

import re
import pytest
from tests.cli.cli_test_helpers import run_cli_command

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
    """
    output_data = run_cli_command([
        "add-resource",
        "--category", "Linktree",
        "--url", "ftp://example.com",  # invalid URL
        "--title", "Invalid URL"
    ])
    stdout = output_data["stdout"]
    stderr = output_data["stderr"]
    # Expect the error message about the URL format in either stdout or stderr.
    assert "URL must start with 'http'" in stdout or "URL must start with 'http'" in stderr

def test_cli_remove_resource_negative_id():
    """
    Test removing a resource using a negative ID.
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
    # The argument parser should enforce that --id is required.
    assert "usage:" in stderr
    assert "the following arguments are required: --id" in stderr

def test_list_resources_calls_manager(monkeypatch):
    """
    Test that the 'list-resources' CLI command delegates to managers.resources_manager.list_all_resources().
    """
    call_log = []
    def fake_list_all_resources():
        call_log.append(True)
        return []
    monkeypatch.setattr("cli.resources_cli.list_all_resources", fake_list_all_resources)
    output = run_cli_command(["list-resources"])["stdout"]
    assert "No resources found." in output
    assert call_log, "list_all_resources was not called"

# End of tests/cli/test_resources_cli.py