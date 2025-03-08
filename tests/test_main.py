#!/usr/bin/env python
"""
tests/test_main.py – Test for main.py: Verify that the test suite is triggered with the --test flag using runpy.
"""
import sys
from io import StringIO
import contextlib
import runpy

def test_main_test_flag(monkeypatch):
    # Set sys.argv to include --test and capture stdout.
    original_argv = sys.argv
    sys.argv = ["main.py", "--test"]
    captured_output = StringIO()
    with contextlib.redirect_stdout(captured_output):
        # Execute main.py as if it were run as a script.
        runpy.run_module("main", run_name="__main__")
    sys.argv = original_argv
    output = captured_output.getvalue()
    assert "Running all tests" in output

# End of tests/test_main.py