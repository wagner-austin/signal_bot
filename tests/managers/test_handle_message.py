#!/usr/bin/env python
"""
tests/managers/test_handle_message.py - Tests for the message dispatch functionality.
Verifies that fuzzy matching correctly handles near-miss command inputs.
"""

import pytest
from managers.message.message_dispatcher import dispatch_message as handle_message
from core.state import BotStateMachine
from parsers.message_parser import ParsedMessage
from managers.pending_actions import PendingActions
from managers.volunteer_manager import VOLUNTEER_MANAGER

def make_parsed_message(body: str, sender: str = "+1234567890", group_id: str = None) -> ParsedMessage:
    """
    Creates a minimal ParsedMessage for testing.
    
    Parameters:
        body (str): The message body.
        sender (str): The sender's phone number.
        group_id (str): Optional group id.
    
    Returns:
        ParsedMessage: The created message.
    """
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

def test_handle_message_fuzzy_matching(dummy_plugin):
    """
    Test that a near-miss command ("tset") is fuzzy-matched correctly.
    """
    parsed = make_parsed_message("irrelevant body content", sender="+111")
    state_machine = BotStateMachine()
    pending_actions = PendingActions()
    response = handle_message(parsed, "+111", state_machine, pending_actions, VOLUNTEER_MANAGER, msg_timestamp=123)
    assert response == "yes"

# End of tests/managers/test_handle_message.py