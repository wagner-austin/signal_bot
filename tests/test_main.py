#!/usr/bin/env python
"""
tests/test_main.py – Test for main.py: Verifies both --test flag and normal run via subprocess.
"""

import sys
from io import StringIO
import contextlib
import runpy
import pytest
from unittest.mock import patch, AsyncMock
import subprocess
import os

def test_main_test_flag(monkeypatch):
    # Set sys.argv to include --test and capture stdout.
    original_argv = sys.argv
    sys.argv = ["main.py", "--test"]
    with patch("core.signal_bot_service.SignalBotService.run", new=AsyncMock()) as mock_run:
        captured_output = StringIO()
        with contextlib.redirect_stdout(captured_output):
            runpy.run_module("main", run_name="__main__")
        output = captured_output.getvalue()
        assert "Running all tests" in output
        # The bot's .run() method should not be called in --test mode.
        mock_run.assert_not_awaited()
    sys.argv = original_argv

def test_main_no_flags():
    """
    Test running main.py without flags using a subprocess to avoid
    'asyncio.run() cannot be called from a running event loop'.
    Utilizes FAST_EXIT_FOR_TESTS environment variable to force main.py to exit early.
    """
    env = os.environ.copy()
    env["FAST_EXIT_FOR_TESTS"] = "1"
    result = subprocess.run(
        [sys.executable, "main.py"],
        capture_output=True,
        text=True,
        env=env
    )
    # We just verify it doesn't crash with a non-zero exit code:
    assert result.returncode == 0
    # Optionally, confirm no Python traceback was printed:
    assert "Traceback" not in result.stderr

# End of tests/test_main.py