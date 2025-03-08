#!/usr/bin/env python
"""
tests/core/test_signal_bot_service.py - Tests for the SignalBotService run loop.
Simulates a short run loop using a custom state machine and bypasses sleep delays for faster tests.
"""

import asyncio
import pytest
from core.signal_bot_service import SignalBotService
from core.state import BotState, BotStateMachine

class DummyStateMachine(BotStateMachine):
    def __init__(self, iterations):
        super().__init__()
        self.iterations = iterations

    def should_continue(self) -> bool:
        if self.iterations <= 0:
            self.shutdown()
        else:
            self.iterations -= 1
        return super().should_continue()

async def fake_process_incoming(state_machine):
    # Simulate processing messages by always returning 0
    return 0

# Define a fast sleep function to bypass actual delays.
async def fast_sleep(_duration):
    return

@pytest.mark.asyncio
async def test_signal_bot_service_run(monkeypatch):
    # Bypass sleep delays in the service run loop.
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)
    # Patch the process_incoming function where it is used in SignalBotService
    monkeypatch.setattr("core.signal_bot_service.process_incoming", fake_process_incoming)
    dummy_state_machine = DummyStateMachine(iterations=3)
    service = SignalBotService(state_machine=dummy_state_machine)
    # Run the service; it should finish almost instantly.
    await service.run()
    # After run, the state should be SHUTTING_DOWN.
    assert dummy_state_machine.current_state == BotState.SHUTTING_DOWN


@pytest.mark.asyncio
async def test_signal_bot_service_run_shutdown_command(monkeypatch):
    """
    Test that sending a single '@bot shutdown' message causes the bot to transition
    to SHUTTING_DOWN and exit the run loop.
    """
    # We'll override receive_messages to simulate a single shutdown message, then no more.
    messages_list = [
        "Envelope\nfrom: +1111111111\nBody: @bot shutdown\nTimestamp: 1666666666\n"
    ]

    async def dummy_receive_messages(logger=None):
        if messages_list:
            return [messages_list.pop(0)]
        return []

    # Also override asyncio.sleep so the loop doesn't block.
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)

    # Patch out the real async_run_signal_cli to avoid calling signal-cli.bat
    async def dummy_run_signal_cli(args, stdin_input=None):
        # Return a mock success response
        return ""

    monkeypatch.setattr("core.signal_client.async_run_signal_cli", dummy_run_signal_cli)
    monkeypatch.setattr("core.signal_client.receive_messages", dummy_receive_messages)

    state_machine = BotStateMachine()
    service = SignalBotService(state_machine=state_machine)

    # Running the service should process our single shutdown command and then stop.
    await service.run()

    # Confirm the state is SHUTTING_DOWN.
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
        # On the first call, simulate a shutdown message.
        if call_count == 1:
            return [
                "Envelope\nfrom: +2222222222\nBody: @bot shutdown\nTimestamp: 1777777777\n"
            ]
        # If we ever get here, it's a failure: the loop shouldn't poll a second time.
        return ["ShouldNeverHappen"]

    # Override sleeps so the test doesn't block.
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)
    # Patch out signal-cli calls.
    async def dummy_run_signal_cli(args, stdin_input=None):
        return ""
    monkeypatch.setattr("core.signal_client.async_run_signal_cli", dummy_run_signal_cli)
    # Patch to use our dummy message reception.
    monkeypatch.setattr("core.signal_client.receive_messages", dummy_receive_messages)

    state_machine = BotStateMachine()
    service = SignalBotService(state_machine=state_machine)

    await service.run()

    # Confirm we only polled once, then stopped.
    assert call_count == 1, (
        f"Expected receive_messages to be called once, but got {call_count} calls."
    )
    assert state_machine.current_state == BotState.SHUTTING_DOWN, (
        "The state machine should be in SHUTTING_DOWN after handling '@bot shutdown'."
    )

# End of tests/core/test_signal_bot_service.py