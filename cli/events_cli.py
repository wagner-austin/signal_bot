#!/usr/bin/env python
"""
cli/events_cli.py --- CLI tools for event-related operations.
Renamed calls to list_all_events for uniform naming.
"""

from cli.formatters import format_event, format_event_speaker
from cli.common import print_results
from managers.event_manager import list_all_events, list_all_event_speakers

def list_events_cli():
    """
    list_events_cli - List all events in the database.
    """
    events = list_all_events()
    print_results(events, format_event, "No events found.")

def list_event_speakers_cli():
    """
    list_event_speakers_cli - List all event speakers.
    """
    speakers = list_all_event_speakers()
    print_results(speakers, format_event_speaker, "No event speakers found.")

# End of cli/events_cli.py