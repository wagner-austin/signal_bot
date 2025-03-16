"""
plugins/commands/formatters.py - Formatters for volunteer data.
Provides helper functions to format volunteer and deleted volunteer records.
"""

def _ensure_dict(item):
    """
    Ensure that the provided item is a dictionary.
    If it's a sqlite3.Row (or similar), convert it to a dict.
    """
    if not isinstance(item, dict):
        return dict(item)
    return item

def format_volunteer(vol: dict) -> str:
    """
    Format a single volunteer record dictionary.
    """
    vol = _ensure_dict(vol)
    phone = vol.get("phone")
    name = vol.get("name")
    available = vol.get("available")
    return (
        f"Phone: {phone}\n"
        f"Name: {name}\n"
        f"Available: {available}\n"
        + "-" * 40
    )

def format_deleted_volunteer(data: dict) -> str:
    """
    Format a deleted volunteer record.
    """
    data = _ensure_dict(data)
    return (
        f"Phone: {data.get('phone')}\n"
        f"Name: {data.get('name')}\n"
        f"Available: {data.get('available')}\n"
        f"Deleted At: {data.get('deleted_at')}\n"
        + "-" * 40
    )

# End of plugins/commands/formatters.py