#!/usr/bin/env python
"""
core/exceptions.py - Central module for custom exception classes for easier error handling and logging.
"""

class VolunteerError(Exception):
    """Raised when volunteer-related operations encounter invalid or inconsistent data."""
    pass

class ResourceError(Exception):
    """Raised when resource-related operations fail due to invalid input or database constraints."""
    pass

# End of core/exceptions.py