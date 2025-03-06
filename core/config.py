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
POLLING_INTERVAL: int = int(os.environ.get("POLLING_INTERVAL", "2"))

# Signal CLI command to use (e.g., 'signal-cli.bat' for Windows).
SIGNAL_CLI_COMMAND: str = os.environ.get("SIGNAL_CLI_COMMAND", "signal-cli.bat")

# End of core/config.py
