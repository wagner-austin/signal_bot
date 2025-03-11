#!/usr/bin/env python
"""
tests/core/test_signal_client.py - Tests for signal client functionalities.
Verifies that send_message constructs CLI flags correctly by asserting directly on the argument list.
Also includes tests for corrupted incoming messages, partial quoting scenarios, handling invalid group IDs,
and processing messages with partial quoting arguments.
"""

import pytest
import asyncio
from core.signal_client import send_message, process_incoming
import core.signal_client as sc
from core.state import BotStateMachine
from managers.pending_actions import PENDING_ACTIONS
from managers.volunteer_manager import VOLUNTEER_MANAGER

@pytest.fixture
def dummy_async_run_signal_cli(monkeypatch):
    calls = []

    async def dummy_async_run(args, stdin_input=None):
        calls.append(args)
        return "dummy output"

    monkeypatch.setattr(sc, "async_run_signal_cli", dummy_async_run)
    return calls

@pytest.mark.asyncio
async def test_direct_reply_in_group_chat(dummy_async_run_signal_cli):
    calls = dummy_async_run_signal_cli
    await send_message(
        to_number="+111",
        message="Group message",
        group_id="dummyGroupBase64",  # dummy valid base64 string substitute
        reply_quote_author="+222",
        reply_quote_timestamp="123",
        reply_quote_message="original"
    )
    # Assert directly on the list of arguments
    assert "-g" in calls[0]
    assert "--quote-author" in calls[0]

@pytest.mark.asyncio
async def test_indirect_reply_in_private_chat(dummy_async_run_signal_cli):
    calls = dummy_async_run_signal_cli
    await send_message(
        to_number="+111",
        message="Private message"
    )
    # Assert directly on the list of arguments
    assert "-g" not in calls[0]
    assert "--quote-author" not in calls[0]

@pytest.mark.asyncio
async def test_process_incoming_corrupted_messages(monkeypatch):
    """
    Test that process_incoming gracefully handles messages missing 'from:' or 'Body:'.
    Only valid messages (with both sender and body) should be counted.
    """
    messages_list = [
        # Missing "from:" line
        "Envelope\nTimestamp: 1234\nBody: Missing from line\n",
        # Missing "Body:" line
        "Envelope\nfrom: +1234567\nTimestamp: 2345\n",
        # A valid message
        "Envelope\nfrom: +9999999999\nBody: valid body\nTimestamp: 3456\n"
    ]

    async def dummy_receive_messages(logger=None):
        nonlocal messages_list
        to_return = messages_list[:]
        messages_list.clear()
        return to_return

    monkeypatch.setattr(sc, "receive_messages", dummy_receive_messages)

    processed_count = await process_incoming(BotStateMachine())
    # We expect exactly 1 valid message processed
    assert processed_count == 1, f"Expected to process 1 valid message, got {processed_count}"

@pytest.mark.asyncio
async def test_send_message_partial_quoting(dummy_async_run_signal_cli):
    calls = dummy_async_run_signal_cli
    # Provide group_id and some quoting fields, but omit reply_quote_author
    await send_message(
        to_number="+111",
        message="Partial quoting attempt",
        group_id="SomeGroup",
        reply_quote_author=None,
        reply_quote_timestamp="123456789",
        reply_quote_message="some original text"
    )
    # Because reply_quote_author is None, we should NOT see any --quote-* flags.
    invoked_args = calls[0]
    assert "-g" in invoked_args
    assert "--quote-author" not in invoked_args
    assert "--quote-timestamp" not in invoked_args
    assert "--quote-message" not in invoked_args

# New Test: Send message with invalid group_id and partial quoting arguments
@pytest.mark.asyncio
async def test_send_message_invalid_group_id_and_partial_quoting(dummy_async_run_signal_cli):
    calls = dummy_async_run_signal_cli
    # Provide an invalid group_id and partial quoting args: missing reply_quote_author.
    await send_message(
        to_number="+111",
        message="Test message with invalid group",
        group_id="!!invalid_base64!!",
        reply_quote_author=None,
        reply_quote_timestamp="123456789",
        reply_quote_message="original message"
    )
    invoked_args = calls[0]
    # Check that the invalid group_id is present and quoting flags are not added
    assert "!!invalid_base64!!" in invoked_args
    assert "--quote-author" not in invoked_args
    assert "--quote-timestamp" not in invoked_args
    assert "--quote-message" not in invoked_args

# New Test: Test process_incoming with partial quoting arguments in a message context
@pytest.mark.asyncio
async def test_process_incoming_with_partial_quoting(monkeypatch):
    """
    Test process_incoming with a message that includes partial quoting arguments.
    The bot should process the message and handle partial quoting gracefully.
    """
    messages_list = [
        "Envelope\nfrom: +1234567890\nBody: @bot echo Partial quoting test\nTimestamp: 2000\n"
    ]
    
    async def dummy_receive_messages(logger=None):
        nonlocal messages_list
        to_return = messages_list[:]
        messages_list.clear()
        return to_return
    
    monkeypatch.setattr(sc, "receive_messages", dummy_receive_messages)
    
    # Override async_run_signal_cli to simulate a successful send
    async def dummy_async_run_signal_cli(args, stdin_input=None):
        return "dummy output"
    monkeypatch.setattr(sc, "async_run_signal_cli", dummy_async_run_signal_cli)
    
    # Monkey-patch MessageManager.process_message to simulate a response without quoting details
    from managers.message_manager import MessageManager
    original_process_message = MessageManager.process_message
    def dummy_process_message(self, parsed, sender, pending_actions, volunteer_manager, msg_timestamp=None):
        return "Processed message with partial quoting"
    monkeypatch.setattr(MessageManager, "process_message", dummy_process_message)
    
    processed_count = await process_incoming(BotStateMachine())
    # Only one valid message should be processed
    assert processed_count == 1
    
    # Restore original method
    monkeypatch.setattr(MessageManager, "process_message", original_process_message)

@pytest.mark.asyncio
async def test_send_message_partial_quoting_with_missing_reply_fields(dummy_async_run_signal_cli):
    """
    Test that when some quoting arguments are missing (e.g., reply_quote_author is None),
    send_message skips the quoting flags without error.
    """
    calls = dummy_async_run_signal_cli
    await send_message(
        to_number="+111",
        message="Test message with missing reply quoting fields",
        group_id="ValidGroup",
        reply_quote_author=None,
        reply_quote_timestamp="987654321",
        reply_quote_message="partial reply"
    )
    invoked_args = calls[0]
    # Ensure group flag is present but no quoting flags appear due to missing reply_quote_author
    assert "ValidGroup" in invoked_args
    assert "--quote-author" not in invoked_args
    assert "--quote-timestamp" not in invoked_args
    assert "--quote-message" not in invoked_args

# End of tests/core/test_signal_client.py