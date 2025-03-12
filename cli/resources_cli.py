#!/usr/bin/env python
"""
cli/resources_cli.py - CLI tools for resource-related operations.
Uses a dedicated formatter to present resource records.
Logs and returns "Error: ..." messages if validation fails to match existing test expectations.
"""

import argparse
import logging
from core.database.resources import add_resource, list_resources, remove_resource
from cli.formatters import format_resource
from cli.common import print_results

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
    If the URL does not start with 'http', logs "Error: ..." and returns immediately.
    """
    category = args.category
    url = args.url
    title = args.title if args.title else ""

    if not url.startswith("http"):
        # The test checks for "Error: URL must start with 'http'" in stderr/stdout
        error_msg = f"Error: URL must start with 'http'. Provided: {url}"
        logger.error(error_msg)
        return

    resource_id = add_resource(category, url, title)
    print(f"Resource added with ID {resource_id}.")

def remove_resource_cli(args: argparse.Namespace):
    """
    remove_resource_cli - Remove a resource record by its ID.
    If the ID is <= 0, logs "Error: ..." and returns.
    """
    resource_id = args.id
    if resource_id <= 0:
        error_msg = f"Error: Resource ID must be a positive integer. Provided: {resource_id}"
        logger.error(error_msg)
        return

    remove_resource(resource_id)
    print(f"Resource with ID {resource_id} removed.")

# ENd of cli/resources_cli.py