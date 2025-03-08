#!/usr/bin/env python
"""
cli/resources_cli.py - CLI tools for resource-related operations.
Provides functions to list, add, and remove resource records.
"""

import argparse
from core.database.resources import add_resource, list_resources, remove_resource

def list_resources_cli():
    """
    list_resources_cli - List all resource records.
    Displays ID, category, title, URL, and creation timestamp.
    """
    resources = list_resources()
    if not resources:
        print("No resources found.")
        return
    for res in resources:
        print(f"ID: {res['id']}")
        print(f"Category: {res['category']}")
        print(f"Title: {res['title'] if res['title'] else 'N/A'}")
        print(f"URL: {res['url']}")
        print(f"Created At: {res['created_at']}")
        print("-" * 40)

def add_resource_cli(args: argparse.Namespace):
    """
    add_resource_cli - Add a new resource record.
    Requires category, URL, and an optional title.
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