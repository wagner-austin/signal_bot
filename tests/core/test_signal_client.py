#!/usr/bin/env python
"""
tests/core/test_signal_client.py - Tests for signal client functionalities.
Verifies that send_message constructs CLI flags correctly by asserting directly on the argument list.
"""

import pytest
import asyncio
from core.signal_client import send_message
import core.signal_client as sc

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
    # Assert directly on the list of arguments.
    assert "-g" in calls[0]
    assert "--quote-author" in calls[0]

@pytest.mark.asyncio
async def test_indirect_reply_in_private_chat(dummy_async_run_signal_cli):
    calls = dummy_async_run_signal_cli
    await send_message(
        to_number="+111",
        message="Private message"
    )
    # Assert directly on the list of arguments.
    assert "-g" not in calls[0]
    assert "--quote-author" not in calls[0]

# End of tests/core/test_signal_client.py