#!/usr/bin/env python
"""
cli_tools.py - Aggregated CLI Tools Facade - Provides a unified command-line interface
to perform various database operations. Direct error messages via print() have been replaced
with logger calls to standardize logging and exception handling.
Usage Examples:
  python cli_tools.py list-volunteers
  python cli_tools.py add-volunteer --phone +1234567890 --name "John Doe" --skills "Python, SQL" --available 1 --role "Coordinator"
  python cli_tools.py list-events
  python cli_tools.py list-logs
  python cli_tools.py list-resources
  python cli_tools.py add-resource --category "Linktree" --url "https://linktr.ee/50501oc" --title "Official Linktree"
  python cli_tools.py remove-resource --id 3
  python cli_tools.py list-deleted-volunteers
  python cli_tools.py list-event-speakers
  python cli_tools.py list-tasks
"""

import argparse
import logging
from core.logger_setup import setup_logging

from cli.volunteers_cli import list_volunteers_cli, add_volunteer_cli, list_deleted_volunteers_cli
from cli.events_cli import list_events_cli, list_event_speakers_cli
from cli.logs_cli import list_logs_cli
from cli.resources_cli import list_resources_cli, add_resource_cli as original_add_resource_cli, remove_resource_cli as original_remove_resource_cli
from cli.tasks_cli import list_tasks_cli

logger = logging.getLogger(__name__)

def add_resource_cli(args: argparse.Namespace):
    """
    add_resource_cli - Enhanced with a basic URL format validation.
    """
    category = args.category
    url = args.url
    title = args.title if args.title else ""
    # Minimal validation: require the URL to start with 'http'
    if not url.startswith("http"):
        logger.error(f"Error: URL must start with 'http'. Provided: {url}")
        return
    # Delegate to the original function if valid
    original_add_resource_cli(args)

def remove_resource_cli(args: argparse.Namespace):
    """
    remove_resource_cli - Enhanced to check the resource ID is > 0.
    """
    resource_id = args.id
    if resource_id <= 0:
        logger.error(f"Error: Resource ID must be a positive integer. Provided: {resource_id}")
        return
    # Delegate to the original function if valid
    original_remove_resource_cli(args)

def main():
    """
    main - Parse command-line arguments and dispatch to the appropriate CLI function.
    """
    # Set up logging so that errors are output to stderr and captured by tests.
    setup_logging()

    parser = argparse.ArgumentParser(description="Aggregated CLI Tools for database operations.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Volunteers commands
    subparsers.add_parser("list-volunteers", help="List all volunteers")
    
    parser_add_vol = subparsers.add_parser("add-volunteer", help="Add a volunteer")
    parser_add_vol.add_argument("--phone", required=True, help="Volunteer phone number")
    parser_add_vol.add_argument("--name", required=True, help="Volunteer name")
    parser_add_vol.add_argument("--skills", default="", help="Comma-separated list of skills")
    parser_add_vol.add_argument("--available", default="1", help="Availability (1 for available, 0 for not available)")
    parser_add_vol.add_argument("--role", default="", help="Current role (optional)")
    
    subparsers.add_parser("list-deleted-volunteers", help="List deleted volunteer records")
    
    # Events commands
    subparsers.add_parser("list-events", help="List all events")
    subparsers.add_parser("list-event-speakers", help="List all event speakers")
    
    # Logs command
    subparsers.add_parser("list-logs", help="List all command logs")
    
    # Resources commands
    subparsers.add_parser("list-resources", help="List all resources")
    
    parser_add_res = subparsers.add_parser("add-resource", help="Add a new resource")
    parser_add_res.add_argument("--category", required=True, help="Resource category")
    parser_add_res.add_argument("--url", required=True, help="URL of the resource")
    parser_add_res.add_argument("--title", default="", help="Resource title (optional)")
    
    parser_remove_res = subparsers.add_parser("remove-resource", help="Remove a resource by ID")
    parser_remove_res.add_argument("--id", type=int, required=True, help="Resource ID to remove")
    
    # Tasks command
    subparsers.add_parser("list-tasks", help="List all tasks")
    
    args = parser.parse_args()
    
    if args.command == "list-volunteers":
        list_volunteers_cli()
    elif args.command == "add-volunteer":
        try:
            add_volunteer_cli(args)
        except ValueError as ve:
            logger.error(f"Error parsing --available value: {ve}")
    elif args.command == "list-deleted-volunteers":
        list_deleted_volunteers_cli()
    elif args.command == "list-events":
        list_events_cli()
    elif args.command == "list-event-speakers":
        list_event_speakers_cli()
    elif args.command == "list-logs":
        list_logs_cli()
    elif args.command == "list-resources":
        list_resources_cli()
    elif args.command == "add-resource":
        add_resource_cli(args)
    elif args.command == "remove-resource":
        remove_resource_cli(args)
    elif args.command == "list-tasks":
        list_tasks_cli()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

# End of cli_tools.py