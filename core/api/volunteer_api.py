#!/usr/bin/env python
"""
core/api/volunteer_api.py
-------------------------
Provides stable functions to manage volunteers.
Re-exports selected methods from the internal VolunteerManager for plugin usage.
"""

import logging
from typing import List, Optional, Dict, Any

from core.exceptions import VolunteerError
from managers.volunteer_manager import (
    VOLUNTEER_MANAGER,
    register_volunteer as mgr_register_volunteer,
    delete_volunteer as mgr_delete_volunteer,
    check_in as mgr_check_in,
    volunteer_status as mgr_volunteer_status,
    check_out as mgr_check_out
)

logger = logging.getLogger(__name__)

def register_volunteer(phone: str,
                       name: str,
                       available: bool = True) -> str:
    """
    register_volunteer(phone, name, available=True) -> str
    ------------------------------------------------------
    Create or update a volunteer with the given phone and name.
    Returns a user-facing confirmation message. Raises VolunteerError if invalid phone.

    Usage Example:
        from core.api.volunteer_api import register_volunteer

        msg = register_volunteer("+15551234567", "Alice", True)
        print(msg)
    """
    return mgr_register_volunteer(phone, name, available)

def delete_volunteer(phone: str) -> str:
    """
    delete_volunteer(phone) -> str
    ------------------------------
    Remove the volunteer from the active roster, archiving them in DeletedVolunteers.
    Returns a user-facing confirmation message. Raises VolunteerError if not registered.
    """
    return mgr_delete_volunteer(phone)

def check_in(phone: str) -> str:
    """
    check_in(phone) -> str
    -----------------------
    Mark an existing volunteer as available.
    Returns a user-facing message. Raises VolunteerError if the phone is not registered.
    """
    return mgr_check_in(phone)

def check_out(phone: str) -> str:
    """
    check_out(phone) -> str
    ------------------------
    Mark an existing volunteer as unavailable.
    Returns a user-facing message. Raises VolunteerError if the phone is not registered.
    """
    return mgr_check_out(phone)

def volunteer_status() -> str:
    """
    volunteer_status() -> str
    --------------------------
    Returns a text summary of all volunteers' availability.
    This is primarily for debugging or listing in a plugin command.
    """
    return mgr_volunteer_status()

def get_volunteer_record(phone: str) -> Optional[Dict[str, Any]]:
    """
    get_volunteer_record(phone) -> dict or None
    -------------------------------------------
    Return a single volunteer record dictionary, or None if not found.
    """
    return VOLUNTEER_MANAGER.get_volunteer_record(phone)

def list_deleted_volunteers() -> List[Dict[str, Any]]:
    """
    list_deleted_volunteers() -> list of dict
    -----------------------------------------
    Return all records from DeletedVolunteers in descending order by deleted_at.
    Each record is a dictionary with phone, name, available, and deleted_at.
    """
    return VOLUNTEER_MANAGER.list_deleted_volunteers()

def list_all_volunteers_list() -> List[Dict[str, Any]]:
    """
    list_all_volunteers_list() -> list of dict
    ------------------------------------------
    Return a list of all volunteer records (phone, name, available).
    """
    return VOLUNTEER_MANAGER.list_all_volunteers_list()

# End of core/api/volunteer_api.py