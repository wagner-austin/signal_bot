#!/usr/bin/env python
"""
cli/formatters.py - CLI formatters for presenting data.
Provides helper functions to convert raw data dictionaries from business logic into formatted strings.
Now updated to unify volunteer formatting with a single dictionary param.
"""

def _ensure_dict(item) -> dict:
    """
    Ensure that the provided item is a dictionary.
    If it's a sqlite3.Row (or similar), convert it to a dict.
    """
    if not isinstance(item, dict):
        return dict(item)
    return item

def format_event(event: dict) -> str:
    """
    Format a single event record.
    """
    event = _ensure_dict(event)
    return (
        f"Event ID: {event.get('event_id')}\n"
        f"Title: {event.get('title')}\n"
        f"Date: {event.get('date')}\n"
        f"Time: {event.get('time')}\n"
        f"Location: {event.get('location')}\n"
        f"Description: {event.get('description')}\n"
        + "-" * 40
    )

def format_event_speaker(speaker: dict) -> str:
    """
    Format a single event speaker record.
    """
    speaker = _ensure_dict(speaker)
    return (
        f"ID: {speaker.get('id')}\n"
        f"Event ID: {speaker.get('event_id')}\n"
        f"Speaker Name: {speaker.get('speaker_name')}\n"
        f"Speaker Topic: {speaker.get('speaker_topic')}\n"
        f"Created At: {speaker.get('created_at')}\n"
        + "-" * 40
    )

def format_log(log: dict) -> str:
    """
    Format a single command log record.
    """
    log = _ensure_dict(log)
    return (
        f"ID: {log.get('id')}\n"
        f"Sender: {log.get('sender')}\n"
        f"Command: {log.get('command')}\n"
        f"Args: {log.get('args')}\n"
        f"Timestamp: {log.get('timestamp')}\n"
        + "-" * 40
    )

def format_resource(resource: dict) -> str:
    """
    Format a single resource record.
    """
    resource = _ensure_dict(resource)
    title = resource.get('title') if resource.get('title') else 'N/A'
    return (
        f"ID: {resource.get('id')}\n"
        f"Category: {resource.get('category')}\n"
        f"Title: {title}\n"
        f"URL: {resource.get('url')}\n"
        f"Created At: {resource.get('created_at')}\n"
        + "-" * 40
    )

def format_task(task: dict) -> str:
    """
    Format a single task record.
    """
    task = _ensure_dict(task)
    return (
        f"Task ID: {task.get('task_id')}\n"
        f"Description: {task.get('description')}\n"
        f"Status: {task.get('status')}\n"
        f"Created At: {task.get('created_at')}\n"
        f"Created By: {task.get('created_by_name')}\n"
        f"Assigned To: {task.get('assigned_to_name')}\n"
        + "-" * 40
    )

def format_volunteer(vol: dict) -> str:
    """
    format_volunteer - Format a single volunteer record dictionary.
    """
    vol = _ensure_dict(vol)
    phone = vol.get("phone")
    name = vol.get("name")
    skills = ", ".join(vol.get("skills", [])) if vol.get("skills") else "None"
    available = vol.get("available")
    current_role = vol.get("current_role")
    return (
        f"Phone: {phone}\n"
        f"Name: {name}\n"
        f"Skills: {skills}\n"
        f"Available: {available}\n"
        f"Current Role: {current_role}\n"
        + "-" * 40
    )

def format_deleted_volunteer(data: dict) -> str:
    """
    Format a deleted volunteer record.
    """
    data = _ensure_dict(data)
    skills = ", ".join(data.get('skills', '').split(',')) if data.get('skills') else "None"
    return (
        f"Phone: {data.get('phone')}\n"
        f"Name: {data.get('name')}\n"
        f"Skills: {skills}\n"
        f"Available: {data.get('available')}\n"
        f"Current Role: {data.get('current_role')}\n"
        f"Deleted At: {data.get('deleted_at')}\n"
        + "-" * 40
    )

# End of cli/formatters.py