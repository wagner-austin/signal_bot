#!/usr/bin/env python
"""
managers/volunteer/volunteer_common.py - Common utilities for volunteer management.
Provides helper functions and shared constants used across volunteer modules.
"""

def normalize_name(name: str, fallback: str) -> str:
    """
    normalize_name - Normalizes a volunteer's name.
    Returns "Anonymous" if the name equals the fallback.
    """
    return name if name != fallback else "Anonymous"

# End of managers/volunteer/volunteer_common.py