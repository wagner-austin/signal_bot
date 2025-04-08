"""
plugins/constants.py - Contains common constants used throughout the Signal bot.
This module centralizes repeated constants to facilitate future updates.
"""

SKIP_VALUES = {"skip", "s", "no", "n", "quit", "q", "no thank you", "unsubscribe", "help", "stop", "cancel", ""}
ALLOWED_CLI_FLAGS = {
    "send", "-g", "--quote-author", "--quote-timestamp", "--quote-message", "--message-from-stdin",
    "receive", "--attachment"
}
DANGEROUS_PATTERN = r'[;&|`]'

# End of plugins/constants.py