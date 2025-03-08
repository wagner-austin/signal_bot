#!/usr/bin/env python
"""
core/config.py - Centralized configuration for the Signal bot.
Loads configuration settings from environment variables with default values.
"""

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def parse_int_env(value_str: str, default: int, var_name: str) -> int:
    """
    parse_int_env(value_str: str, default: int, var_name: str) -> int
    Safely parse an integer from a string environment variable.

    If parsing fails, logs a warning and returns the provided default.

    Args:
        value_str (str): The string value from environment to parse.
        default (int): Default integer to return if parsing fails.
        var_name (str): Name of the environment variable (for logging).

    Returns:
        int: The parsed integer or the default on error.
    """
    try:
        return int(value_str)
    except (ValueError, TypeError):
        logger.warning(
            f"Invalid integer value for {var_name}: {value_str!r}. "
            f"Using default {default}."
        )
        return default

# Check if .env file exists; if not, log info. Otherwise, load it.
dotenv_path = os.path.join(os.getcwd(), '.env')
if not os.path.exists(dotenv_path):
    logger.info(f"No .env found at {dotenv_path}, skipping environment file load.")
else:
    load_dotenv(dotenv_path)

# Bot phone number in E.164 format, defaulting to a specified value.
BOT_NUMBER: str = os.environ.get("BOT_NUMBER", "YOUR_SIGNAL_NUMBER")

# Polling interval in seconds for checking incoming messages.
POLLING_INTERVAL: int = int(os.environ.get("POLLING_INTERVAL", "1"))

# Signal CLI command to use (e.g., 'signal-cli.bat' for Windows).
SIGNAL_CLI_COMMAND: str = os.environ.get("SIGNAL_CLI_COMMAND", "signal-cli.bat")

# Enable or disable direct reply quoting feature.
DIRECT_REPLY_ENABLED: bool = os.environ.get("DIRECT_REPLY_ENABLED", "True").lower() in ("true", "1", "yes")

# Toggle requirement of the @bot command prefix.
ENABLE_BOT_PREFIX: bool = os.environ.get("ENABLE_BOT_PREFIX", "true").lower() in ("true", "1", "yes")

# Database name for SQLite, defaulting to "bot_data.db" if not set.
DB_NAME: str = os.environ.get("DB_NAME", "bot_data.db")

# Backup interval in seconds (default 3600 seconds = 1 hour),
# safely parse int to handle corrupted or non-numeric values.
BACKUP_INTERVAL: int = parse_int_env(
    os.environ.get("BACKUP_INTERVAL", "3600"),
    3600,
    "BACKUP_INTERVAL"
)

# Number of backup snapshots to retain (default 5),
# safely parse int to handle corrupted or non-numeric values.
BACKUP_RETENTION_COUNT: int = parse_int_env(
    os.environ.get("BACKUP_RETENTION_COUNT", "10"),
    5,
    "BACKUP_RETENTION_COUNT"
)

# End of config.py