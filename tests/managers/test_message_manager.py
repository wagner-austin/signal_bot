#!/usr/bin/env python
"""
tests/managers/test_message_manager.py --- Tests for the MessageManager facade.
Verifies that process_message correctly delegates to the message dispatcher.
Note: The GETTING_STARTED message is now sent separately via process_incoming.

CHANGES:
 - Added tests for multi-flow auto-dispatch logic (no recognized command + active flow).
 - Confirm recognized command overrides any active flow.
 - Retained original dummy command test.
"""

import pytest
from managers.message_manager import MessageManager
from core.state import BotStateMachine
from parsers.message_parser import ParsedMessage
from core.messages import GETTING_STARTED

# Import multi-flow helpers
from managers.user_states_manager import create_flow, get_flow_state, clear_flow_state

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
    
    Returns:
        ParsedMessage: A dummy message object.
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
# New Tests for Multi-Flow Auto-Dispatch
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
    should be auto-dispatched to the flow logic (stub) in MessageManager.
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
    # The stub in message_manager returns:
    #  f"Flow '{flow_name}' is active. You said: {raw_text}. (Flow logic not implemented here.)"
    assert "Flow 'testflow' is active." in response, "Expected flow stub message."
    assert "You said: some message." in response

def test_command_takes_precedence(message_manager, dummy_phone):
    """
    If there's a recognized command, it should override the active flow,
    and the recognized command's plugin response should be returned.
    """
    # Put user in an active flow
    create_flow(dummy_phone, "flowA")
    # Prepare a parsed message with command 'dummy'
    parsed = ParsedMessage(
        sender=dummy_phone,
        body="@bot dummy",  # recognized command
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
    assert get_flow_state(dummy_phone) == "flowA"

# End of tests/managers/test_message_manager.py