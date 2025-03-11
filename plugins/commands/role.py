#!/usr/bin/env python
"""
plugins/commands/role.py --- Role command plugins.
Now with Pydantic-based argument validation using the unified validate_model helper.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.volunteer_manager import VOLUNTEER_MANAGER
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import (
    PluginArgError,
    RoleSetModel,
    RoleSwitchModel,
    validate_model
)

@plugin('role', canonical='role')
def role_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    role - Manage volunteer roles.
    
    Subcommands:
      list                : List all recognized volunteer roles with required skills.
      set <role>          : Set your preferred role.
      switch <role>       : Switch from your current role to a new role.
      unassign            : Unassign/clear your current role.
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional', maxsplit=1)
        tokens = parsed["tokens"]
        if not tokens:
            roles = VOLUNTEER_MANAGER.list_roles()
            return "Recognized roles:\n" + "\n".join(f" - {role}" for role in roles)

        subcmd = tokens[0].lower()
        remainder = tokens[1].strip() if len(tokens) > 1 else ""

        if subcmd == "list":
            roles = VOLUNTEER_MANAGER.list_roles()
            return "Recognized roles:\n" + "\n".join(f" - {role}" for role in roles)
        elif subcmd == "set":
            if not remainder:
                raise PluginArgError("Usage: @bot role set <role>")
            validated = validate_model({"role": remainder}, RoleSetModel, "role set <role>")
            return VOLUNTEER_MANAGER.assign_role(sender, validated.role)
        elif subcmd == "switch":
            if not remainder:
                raise PluginArgError("Usage: @bot role switch <role>")
            validated = validate_model({"role": remainder}, RoleSwitchModel, "role switch <role>")
            return VOLUNTEER_MANAGER.switch_role(sender, validated.role)
        elif subcmd in {"unassign", "unset"}:
            return VOLUNTEER_MANAGER.unassign_role(sender)
        else:
            raise PluginArgError(
                "Invalid subcommand for role. Use 'list', 'set <role>', 'switch <role>', or 'unassign'."
            )
    except PluginArgError as e:
        return str(e)

# End of plugins/commands/role.py