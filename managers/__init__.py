"""
managers/__init__.py
--------------------
Imports and exposes the main managers for volunteer data, roles, and skills.
"""

__all__ = [
    "volunteer_manager",
    "VOLUNTEER_MANAGER",
]

from .volunteer_manager import VOLUNTEER_MANAGER

# End of managers/__init__.py