#!/usr/bin/env python
"""
tests/core/test_logger_setup.py - Unit tests for logger setup.
Tests default configuration, overrides, output formatting, and merge_dicts functionality including edge cases.
"""

import logging
import pytest
import re
import warnings
from core.logger_setup import setup_logging, merge_dicts

@pytest.fixture(autouse=True)
def reset_logging():
    # Reset logging configuration before each test.
    logging.root.handlers = []
    yield
    logging.root.handlers = []

def test_setup_logging_defaults():
    setup_logging()
    root_logger = logging.getLogger()
    # Check that at least one handler is attached.
    assert len(root_logger.handlers) > 0
    # Check that the default level is INFO.
    assert root_logger.level == logging.INFO

def test_setup_logging_with_override():
    override_config = {
        "root": {
            "level": "DEBUG",
        }
    }
    setup_logging(override_config)
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG

def test_logging_output_format(capsys):
    # Test that logging output matches the expected format.
    setup_logging()
    logger = logging.getLogger("test_logger")
    logger.info("Test message")
    # Capture output from stderr since StreamHandler defaults to sys.stderr.
    captured = capsys.readouterr()
    # Expect the output to contain the log level "INFO" and our message.
    assert "INFO" in captured.err
    assert "Test message" in captured.err

def test_custom_formatter_override(capsys):
    """
    test_custom_formatter_override - Verifies that custom formatter overrides produce expected output.
    """
    custom_config = {
        "formatters": {
            "default": {
                "format": "CUSTOM: %(message)s"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }
    setup_logging(custom_config)
    logger = logging.getLogger("custom_test_logger")
    logger.info("My custom message")
    captured = capsys.readouterr()
    # The expected output should match exactly (allowing for a newline).
    expected_output = "CUSTOM: My custom message"
    # Remove trailing newline and any surrounding whitespace.
    assert captured.err.strip() == expected_output

def test_merge_dicts():
    base = {"a": 1, "b": {"c": 2}}
    overrides = {"b": {"d": 3}, "e": 4}
    merged = merge_dicts(base.copy(), overrides)
    expected = {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}
    assert merged == expected

def test_merge_dicts_type_mismatch():
    base = {"a": 1, "b": {"c": 2}}
    overrides = {"b": "not a dict", "d": {"e": 5}}
    with pytest.warns(UserWarning, match="Type mismatch for key 'b'"):
        merged = merge_dicts(base.copy(), overrides)
    expected = {"a": 1, "b": "not a dict", "d": {"e": 5}}
    assert merged == expected

def test_setup_logging_no_handlers(capsys):
    # Override config to have empty handlers and root handlers.
    override_config = {
        "handlers": {},
        "root": {"handlers": []}
    }
    with pytest.warns(UserWarning, match="Logging configuration missing handlers"):
        setup_logging(override_config)
    root_logger = logging.getLogger()
    # Check that fallback console handler is used by ensuring there's at least one handler.
    assert len(root_logger.handlers) > 0
    logger = logging.getLogger("fallback_test")
    logger.info("Fallback test message")
    captured = capsys.readouterr()
    assert "Fallback test message" in captured.err

# End of tests/core/test_logger_setup.py