#!/usr/bin/env python
"""
cli/events_cli.py - CLI tools for event-related operations.
Provides functions to list events and list event speakers.
"""

from core.database.helpers import execute_sql

def list_events_cli():
    """
    list_events_cli - List all events in the database.
    Displays event ID, title, date, time, location, and description.
    """
    query = "SELECT * FROM Events ORDER BY created_at DESC"
    rows = execute_sql(query, fetchall=True)
    if not rows:
        print("No events found.")
        return
    for row in rows:
        print(f"Event ID: {row['event_id']}")
        print(f"Title: {row['title']}")
        print(f"Date: {row['date']}")
        print(f"Time: {row['time']}")
        print(f"Location: {row['location']}")
        print(f"Description: {row['description']}")
        print("-" * 40)

def list_event_speakers_cli():
    """
    list_event_speakers_cli - List all event speakers.
    Displays speaker details for each event speaker record.
    """
    query = "SELECT * FROM EventSpeakers ORDER BY created_at DESC"
    rows = execute_sql(query, fetchall=True)
    if not rows:
        print("No event speakers found.")
        return
    for row in rows:
        print(f"ID: {row['id']}")
        print(f"Event ID: {row['event_id']}")
        print(f"Speaker Name: {row['speaker_name']}")
        print(f"Speaker Topic: {row['speaker_topic']}")
        print(f"Created At: {row['created_at']}")
        print("-" * 40)

# End of cli/events_cli.py