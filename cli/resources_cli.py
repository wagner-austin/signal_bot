#!/usr/bin/env python
"""
cli/resources_cli.py - CLI tools for resource-related operations.
Delegates listing, adding, and removing logic to managers.resources_manager,
using print_results + format_resource for consistent listing output.
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
    list_resources_cli - Lists all resource records by calling managers.resources_manager.list_all_resources(),
    printing them via print_results + format_resource.
    """
    print_results(list_all_resources(), format_resource, "No resources found.")

def add_resource_cli(args: argparse.Namespace):
    """
    add_resource_cli - Minimal parse. Manager handles validation.
    Prints a simple success message with the new resource ID.
    """
    category = args.category
    url = args.url
    title = args.title if args.title else ""
    resource_id = create_resource(category, url, title)
    print(f"Resource added with ID {resource_id}.")

def remove_resource_cli(args: argparse.Namespace):
    """
    remove_resource_cli - Minimal parse. Manager handles validation.
    Prints a simple confirmation on success.
    """
    resource_id = args.id
    delete_resource(resource_id)
    print(f"Resource with ID {resource_id} removed.")

# End of cli/resources_cli.py