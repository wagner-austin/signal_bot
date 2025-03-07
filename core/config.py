"""
core/config.py - Centralized configuration for the Signal bot.
Loads configuration settings from environment variables with default values.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from the .env file

# Bot phone number in E.164 format, defaulting to a specified value.
BOT_NUMBER: str = os.environ.get("BOT_NUMBER", "REDACTED_PHONE_NUMBER")

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

# End of core/config.py