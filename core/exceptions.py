#!/usr/bin/env python
"""
core/exceptions.py - Central module for custom exception classes with unified error message formatting.
Provides a base exception class to enforce consistent error messaging across domain errors.
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

class ResourceError(DomainError):
    """
    Raised when resource-related operations fail due to invalid input or database constraints.
    """
    pass

# End of core/exceptions.py