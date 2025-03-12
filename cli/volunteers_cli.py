#!/usr/bin/env python
"""
cli/volunteers_cli.py - CLI tools for volunteer-related operations.
Now ensures all add/remove logic is handled by the manager.
"""

import argparse
from managers.volunteer.volunteer_common import normalize_name
from cli.formatters import format_volunteer, format_deleted_volunteer
from cli.common import print_results
from managers.volunteer_manager import VOLUNTEER_MANAGER

def list_volunteers_cli():
    """
    list_volunteers_cli - List all volunteers by calling VOLUNTEER_MANAGER.list_all_volunteers_list().
    """
    print_results(
        VOLUNTEER_MANAGER.list_all_volunteers_list(),
        format_volunteer,
        "No volunteers found."
    )

def add_volunteer_cli(args: argparse.Namespace):
    """
    add_volunteer_cli - Parse CLI args, then call the manager to register or update a volunteer.
    Does only minimal argument extraction. Any domain checks (phone format, skill merging, availability parsing)
    occur in the manager.
    """
    phone = args.phone
    name = args.name
    skills = [s.strip() for s in args.skills.split(",")] if args.skills else []
    available = args.available  # Pass as raw; manager handles validation
    current_role = args.role if args.role else None
    message = VOLUNTEER_MANAGER.register_volunteer(phone, name, skills, available, current_role)
    print(message)

def list_deleted_volunteers_cli():
    """
    list_deleted_volunteers_cli - List deleted volunteer records by calling VOLUNTEER_MANAGER.list_deleted_volunteers().
    """
    print_results(
        VOLUNTEER_MANAGER.list_deleted_volunteers(),
        format_deleted_volunteer,
        "No deleted volunteers found."
    )

# End of cli/volunteers_cli.py