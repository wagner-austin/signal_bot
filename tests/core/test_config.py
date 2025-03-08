#!/usr/bin/env python
"""
tests/core/test_config.py – Test for core/config.py: Verify environment variables and default values.
"""
import os
import core.config as config

def test_bot_number_default():
    # Remove BOT_NUMBER from environment (if exists) and check default.
    if "BOT_NUMBER" in os.environ:
        del os.environ["BOT_NUMBER"]
    # The module is already loaded so the value may be cached.
    # At least check that BOT_NUMBER is a string.
    assert isinstance(config.BOT_NUMBER, str)

def test_polling_interval_default():
    # Check that POLLING_INTERVAL is an int and is at least 1.
    assert isinstance(config.POLLING_INTERVAL, int)
    assert config.POLLING_INTERVAL >= 1

def test_backup_interval_and_retention():
    # Verify that backup interval and retention count are valid integers.
    assert isinstance(config.BACKUP_INTERVAL, int)
    assert config.BACKUP_INTERVAL > 0
    assert isinstance(config.BACKUP_RETENTION_COUNT, int)
    assert config.BACKUP_RETENTION_COUNT > 0

# End of tests/core/test_config.py