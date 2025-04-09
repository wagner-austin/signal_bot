#!/usr/bin/env python
"""
cli/cli_tools.py - CLI Tools for Signal bot.
----------------
Aggregated CLI Tools for the Signal bot, now unified with the plugin system.
Dynamically generates usage help based on the registered plugins.
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

def print_usage():
    """
    Print usage information for the CLI tool, listing commands dynamically from the plugin registry.
    """
    from plugins.manager import get_all_plugins, disabled_plugins
    usage_lines = ["Usage: cli_tools.py <command> [options]", "Available commands:"]
    plugins_info = get_all_plugins()
    # Sort the commands to ensure a consistent order in the usage output.
    for canonical, info in sorted(plugins_info.items()):
        # Only include help-visible commands.
        if not info.get("help_visible", True):
            continue
        if canonical in disabled_plugins:
            command_line = f"  {canonical} (disabled) - {info.get('help_text', 'No description')}"
        else:
            command_line = f"  {canonical} - {info.get('help_text', 'No description')}"
        usage_lines.append(command_line)
    # Always show the static help command option.
    usage_lines.append("  help - Show this help message.")
    print("\n".join(usage_lines))

def main():
    """
    Main entry point for CLI usage. Grabs the first argument as the plugin command,
    the remaining arguments as 'raw_args', and passes them through the MessageManager.
    """
    setup_logging()

    # Load all plugins so that the CLI usage reflects the current commands.
    from plugins.manager import load_plugins
    load_plugins()

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    command = sys.argv[1].lower()
    if command in ['help', '-h', '--help']:
        print_usage()
        sys.exit(0)

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

    # Use the same message manager as the bot does.
    state_machine = BotStateMachine()
    message_manager = MessageManager(state_machine)

    try:
        response = message_manager.process_message(
            parsed,
            sender="cli_user",
            volunteer_manager=VOLUNTEER_MANAGER
        )
        if response and response.strip():
            print(response)
        else:
            # When no valid plugin command is found, show usage help.
            print_usage()
            sys.exit(0)
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