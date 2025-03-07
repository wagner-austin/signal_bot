"""
plugins/commands/volunteer.py - Volunteer-related command plugins.
Includes commands such as volunteer status, check in, register, edit, delete, skills,
find (by skill), and add skills to your profile.
Utilizes PendingActions for interactive flows.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from core.database import get_volunteer_record
from managers.volunteer_manager import VOLUNTEER_MANAGER
from managers.pending_actions import PENDING_ACTIONS
from core.messages import (
    REGISTRATION_PROMPT, ALREADY_REGISTERED, EDIT_PROMPT,
    DELETION_PROMPT, NEW_VOLUNTEER_REGISTERED
)

@plugin('volunteer status', canonical='volunteer status')
def volunteer_status_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    volunteer status - Display the current status of all volunteers.
    """
    return VOLUNTEER_MANAGER.volunteer_status()

@plugin('check in', canonical='check in')
def check_in_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    check in - Check in a volunteer.
    Expected format: "@bot check in" (the sender is assumed to be the volunteer).
    """
    return VOLUNTEER_MANAGER.check_in(sender)

@plugin('register', canonical='register')
def register_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    register - Interactive volunteer registration command.
    If invoked without arguments, prompts for registration; otherwise registers the volunteer.
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

@plugin(['edit', 'change my name please', 'change my name to', 'change my name', 'change name',
         'can you change my name please', 'can you change my name to', 'can you change my name',
         'can i change my name to', 'can i change my name', 'not my name', "that's not my name",
         'wrong name', 'i mispelled'], canonical='edit', help_visible=False)
def edit_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    edit - Edit your registered name.
    If no arguments are provided, initiates an interactive edit; otherwise updates the name.
    """
    record = get_volunteer_record(sender)
    if not record:
        PENDING_ACTIONS.set_registration(sender, "register")
        return REGISTRATION_PROMPT
    if not args.strip():
        PENDING_ACTIONS.set_registration(sender, "edit")
        return EDIT_PROMPT.format(name=record['name'])
    return VOLUNTEER_MANAGER.sign_up(sender, args.strip(), [])

@plugin(['delete', 'del', 'stop', 'unsubscribe', 'remove', 'opt out'], canonical='delete', help_visible=False)
def delete_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    delete - Delete your registration.
    When invoked without arguments, asks for deletion confirmation.
    """
    if not args.strip():
        PENDING_ACTIONS.set_deletion(sender, "initial")
        return DELETION_PROMPT
    PENDING_ACTIONS.set_deletion(sender, "initial")
    return DELETION_PROMPT

@plugin('skills', canonical='skills')
def skills_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    skills - Display your current skills and list available skills for addition.
    If not registered, initiates the registration process.
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

@plugin('find', canonical='find')
def find_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    find - Finds volunteers with the specified skill(s).
    Usage: "@bot find <skill1> <skill2> ..."
    """
    skills = [s.strip().lower() for s in args.split() if s.strip()]
    if not skills:
        return "Usage: @bot find <skill1> <skill2> ..."
    
    from core.database import get_all_volunteers
    volunteers = get_all_volunteers()
    matching_volunteers = []
    for phone, data in volunteers.items():
        volunteer_skills = [s.lower() for s in data.get("skills", [])]
        if all(skill in volunteer_skills for skill in skills):
            matching_volunteers.append(data.get("name", phone))
    if matching_volunteers:
        return "Volunteers with specified skills: " + ", ".join(matching_volunteers)
    else:
        return "No volunteers found with the specified skills."

@plugin('add skills', canonical='add skills')
def add_skills_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    add skills - Adds skills to your profile.
    Usage: "@bot add skills <skill1>, <skill2>, ..."
    """
    skills = [s.strip() for s in args.split(",") if s.strip()]
    if not skills:
        return "Usage: @bot add skills <skill1>, <skill2>, ..."
    record = get_volunteer_record(sender)
    if not record:
        return "You are not registered. Please register first."
    # Use the sign-up function to update the volunteer's skills without changing the name.
    return VOLUNTEER_MANAGER.sign_up(sender, "skip", skills)

# End of plugins/commands/volunteer.py