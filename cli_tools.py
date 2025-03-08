#!/usr/bin/env python
"""
cli_tools.py - Database CLI Tools for manual inspection and modification.
Provides command-line utilities to view database content (volunteers, events, command logs, resources, tasks, deleted volunteers, event speakers)
and manually add, remove, or list records.
Usage Examples:
  python cli_tools.py list-volunteers
  python cli_tools.py add-volunteer --phone +1234567890 --name "John Doe" --skills "Python, SQL" --available 1 --role "Coordinator"
  python cli_tools.py list-events
  python cli_tools.py list-logs
  python cli_tools.py list-resources
  python cli_tools.py list-tasks
  python cli_tools.py list-deleted-volunteers
  python cli_tools.py list-event-speakers
  python cli_tools.py add-resource --category "Linktree" --url "https://linktr.ee/50501oc" --title "Official Linktree"
  python cli_tools.py remove-resource --id 3
"""

import os
import sys
# Ensure the project root is in sys.path so that the core package can be imported.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import argparse
from core.database.helpers import execute_sql
from core.database.volunteers import add_volunteer_record, get_all_volunteers
from core.database.resources import add_resource, list_resources, remove_resource
from managers.volunteer.volunteer_common import normalize_name  # Ensure volunteer names are normalized

def list_volunteers() -> None:
    """
    list_volunteers - List all volunteer records in the database.
    Prints details such as phone, normalized name, skills, availability, and current role for each volunteer.
    """
    volunteers = get_all_volunteers()
    if not volunteers:
        print("No volunteers found.")
        return
    for phone, data in volunteers.items():
        display_name = normalize_name(data.get("name"), phone)
        print(f"Phone: {phone}")
        print(f"Name: {display_name}")
        skills = ", ".join(data.get("skills", []))
        print(f"Skills: {skills if skills else 'None'}")
        print(f"Available: {data.get('available')}")
        print(f"Current Role: {data.get('current_role')}")
        print("-" * 40)

def add_volunteer(args: argparse.Namespace) -> None:
    """
    add_volunteer - Manually add a new volunteer record to the database.
    Uses command-line arguments to create a new volunteer entry.
    """
    phone = args.phone
    name = args.name
    skills = [s.strip() for s in args.skills.split(",")] if args.skills else []
    available = bool(int(args.available))
    current_role = args.role if args.role else None
    add_volunteer_record(phone, name, skills, available, current_role)
    print(f"Volunteer '{name}' added with phone {phone}.")

def list_events() -> None:
    """
    list_events - List all events in the database.
    Retrieves and prints event details such as event_id, title, date, time, location, and description.
    """
    query = "SELECT * FROM Events ORDER BY created_at DESC"
    rows = execute_sql(query, fetchall=True)
    if not rows:
        print("No events found.")
        return
    for row in rows:
        print(f"Event ID: {row['event_id']}")
        print(f"Title: {row['title']}")
        print(f"Date: {row['date']}")
        print(f"Time: {row['time']}")
        print(f"Location: {row['location']}")
        print(f"Description: {row['description']}")
        print("-" * 40)

def list_logs() -> None:
    """
    list_logs - List all command logs in the database.
    Retrieves and prints details of command logs including id, sender, command, arguments, and timestamp.
    """
    query = "SELECT * FROM CommandLogs ORDER BY timestamp DESC"
    rows = execute_sql(query, fetchall=True)
    if not rows:
        print("No command logs found.")
        return
    for row in rows:
        print(f"ID: {row['id']}")
        print(f"Sender: {row['sender']}")
        print(f"Command: {row['command']}")
        print(f"Args: {row['args']}")
        print(f"Timestamp: {row['timestamp']}")
        print("-" * 40)

