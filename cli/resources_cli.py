#!/usr/bin/env python
"""
resources_cli.py - CLI tools for resource-related operations.
Delegates listing to managers.resources_manager.
"""

import argparse
import logging
from cli.formatters import format_resource
from cli.common import print_results
from managers.resources_manager import (
    list_all_resources,
    create_resource,
    delete_resource
)

logger = logging.getLogger(__name__)

def list_resources_cli():
    """
    list_resources_cli - List all resource records by calling managers.resources_manager.list_all_resources().
    """
    print_results(list_all_resources(), format_resource, "No resources found.")

def add_resource_cli(args: argparse.Namespace):
    """
    add_resource_cli - Parses CLI args and calls manager to create a new resource.
    """
    category = args.category
    url = args.url
    title = args.title if args.title else ""
    resource_id = create_resource(category, url, title)
    print(f"Resource added with ID {resource_id}.")

def remove_resource_cli(args: argparse.Namespace):
    """
    remove_resource_cli - Parses CLI args and calls manager to delete a resource by ID.
    """
    resource_id = args.id
    delete_resource(resource_id)
    print(f"Resource with ID {resource_id} removed.")

# End of cli/resources_cli.py