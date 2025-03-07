"""
plugins/commands.py - Implements command plugins for the Signal bot.
This module uses the VolunteerManager, which now directly interfaces with the database.
"""

from typing import Optional
from plugins.manager import plugin
from managers.volunteer_manager import VOLUNTEER_MANAGER, PENDING_REGISTRATIONS
from core.state import BotStateMachine

@plugin('assign')
def assign_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Assign a volunteer based on a required skill.
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
    Test command for verifying bot response.
    Expected format: "test" or "@bot test"
    """
    return "yes"

@plugin('shutdown')
def shutdown_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Shut down the bot gracefully.
    Expected format: "@bot shutdown"
    """
    state_machine.shutdown()
    return "Bot is shutting down."

@plugin('test_all')
async def test_all_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Run integration tests.
    """
    from tests.test_all import run_tests
    summary = await run_tests()
    return summary

@plugin('event_info')
def event_info_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Display details about the upcoming event.
    """
    from core.event_config import EVENT_DETAILS
    event = EVENT_DETAILS.get("upcoming_event", {})
    if not event:
        return "No upcoming event information available."
    details = (
        f"Event: {event.get('title')}\n"
        f"Date: {event.get('date')}\n"
        f"Time: {event.get('time')}\n"
        f"Location: {event.get('location')}\n"
        f"Description: {event.get('description')}\n"
        f"Volunteer Roles:"
    )
    for role, person in event.get("volunteer_roles", {}).items():
        details += f"\n - {role.capitalize()}: {person}"
    return details

@plugin('volunteer_status')
def volunteer_status_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Display the current status of all volunteers.
    """
    return VOLUNTEER_MANAGER.volunteer_status()

@plugin('check_in')
def check_in_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Check in a volunteer.
    Expected format: "@bot check_in" (the sender is assumed to be the volunteer).
    """
    return VOLUNTEER_MANAGER.check_in(sender)

@plugin('feedback')
def feedback_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Submit feedback or report issues.
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
         - If the sender is not registered, respond with:
           "Please provide your first and last name or skip if you wish"
         - If the sender is already registered, respond with:
           "Volunteer '<Existing Name>' already registered. Provide new name to update if desired."
      2. If invoked with arguments (or a pending update reply), registers or updates the volunteer,
         returning:
         "New volunteer '<Name>' registered" or "Volunteer '<Name>' updated"
    """
    if args.strip():
        name = args.strip()
        return VOLUNTEER_MANAGER.sign_up(sender, name, [])
    else:
        record = get_volunteer_record(sender)
        if record:
            existing_name = record["name"] if record["name"] != sender else "Anonymous"
            PENDING_REGISTRATIONS[sender] = True
            return f"Volunteer '{existing_name}' already registered. Provide new name to update if desired."
        else:
            PENDING_REGISTRATIONS[sender] = True
            return "Please provide your first and last name or skip if you wish"

# End of plugins/commands.py