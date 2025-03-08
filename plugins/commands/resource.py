#!/usr/bin/env python
"""
plugins/commands/resource.py - Resource command plugins for link sharing.
Provides commands to add, list, and remove commonly referenced links.
Usage:
  "@bot resource add <category> <url> [title?]"
  "@bot resource list [<category>]"
  "@bot resource remove <resource_id>"
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from core.database.resources import add_resource, list_resources, remove_resource
from parsers.argument_parser import split_args

logger = logging.getLogger(__name__)

@plugin('resource', canonical='resource')
def resource_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    resource - Manage shared resource links.
    
    Subcommands:
      add <category> <url> [title?] : Add a new resource.
      list [<category>]             : List resources, optionally filtered by category.
      remove <resource_id>          : Remove a resource by its ID.
      
    Usage examples:
      "@bot resource add Flyers https://example.com/flyer FlyerPDF"
      "@bot resource list Flyers"
      "@bot resource remove 3"
    """
    args = args.strip()
    if not args:
        return (
            "Usage:\n"
            "  @bot resource add <category> <url> [title?]\n"
            "  @bot resource list [<category>]\n"
            "  @bot resource remove <resource_id>"
        )
    parts = split_args(args, maxsplit=1)
    subcommand = parts[0].lower()
    rest = parts[1].strip() if len(parts) > 1 else ""
    
    if subcommand == "add":
        tokens = split_args(rest, maxsplit=2)

        # Handle cases where user typed partial fields
        if len(tokens) == 0:
            # e.g., "add" with no further text
            return "Usage: @bot resource add <category> <url> [title?]"
        elif len(tokens) == 1:
            # Decide if they're missing category or URL
            if tokens[0].startswith("http"):
                return "Error: Category is required. Usage: @bot resource add <category> <url> [title?]"
            else:
                return "Error: URL is required. Usage: @bot resource add <category> <url> [title?]"

        category = tokens[0].strip()
        url = tokens[1].strip()
        title = tokens[2].strip() if len(tokens) == 3 else ""

        if not category:
            return "Error: Category is required. Usage: @bot resource add <category> <url> [title?]"
        if not url:
            return "Error: URL is required. Usage: @bot resource add <category> <url> [title?]"
        if not url.startswith("http"):
            return f"Error: URL must start with 'http'. Provided: {url}"
        
        if title == "":
            logger.debug("Empty resource title is allowed; proceeding without error.")
        
        resource_id = add_resource(category, url, title)
        return f"Resource added with ID {resource_id}."
    
    elif subcommand == "list":
        category_filter = rest if rest else None
        resources = list_resources(category_filter)
        if not resources:
            if category_filter:
                return f"No resources found in category '{category_filter}'."
            else:
                return "No resources found."
        response = "Resources:\n"
        for res in resources:
            response += f"ID {res['id']}: [{res['category']}] {res['title']} - {res['url']}\n"
        return response.strip()
    
    elif subcommand == "remove":
        if not rest:
            return "Usage: @bot resource remove <resource_id>"
        try:
            resource_id = int(rest)
        except ValueError:
            return "Invalid resource_id. It should be a number."
        remove_resource(resource_id)
        return f"Resource with ID {resource_id} removed."
    
    else:
        return "Invalid subcommand. Use add, list, or remove."

# End of plugins/commands/resource.py