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

# End of tests/core/test_signal_bot_service.py