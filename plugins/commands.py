"""
plugins/commands.py - Command plugins for the Signal bot.
Implements various command plugins including event summary, detailed event info, registration, and name editing.
"""

from typing import Optional
import difflib
from plugins.manager import plugin, get_all_plugins
from managers.volunteer_manager import VOLUNTEER_MANAGER, PENDING_REGISTRATIONS
from core.state import BotStateMachine
from core.database import get_volunteer_record  # Needed in register_command

@plugin('assign')
def assign_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    assign - Assign a volunteer based on a required skill.
    Expected format: "@bot assign <Skill Name>"
    """
    skill = args.strip()
    if not skill:
        return "Usage: @bot assign <Skill Name>"
    volunteer = VOLUNTEER_MANAGER.assign_volunteer(skill, skill)
    if volunteer:
        return f"{skill} assigned to {volunteer}."
    return f"No available volunteer for {skill}."

@plugin('test')
def test_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    test - Test command for verifying bot response.
    Expected format: "@bot test"
    """
    return "yes"

@plugin('shutdown')
def shutdown_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    shutdown - Shut down the bot gracefully.
    Expected format: "@bot shutdown"
    """
    state_machine.shutdown()
    return "Bot is shutting down."

@plugin('test all')
async def test_all_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    test all - Run integration tests.
    """
    from tests.test_all import run_tests
    summary = await run_tests()
    return summary

@plugin('event')
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
        f"{event.get('date', 'Unknown Date')} "
        f"from {event.get('time', 'Unknown Time')}.\n\n"
        f"{event.get('description', 'No description')}\n\n"
        f"{event.get('location', 'Unknown Location')}"
    )
    return summary

@plugin('event info')
def event_info_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    event info - Provides detailed information on the next event.
    Usage: "@bot event info"
    """
    from core.event_config import EVENT_DETAILS
    event = EVENT_DETAILS.get("upcoming_event", {})
    if not event:
        return "No upcoming event information available."
    skills = VOLUNTEER_MANAGER.get_all_skills()
    details = (
        f"Title: {event.get('title', 'Next Event')}\n"
        f"Date: {event.get('date', 'Unknown')}\n"
        f"Time: {event.get('time', 'Unknown')}\n"
        f"Location: {event.get('location', 'Unknown')}\n"
        f"Description: {event.get('description', 'No description')}\n"
        "Volunteer Roles:"
    )
    for role, person in event.get("volunteer_roles", {}).items():
        details += f"\n  - {role.capitalize()}: {person}"
    details += "\n\nAvailable Skills:\n" + (", ".join(skills) if skills else "No skills recorded.")
    return details

@plugin('volunteer status')
def volunteer_status_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    volunteer status - Display the current status of all volunteers.
    """
    return VOLUNTEER_MANAGER.volunteer_status()

@plugin('check in')
def check_in_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    check in - Check in a volunteer.
    Expected format: "@bot check in" (the sender is assumed to be the volunteer).
    """
    return VOLUNTEER_MANAGER.check_in(sender)

@plugin('feedback')
def feedback_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    feedback - Submit feedback or report issues.
    Expected format: "@bot feedback <Your feedback or report>"
    """
    feedback_text = args.strip()
    if not feedback_text:
        return "Usage: @bot feedback <Your feedback or report>"
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Feedback from {sender}: {feedback_text}")
    return "Thank you for your feedback. It has been logged for review."

@plugin('register')
def register_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    register - Interactive volunteer registration command.
    Handles registration in two steps:
      1. If invoked as "@bot register" without arguments:
         - If the sender is not registered, prompt:
           "Welcome! Please respond with your first and last name to get registered. Or \"skip\" to remain anonymous."
         - If the sender is already registered, reply:
           "You are registered as \"<Existing Name>\". Use command \"@bot edit\" to edit your name."
      2. If invoked with arguments, registers the volunteer,
         returning "New volunteer '<Name>' registered".
    """
    from managers.volunteer_manager import PENDING_REGISTRATIONS, VOLUNTEER_MANAGER
    from core.database import get_volunteer_record
    if args.strip():
        name = args.strip()
        # For registration, if the user sends a name, only allow registration if not already registered.
        record = get_volunteer_record(sender)
        if record:
            return f"You are registered as \"{record['name']}\". Use command \"@bot edit\" to edit your name."
        else:
            return VOLUNTEER_MANAGER.sign_up(sender, name, [])
    else:
        record = get_volunteer_record(sender)
        if record:
            return f"You are registered as \"{record['name']}\". Use command \"@bot edit\" to edit your name."
        else:
            PENDING_REGISTRATIONS[sender] = True
            return "Welcome! Please respond with your first and last name to get registered. Or \"skip\" to remain anonymous."

@plugin('edit')
def edit_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    edit - Edit your registered name.
    Usage: "@bot edit <new first and last name>"
    """
    from core.database import get_volunteer_record
    if not args.strip():
        return "Usage: @bot edit <new first and last name>"
    record = get_volunteer_record(sender)
    if not record:
        return "You are not registered. Please use '@bot register' to register first."
    # Use sign_up to update the volunteer record since it updates if record exists.
    return VOLUNTEER_MANAGER.sign_up(sender, args.strip(), [])

@plugin('help')
def help_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    help - Provides a concise list of available commands.
    Usage: "@bot help"
    """
    commands = get_all_plugins()
    excluded_commands = {"assign", "test", "shutdown", "test all"}
    lines = []
    for cmd, func in sorted(commands.items()):
        if cmd in excluded_commands:
            continue
        doc_line = func.__doc__.strip().splitlines()[0] if func.__doc__ else "No description"
        lines.append(f"@bot {cmd} - {doc_line}")
    return "\n\n".join(lines)

@plugin('more help')
def more_help_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    more help - Provides detailed information for available commands.
    Usage: "@bot more help"
    """
    commands = get_all_plugins()
    excluded_commands = {"assign", "test", "shutdown", "test all"}
    lines = []
    for cmd, func in sorted(commands.items()):
        if cmd in excluded_commands:
            continue
        doc = func.__doc__.strip() if func.__doc__ else "No detailed help available."
        lines.append(f"@bot {cmd}\n{doc}")
    return "\n\n".join(lines)

@plugin('info')
def info_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    info - Provides a brief overview of the 50501 OC Grassroots Movement.
    Usage: "@bot info"
    """
    return (
        "50501 OC Grassroots Movement is dedicated to upholding the Constitution and ending executive overreach. \n\n"
        "Our objective is to foster peaceful, visible, and sustained community engagement through nonviolent protest. "
        "We empower citizens to reclaim democracy and hold power accountable, inspiring change through unity and active resistance."
    )

# End of plugins/commands.py
