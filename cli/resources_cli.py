#!/usr/bin/env python
"""
cli/resources_cli.py --- CLI tools for resource-related operations.
Now delegates all resource-related logic to the resources_manager.
"""

import argparse
import logging
from cli.formatters import format_resource
from cli.common import print_results
from core.exceptions import ResourceError
from managers.resources_manager import (
    list_all_resources,
    add_new_resource,
    remove_resource_by_id
)

logger = logging.getLogger(__name__)

def list_resources_cli():
    """
    list_resources_cli - List all resource records.
    Retrieves resource data via resources_manager and displays formatted output.
    """
    resources = list_all_resources()
    print_results(resources, format_resource, "No resources found.")

def add_resource_cli(args: argparse.Namespace):
    """
    add_resource_cli - Add a new resource record.
    Delegates all validation and data handling to the manager.
    """
    category = args.category
    url = args.url
    title = args.title if args.title else ""

    # Delegate business logic to the manager:
    resource_id = add_new_resource(category, url, title)
    print(f"Resource added with ID {resource_id}.")

def remove_resource_cli(args: argparse.Namespace):
    """
    remove_resource_cli - Remove a resource record by its ID.
    Delegates validation to the manager.
    """
    resource_id = args.id
    remove_resource_by_id(resource_id)
    print(f"Resource with ID {resource_id} removed.")

# End of cli/resources_cli.py