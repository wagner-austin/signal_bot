#!/usr/bin/env python
"""
File: plugins/commands/help.py
------------------------------
Summary: Help command plugin. Lists available commands.

Now only shows commands that the user has permission to use, based on their volunteer role.
Focuses on modular, unified, consistent code that facilitates future updates.
"""

import logging
from typing import Optional
from plugins.manager import plugin, get_all_plugins, disabled_plugins
from core.permissions import has_permission, EVERYONE
from core.state import BotStateMachine
from plugins.abstract import BasePlugin
from plugins.messages import HELP_UNKNOWN_SUBCOMMAND, INTERNAL_ERROR
from managers.volunteer_manager import VOLUNTEER_MANAGER

@plugin(["help"], canonical="help", required_role=EVERYONE) 
class HelpPlugin(BasePlugin):
    """
    Help command plugin.
    Lists available commands, filtered by user role.

    Usage:
      @bot help
    """
    def __init__(self):
        super().__init__(
            "help",
            help_text="List available commands."
        )
        self.logger = logging.getLogger(__name__)

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        usage = "Usage: @bot help"
        user_input = args.strip()

        # If there's extraneous user input, show usage
        if user_input:
            return usage

        try:
            # Determine user's role
            user_record = VOLUNTEER_MANAGER.get_volunteer_record(sender)
            if not user_record:
                user_role = EVERYONE
            else:
                user_role = user_record.get("role", EVERYONE)

            plugins_info = get_all_plugins()
            lines = []

            for canonical, info in sorted(plugins_info.items()):
                help_text = info.get("help_text", "No description")
                required_role = info.get("required_role", "owner")

                # Skip if plugin is disabled
                if canonical in disabled_plugins:
                    lines.append(f"@bot {canonical} (disabled) - {help_text}")
                    continue

                # Skip if not help_visible
                if not info.get("help_visible", True):
                    continue

                # Check user permission for this plugin
                if has_permission(user_role, required_role):
                    lines.append(f"@bot {canonical} - {help_text}")

            return "\n\n".join(lines) if lines else "No commands available."
        except Exception as e:
            self.logger.error(f"Unexpected error in help command: {e}", exc_info=True)
            return INTERNAL_ERROR

# End of plugins/commands/help.py