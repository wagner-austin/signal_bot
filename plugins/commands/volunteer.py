"""
plugins/commands/volunteer.py - Volunteer-related command plugins for the Signal bot.
Includes commands such as volunteer status, check in, feedback, register, edit, delete, and skills.
Utilizes PendingActions to manage interactive registration and deletion flows.
"""

from typing import Optional
from plugins.manager import plugin, get_all_plugins
from core.state import BotStateMachine
from core.database import get_volunteer_record
from managers.volunteer_manager import VOLUNTEER_MANAGER
from managers.pending_actions import PENDING_ACTIONS
from core.messages import (
    REGISTRATION_PROMPT, ALREADY_REGISTERED, EDIT_PROMPT,
    DELETION_PROMPT, NEW_VOLUNTEER_REGISTERED
)

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
         - If the sender is not registered, prompt for registration.
         - If the sender is already registered, inform them and suggest editing.
      2. If invoked with arguments, registers the volunteer,
         returning a confirmation message.
    """
    if args.strip():
        name = args.strip()
        record = get_volunteer_record(sender)
        if record:
            return ALREADY_REGISTERED.format(name=record['name'])
        else:
            return VOLUNTEER_MANAGER.sign_up(sender, name, [])
    else:
        record = get_volunteer_record(sender)
        if record:
            return ALREADY_REGISTERED.format(name=record['name'])
        else:
            PENDING_ACTIONS.set_registration(sender, "register")
            return REGISTRATION_PROMPT

@plugin(['edit', 'change my name please', 'change my name to', 'change my name',
         'change name', 'can you change my name please', 'can you change my name to',
         'can you change my name', 'can i change my name to', 'can i change my name',
         'not my name', "that's not my name", 'wrong name', 'i mispelled'])
def edit_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    edit - Edit your registered name.
    Usage:
      - If invoked without arguments:
          For new users: interpreted as register, initiating the registration process.
          For existing users: prompt for a new name or cancellation.
      - If invoked with arguments, updates the volunteer's name immediately.
    """
    record = get_volunteer_record(sender)
    if not record:
        PENDING_ACTIONS.set_registration(sender, "register")
        return REGISTRATION_PROMPT
    if not args.strip():
        PENDING_ACTIONS.set_registration(sender, "edit")
        return EDIT_PROMPT.format(name=record['name'])
    return VOLUNTEER_MANAGER.sign_up(sender, args.strip(), [])

@plugin(['delete', 'del', 'stop', 'unsubscribe', 'remove', 'opt out'])
def delete_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    delete - Delete your registration.
    Usage:
      - When invoked without arguments, the bot asks for deletion confirmation.
    """
    if not args.strip():
        PENDING_ACTIONS.set_deletion(sender, "initial")
        return DELETION_PROMPT
    PENDING_ACTIONS.set_deletion(sender, "initial")
    return DELETION_PROMPT

@plugin('skills')
def skills_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    skills - Display current skills and list available skills for addition.
    For existing users: Shows their registered skills and available skills.
    For new users: Initiates registration.
    """
    from core.database import get_volunteer_record
    from core.skill_config import AVAILABLE_SKILLS
    record = get_volunteer_record(sender)
    if not record:
        PENDING_ACTIONS.set_registration(sender, "register")
        return REGISTRATION_PROMPT
    else:
        current_skills = record.get("skills", [])
        if current_skills:
            current_skills_formatted = "\n".join([f" - {skill}" for skill in current_skills])
        else:
            current_skills_formatted = " - None"
        available_skills_formatted = "\n".join([f" - {skill}" for skill in AVAILABLE_SKILLS])
        name = record.get("name", "Anonymous")
        message = f"{name} currently has skills:\n{current_skills_formatted}\n\n"
        message += "Here is a list of relevant skills you can add to your profile:\n" + available_skills_formatted
        return message

# End of plugins/commands/volunteer.py
