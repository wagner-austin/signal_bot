"""
core/config.py
--------------
Configuration file for the Signal bot.
Loads configuration settings from environment variables with default values.
"""

import os

# Bot phone number in E.164 format, defaulting to a specified value.
BOT_NUMBER: str = os.environ.get("BOT_NUMBER", "REDACTED_PHONE_NUMBER")

# Polling interval in seconds for checking incoming messages.
# Reduced default to 1 second for improved responsiveness.
POLLING_INTERVAL: int = int(os.environ.get("POLLING_INTERVAL", "1"))

# Signal CLI command to use (e.g., 'signal-cli.bat' for Windows).
SIGNAL_CLI_COMMAND: str = os.environ.get("SIGNAL_CLI_COMMAND", "signal-cli.bat")

# Enable or disable direct reply quoting feature.
# Accepts values like "true", "1", or "yes" (case-insensitive) as True.
DIRECT_REPLY_ENABLED: bool = os.environ.get("DIRECT_REPLY_ENABLED", "True").lower() in ("true", "1", "yes")
