#!/usr/bin/env python
"""
cli_tools.py - Database CLI Tools for manual inspection and modification.
Provides command-line utilities to view database content (volunteers, events, command logs)
and manually add volunteer records.

Usage Examples:
  python cli_tools.py list-volunteers
  python cli_tools.py add-volunteer --phone +1234567890 --name "John Doe" --skills "Python, SQL" --available 1 --role "Coordinator"
  python cli_tools.py list-events
  python cli_tools.py list-logs
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

def list_volunteers() -> None:
    """
    List all volunteer records in the database.
    
    Prints details such as phone, name, skills, availability, and current role for each volunteer.
    """
    volunteers = get_all_volunteers()
    if not volunteers:
        print("No volunteers found.")
        return
    for phone, data in volunteers.items():
        print(f"Phone: {phone}")
        print(f"Name: {data.get('name')}")
        skills = ", ".join(data.get("skills", []))
        print(f"Skills: {skills if skills else 'None'}")
        print(f"Available: {data.get('available')}")
        print(f"Current Role: {data.get('current_role')}")
        print("-" * 40)

def add_volunteer(args: argparse.Namespace) -> None:
    """
    Manually add a new volunteer record to the database.
    
    Uses command-line arguments to create a new volunteer entry.
    
    Args:
        args (argparse.Namespace): Parsed command-line arguments containing phone, name, skills, availability, and role.
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
    List all events in the database.
    
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
    List all command logs in the database.
    
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

def main() -> None:
    """
    Parse command-line arguments and execute the corresponding database CLI action.
    
    Available commands include:
      - list-volunteers: List all volunteer records.
      - add-volunteer: Manually add a new volunteer record.
      - list-events: List all events.
      - list-logs: List all command logs.
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
    
    args = parser.parse_args()
    
    if args.command == "list-volunteers":
        list_volunteers()
    elif args.command == "add-volunteer":
        add_volunteer(args)
    elif args.command == "list-events":
        list_events()
    elif args.command == "list-logs":
        list_logs()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

# End of cli_tools.py