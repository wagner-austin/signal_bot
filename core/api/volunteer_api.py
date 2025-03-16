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
    volunteer_status as mgr_volunteer_status
)

logger = logging.getLogger(__name__)

def register_volunteer(phone: str,
                       name: str,
                       skills: List[str],
                       available: bool = True,
                       current_role: Optional[str] = None) -> str:
    """
    register_volunteer(phone, name, skills, available=True, current_role=None) -> str
    ---------------------------------------------------------------------------------
    Create or update a volunteer with the given phone, name, and skill list.
    Returns a user-facing confirmation message. Raises VolunteerError if invalid phone.

    Usage Example:
        from core.api.volunteer_api import register_volunteer

        msg = register_volunteer("+15551234567", "Alice", ["teaching", "writing"], True)
        print(msg)
    """
    return mgr_register_volunteer(phone, name, skills, available, current_role)

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

def volunteer_status() -> str:
    """
    volunteer_status() -> str
    --------------------------
    Returns a text summary of all volunteers' availability and roles.
    This is primarily for debugging or listing in a plugin command.
    """
    return mgr_volunteer_status()

# End of core/api/volunteer_api.py