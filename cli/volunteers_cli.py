#!/usr/bin/env python
"""
cli/volunteers_cli.py - CLI tools for volunteer-related operations.
Provides functions to list volunteers, add a volunteer, and list deleted volunteers.
"""

import argparse
from core.database.volunteers import add_volunteer_record, get_all_volunteers
from core.database.helpers import execute_sql
from managers.volunteer.volunteer_common import normalize_name

def list_volunteers_cli():
    """
    list_volunteers_cli - List all volunteer records in the database.
    Displays phone, normalized name, skills, availability, and current role.
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
    Retrieves and prints details from the DeletedVolunteers table.
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

# End of cli/volunteers_cli.py