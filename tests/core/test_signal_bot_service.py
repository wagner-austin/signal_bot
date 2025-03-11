#!/usr/bin/env python
"""
tests/core/test_signal_bot_service.py - Tests for the SignalBotService run loop and edge cases.
Includes tests for normal operation, forced shutdown, idle loop behavior, group chat command filtering,
mixed batch processing of valid/invalid messages, and empty group messages with zero arguments.
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

    assert state_machine.current_state == BotState.SHUTTING_DOWN, "Bot should be shutting down after the last message."

# --------------------------------------------------------------------------------
# NEW TEST: Prolonged Idle Loop
# --------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_signal_bot_service_idle_loop(monkeypatch):
    """
    Test for prolonged idle loop.
    Simulate a scenario where process_incoming always returns 0 messages for multiple iterations.
    Confirm that the bot sleeps for POLLING_INTERVAL on each iteration and does not exit prematurely.
    """
    sleep_durations = []

    async def dummy_sleep(duration):
        sleep_durations.append(duration)

    async def dummy_receive_messages(logger=None):
        return []

    async def dummy_async_run_signal_cli(*args, **kwargs):
        return ""

    monkeypatch.setattr("core.signal_client.receive_messages", dummy_receive_messages)
    monkeypatch.setattr("core.signal_client.async_run_signal_cli", dummy_async_run_signal_cli)
    monkeypatch.setattr(asyncio, "sleep", dummy_sleep)

    # Define a dummy state machine that will run for 5 iterations
    class DummyIdleStateMachine(BotStateMachine):
        def __init__(self, iterations):
            super().__init__()
            self.iterations = iterations
        def should_continue(self) -> bool:
            if self.iterations <= 0:
                self.shutdown()
            else:
                self.iterations -= 1
            return super().should_continue()

    dummy_state_machine = DummyIdleStateMachine(iterations=5)
    service = SignalBotService(state_machine=dummy_state_machine)
    await service.run()

    from core.config import POLLING_INTERVAL
    # There should be 5 sleep calls, each with POLLING_INTERVAL since no messages processed.
    assert len(sleep_durations) == 5, f"Expected 5 sleep calls, got {len(sleep_durations)}"
    for duration in sleep_durations:
        assert duration == POLLING_INTERVAL, f"Expected sleep duration {POLLING_INTERVAL}, got {duration}"
    assert dummy_state_machine.current_state == BotState.SHUTTING_DOWN

# --------------------------------------------------------------------------------
# NEW TEST: Group Chat Partial Command
# --------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_signal_bot_service_group_chat_partial_command(monkeypatch):
    """
    Test for group chat partial command.
    Simulate an incoming group message missing the '@bot' prefix and confirm it is ignored.
    """
    messages_list = [
        "Dummy message text to be replaced by dummy parser"
    ]

    async def dummy_receive_messages(logger=None):
        if messages_list:
            return [messages_list.pop(0)]
        return []

    send_call_count = [0]
    async def dummy_async_run_signal_cli(args, stdin_input=None):
        # Distinguish between 'receive' and 'send' commands
        if args and args[0] != 'receive':
            send_call_count[0] += 1
        return ""

    monkeypatch.setattr("core.signal_client.receive_messages", dummy_receive_messages)
    monkeypatch.setattr("core.signal_client.async_run_signal_cli", dummy_async_run_signal_cli)
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)

    # Monkey-patch the parser to return a dummy parsed message that reflects a group chat message.
    def dummy_parse_message(_message):
        class DummyParsed:
            sender = "+1111111111"
            body = "Hello group"  # missing the '@bot' prefix
            timestamp = "5555"
            group_id = "group123"
        return DummyParsed()
    monkeypatch.setattr("parsers.message_parser.parse_message", dummy_parse_message)

    # Monkey-patch MessageManager.process_message to simulate ignoring group messages without '@bot'
    from managers.message_manager import MessageManager
    def dummy_process_message(self, parsed, sender, pending_actions, volunteer_manager, msg_timestamp=None):
        # If in group chat and body does not contain '@bot', ignore the message.
        if getattr(parsed, 'group_id', None) and '@bot' not in parsed.body:
            return ""
        return "response"
    monkeypatch.setattr(MessageManager, "process_message", dummy_process_message)

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

    dummy_state_machine = DummyShortStateMachine(iterations=1)
    service = SignalBotService(state_machine=dummy_state_machine)
    await service.run()

    assert send_call_count[0] == 0, f"Expected 0 send calls, got {send_call_count[0]}"
    assert dummy_state_machine.current_state == BotState.SHUTTING_DOWN

# --------------------------------------------------------------------------------
# NEW TEST: Mixed Batch of Envelopes
# --------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_signal_bot_service_mixed_messages(monkeypatch):
    """
    Test for mixed batch of envelopes.
    Simulate a batch with:
      - Valid private message.
      - Message missing Body.
      - Message missing sender.
      - Group message without '@bot' prefix.
      - Valid shutdown message.
    Confirm that the bot processes valid messages and ignores invalid ones.
    """
    messages_list = [
        "Envelope\nfrom: +1234567890\nBody: @bot echo Hello\nTimestamp: 1000\n",
        "Envelope\nfrom: +1234567891\nTimestamp: 1001\n",  # missing Body
        "Envelope\nBody: @bot echo Missing sender\nTimestamp: 1002\n",  # missing from
        "Envelope\nfrom: +1234567892\nBody: Hello group\nTimestamp: 1003\nGroup info: groupXYZ\n",  # group without '@bot'
        "Envelope\nfrom: +1234567893\nBody: @bot shutdown\nTimestamp: 1004\n"
    ]
    poll_count = 0

    async def dummy_receive_messages(logger=None):
        nonlocal poll_count
        poll_count += 1
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

    # Expect poll_count to be equal to number of messages processed (5)
    assert poll_count == 5, f"Expected 5 polls, got {poll_count}"
    assert state_machine.current_state == BotState.SHUTTING_DOWN

# --------------------------------------------------------------------------------
# NEW TEST: Empty Group Message with @bot but Zero Arguments
# --------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_signal_bot_service_empty_group_message(monkeypatch):
    """
    Test for an empty group message with @bot present but zero arguments.
    Simulate a group message with Body '@bot' and ensure it is gracefully processed (ignored/no response).
    """
    messages_list = [
        "Envelope\nfrom: +1111111111\nBody: @bot\nTimestamp: 5555\nGroup info: group123\n"
    ]
    poll_count = 0
    async def dummy_receive_messages(logger=None):
        nonlocal poll_count
        poll_count += 1
        if messages_list:
            return [messages_list.pop(0)]
        return []
    send_call_count = [0]
    async def dummy_async_run_signal_cli(args, stdin_input=None):
        if args and args[0] != 'receive':
            send_call_count[0] += 1
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

    dummy_state_machine = DummyShortStateMachine(iterations=1)
    service = SignalBotService(state_machine=dummy_state_machine)
    await service.run()

    assert send_call_count[0] == 0, f"Expected 0 send calls, got {send_call_count[0]}"
    from core.state import BotState
    assert dummy_state_machine.current_state == BotState.SHUTTING_DOWN

# End of tests/core/test_signal_bot_service.py