def list_resources_cli() -> None:
    """
    list_resources_cli - List all resource records in the database.
    Optionally can filter by category if provided.
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

def list_deleted_volunteers() -> None:
    """
    list_deleted_volunteers - List all deleted volunteer records in the database.
    """
    query = "SELECT * FROM DeletedVolunteers ORDER BY deleted_at DESC"
    rows = execute_sql(query, fetchall=True)
    if not rows:
        print("No deleted volunteers found.")
        return
    for row in rows:
        print(f"Phone: {row['phone']}")
        print(f"Name: {row['name']}")
        skills = ", ".join(row['skills'].split(',')) if row['skills'] else "None"
        print(f"Skills: {skills}")
        print(f"Available: {row['available']}")
        print(f"Current Role: {row['current_role']}")
        print(f"Deleted At: {row['deleted_at']}")
        print("-" * 40)

def list_event_speakers() -> None:
    """
    list_event_speakers - List all event speakers from the database.
    """
    query = "SELECT * FROM EventSpeakers ORDER BY created_at DESC"
    rows = execute_sql(query, fetchall=True)
    if not rows:
        print("No event speakers found.")
        return
    for row in rows:
        print(f"ID: {row['id']}")
        print(f"Event ID: {row['event_id']}")
        print(f"Speaker Name: {row['speaker_name']}")
        print(f"Speaker Topic: {row['speaker_topic']}")
        print(f"Created At: {row['created_at']}")
        print("-" * 40)

def list_tasks_cli() -> None:
    """
    list_tasks_cli - List all tasks from the Tasks table.
    """
    from core.task_manager import list_tasks
    tasks = list_tasks()
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        print(f"Task ID: {task['task_id']}")
        print(f"Description: {task['description']}")
        print(f"Status: {task['status']}")
        print(f"Created At: {task['created_at']}")
        print(f"Created By: {task['created_by_name']}")
        print(f"Assigned To: {task['assigned_to_name']}")
        print("-" * 40)

def add_resource_cli(args: argparse.Namespace) -> None:
    """
    add_resource_cli - Manually add a new resource record to the database.
    """
    category = args.category
    url = args.url
    title = args.title if args.title else ""
    resource_id = add_resource(category, url, title)
    print(f"Resource added with ID {resource_id}.")

def remove_resource_cli(args: argparse.Namespace) -> None:
    """
    remove_resource_cli - Remove a resource record from the database by its ID.
    """
    resource_id = args.id
    remove_resource(resource_id)
    print(f"Resource with ID {resource_id} removed.")

def main() -> None:
    """
    main - Parse command-line arguments and execute the corresponding database CLI action.
    Available commands include:
      - list-volunteers: List all volunteer records.
      - add-volunteer: Manually add a new volunteer record.
      - list-events: List all events.
      - list-logs: List all command logs.
      - list-resources: List all resource records.
      - list-deleted-volunteers: List all deleted volunteer records.
      - list-event-speakers: List all event speakers.
      - list-tasks: List all tasks.
      - add-resource: Manually add a new resource record.
      - remove-resource: Remove a resource record by its ID.
    """
    parser = argparse.ArgumentParser(description="Database CLI Tools for inspection and manual modification.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Sub-command: list volunteers
    subparsers.add_parser("list-volunteers", help="List all volunteers in the database")
    
    # Sub-command: add volunteer
    parser_add = subparsers.add_parser("add-volunteer", help="Manually add a volunteer to the database")
    parser_add.add_argument("--phone", required=True, help="Volunteer phone number")
    parser_add.add_argument("--name", required=True, help="Volunteer name")
    parser_add.add_argument("--skills", default="", help="Comma-separated list of skills")
    parser_add.add_argument("--available", default="1", help="Availability (1 for available, 0 for not available)")
    parser_add.add_argument("--role", default="", help="Current role (optional)")
    
    # Sub-command: list events
    subparsers.add_parser("list-events", help="List all events in the database")
    
    # Sub-command: list logs
    subparsers.add_parser("list-logs", help="List all command logs in the database")
    
    # Sub-command: list resources
    subparsers.add_parser("list-resources", help="List all resource records in the database")
    
    # Sub-command: list deleted volunteers
    subparsers.add_parser("list-deleted-volunteers", help="List all deleted volunteer records in the database")
    
    # Sub-command: list event speakers
    subparsers.add_parser("list-event-speakers", help="List all event speakers in the database")
    
    # Sub-command: list tasks
    subparsers.add_parser("list-tasks", help="List all tasks in the database")
    
    # Sub-command: add resource
    parser_add_res = subparsers.add_parser("add-resource", help="Manually add a resource record to the database")
    parser_add_res.add_argument("--category", required=True, help="Resource category (e.g., Flyers, Videos, Linktree)")
    parser_add_res.add_argument("--url", required=True, help="URL of the resource")
    parser_add_res.add_argument("--title", default="", help="Title or description of the resource (optional)")
    
    # Sub-command: remove resource
    parser_remove_res = subparsers.add_parser("remove-resource", help="Remove a resource record by its ID")
    parser_remove_res.add_argument("--id", type=int, required=True, help="ID of the resource to remove")
    
    args = parser.parse_args()
    
    if args.command == "list-volunteers":
        list_volunteers()
    elif args.command == "add-volunteer":
        add_volunteer(args)
    elif args.command == "list-events":
        list_events()
    elif args.command == "list-logs":
        list_logs()
    elif args.command == "list-resources":
        list_resources_cli()
    elif args.command == "list-deleted-volunteers":
        list_deleted_volunteers()
    elif args.command == "list-event-speakers":
        list_event_speakers()
    elif args.command == "list-tasks":
        list_tasks_cli()
    elif args.command == "add-resource":
        add_resource_cli(args)
    elif args.command == "remove-resource":
        remove_resource_cli(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

# End of cli_tools.py