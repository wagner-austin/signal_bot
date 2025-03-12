#!/usr/bin/env python
"""
cli/events_cli.py --- CLI tools for event-related operations.
Provides functions to list events and event speakers using a dedicated formatter for presentation.
Delegates data retrieval to the event manager.
"""

from cli.formatters import format_event, format_event_speaker
from cli.common import print_results
from core.event_manager import list_events, list_all_event_speakers

def list_events_cli():
    """
    list_events_cli - List all events in the database.
    Retrieves event data via event_manager and uses a formatter to present the data.
    """
    events = list_events()
    print_results(events, format_event, "No events found.")

def list_event_speakers_cli():
    """
    list_event_speakers_cli - List all event speakers.
    Retrieves speaker data via event_manager and uses a formatter to present the data.
    """
    speakers = list_all_event_speakers()
    print_results(speakers, format_event_speaker, "No event speakers found.")

# End of cli/events_cli.py