#!/usr/bin/env python
"""
tests/plugins/test_resource_commands.py - Tests for the resource command plugin.
Verifies that the resource_command function correctly handles usage, add, list, and remove subcommands.
"""

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
    assert "resource list [<category>]" in response
    assert "resource remove <resource_id>" in response


def test_resource_add_command():
    """
    Tests the 'add' subcommand for resource_command.
    """
    state_machine = BotStateMachine()
    sender = "+10000000000"
    response = resource_command("add Linktree https://linktr.ee/50501oc Official Linktree",
                                sender, state_machine, msg_timestamp=123)
    assert "Resource added with ID" in response
    # Verify that the resource exists in the database.
    resources = list_resources("Linktree")
    assert any("Official Linktree" in res["title"] for res in resources)


def test_resource_list_command_with_category():
    """
    Tests listing resources filtered by category.
    """
    state_machine = BotStateMachine()
    sender = "+10000000000"
    # Pre-add a resource.
    resource_command("add Linktree https://linktr.ee/50501oc Official Linktree",
                     sender, state_machine, msg_timestamp=123)
    # Now list resources filtered by the "Linktree" category.
    response = resource_command("list Linktree", sender, state_machine, msg_timestamp=123)
    assert "ID" in response and "Linktree" in response and "Official Linktree" in response


def test_resource_list_command_all():
    """
    Tests listing all resources without specifying a category.
    """
    state_machine = BotStateMachine()
    sender = "+10000000000"
    # Pre-add resources in different categories.
    resource_command("add Linktree https://linktr.ee/50501oc Official Linktree",
                     sender, state_machine, msg_timestamp=123)
    resource_command("add Flyers https://example.com/flyer Flyer1",
                     sender, state_machine, msg_timestamp=123)
    # List all resources without filtering by category.
    response = resource_command("list", sender, state_machine, msg_timestamp=123)
    assert "Official Linktree" in response and "Flyer1" in response


def test_resource_remove_command():
    """
    Tests removing a resource by its ID.
    """
    state_machine = BotStateMachine()
    sender = "+10000000000"
    # Add a resource and capture its ID from the response.
    add_response = resource_command("add Linktree https://linktr.ee/50501oc Official Linktree",
                                    sender, state_machine, msg_timestamp=123)
    # Extract the resource ID (assuming response format "Resource added with ID X.").
    parts = add_response.split()
    resource_id = int(parts[-1].strip("."))

    # Remove the resource.
    remove_response = resource_command(f"remove {resource_id}", sender, state_machine, msg_timestamp=123)
    assert f"Resource with ID {resource_id} removed" in remove_response

    # Verify that the resource no longer appears in the listing.
    list_response = resource_command("list Linktree", sender, state_machine, msg_timestamp=123)
    assert str(resource_id) not in list_response

# End of tests/plugins/test_resource_commands.py