"""
plugins/commands/role.py - Role management commands.
Manages volunteer roles using a unified subcommand dispatcher.
"""

from typing import Optional, List
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.volunteer_manager import VOLUNTEER_MANAGER
from parsers.plugin_arg_parser import (
    PluginArgError,
    RoleSetModel,
    RoleSwitchModel,
    validate_model
)
import logging
from core.exceptions import ResourceError, VolunteerError
from core.plugin_usage import USAGE_ROLE, USAGE_ROLE_SET, USAGE_ROLE_SWITCH
from plugins.commands.subcommand_dispatcher import handle_subcommands

logger = logging.getLogger(__name__)

@plugin('role', canonical='role')
def role_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/role.py - Manage volunteer roles.
    Subcommands:
      list         : List all recognized volunteer roles.
      set <role>   : Set your preferred role.
      switch <role>: Switch your current role.
      unassign   : Unassign your current role.
    USAGE: {USAGE_ROLE}
    """
    try:
        def sub_list(rest: List[str]) -> str:
            roles = VOLUNTEER_MANAGER.list_roles()
            return "Recognized roles:\n" + "\n".join(f" - {role}" for role in roles)

        def sub_set(rest: List[str]) -> str:
            if not rest:
                raise PluginArgError(USAGE_ROLE_SET)
            validated = validate_model({"role": " ".join(rest)}, RoleSetModel, USAGE_ROLE_SET)
            confirmation = VOLUNTEER_MANAGER.assign_role(sender, validated.role)
            return confirmation

        def sub_switch(rest: List[str]) -> str:
            if not rest:
                raise PluginArgError(USAGE_ROLE_SWITCH)
            validated = validate_model({"role": " ".join(rest)}, RoleSwitchModel, USAGE_ROLE_SWITCH)
            confirmation = VOLUNTEER_MANAGER.switch_role(sender, validated.role)
            return confirmation

        def sub_unassign(rest: List[str]) -> str:
            confirmation = VOLUNTEER_MANAGER.unassign_role(sender)
            return confirmation

        subcommands = {
            "list": sub_list,
            "set": sub_set,
            "switch": sub_switch,
            "unassign": sub_unassign
        }

        return handle_subcommands(
            args,
            subcommands,
            usage_msg=USAGE_ROLE,
            unknown_subcmd_msg="Unknown subcommand",
            parse_maxsplit=1,
            default_subcommand="list"
        )

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