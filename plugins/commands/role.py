#!/usr/bin/env python
"""
plugins/commands/role.py - Role command plugins.
Provides commands to list, set, switch, and unassign volunteer roles.
Usage examples:
  "@bot role list"           - Lists available roles with required skills.
  "@bot role set <role>"       - Sets your preferred role.
  "@bot role switch <role>"    - Switches from your current role to a new role.
  "@bot role unassign"         - Clears your assigned role.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.volunteer_manager import VOLUNTEER_MANAGER

@plugin('role', canonical='role')
def role_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    role - Manage volunteer roles.
    
    Subcommands:
      list                : List all recognized volunteer roles with required skills.
      set <role>          : Set your preferred role.
      switch <role>       : Switch from your current role to a new role.
      unassign            : Unassign/clear your current role.
    
    Usage examples:
      "@bot role list"
      "@bot role set greeter"
      "@bot role switch emcee"
      "@bot role unassign"
    """
    args = args.strip()
    if not args or args.lower() == "list":
        roles = VOLUNTEER_MANAGER.list_roles()
        return "Recognized roles:\n" + "\n".join(f" - {role}" for role in roles)
    elif args.lower().startswith("set"):
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            return "Usage: @bot role set <role>"
        role = parts[1].strip()
        return VOLUNTEER_MANAGER.assign_role(sender, role)
    elif args.lower().startswith("switch"):
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            return "Usage: @bot role switch <role>"
        role = parts[1].strip()
        return VOLUNTEER_MANAGER.switch_role(sender, role)
    elif args.lower() in {"unassign", "unset"}:
        return VOLUNTEER_MANAGER.unassign_role(sender)
    else:
        return "Invalid subcommand for role. Use 'list', 'set <role>', 'switch <role>', or 'unassign'."

# End of plugins/commands/role.py