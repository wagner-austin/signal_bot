#!/usr/bin/env python
"""
cli/volunteers_cli.py - CLI tools for volunteer-related operations.
Uses dedicated formatters to present volunteer records in a consistent manner.
Now avoids direct DB calls by delegating to volunteer_manager.
"""

import argparse
from managers.volunteer.volunteer_operations import sign_up
from managers.volunteer.volunteer_common import normalize_name
from cli.formatters import format_volunteer, format_deleted_volunteer
from cli.common import print_results
from managers.volunteer_manager import VOLUNTEER_MANAGER

def list_volunteers_cli():
    """
    list_volunteers_cli - List all volunteer records in the database.
    Uses volunteer_manager.list_volunteers to retrieve data and displays formatted output.
    """
    volunteers = VOLUNTEER_MANAGER.list_volunteers()
    if not volunteers:
        print("No volunteers found.")
        return
    for phone, data in volunteers.items():
        print(format_volunteer(phone, data))

def add_volunteer_cli(args: argparse.Namespace):
    """
    add_volunteer_cli - Adds a new volunteer record using the centralized sign up method.
    
    Args:
        args (argparse.Namespace): Command-line arguments containing phone, name, skills, available, and role.
    """
    phone = args.phone
    name = args.name
    skills = [s.strip() for s in args.skills.split(",")] if args.skills else []
    try:
        available = bool(int(args.available))
    except ValueError:
        raise ValueError("--available must be 0 or 1.")
    current_role = args.role if args.role else None
    message = sign_up(phone, name, skills, available, current_role)
    print(message)

def list_deleted_volunteers_cli():
    """
    list_deleted_volunteers_cli - List all deleted volunteer records.
    Delegates data retrieval to volunteer_manager.
    """
    rows = VOLUNTEER_MANAGER.list_deleted_volunteers()
    print_results(rows, format_deleted_volunteer, "No deleted volunteers found.")

# End of cli/volunteers_cli.py