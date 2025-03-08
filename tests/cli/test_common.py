#!/usr/bin/env python
"""
tests/cli/test_common.py - Unit tests for cli/common.py.
Tests the print_results function with empty and non-empty data.
"""

import io
from cli.common import print_results

def dummy_formatter(record):
    return f"Record: {record}"

def test_print_results_empty(capsys):
    # Test that when data is empty, the empty_message is printed.
    print_results([], dummy_formatter, empty_message="No data found.")
    captured = capsys.readouterr().out
    assert "No data found." in captured

def test_print_results_non_empty(capsys):
    # Test that each record is printed using the provided formatter.
    data = [1, 2, 3]
    print_results(data, dummy_formatter, empty_message="No data found.")
    captured = capsys.readouterr().out
    for item in data:
        assert f"Record: {item}" in captured

# End of tests/cli/test_common.py