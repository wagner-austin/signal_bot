#!/usr/bin/env python
"""
core/exceptions.py - Central module for custom exception classes.
Removed ResourceError; only VolunteerError remains for volunteer-related operations.
"""

class DomainError(Exception):
    """
    Base class for domain-specific exceptions with a unified error message format.
    """
    def __init__(self, message: str):
        formatted_message = f"{self.__class__.__name__}: {message}"
        super().__init__(formatted_message)

class VolunteerError(DomainError):
    """
    Raised when volunteer-related operations encounter invalid or inconsistent data.
    """
    pass

# End of core/exceptions.py