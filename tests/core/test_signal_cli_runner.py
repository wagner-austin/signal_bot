"""
tests/core/test_signal_cli_runner.py – Tests for signal-cli runner error handling.
Simulates subprocess errors and timeouts to ensure SignalCLIError is raised.
"""

import asyncio
import pytest
from core.signal_cli_runner import async_run_signal_cli, SignalCLIError

@pytest.mark.asyncio
async def test_async_run_signal_cli_nonzero_exit(monkeypatch):
    # Simulate _run_subprocess returning nonzero exit code.
    async def fake_run_subprocess(args, timeout=30, input_data=None):
        return (b"", b"error occurred", 1)
    monkeypatch.setattr("core.signal_cli_runner._run_subprocess", fake_run_subprocess)
    with pytest.raises(SignalCLIError) as excinfo:
        await async_run_signal_cli(["send", "--message-from-stdin"], stdin_input="Test message")
    assert "Nonzero return code" in str(excinfo.value)

@pytest.mark.asyncio
async def test_async_run_signal_cli_timeout(monkeypatch):
    # Simulate _run_subprocess raising a TimeoutError.
    async def fake_run_subprocess(args, timeout=30, input_data=None):
        raise asyncio.TimeoutError("Timeout")
    # Wrap the fake function with the same async error handler used in the module.
    from core.signal_cli_runner import async_error_handler
    decorated_fake = async_error_handler(fake_run_subprocess)
    monkeypatch.setattr("core.signal_cli_runner._run_subprocess", decorated_fake)
    with pytest.raises(SignalCLIError) as excinfo:
        await async_run_signal_cli(["send", "--message-from-stdin"], stdin_input="Test message")
    assert "Async subprocess error" in str(excinfo.value)

# End of tests/core/test_signal_cli_runner.py