#!/usr/bin/env python
"""
tests/plugins/test_resource_commands.py - Tests for the resource command plugin.
Verifies that the resource_command function correctly handles usage, add, list, and remove subcommands,
including edge/negative cases like missing category or URL, empty titles, and unrecognized subcommands.
"""

import re
import pytest
from plugins.commands.resource import resource_command
from core.state import BotStateMachine
from core.database.resources import list_resources

def test_resource_no_args_shows_usage():
    """
    Test that calling resource_command with no arguments returns usage instructions.
    """
    state_machine = BotStateMachine()
    sender = "+10000000000"
    response = resource_command("", sender, state_machine, msg_timestamp=123)
    assert "Usage:" in response
    assert "resource add <category> <url> [title?]" in response

def test_resource_add_command():
    """
    Tests the 'add' subcommand for resource_command with valid arguments.
    """
    state_machine = BotStateMachine()
    sender = "+10000000000"
    response = resource_command("add Linktree https://linktr.ee/50501oc OfficialLinktree",
                                sender, state_machine, msg_timestamp=123)
    assert "Resource added with ID" in response
    # Verify that the resource exists in the database.
    resources = list_resources("Linktree")
    assert any("OfficialLinktree" in res["title"] for res in resources)

def test_resource_list_command_with_category():
    """
    Tests listing resources filtered by category.
    """
    state_machine = BotStateMachine()
    sender = "+10000000000"
    # Pre-add a resource.
    resource_command("add Linktree https://linktr.ee/50501oc OfficialLinktree",
                     sender, state_machine, msg_timestamp=123)
    # Now list resources filtered by the "Linktree" category.
    response = resource_command("list Linktree", sender, state_machine, msg_timestamp=123)
    assert "ID" in response and "Linktree" in response and "OfficialLinktree" in response

def test_resource_list_command_all():
    """
    Tests listing all resources without specifying a category.
    """
    state_machine = BotStateMachine()
    sender = "+10000000000"
    # Pre-add resources in different categories.
    resource_command("add Linktree https://linktr.ee/50501oc OfficialLinktree",
                     sender, state_machine, msg_timestamp=123)
    resource_command("add Flyers https://example.com/flyer Flyer1",
                     sender, state_machine, msg_timestamp=123)
    # List all resources without filtering by category.
    response = resource_command("list", sender, state_machine, msg_timestamp=123)
    assert "OfficialLinktree" in response and "Flyer1" in response

def test_resource_remove_command():
    """
    Tests removing a resource by its ID.
    """
    state_machine = BotStateMachine()
    sender = "+10000000000"
    # Add a resource and capture its ID from the response.
    add_response = resource_command("add Linktree https://linktr.ee/50501oc OfficialLinktree",
                                    sender, state_machine, msg_timestamp=123)
    assert "Resource added with ID" in add_response
    # Extract the resource ID
    match = re.search(r"Resource added with ID (\d+)", add_response)
    assert match, "No resource ID found in add output"
    resource_id = match.group(1)

    # Remove the resource.
    remove_response = resource_command(f"remove {resource_id}", sender, state_machine, msg_timestamp=123)
    assert f"Resource with ID {resource_id} removed" in remove_response

    # Verify resource no longer appears in listing.
    list_output = resource_command("list Linktree", sender, state_machine, msg_timestamp=123)
    assert str(resource_id) not in list_output

def test_resource_add_missing_category():
    """
    Test passing only the URL, omitting the category completely.
    Should show an error about missing category.
    """
    state_machine = BotStateMachine()
    sender = "+10000000001"
    response = resource_command("add  https://example.com", sender, state_machine, msg_timestamp=123)
    assert "Error: Category is required" in response

def test_resource_add_missing_url():
    """
    Test passing only the category, omitting the URL.
    Should show an error about missing URL.
    """
    state_machine = BotStateMachine()
    sender = "+10000000002"
    response = resource_command("add Flyers", sender, state_machine, msg_timestamp=123)
    assert "Error: URL is required" in response

def test_resource_add_empty_title():
    """
    Test adding a resource with an empty title.
    This should succeed quietly, storing an empty title string in the database.
    """
    state_machine = BotStateMachine()
    sender = "+10000000003"
    response = resource_command("add Docs https://example.com", sender, state_machine, msg_timestamp=123)
    assert "Resource added with ID" in response

    # Verify the resource was created with empty title
    resources = list_resources("Docs")
    assert any(r["title"] == "" for r in resources)

def test_resource_unknown_subcommand():
    """
    Test that an unrecognized subcommand returns an error message indicating an invalid subcommand.
    """
    state_machine = BotStateMachine()
    sender = "+10000000000"
    response = resource_command("foo", sender, state_machine, msg_timestamp=123)
    assert "Invalid subcommand" in response

# End of tests/plugins/test_resource_commands.py