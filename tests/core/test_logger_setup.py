"""
tests/core/test_logger_setup.py - Tests for the logging setup in core/logger_setup.py.
Verifies that calling setup_logging() correctly configures the root logger.
"""

import logging
import pytest
from core.logger_setup import setup_logging

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

# End of tests/core/test_logger_setup.py