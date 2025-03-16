"""
plugins/commands/plugin.py - Plugin management command plugin.
Provides subcommands for listing, enabling, and disabling plugins.
Usage:
  @bot plugin list
  @bot plugin enable <plugin_name>
  @bot plugin disable <plugin_name>
"""

import logging
from typing import Optional, List
from plugins.manager import plugin, get_all_plugins, enable_plugin, disable_plugin, disabled_plugins
from core.state import BotStateMachine
from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError
from plugins.abstract import BasePlugin

logger = logging.getLogger(__name__)

@plugin(commands=['plugin'], canonical='plugin')
class PluginManagerCommand(BasePlugin):
    """
    Manage plugins at runtime with subcommands: list, enable, disable.
    Usage:
      @bot plugin list
      @bot plugin enable <plugin_name>
      @bot plugin disable <plugin_name>
    """
    def __init__(self):
        super().__init__(
            "plugin",
            help_text=(
                "Manage plugins at runtime.\n\n"
                "Usage:\n"
                "  @bot plugin list\n"
                "  @bot plugin enable <plugin_name>\n"
                "  @bot plugin disable <plugin_name>"
            )
        )
        self.logger = logging.getLogger(__name__)
        self.subcommands = {
            "list": self._sub_list,
            "enable": self._sub_enable,
            "disable": self._sub_disable
        }

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        usage = (
            "Usage: @bot plugin <list|enable|disable> [args]\n"
            "Examples:\n"
            "  @bot plugin list\n"
            "  @bot plugin enable <plugin_name>\n"
            "  @bot plugin disable <plugin_name>"
        )
        try:
            return handle_subcommands(
                args,
                subcommands=self.subcommands,
                usage_msg=usage,
                unknown_subcmd_msg="Unknown subcommand. See usage: " + usage,
                default_subcommand="default"
            )
        except PluginArgError as e:
            self.logger.error(f"Argument parsing error in plugin command: {e}", exc_info=True)
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error in plugin command: {e}", exc_info=True)
            return "An internal error occurred."

    def _sub_list(self, rest: List[str]) -> str:
        info = get_all_plugins()
        if not info:
            return "No plugins found."
        lines = []
        for canonical, pdata in sorted(info.items()):
            if canonical in disabled_plugins:
                lines.append(f"{canonical} (disabled)")
            else:
                lines.append(f"{canonical}")
        return "Installed Plugins:\n" + "\n".join(lines)

    def _sub_enable(self, rest: List[str]) -> str:
        if not rest:
            return "Usage: @bot plugin enable <plugin_name>"
        target = rest[0].lower()
        plugins_dict = get_all_plugins()
        if target not in plugins_dict:
            return f"No plugin found with canonical name '{target}'."
        enable_plugin(target)
        return f"Plugin '{target}' has been enabled."

    def _sub_disable(self, rest: List[str]) -> str:
        if not rest:
            return "Usage: @bot plugin disable <plugin_name>"
        target = rest[0].lower()
        plugins_dict = get_all_plugins()
        if target not in plugins_dict:
            return f"No plugin found with canonical name '{target}'."
        disable_plugin(target)
        return f"Plugin '{target}' has been disabled."

# End of plugins/commands/plugin.py