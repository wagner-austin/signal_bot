#!/usr/bin/env python
"""
tests/core/test_signal_bot_service.py - Tests for the SignalBotService run loop.
Simulates a short run loop using a custom state machine and bypasses sleep delays for faster tests.
Now includes a scenario where multiple messages arrive before a delayed shutdown message.
"""

import asyncio
import pytest
from core.signal_bot_service import SignalBotService
from core.state import BotState, BotStateMachine

# A simple function to bypass actual sleeps in tests
async def fast_sleep(_duration):
    return

@pytest.mark.asyncio
async def test_signal_bot_service_run(monkeypatch):
    """
    Test that the service runs for a small number of iterations (mock no incoming messages),
    then we force the state machine to shut down.
    """
    call_count = 0

    async def dummy_receive_messages(logger=None):
        nonlocal call_count
        call_count += 1
        # No messages; after a few polls we artificially end
        return []

    # Use an async no-op for signal_cli to avoid 'object str can't be used in await'
    async def dummy_async_run_signal_cli(*args, **kwargs):
        return ""

    monkeypatch.setattr("core.signal_client.receive_messages", dummy_receive_messages)
    monkeypatch.setattr("core.signal_client.async_run_signal_cli", dummy_async_run_signal_cli)
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)

    class DummyShortStateMachine(BotStateMachine):
        def __init__(self, iterations):
            super().__init__()
            self.iterations = iterations
        def should_continue(self) -> bool:
            if self.iterations <= 0:
                self.shutdown()
            else:
                self.iterations -= 1
            return super().should_continue()

    dummy_state_machine = DummyShortStateMachine(iterations=3)
    service = SignalBotService(state_machine=dummy_state_machine)
    await service.run()
    assert dummy_state_machine.current_state == BotState.SHUTTING_DOWN

@pytest.mark.asyncio
async def test_signal_bot_service_run_shutdown_command(monkeypatch):
    """
    Test that sending a single '@bot shutdown' message causes the bot to transition
    to SHUTTING_DOWN and exit the run loop.
    """
    messages_list = [
        "Envelope\nfrom: +1111111111\nBody: @bot shutdown\nTimestamp: 1666666666\n"
    ]

    async def dummy_receive_messages(logger=None):
        if messages_list:
            return [messages_list.pop(0)]
        return []

    # Again, must be async function returning a string
    async def dummy_async_run_signal_cli(*args, **kwargs):
        return ""

    monkeypatch.setattr("core.signal_client.receive_messages", dummy_receive_messages)
    monkeypatch.setattr("core.signal_client.async_run_signal_cli", dummy_async_run_signal_cli)
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)

    state_machine = BotStateMachine()
    service = SignalBotService(state_machine=state_machine)
    await service.run()
    assert state_machine.current_state == BotState.SHUTTING_DOWN

@pytest.mark.asyncio
async def test_signal_bot_service_run_shutdown_no_extraneous_polls(monkeypatch):
    """
    Test that after receiving '@bot shutdown', the bot transitions to SHUTTING_DOWN
    and does NOT poll again. We track how many times receive_messages is called
    and expect exactly 1 call.
    """
    call_count = 0

    async def dummy_receive_messages(logger=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return ["Envelope\nfrom: +2222222222\nBody: @bot shutdown\nTimestamp: 1777777777\n"]
        # Should never reach here if the bot stops after shutdown
        return []

    async def dummy_async_run_signal_cli(*args, **kwargs):
        return ""

    monkeypatch.setattr("core.signal_client.receive_messages", dummy_receive_messages)
    monkeypatch.setattr("core.signal_client.async_run_signal_cli", dummy_async_run_signal_cli)
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)

    state_machine = BotStateMachine()
    service = SignalBotService(state_machine=state_machine)
    await service.run()

    assert call_count == 1, f"Expected 1 poll, got {call_count}."
    assert state_machine.current_state == BotState.SHUTTING_DOWN

# --------------------------------------------------------------------------------
# NEW TEST: Graceful shutdown with multiple backlog messages
# --------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_signal_bot_service_run_shutdown_with_backlog(monkeypatch):
    """
    Test that if multiple messages arrive before the shutdown message, the bot processes
    them all, then handles the shutdown message and stops.
    """
    messages_list = [
        # Three normal messages
        "Envelope\nfrom: +1111111111\nBody: Hello 1\nTimestamp: 1111\n",
        "Envelope\nfrom: +1111111112\nBody: Hello 2\nTimestamp: 2222\n",
        "Envelope\nfrom: +1111111113\nBody: Hello 3\nTimestamp: 3333\n",
        # Shutdown arrives last
        "Envelope\nfrom: +9999999999\nBody: @bot shutdown\nTimestamp: 4444\n"
    ]

    async def dummy_receive_messages(logger=None):
        # Return 1 message at a time from messages_list
        if messages_list:
            return [messages_list.pop(0)]
        return []

    async def dummy_async_run_signal_cli(*args, **kwargs):
        return ""

    monkeypatch.setattr("core.signal_client.receive_messages", dummy_receive_messages)
    monkeypatch.setattr("core.signal_client.async_run_signal_cli", dummy_async_run_signal_cli)
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)

    state_machine = BotStateMachine()
    service = SignalBotService(state_machine=state_machine)
    await service.run()

    # Once we see the final '@bot shutdown', the service should stop,
    # ensuring it has processed the earlier messages as well.
    assert state_machine.current_state == BotState.SHUTTING_DOWN, "Bot should be shutting down after the last message."

# End of tests/core/test_signal_bot_service.py