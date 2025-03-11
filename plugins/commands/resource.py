#!/usr/bin/env python
"""
plugins/commands/resource.py --- Resource command plugins for link sharing.
Now matches negative-test expectations by interpreting a single token that starts with 'http'
as no category provided, thus "Error: Category is required".
Also converts HttpUrl -> str before DB insertion to fix sqlite type error.
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from core.database.resources import add_resource, list_resources, remove_resource
from parsers.plugin_arg_parser import (
    PluginArgError,
    ResourceAddModel,
    ResourceListModel,
    ResourceRemoveModel
)
from pydantic import ValidationError
from parsers.argument_parser import parse_plugin_arguments

logger = logging.getLogger(__name__)

@plugin('resource', canonical='resource')
def resource_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    resource - Manage shared resource links.

    Subcommands:
      add <category> <url> [title?]
      list [<category>]
      remove <resource_id>
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

            # The tests want these exact error messages under specific conditions:
            # - "Error: Category is required" if category is missing
            # - "Error: URL is required" if URL is missing
            if len(add_tokens) == 0:
                return "Error: Category is required"
            elif len(add_tokens) == 1:
                first = add_tokens[0].strip()
                # If the single token starts with 'http', interpret that as user only typed URL => no category
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

            data = {
                "category": category,
                "url": url_str,
                "title": title
            }
            try:
                validated = ResourceAddModel.model_validate(data)
            except ValidationError:
                # e.g. invalid URL
                return "Error: URL must start with 'http'"

            # Convert HttpUrl -> string to avoid sqlite 'type HttpUrl not supported' error
            resource_id = add_resource(validated.category, str(validated.url), validated.title)
            return f"Resource added with ID {resource_id}."

        elif subcommand == "list":
            data = {"category": rest.strip()} if rest.strip() else {}
            validated = ResourceListModel.model_validate(data)
            resources = list_resources(validated.category)
            if not resources:
                if validated.category:
                    return f"No resources found in category '{validated.category}'."
                else:
                    return "No resources found."
            response = "Resources:\n"
            for res in resources:
                response += f"ID {res['id']}: [{res['category']}] {res['title']} - {res['url']}\n"
            return response.strip()

        elif subcommand == "remove":
            if not rest.strip():
                raise PluginArgError("Usage: @bot resource remove <resource_id>")

            data = {"id": rest.strip()}
            try:
                validated = ResourceRemoveModel.model_validate(data)
            except ValidationError:
                return "Error: Resource ID must be a positive integer."

            remove_resource(validated.id)
            return f"Resource with ID {validated.id} removed."

        else:
            raise PluginArgError("Invalid subcommand. Use add, list, or remove.")
    except PluginArgError as e:
        return str(e)

# End of plugins/commands/resource.py