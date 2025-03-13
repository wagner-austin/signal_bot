#!/usr/bin/env python
"""
plugins/commands/role.py - Role command plugins.
Manages volunteer roles using unified validation and centralized error messages.
USAGE: Refer to usage constants in core/plugin_usage.py (USAGE_ROLE_SET, USAGE_ROLE_SWITCH, USAGE_ROLE)
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
import logging
from core.exceptions import ResourceError, VolunteerError
from core.plugin_usage import USAGE_ROLE_SET, USAGE_ROLE_SWITCH, USAGE_ROLE

logger = logging.getLogger(__name__)

@plugin('role', canonical='role')
def role_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    role - Manage volunteer roles.
    
    Subcommands:
      list                : List all recognized volunteer roles.
      set <role>          : Set your preferred role.
      switch <role>       : Switch your current role.
      unassign            : Unassign your current role.
    
    USAGE: {USAGE_ROLE}
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
                raise PluginArgError(USAGE_ROLE_SET)
            validated = validate_model({"role": remainder}, RoleSetModel, USAGE_ROLE_SET)
            confirmation = VOLUNTEER_MANAGER.assign_role(sender, validated.role)
            return confirmation
        elif subcmd == "switch":
            if not remainder:
                raise PluginArgError(USAGE_ROLE_SWITCH)
            validated = validate_model({"role": remainder}, RoleSwitchModel, USAGE_ROLE_SWITCH)
            confirmation = VOLUNTEER_MANAGER.switch_role(sender, validated.role)
            return confirmation
        elif subcmd in {"unassign", "unset"}:
            confirmation = VOLUNTEER_MANAGER.unassign_role(sender)
            return confirmation
        else:
            raise PluginArgError(USAGE_ROLE)
    except PluginArgError as e:
        logger.warning(f"role_command PluginArgError: {e}")
        return str(e)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"role_command domain error: {e}", exc_info=True)
        error_msg = str(e)
        if ":" in error_msg:
            error_msg = error_msg.split(":", 1)[1].strip()
        return f"An error occurred: {error_msg}"
    except Exception as e:
        logger.error(f"role_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in role_command."

# End of plugins/commands/role.py