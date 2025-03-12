#!/usr/bin/env python
"""
cli/events_cli.py - CLI tools for event-related operations.
Delegates listing to the manager, uses print_results + formatters for consistent output.
"""

from cli.formatters import format_event, format_event_speaker
from cli.common import print_results
from managers.event_manager import list_all_events, list_all_event_speakers

def list_events_cli():
    """
    list_events_cli - List all events by calling managers.event_manager.list_all_events().
    Uses print_results + format_event for standardized output.
    """
    print_results(list_all_events(), format_event, "No events found.")

def list_event_speakers_cli():
    """
    list_event_speakers_cli - List all event speakers by calling managers.event_manager.list_all_event_speakers().
    Uses print_results + format_event_speaker for standardized output.
    """
    print_results(list_all_event_speakers(), format_event_speaker, "No event speakers found.")

# End of cli/events_cli.py