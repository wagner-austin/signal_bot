#!/usr/bin/env python
"""
tests/managers/test_message_manager.py --- Tests for MessageManager facade and multi-flow logic.
Ensures process_message delegates to plugin commands or to FlowManager when a user is in an active flow.
Includes step-by-step tests for registration, edit, and deletion flows.
"""

import pytest
from managers.message_manager import MessageManager
from core.state import BotStateMachine
from parsers.message_parser import ParsedMessage

from managers.user_states_manager import (
    create_flow, get_active_flow, clear_flow_state
)

# We import the FlowManager to verify flow transitions in step-by-step tests
from managers.flow_manager import FlowManager

@pytest.fixture(autouse=True)
def register_dummy_command_plugin(monkeypatch):
    """
    Registers a dummy plugin command named 'dummy' that always returns 'dummy response'.
    This fixture runs automatically for all tests.
    """
    from plugins.manager import plugin_registry, alias_mapping
    alias_mapping["dummy"] = "dummy"
    plugin_registry["dummy"] = {
        "function": lambda args, sender, state_machine, msg_timestamp=None: "dummy response",
        "aliases": ["dummy"],
        "help_visible": True
    }
    yield
    alias_mapping.pop("dummy", None)
    plugin_registry.pop("dummy", None)

@pytest.fixture
def dummy_phone():
    return "+1111111111"

@pytest.fixture
def message_manager():
    state_machine = BotStateMachine()
    return MessageManager(state_machine)

def make_dummy_parsed_message() -> ParsedMessage:
    """
    make_dummy_parsed_message --- Creates a dummy ParsedMessage with command "dummy" and no arguments.
    """
    return ParsedMessage(
        sender="+1111111111",
        body="@bot dummy",
        timestamp=123,
        group_id=None,
        reply_to=None,
        message_timestamp=None,
        command="dummy",
        args=""
    )

def test_message_manager_process_message(message_manager):
    """
    Test that MessageManager.process_message dispatches the dummy command correctly.
    The response should be "dummy response".
    """
    parsed = make_dummy_parsed_message()
    volunteer_manager = DummyVolunteerManager()
    response = message_manager.process_message(parsed, parsed.sender, volunteer_manager, msg_timestamp=123)
    expected_response = "dummy response"
    assert response == expected_response

class DummyVolunteerManager:
    def register_volunteer(self, sender: str, name: str, skills: list):
        return f"registered {name}"
    def volunteer_status(self):
        return "status ok"

#
# Existing Tests for Multi-Flow Auto-Dispatch
#

@pytest.fixture(autouse=True)
def cleanup_user_flow(dummy_phone):
    """
    Cleanup flow state after each multi-flow test.
    """
    yield
    clear_flow_state(dummy_phone)

def test_no_command_no_active_flow(message_manager, dummy_phone):
    """
    If there's no recognized command and no active flow, the response should be empty.
    """
    parsed = ParsedMessage(
        sender=dummy_phone,
        body="random text here",
        timestamp=123,
        group_id=None,
        reply_to=None,
        message_timestamp=None,
        command=None,
        args=None
    )
    response = message_manager.process_message(parsed, dummy_phone, volunteer_manager=None)
    assert response == "", "No command + no active flow => empty response"

def test_active_flow_auto_dispatch(message_manager, dummy_phone):
    """
    If the user has an active flow, a message with no recognized command
    should be auto-dispatched to the flow logic (stub or real) in MessageManager.
    """
    create_flow(dummy_phone, "testflow")
    parsed = ParsedMessage(
        sender=dummy_phone,
        body="some message",
        timestamp=999,
        group_id=None,
        reply_to=None,
        message_timestamp=None,
        command=None,
        args=None
    )
    response = message_manager.process_message(parsed, dummy_phone, volunteer_manager=None)
    # By default, the FlowManager doesn't handle "testflow" specifically, so we get an empty response
    # or a default fallback.
    assert response == "", "Unrecognized flow name => no recognized step => empty response"

def test_command_takes_precedence(message_manager, dummy_phone):
    """
    If there's a recognized command, it should override the active flow,
    and the recognized command's plugin response should be returned.
    """
    create_flow(dummy_phone, "flowA")
    parsed = ParsedMessage(
        sender=dummy_phone,
        body="@bot dummy",
        timestamp=111,
        group_id=None,
        reply_to=None,
        message_timestamp=None,
        command="dummy",
        args=""
    )
    response = message_manager.process_message(parsed, dummy_phone, volunteer_manager=None)
    assert response == "dummy response", "Recognized command must override flow dispatch."
    # Flow remains active, but the command took precedence
    assert get_active_flow(dummy_phone) == "flowA"

