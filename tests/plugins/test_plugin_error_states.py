#!/usr/bin/env python
"""
tests/plugins/test_plugin_error_states.py - Plugin error state tests.
Covers a plugin returning a non-string, and one that raises an unhandled exception.
Confirms graceful handling and proper logging without crashing.
"""

import pytest
import logging
from managers.message.message_dispatcher import dispatch_message
from parsers.message_parser import ParsedMessage
from plugins.manager import plugin_registry, alias_mapping
from core.state import BotStateMachine
# NEW: We now import real pending actions and volunteer manager
from managers.pending_actions import PENDING_ACTIONS
from managers.volunteer_manager import VOLUNTEER_MANAGER

@pytest.fixture
def dummy_logger(caplog):
    """
    A fixture to capture logs for validation.
    """
    caplog.set_level(logging.WARNING, logger="managers.message.message_dispatcher")
    return caplog

@pytest.fixture
def dummy_state_machine():
    return BotStateMachine()

def make_parsed_message(command_name: str) -> ParsedMessage:
    return ParsedMessage(
        sender="+9999999999",
        body=f"@bot {command_name}",
        timestamp=123,
        group_id=None,
        reply_to=None,
        message_timestamp=None,
        command=command_name,
        args=""
    )

def test_plugin_returning_non_string(dummy_logger, dummy_state_machine):
    """
    Dynamically register a plugin that returns a list instead of a string.
    Then call dispatch_message to confirm it logs a warning and returns empty string.
    """
    def return_list(args, sender, state_machine, msg_timestamp=None):
        return ["This", "is", "a", "list"]

    alias_mapping["nonstring"] = "nonstring"
    plugin_registry["nonstring"] = {
        "function": return_list,
        "aliases": ["nonstring"],
        "help_visible": True,
    }

    parsed = make_parsed_message("nonstring")
    try:
        # Pass real pending actions & volunteer manager here
        response = dispatch_message(parsed, parsed.sender, dummy_state_machine, PENDING_ACTIONS, VOLUNTEER_MANAGER)
        # We expect response to be an empty string since the plugin returned a non-string
        assert response == ""
        # Confirm we logged a warning about non-string result
        logs = [r.message for r in dummy_logger.records]
        assert any("returned a non-string result" in msg for msg in logs)
    finally:
        # Cleanup plugin registrations
        alias_mapping.pop("nonstring", None)
        plugin_registry.pop("nonstring", None)


def test_plugin_raising_exception(dummy_logger, dummy_state_machine):
    """
    Dynamically register a plugin that raises an exception. Confirm dispatch_message
    returns the "internal error" message and logs an exception.
    """
    def explode_plugin(args, sender, state_machine, msg_timestamp=None):
        raise RuntimeError("Boom!")

    alias_mapping["explode"] = "explode"
    plugin_registry["explode"] = {
        "function": explode_plugin,
        "aliases": ["explode"],
        "help_visible": True,
    }

    parsed = make_parsed_message("explode")
    try:
        # Pass real pending actions & volunteer manager here
        response = dispatch_message(parsed, parsed.sender, dummy_state_machine, PENDING_ACTIONS, VOLUNTEER_MANAGER)
        assert "An internal error occurred" in response
        # Confirm we logged an exception
        logs = [r.message for r in dummy_logger.records]
        assert any("Error executing plugin for command 'explode'" in msg for msg in logs)
    finally:
        # Cleanup plugin registrations
        alias_mapping.pop("explode", None)
        plugin_registry.pop("explode", None)

# End of tests/plugins/test_plugin_error_states.py