#!/usr/bin/env python
"""
cli/volunteers_cli.py - CLI tools for volunteer-related operations.
Uses dedicated formatters to present volunteer records in a consistent manner.
Integrates a centralized volunteer sign up method for unified registration.
"""

import argparse
from managers.volunteer.volunteer_operations import sign_up
from core.database.volunteers import get_all_volunteers
from managers.volunteer.volunteer_common import normalize_name
from cli.formatters import format_volunteer, format_deleted_volunteer
from cli.common import print_results

def list_volunteers_cli():
    """
    list_volunteers_cli - List all volunteer records in the database.
    Uses a formatter to display volunteer details.
    """
    volunteers = get_all_volunteers()
    if not volunteers:
        print("No volunteers found.")
        return
    for phone, data in volunteers.items():
        print(format_volunteer(phone, data))

def add_volunteer_cli(args: argparse.Namespace):
    """
    cli/volunteers_cli.py - add_volunteer_cli
    Adds a new volunteer record using the centralized sign up method.
    
    Args:
        args (argparse.Namespace): Command-line arguments containing phone, name, skills, available, and role.
    """
    phone = args.phone
    name = args.name
    skills = [s.strip() for s in args.skills.split(",")] if args.skills else []
    available = bool(int(args.available))
    current_role = args.role if args.role else None
    message = sign_up(phone, name, skills, available, current_role)
    print(message)

def list_deleted_volunteers_cli():
    """
    list_deleted_volunteers_cli - List all deleted volunteer records.
    Uses a formatter to display details from the DeletedVolunteers table.
    """
    query = "SELECT * FROM DeletedVolunteers ORDER BY deleted_at DESC"
    rows = __import__("core.database.helpers", fromlist=["execute_sql"]).execute_sql(query, fetchall=True)
    print_results(rows, format_deleted_volunteer, "No deleted volunteers found.")

# End of cli/volunteers_cli.py