#
# New Step-by-Step Tests for Volunteer Flows
#

FLOW_MANAGER = FlowManager()

def _make_parsed(sender, command=None, body="", timestamp=999):
    """
    Helper to create a ParsedMessage with optional command, body, and timestamp.
    """
    return ParsedMessage(
        sender=sender,
        body=body,
        timestamp=timestamp,
        group_id=None,
        reply_to=None,
        message_timestamp=None,
        command=command,
        args=None if command is None else ""
    )

def test_registration_flow_step_by_step(message_manager, dummy_phone):
    """
    Test the volunteer registration flow from start to end.
    1) The user issues '@bot register' => starts flow
    2) The user responds with a valid full name or 'skip'
    3) Final outcome is a successful registration.
    """
    # Step 1: user triggers register command
    parsed1 = _make_parsed(dummy_phone, command="register", body="@bot register")
    response1 = message_manager.process_message(parsed1, dummy_phone, volunteer_manager=None)
    assert "starting registration flow." in response1.lower(), "Should prompt user to provide name or skip"

    # Step 2: user sends a valid full name (at least two words)
    parsed2 = _make_parsed(dummy_phone, body="My Name")
    response2 = message_manager.process_message(parsed2, dummy_phone, volunteer_manager=None)
    # The FlowManager should complete registration and return a message with 'registered' or 'volunteer'
    assert "registered" in response2.lower() or "volunteer" in response2.lower(), \
        "Expected a response about the user being registered"

def test_edit_flow_step_by_step(message_manager, dummy_phone):
    """
    Test the volunteer edit flow from start to end.
    1) Ensure user is first registered (so edit flow can proceed).
    2) The user issues '@bot edit' => starts flow
    3) The user sends new name => flow completes
    """
    # Pre-register user
    parsed_reg1 = _make_parsed(dummy_phone, command="register", body="@bot register")
    _ = message_manager.process_message(parsed_reg1, dummy_phone, volunteer_manager=None)
    parsed_reg2 = _make_parsed(dummy_phone, body="skip")
    _ = message_manager.process_message(parsed_reg2, dummy_phone, volunteer_manager=None)

    # Step 1: user triggers edit command
    parsed1 = _make_parsed(dummy_phone, command="edit", body="@bot edit")
    response1 = message_manager.process_message(parsed1, dummy_phone, volunteer_manager=None)
    assert "starting edit flow." in response1.lower(), "Should prompt user for a new name"

    # Step 2: user sends the new name (unrecognized command => flow handles it)
    parsed2 = _make_parsed(dummy_phone, body="MyNewName")
    response2 = message_manager.process_message(parsed2, dummy_phone, volunteer_manager=None)
    assert "updated" in response2.lower() or "registered" in response2.lower(), \
        "Expected a response about the volunteer name being updated"

def test_deletion_flow_step_by_step(message_manager, dummy_phone):
    """
    Test the volunteer deletion flow from start to finish.
    1) Register the user
    2) Issue '@bot delete' => starts flow
    3) Type 'yes' => prompts for 'delete'
    4) Type 'delete' => actually deletes
    """
    # 1) Register user quickly
    parsed_reg1 = _make_parsed(dummy_phone, command="register", body="@bot register")
    _ = message_manager.process_message(parsed_reg1, dummy_phone, volunteer_manager=None)
    parsed_reg2 = _make_parsed(dummy_phone, body="skip")
    _ = message_manager.process_message(parsed_reg2, dummy_phone, volunteer_manager=None)

    # 2) Start deletion flow
    parsed_delete_init = _make_parsed(dummy_phone, command="delete", body="@bot delete")
    response_init = message_manager.process_message(parsed_delete_init, dummy_phone, volunteer_manager=None)
    assert "starting deletion flow." in response_init.lower(), "Expected to start the deletion flow"

    # 3) user says 'yes' => proceed to next step
    parsed_yes = _make_parsed(dummy_phone, body="yes")
    response_yes = message_manager.process_message(parsed_yes, dummy_phone, volunteer_manager=None)
    assert "type 'delete'" in response_yes.lower() or "are you sure" in response_yes.lower(), \
        "Should prompt user for final confirmation"

    # 4) user types 'delete' => final
    parsed_confirm = _make_parsed(dummy_phone, body="delete")
    response_confirm = message_manager.process_message(parsed_confirm, dummy_phone, volunteer_manager=None)
    assert "deleted" in response_confirm.lower(), \
        "Expected confirmation of volunteer deletion"

# End of tests/managers/test_message_manager.py