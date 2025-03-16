"""
managers/utils.py
-----------------
Utility methods shared across manager modules to avoid circular imports.
No database or flow-state changes needed.
"""

import re

def normalize_name(name: str, fallback: str) -> str:
    """
    normalize_name - Normalizes a volunteer's name.
    Returns "Anonymous" if the name equals the fallback or if the name looks like a phone number.
    """
    if name == fallback or re.fullmatch(r'\+?\d+', name):
        return "Anonymous"
    return name

# End of managers/utils.py