#!/usr/bin/env python
"""
managers/volunteer/volunteer_operations.py --- Volunteer operations.
Provides functions for volunteer registration, check‑in, and deletion.
Uses a centralized sign_up method for consistent volunteer creation/updates.
Changes:
 - Use 'external_connection=True' in repository calls to avoid closing a shared connection during sign_up.
 - Add per-phone locking to prevent race conditions during concurrent sign-ups.
"""

import logging
import re
import threading
from typing import List, Optional
from core.database import (
    get_volunteer_record, add_volunteer_record, update_volunteer_record,
    delete_volunteer_record, add_deleted_volunteer_record, remove_deleted_volunteer_record
)
from core.messages import NEW_VOLUNTEER_REGISTERED, VOLUNTEER_UPDATED, VOLUNTEER_DELETED, VOLUNTEER_CHECKED_IN
from managers.volunteer.volunteer_common import normalize_name
from core.skill_config import AVAILABLE_SKILLS
from core.database.connection import db_connection

logger = logging.getLogger(__name__)

# A basic phone regex that allows optional leading '+' and 7-15 digits.
PHONE_REGEX = re.compile(r'^\+?\d{7,15}$')

# Global locks for volunteer sign-up concurrency control.
_SIGN_UP_LOCKS = {}
_SIGN_UP_LOCKS_LOCK = threading.Lock()


def sign_up(phone: str, name: str, skills: List[str], available: bool = True,
            current_role: Optional[str] = None) -> str:
    """
    sign_up - Registers/updates a volunteer in an atomic transaction.

    Args:
        phone (str): Volunteer phone number (E.164).
        name (str): Volunteer full name (or 'skip' to remain anonymous).
        skills (List[str]): List of skill strings to union with existing.
        available (bool): Availability status.
        current_role (Optional[str]): If provided, updates volunteer's current role.

    Returns:
        str: Confirmation or error message.
    """
    if not phone or not PHONE_REGEX.match(phone):
        return "Error: Invalid phone number format. Please provide a valid phone (e.g., +1234567890)."

    # Acquire a per-phone lock to prevent race conditions during concurrent sign-ups.
    with _SIGN_UP_LOCKS_LOCK:
        lock = _SIGN_UP_LOCKS.get(phone)
        if lock is None:
            lock = threading.Lock()
            _SIGN_UP_LOCKS[phone] = lock
    with lock:
        with db_connection() as conn:
            # Remove them from DeletedVolunteers if present, using the same conn.
            remove_deleted_volunteer_record(phone, conn=conn)

            record = get_volunteer_record(phone, conn=conn)
            if record:
                updated_name = record["name"] if name.lower() == "skip" else name
                new_skills = set(record["skills"]).union(set(sk.strip() for sk in skills))
                updated_name = normalize_name(updated_name, phone)
                new_role = current_role.strip() if current_role and current_role.strip() else record["current_role"]

                update_volunteer_record(phone, updated_name, list(new_skills), available, new_role, conn=conn)
                return VOLUNTEER_UPDATED.format(name=updated_name)
            else:
                # Not found in Volunteers -> create
                final_name = "Anonymous" if name.lower() == "skip" or not name.strip() else name
                final_name = normalize_name(final_name, phone)
                role_to_set = current_role.strip() if current_role and current_role.strip() else None

                add_volunteer_record(phone, final_name, skills, available, role_to_set, role_to_set, conn=conn)
                return NEW_VOLUNTEER_REGISTERED.format(name=final_name)


def delete_volunteer(phone: str) -> str:
    """
    delete_volunteer - Deletes a volunteer's registration.

    Args:
        phone (str): Volunteer phone.

    Returns:
        str: Deletion confirmation or 'You are not registered.'
    """
    record = get_volunteer_record(phone)
    if not record:
        return "You are not registered."
    add_deleted_volunteer_record(
        phone,
        record["name"],
        record["skills"],
        record["available"],
        record["current_role"]
    )
    delete_volunteer_record(phone)
    logger.info(f"Volunteer record for {phone} has been deleted from the system.")
    return VOLUNTEER_DELETED


def check_in(phone: str) -> str:
    """
    check_in - Marks a volunteer as available.

    Args:
        phone (str): Volunteer phone number.

    Returns:
        str: Confirmation or an error if volunteer not found.
    """
    record = get_volunteer_record(phone)
    if record:
        update_volunteer_record(phone, record["name"], record["skills"], True, record["current_role"])
        return VOLUNTEER_CHECKED_IN.format(name=normalize_name(record['name'], phone))
    return "Volunteer not found."

# End of managers/volunteer/volunteer_operations.py