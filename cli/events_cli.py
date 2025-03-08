#!/usr/bin/env python
"""
cli/events_cli.py - CLI tools for event-related operations.
Provides functions to list events and list event speakers using a dedicated formatter for presentation.
"""

from core.database.helpers import execute_sql
from cli.formatters import format_event, format_event_speaker
from cli.common import print_results

def list_events_cli():
    """
    list_events_cli - List all events in the database.
    Retrieves event data from the business logic and uses a formatter to present the data.
    """
    query = "SELECT * FROM Events ORDER BY created_at DESC"
    rows = execute_sql(query, fetchall=True)
    print_results(rows, format_event, "No events found.")

def list_event_speakers_cli():
    """
    list_event_speakers_cli - List all event speakers.
    Retrieves speaker data and uses a formatter to present the data.
    """
    query = "SELECT * FROM EventSpeakers ORDER BY created_at DESC"
    rows = execute_sql(query, fetchall=True)
    print_results(rows, format_event_speaker, "No event speakers found.")

# End of cli/events_cli.py