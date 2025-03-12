#!/usr/bin/env python
"""
cli/volunteers_cli.py - CLI tools for volunteer-related operations.
Now calls register_volunteer and list_all_volunteers from the volunteer manager.
Streamlined to one-liner "list" commands for volunteers.
"""

import argparse
from managers.volunteer.volunteer_common import normalize_name
from cli.formatters import format_volunteer, format_deleted_volunteer
from cli.common import print_results
from managers.volunteer_manager import VOLUNTEER_MANAGER

def list_volunteers_cli():
    """
    list_volunteers_cli - List all volunteer records in the database (one-liner).
    """
    print_results(
        VOLUNTEER_MANAGER.list_all_volunteers_list(),
        format_volunteer,
        "No volunteers found."
    )

def add_volunteer_cli(args: argparse.Namespace):
    """
    add_volunteer_cli - Adds a new volunteer record using the manager's register_volunteer.
    """
    phone = args.phone
    name = args.name
    skills = [s.strip() for s in args.skills.split(",")] if args.skills else []
    try:
        available = bool(int(args.available))
    except ValueError:
        raise ValueError("--available must be 0 or 1.")
    current_role = args.role if args.role else None
    message = VOLUNTEER_MANAGER.register_volunteer(phone, name, skills, available, current_role)
    print(message)

def list_deleted_volunteers_cli():
    """
    list_deleted_volunteers_cli - List all deleted volunteer records (one-liner).
    """
    print_results(
        VOLUNTEER_MANAGER.list_deleted_volunteers(),
        format_deleted_volunteer,
        "No deleted volunteers found."
    )

# End of cli/volunteers_cli.py