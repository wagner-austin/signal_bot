"""
plugins/commands/theme.py - Theme management command plugins.
Subcommands:
  theme      : default - Display the current theme.
  plan theme : default - Walk through adding the theme for this week.
USAGE: See respective USAGE constants.
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from parsers.plugin_arg_parser import PluginArgError
from core.plugin_usage import USAGE_THEME, USAGE_PLAN_THEME

logger = logging.getLogger(__name__)

@plugin(commands=['theme'], canonical='theme')
def theme_command(args: str, sender: str, state_machine: BotStateMachine,
                  msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/theme.py - Theme display command.
    Subcommands:
      default : Display the current theme.
    USAGE: {USAGE_THEME}
    """
    if args.strip() and args.strip().lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_THEME}"
    try:
        if args.strip():
            raise PluginArgError(USAGE_THEME)
        return "This week's theme is: [Insert theme here]."
    except PluginArgError as e:
        logger.warning(f"theme_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"theme_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in theme_command."

@plugin(commands=['plan theme'], canonical='plan theme')
def plan_theme_command(args: str, sender: str, state_machine: BotStateMachine,
                       msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/theme.py - Theme planning command.
    Subcommands:
      default : Walk through adding the theme.
    USAGE: {USAGE_PLAN_THEME}
    """
    if args.strip() and args.strip().lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_PLAN_THEME}"
    try:
        if args.strip():
            raise PluginArgError(USAGE_PLAN_THEME)
        return "Plan Theme: Feature under development. Follow the prompts to set this week's theme."
    except PluginArgError as e:
        logger.warning(f"plan_theme_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"plan_theme_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in plan_theme_command."

# End of plugins/commands/theme.py