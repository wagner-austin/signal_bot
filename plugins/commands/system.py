#!/usr/bin/env python
"""
plugins/commands/system.py - System command plugins - Provides system-level commands such as assign, test, shutdown, info, weekly update, and theme.
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.volunteer_manager import VOLUNTEER_MANAGER
from core.metrics import get_uptime
import core.metrics
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import (
    PluginArgError,
    SystemAssignModel,
    validate_model
)

logger = logging.getLogger(__name__)

@plugin('assign', canonical='assign')
def assign_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    assign - Assign a volunteer based on a required skill.
    Usage: "@bot assign <Skill Name>"
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if not tokens:
            raise PluginArgError("Usage: @bot assign <Skill Name>")
        data = {"skill": " ".join(tokens)}
        validated = validate_model(data, SystemAssignModel, "assign <Skill Name>")
        volunteer = VOLUNTEER_MANAGER.assign_volunteer(validated.skill, validated.skill)
        if volunteer:
            return f"{validated.skill} assigned to {volunteer}."
        return f"No available volunteer for {validated.skill}."
    except PluginArgError as e:
        logger.warning(f"assign_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"assign_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in assign_command."

@plugin('test', canonical='test')
def plugin_test_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    test - Test command for verifying bot response.
    Usage: "@bot test"
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if tokens:
            raise PluginArgError("Usage: @bot test")
        return "yes"
    except PluginArgError as e:
        logger.warning(f"plugin_test_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"plugin_test_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in plugin_test_command."

@plugin('shutdown', canonical='shutdown')
def shutdown_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    shutdown - Shut down the bot gracefully.
    If extra arguments are provided, usage error.
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if tokens:
            raise PluginArgError("Usage: @bot shutdown")
        state_machine.shutdown()
        return "Bot is shutting down."
    except PluginArgError as e:
        logger.warning(f"shutdown_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"shutdown_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in shutdown_command."

@plugin('info', canonical='info')
def info_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    info - Provides a brief overview of the 50501 OC Grassroots Movement.
    Usage: "@bot info"
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if tokens:
            raise PluginArgError("Usage: @bot info")
        return (
            "50501 OC Grassroots Movement is dedicated to upholding the Constitution "
            "and ending executive overreach.\n\n"
            "We empower citizens to reclaim democracy and hold power accountable "
            "through peaceful, visible, and sustained engagement."
        )
    except PluginArgError as e:
        logger.warning(f"info_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"info_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in info_command."

@plugin('weekly update', canonical='weekly update')
def weekly_update_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    weekly update - Provides a summary of Trump's actions and Democrat advances this week.
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if tokens:
            raise PluginArgError("Usage: @bot weekly update")
        return (
            "Weekly Update:\n\n"
            "Trump Actions:\n - Held rallies, executive orders.\n\n"
            "Democrat Advances:\n - Pushed key legislation, local election wins.\n"
        )
    except PluginArgError as e:
        logger.warning(f"weekly_update_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"weekly_update_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in weekly_update_command."

@plugin('theme', canonical='theme')
def theme_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    theme - Displays the important theme for this week.
    Usage: "@bot theme"
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if tokens:
            raise PluginArgError("Usage: @bot theme")
        return "This week's theme is: [Insert theme here]."
    except PluginArgError as e:
        logger.warning(f"theme_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"theme_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in theme_command."

# End of plugins/commands/system.py