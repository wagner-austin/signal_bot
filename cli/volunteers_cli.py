#!/usr/bin/env python
"""
cli/volunteers_cli.py - CLI tools for volunteer-related operations.
Ensures all list commands use print_results + formatters for consistent output.
"""

import argparse
from cli.formatters import format_volunteer, format_deleted_volunteer
from cli.common import print_results
from managers.volunteer_manager import VOLUNTEER_MANAGER

def list_volunteers_cli():
    """
    list_volunteers_cli - List all volunteers via manager, printing them consistently with format_volunteer.
    """
    print_results(
        VOLUNTEER_MANAGER.list_all_volunteers_list(),
        format_volunteer,
        "No volunteers found."
    )

def add_volunteer_cli(args: argparse.Namespace):
    """
    add_volunteer_cli - minimal parse. Manager handles domain validation.
    """
    phone = args.phone
    name = args.name
    skills = [s.strip() for s in args.skills.split(",")] if args.skills else []
    available = args.available  # pass raw to manager
    current_role = args.role if args.role else None
    message = VOLUNTEER_MANAGER.register_volunteer(phone, name, skills, available, current_role)
    print(message)

def list_deleted_volunteers_cli():
    """
    list_deleted_volunteers_cli - Prints via print_results + format_deleted_volunteer for consistent output.
    """
    print_results(
        VOLUNTEER_MANAGER.list_deleted_volunteers(),
        format_deleted_volunteer,
        "No deleted volunteers found."
    )

# End of cli/volunteers_cli.py