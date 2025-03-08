#!/usr/bin/env python
"""
tests/core/test_signal_client.py - Tests for signal client functionalities.
Verifies that send_message constructs CLI flags correctly by asserting directly on the argument list.
Also includes tests for corrupted incoming messages and partial quoting scenarios.
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

# --------------------------------------------------------------------------------
# NEW TEST: Corrupted incoming messages with missing "from:" or "Body:" lines
# --------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_process_incoming_corrupted_messages(monkeypatch):
    """
    Test that process_incoming gracefully handles messages missing 'from:' or 'Body:'.
    Only valid messages (with both sender and body) should be counted.
    """
    # We'll return all queued messages in one go,
    # allowing a single process_incoming call to see them all.
    messages_list = [
        # Missing "from:" line
        "Envelope\nTimestamp: 1234\nBody: Missing from line\n",
        # Missing "Body:" line
        "Envelope\nfrom: +1234567\nTimestamp: 2345\n",
        # A valid message
        "Envelope\nfrom: +9999999999\nBody: valid body\nTimestamp: 3456\n"
    ]

    async def dummy_receive_messages(logger=None):
        # Return all messages at once
        nonlocal messages_list
        to_return = messages_list[:]
        messages_list.clear()
        return to_return

    monkeypatch.setattr(sc, "receive_messages", dummy_receive_messages)

    processed_count = await process_incoming(BotStateMachine())
    # We expect exactly 1 valid message processed
    assert processed_count == 1, f"Expected to process 1 valid message, got {processed_count}"

# --------------------------------------------------------------------------------
# NEW TEST: Partial quoting arguments scenario
# --------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_send_message_partial_quoting(dummy_async_run_signal_cli):
    """
    Test that when some quoting arguments are missing, we skip the quoting flags
    without error.
    """
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

# End of tests/core/test_signal_client.py