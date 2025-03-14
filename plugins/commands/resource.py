"""
plugins/commands/resource.py - Manages shared resource links.
Uses a unified subcommand dispatcher for consistent argument parsing.
Subcommands:
  add    : Add a new resource.
  list   : List all resources.
  remove : Remove a resource.
USAGE: {USAGE_RESOURCE}
"""

import logging
from typing import Optional, List
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.resources_manager import create_resource, list_all_resources, delete_resource
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import PluginArgError
from plugins.commands.formatters import format_resource
from core.plugin_usage import USAGE_RESOURCE

logger = logging.getLogger(__name__)

@plugin('resource', canonical='resource')
def resource_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/resource.py - Manage shared resource links.
    Subcommands:
      add    : Add a new resource.
      list   : List all resources.
      remove : Remove a resource.
    USAGE: {USAGE_RESOURCE}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        return f"Usage: {USAGE_RESOURCE}"
    allowed = {"add", "list", "remove"}
    if tokens[0].lower() not in allowed:
        return f"Unknown subcommand. USAGE: {USAGE_RESOURCE}"
    subcmd = tokens[0].lower()
    new_args = tokens[1] if len(tokens) > 1 else ""
    try:
        if subcmd == "add":
            if not new_args.strip():
                return f"Usage: {USAGE_RESOURCE}"
            add_tokens = new_args.strip().split()
            if len(add_tokens) == 1:
                if add_tokens[0].lower().startswith("http"):
                    return "Error: Category is required."
                else:
                    return "Error: URL is required."
            category = add_tokens[0].strip()
            url_str = add_tokens[1].strip()
            title = " ".join(add_tokens[2:]) if len(add_tokens) > 2 else ""
            resource_id = create_resource(category, url_str, title)
            return f"Resource added with ID {resource_id}."
        elif subcmd == "list":
            # If no extra argument, list all resources.
            if new_args.strip():
                resources = list_all_resources(new_args.strip())
            else:
                resources = list_all_resources()
            if not resources:
                return "No resources found."
            return "\n".join(format_resource(r) for r in resources)
        elif subcmd == "remove":
            if not new_args.strip():
                return f"Usage: {USAGE_RESOURCE}"
            resource_id_str = new_args.strip().split()[0]
            try:
                resource_id = int(resource_id_str)
            except ValueError:
                return "Error: Resource ID must be a positive integer."
            delete_resource(resource_id)
            return f"Resource with ID {resource_id} removed."
    except PluginArgError as e:
        logger.warning(f"resource_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"resource_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in resource_command."

# End of plugins/commands/resource.py