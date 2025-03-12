#!/usr/bin/env python
"""
cli/resources_cli.py - CLI tools for resource-related operations.
Uses a dedicated formatter to present resource records.
Raises ResourceError for invalid conditions instead of logging error messages.
"""

import argparse
import logging
from core.database.resources import add_resource, list_resources, remove_resource
from cli.formatters import format_resource
from cli.common import print_results
from core.exceptions import ResourceError

logger = logging.getLogger(__name__)

def list_resources_cli():
    """
    list_resources_cli - List all resource records.
    Retrieves resource data and prints formatted output.
    """
    resources = list_resources()
    print_results(resources, format_resource, "No resources found.")

def add_resource_cli(args: argparse.Namespace):
    """
    add_resource_cli - Add a new resource record.
    Raises ResourceError if the URL does not start with 'http'.
    """
    category = args.category
    url = args.url
    title = args.title if args.title else ""

    if not url.startswith("http"):
        error_msg = f"URL must start with 'http'. Provided: {url}"
        raise ResourceError(error_msg)

    resource_id = add_resource(category, url, title)
    print(f"Resource added with ID {resource_id}.")

def remove_resource_cli(args: argparse.Namespace):
    """
    remove_resource_cli - Remove a resource record by its ID.
    Raises ResourceError if the ID is not a positive integer.
    """
    resource_id = args.id
    if resource_id <= 0:
        error_msg = f"Resource ID must be a positive integer. Provided: {resource_id}"
        raise ResourceError(error_msg)

    remove_resource(resource_id)
    print(f"Resource with ID {resource_id} removed.")

# End cli/resources_cli.py