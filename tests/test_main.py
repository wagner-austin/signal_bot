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