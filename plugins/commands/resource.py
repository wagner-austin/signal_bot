#!/usr/bin/env python
"""
plugins/commands/resource.py
----------------------------
Resource command plugins. Manages shared resource links by calling managers.resources_manager for all logic.
"""

import logging
from typing import Optional

from plugins.manager import plugin
from core.state import BotStateMachine
from managers.resources_manager import create_resource, list_all_resources, delete_resource
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import PluginArgError
from pydantic import ValidationError

# New import to unify formatting:
from cli.formatters import format_resource

logger = logging.getLogger(__name__)

@plugin('resource', canonical='resource')
def resource_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    resource - Manage shared resource links via managers.resources_manager.
    
    Subcommands:
      add <category> <url> [title?]
      list [<category>]
      remove <resource_id>
    
    All underlying creation/removal/listing logic is in managers.resources_manager.
    This plugin only parses arguments and calls that manager as the 'source of truth'.
    """
    try:
        parsed_main = parse_plugin_arguments(args, mode='positional', maxsplit=1)
        tokens = parsed_main["tokens"]
        if not tokens:
            raise PluginArgError(
                "Usage:\n"
                "  @bot resource add <category> <url> [title?]\n"
                "  @bot resource list [<category>]\n"
                "  @bot resource remove <resource_id>"
            )

        subcommand = tokens[0].lower()
        rest = tokens[1] if len(tokens) > 1 else ""

        if subcommand == "add":
            positional = parse_plugin_arguments(rest, mode='positional')
            add_tokens = positional["tokens"]

            if len(add_tokens) == 0:
                return "Error: Category is required"
            elif len(add_tokens) == 1:
                first = add_tokens[0].strip()
                if first.lower().startswith("http"):
                    return "Error: Category is required"
                else:
                    return "Error: URL is required"

            category = add_tokens[0].strip()
            url_str = add_tokens[1].strip()
            if not category:
                return "Error: Category is required"
            if not url_str:
                return "Error: URL is required"

            title = " ".join(add_tokens[2:]) if len(add_tokens) > 2 else ""

            resource_id = create_resource(category, url_str, title)
            return f"Resource added with ID {resource_id}."

        elif subcommand == "list":
            data = {"category": rest.strip()} if rest.strip() else {}
            resources = list_all_resources(data["category"]) if "category" in data else list_all_resources()
            if not resources:
                if data.get("category"):
                    return f"No resources found in category '{data['category']}'."
                else:
                    return "No resources found."

            # Use the same formatting used by CLI:
            output_lines = [format_resource(r) for r in resources]
            return "\n".join(output_lines)

        elif subcommand == "remove":
            if not rest.strip():
                raise PluginArgError("Usage: @bot resource remove <resource_id>")

            resource_id_str = rest.strip()
            try:
                resource_id = int(resource_id_str)
            except ValueError:
                return "Error: Resource ID must be a positive integer."

            delete_resource(resource_id)
            return f"Resource with ID {resource_id} removed."

        else:
            raise PluginArgError("Invalid subcommand. Use add, list, or remove.")

    except PluginArgError as e:
        logger.warning(f"resource_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"resource_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in resource_command."

# End of plugins/commands/resource.py