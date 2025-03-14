"""
managers/__init__.py
--------------------
Imports and exposes the main managers for volunteer data, roles, and skills.
"""

__all__ = [
    "volunteer_manager",
    "volunteer_role_manager",
    "volunteer_skills_manager",
    "VOLUNTEER_MANAGER",
    "ROLE_MANAGER",
    "SKILLS_MANAGER"
]

from .volunteer_manager import VOLUNTEER_MANAGER
from .volunteer_role_manager import ROLE_MANAGER
from .volunteer_skills_manager import SKILLS_MANAGER

# End of managers/__init__.py