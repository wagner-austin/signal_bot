#!/usr/bin/env python
"""
cli/resources_cli.py - CLI tools for resource-related operations.
Uses a dedicated formatter to present resource records.
"""

import argparse
from core.database.resources import add_resource, list_resources, remove_resource
from cli.formatters import format_resource

def list_resources_cli():
    """
    list_resources_cli - List all resource records.
    Retrieves resource data and prints formatted output.
    """
    resources = list_resources()
    if not resources:
        print("No resources found.")
        return
    for res in resources:
        output = format_resource(res)
        print(output)

def add_resource_cli(args: argparse.Namespace):
    """
    add_resource_cli - Add a new resource record.
    Uses business logic to add the resource and then displays a confirmation message.
    """
    category = args.category
    url = args.url
    title = args.title if args.title else ""
    resource_id = add_resource(category, url, title)
    print(f"Resource added with ID {resource_id}.")

def remove_resource_cli(args: argparse.Namespace):
    """
    remove_resource_cli - Remove a resource record by its ID.
    """
    resource_id = args.id
    remove_resource(resource_id)
    print(f"Resource with ID {resource_id} removed.")

# End of cli/resources_cli.py