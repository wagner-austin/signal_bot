"""
tests/managers/test_handle_message.py – Tests for the handle_message function.
Verifies that fuzzy matching correctly handles near-miss command inputs.
"""

import pytest
from managers.message_handler import handle_message
from core.state import BotStateMachine
from parsers.message_parser import ParsedMessage
from managers.pending_actions import PendingActions
from managers.volunteer_manager import VOLUNTEER_MANAGER

def make_parsed_message(body: str, sender: str = "+1234567890", group_id=None) -> ParsedMessage:
    # Minimal ParsedMessage for testing, including a mistyped command ("tset") and empty args.
    return ParsedMessage(
        sender=sender,
        body=body,
        timestamp=123,
        group_id=group_id,
        reply_to=None,
        message_timestamp=None,
        command="tset",
        args=""
    )

def dummy_test_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp=None) -> str:
    """dummy test command – returns 'yes'."""
    return "yes"

@pytest.fixture(autouse=True)
def register_dummy_plugin(monkeypatch):
    # Inject a dummy plugin for fuzzy matching tests.
    from plugins.manager import plugin_registry
    plugin_registry["test"] = dummy_test_command
    yield
    plugin_registry.pop("test", None)

def test_handle_message_fuzzy_matching():
    # Provide an input command with a small typo ("tset") that should fuzzy-match to "test".
    parsed = make_parsed_message("irrelevant body content", sender="+111")
    state_machine = BotStateMachine()
    pending_actions = PendingActions()
    response = handle_message(parsed, parsed.sender, state_machine, pending_actions, VOLUNTEER_MANAGER, msg_timestamp=123)
    assert response == "yes"

# End of tests/managers/test_handle_message.py