#!/usr/bin/env python
"""
cli/volunteers_cli.py - CLI tools for volunteer-related operations.
Uses dedicated formatters to present volunteer records in a consistent manner.
"""

import argparse
from core.database.volunteers import add_volunteer_record, get_all_volunteers
from core.database.helpers import execute_sql
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
    add_volunteer_cli - Add a new volunteer record to the database.
    Uses command-line arguments to register the volunteer.
    """
    phone = args.phone
    name = args.name
    skills = [s.strip() for s in args.skills.split(",")] if args.skills else []
    available = bool(int(args.available))
    current_role = args.role if args.role else None
    add_volunteer_record(phone, name, skills, available, current_role)
    print(f"Volunteer '{name}' added with phone {phone}.")

def list_deleted_volunteers_cli():
    """
    list_deleted_volunteers_cli - List all deleted volunteer records.
    Uses a formatter to display details from the DeletedVolunteers table.
    """
    query = "SELECT * FROM DeletedVolunteers ORDER BY deleted_at DESC"
    rows = execute_sql(query, fetchall=True)
    print_results(rows, format_deleted_volunteer, "No deleted volunteers found.")

# End of cli/volunteers_cli.py