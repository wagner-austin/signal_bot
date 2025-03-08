#!/usr/bin/env python
"""
test_config.py - Tests for core/config.py.
Verifies environment variables for BOT_NUMBER and SIGNAL_CLI_COMMAND, ensuring default values
are used when unset and that overrides are applied when set. Also checks backup interval and retention.
"""

import os
import importlib
import pytest
import core.config as config
from unittest.mock import patch

@pytest.mark.usefixtures("clear_database_tables")  # If needed in your environment
class TestCoreConfig:
    """
    TestCoreConfig - Grouped tests for verifying environment variable fallback and overrides.
    """

    @patch.dict(os.environ, {}, clear=True)
    @patch("dotenv.load_dotenv", lambda *args, **kwargs: None)
    def test_bot_number_default(self):
        """
        Test that BOT_NUMBER defaults to 'YOUR_SIGNAL_NUMBER' if not in environment or .env.
        """
        importlib.reload(config)
        assert isinstance(config.BOT_NUMBER, str)
        assert config.BOT_NUMBER == "YOUR_SIGNAL_NUMBER"

    @patch.dict(os.environ, {}, clear=True)
    @patch("dotenv.load_dotenv", lambda *args, **kwargs: None)
    def test_signal_cli_command_default(self):
        """
        Test that SIGNAL_CLI_COMMAND defaults to 'signal-cli.bat' if not in environment or .env.
        """
        importlib.reload(config)
        assert isinstance(config.SIGNAL_CLI_COMMAND, str)
        assert config.SIGNAL_CLI_COMMAND == "signal-cli.bat"

    @patch("dotenv.load_dotenv", lambda *args, **kwargs: None)
    def test_bot_number_override(self):
        """
        Test that BOT_NUMBER is set to the environment override if present.
        """
        original_value = os.environ.get("BOT_NUMBER", None)
        os.environ["BOT_NUMBER"] = "+19876543210"
        importlib.reload(config)
        assert config.BOT_NUMBER == "+19876543210"
        # Cleanup
        if original_value is None:
            del os.environ["BOT_NUMBER"]
        else:
            os.environ["BOT_NUMBER"] = original_value
        importlib.reload(config)

    @patch("dotenv.load_dotenv", lambda *args, **kwargs: None)
    def test_signal_cli_command_override(self):
        """
        Test that SIGNAL_CLI_COMMAND is set to the environment override if present.
        """
        original_value = os.environ.get("SIGNAL_CLI_COMMAND", None)
        os.environ["SIGNAL_CLI_COMMAND"] = "mysignalcli"
        importlib.reload(config)
        assert config.SIGNAL_CLI_COMMAND == "mysignalcli"
        # Cleanup
        if original_value is None:
            del os.environ["SIGNAL_CLI_COMMAND"]
        else:
            os.environ["SIGNAL_CLI_COMMAND"] = original_value
        importlib.reload(config)

    def test_polling_interval_default(self):
        # Check that POLLING_INTERVAL is an int and is at least 1.
        assert isinstance(config.POLLING_INTERVAL, int)
        assert config.POLLING_INTERVAL >= 1

    def test_backup_interval_and_retention(self):
        # Verify that backup interval and retention count are valid integers.
        assert isinstance(config.BACKUP_INTERVAL, int)
        assert config.BACKUP_INTERVAL > 0
        assert isinstance(config.BACKUP_RETENTION_COUNT, int)
        assert config.BACKUP_RETENTION_COUNT > 0

# End of tests/core/test_config.py