"""
plugins/commands/system.py - System command plugins.
Subcommands for each command:
  assign         : default - Assign a volunteer.
  test           : default - Test command.
  shutdown       : default - Shut down the bot.
  info           : default - Display bot information.
  weekly update  : default - Display weekly update.
  theme          : default - Display the current theme.
USAGE: See respective USAGE constants in core/plugin_usage.
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.volunteer_manager import VOLUNTEER_MANAGER
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import (
    PluginArgError,
    SystemAssignModel,
    validate_model
)
from core.plugin_usage import USAGE_ASSIGN, USAGE_TEST, USAGE_SHUTDOWN, USAGE_INFO, USAGE_WEEKLY_UPDATE_SYSTEM, USAGE_THEME_SYSTEM

logger = logging.getLogger(__name__)

@plugin('assign', canonical='assign')
def assign_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/system.py - Assign command.
    Subcommands:
      default : Assign a volunteer based on a required skill.
    USAGE: {USAGE_ASSIGN}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_ASSIGN}"
    new_args = tokens[1] if len(tokens) > 1 else ""
    try:
        parsed = parse_plugin_arguments(new_args, mode='positional')
        tokens_parsed = parsed["tokens"]
        if not tokens_parsed:
            raise PluginArgError(USAGE_ASSIGN)
        data = {"skill": " ".join(tokens_parsed)}
        validated = validate_model(data, SystemAssignModel, USAGE_ASSIGN)
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
def plugin_test_command(args: str, sender: str, state_machine: BotStateMachine,
                        msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/system.py - Test command.
    Subcommands:
      default : Test bot response.
    USAGE: {USAGE_TEST}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_TEST}"
    new_args = tokens[1] if len(tokens) > 1 else ""
    try:
        parsed = parse_plugin_arguments(new_args, mode='positional')
        tokens_parsed = parsed["tokens"]
        if tokens_parsed:
            raise PluginArgError(USAGE_TEST)
        return "yes"
    except PluginArgError as e:
        logger.warning(f"plugin_test_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"plugin_test_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in plugin_test_command."

@plugin('shutdown', canonical='shutdown')
def shutdown_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/system.py - Shutdown command.
    Subcommands:
      default : Shut down the bot gracefully.
    USAGE: {USAGE_SHUTDOWN}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_SHUTDOWN}"
    new_args = tokens[1] if len(tokens) > 1 else ""
    try:
        parsed = parse_plugin_arguments(new_args, mode='positional')
        tokens_parsed = parsed["tokens"]
        if tokens_parsed:
            raise PluginArgError(USAGE_SHUTDOWN)
        state_machine.shutdown()
        return "Bot is shutting down."
    except PluginArgError as e:
        logger.warning(f"shutdown_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"shutdown_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in shutdown_command."

@plugin('info', canonical='info')
def info_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/system.py - Info command.
    Subcommands:
      default : Display bot information.
    USAGE: {USAGE_INFO}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_INFO}"
    new_args = tokens[1] if len(tokens) > 1 else ""
    try:
        parsed = parse_plugin_arguments(new_args, mode='positional')
        tokens_parsed = parsed["tokens"]
        if tokens_parsed:
            raise PluginArgError(USAGE_INFO)
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
def weekly_update_command(args: str, sender: str, state_machine: BotStateMachine,
                          msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/system.py - Weekly update command.
    Subcommands:
      default : Display weekly update.
    USAGE: {USAGE_WEEKLY_UPDATE_SYSTEM}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_WEEKLY_UPDATE_SYSTEM}"
    new_args = tokens[1] if len(tokens) > 1 else ""
    try:
        parsed = parse_plugin_arguments(new_args, mode='positional')
        tokens_parsed = parsed["tokens"]
        if tokens_parsed:
            raise PluginArgError(USAGE_WEEKLY_UPDATE_SYSTEM)
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
def theme_command(args: str, sender: str, state_machine: BotStateMachine,
                  msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/system.py - Theme command.
    Subcommands:
      default : Display the current theme.
    USAGE: {USAGE_THEME_SYSTEM}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_THEME_SYSTEM}"
    new_args = tokens[1] if len(tokens) > 1 else ""
    try:
        parsed = parse_plugin_arguments(new_args, mode='positional')
        tokens_parsed = parsed["tokens"]
        if tokens_parsed:
            raise PluginArgError(USAGE_THEME_SYSTEM)
        return "This week's theme is: [Insert theme here]."
    except PluginArgError as e:
        logger.warning(f"theme_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"theme_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in theme_command."

# End of plugins/commands/system.py