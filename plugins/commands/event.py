"""
plugins/commands/event.py - Event command plugins.
Provides commands to display event information.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.volunteer_manager import VOLUNTEER_MANAGER

@plugin(commands=['event'], canonical='event')
def event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    event - Shows a summary of the next event.
    Usage: "@bot event"
    """
    from core.event_config import EVENT_DETAILS
    event = EVENT_DETAILS.get("upcoming_event", {})
    if not event:
        return "No upcoming event information available."
    summary = (
        f"{event.get('title', 'Next Event')}\n\n"
        f"{event.get('date', 'Unknown Date')} from {event.get('time', 'Unknown Time')}.\n\n"
        f"{event.get('description', 'No description')}\n\n"
        f"{event.get('location', 'Unknown Location')}"
    )
    return summary

# End of plugins/commands/event.py