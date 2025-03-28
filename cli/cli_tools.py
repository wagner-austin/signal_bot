# File: cli/cli_tools.py
#!/usr/bin/env python
"""
cli/cli_tools.py
----------------
Aggregated CLI Tools for the Signal bot, now unified with the plugin system.
Parses sys.argv for a command and its arguments, then simulates a message
through the same plugin dispatch mechanism the bot uses.
"""

import sys
import logging

from core.logger_setup import setup_logging
from core.state import BotStateMachine
from managers.message_manager import MessageManager
from managers.volunteer_manager import VOLUNTEER_MANAGER
from parsers.message_parser import ParsedMessage
from core.exceptions import VolunteerError

logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for CLI usage. Grabs the first argument as the plugin command,
    the remaining arguments as 'raw_args', and passes them through the MessageManager.
    """
    setup_logging()

    if len(sys.argv) < 2:
        print("No command provided. Try 'help' for available commands.")
        sys.exit(0)

    command = sys.argv[1]
    raw_args = " ".join(sys.argv[2:])

    # Create a pseudo message to dispatch via the plugin system:
    parsed = ParsedMessage(
        sender="cli_user",
        body=raw_args,
        timestamp=None,
        group_id=None,
        reply_to=None,
        message_timestamp=None,
        command=command,
        args=raw_args
    )

    # Use the same message manager as the bot does
    state_machine = BotStateMachine()
    message_manager = MessageManager(state_machine)

    try:
        response = message_manager.process_message(
            parsed,
            sender="cli_user",
            volunteer_manager=VOLUNTEER_MANAGER
        )
        if response:
            print(response)
    except VolunteerError as ve:
        logger.error(f"CLI volunteer error: {ve}")
        print(f"Error: {ve}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in CLI: {e}", exc_info=True)
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# End of cli/cli_tools.py