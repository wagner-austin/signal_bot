"""
core/database/__init__.py - Database module for the Signal bot.
Re-exports functions from submodules for unified access.
"""

from .connection import get_connection
from .schema import init_db
from .volunteers import (
    parse_skills,
    get_all_volunteers,
    get_volunteer_record,
    add_volunteer_record,
    update_volunteer_record,
    delete_volunteer_record,
    add_deleted_volunteer_record,
    remove_deleted_volunteer_record,
)
from .logs import log_command
from .resources import add_resource, list_resources, remove_resource

# End of core/database/__init__.py