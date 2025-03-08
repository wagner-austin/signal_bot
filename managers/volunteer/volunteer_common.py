#!/usr/bin/env python
"""
managers/volunteer/volunteer_common.py - Common utilities for volunteer management.
Provides helper functions and shared constants used across volunteer modules.
Ensures volunteer display names are normalized to avoid exposing phone numbers.
"""

import re

def normalize_name(name: str, fallback: str) -> str:
    """
    normalize_name - Normalizes a volunteer's name.
    Returns "Anonymous" if the name equals the fallback or if the name appears to be a phone number.
    
    Args:
        name (str): The volunteer's registered name.
        fallback (str): The fallback identifier (typically the volunteer's phone number).
        
    Returns:
        str: A safe display name that does not reveal any phone numbers.
    """
    # If the registered name is exactly the fallback or matches a phone number pattern, return "Anonymous"
    if name == fallback or re.fullmatch(r'\+?\d+', name):
        return "Anonymous"
    return name

# End of managers/volunteer/volunteer_common.py