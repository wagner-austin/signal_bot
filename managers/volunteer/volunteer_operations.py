#!/usr/bin/env python
"""
managers/volunteer/volunteer_operations.py --- Volunteer operations.
Renamed sign_up -> register_volunteer for consistency.
"""

import logging
import re
from typing import List, Optional
from core.database import (
    get_volunteer_record, add_volunteer_record, update_volunteer_record,
    delete_volunteer_record, add_deleted_volunteer_record, remove_deleted_volunteer_record
)
from core.messages import NEW_VOLUNTEER_REGISTERED, VOLUNTEER_UPDATED, VOLUNTEER_DELETED, VOLUNTEER_CHECKED_IN
from managers.volunteer.volunteer_common import normalize_name
from core.transaction import atomic_transaction
from core.concurrency import per_phone_lock
from core.exceptions import VolunteerError

logger = logging.getLogger(__name__)

PHONE_REGEX = re.compile(r'^\+?\d{7,15}$')

def register_volunteer(phone: str, name: str, skills: List[str], available: bool = True,
                       current_role: Optional[str] = None) -> str:
    """
    register_volunteer - Creates/updates a volunteer in an atomic transaction.
    Raises VolunteerError if phone is invalid or an exception occurs.
    """
    if not phone or not PHONE_REGEX.match(phone):
        msg = f"Invalid phone number format. Provided: {phone}"
        logger.error(msg)
        raise VolunteerError(msg)

    try:
        with per_phone_lock(phone):
            with atomic_transaction(exclusive=True) as conn:
                # Remove from DeletedVolunteers if present.
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
                    final_name = "Anonymous" if name.lower() == "skip" or not name.strip() else name
                    final_name = normalize_name(final_name, phone)
                    role_to_set = current_role.strip() if current_role and current_role.strip() else None

                    add_volunteer_record(phone, final_name, skills, available, role_to_set, role_to_set, conn=conn)
                    return NEW_VOLUNTEER_REGISTERED.format(name=final_name)
    except Exception as e:
        logger.exception("Error during volunteer registration.")
        raise VolunteerError(f"An unexpected sign-up exception occurred: {str(e)}")

def delete_volunteer(phone: str) -> str:
    """
    delete_volunteer - Deletes a volunteer's registration.
    """
    record = get_volunteer_record(phone)
    if not record:
        raise VolunteerError("You are not registered.")
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
    """
    record = get_volunteer_record(phone)
    if record:
        update_volunteer_record(phone, record["name"], record["skills"], True, record["current_role"])
        return VOLUNTEER_CHECKED_IN.format(name=normalize_name(record['name'], phone))
    raise VolunteerError("Volunteer not found.")

# End of managers/volunteer/volunteer_operations.py