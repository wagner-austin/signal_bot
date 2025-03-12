#!/usr/bin/env python
"""
plugins/commands/theme.py - Theme management command plugins - Provides commands to display and plan the weekly theme.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
import logging

logger = logging.getLogger(__name__)

@plugin(commands=['theme'], canonical='theme')
def theme_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    theme - Displays the important theme for this week.
    Usage: "@bot theme"
    """
    try:
        if args.strip():
            raise PluginArgError("Usage: @bot theme")
        return "This week's theme is: [Insert theme here]."
    except Exception as e:
        # If the error message indicates usage, log as a warning.
        if "Usage:" in str(e):
            logger.warning(f"theme_command usage error: {e}")
            return str(e)
        logger.error(f"theme_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in theme_command."

@plugin(commands=['plan theme'], canonical='plan theme')
def plan_theme_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    plan theme - Walks you through adding the theme for this week or pulls from Google Drive.
    Usage: "@bot plan theme"
    """
    try:
        if args.strip():
            raise PluginArgError("Usage: @bot plan theme")
        # Placeholder; implement interactive steps or integration with Google Drive.
        return "Plan Theme: Feature under development. Follow the prompts to set this week's theme."
    except Exception as e:
        if "Usage:" in str(e):
            logger.warning(f"plan_theme_command usage error: {e}")
            return str(e)
        logger.error(f"plan_theme_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in plan_theme_command."

# End of plugins/commands/theme.py