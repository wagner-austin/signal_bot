#!/usr/bin/env python
"""
plugins/commands/volunteer.py
-----------------------------
Volunteer command plugins.
Handles volunteer registration, editing, deletion, skill management.
Now uses format_deleted_volunteer for listing deleted volunteers.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from core.messages import (
    REGISTRATION_WELCOME, ALREADY_REGISTERED, EDIT_PROMPT,
    DELETION_PROMPT, DELETION_CONFIRM, DELETION_CANCELED
)
from managers.volunteer_manager import VOLUNTEER_MANAGER
from core.constants import SKIP_VALUES
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import (
    PluginArgError,
    VolunteerFindModel,
    VolunteerAddSkillsModel,
    validate_model
)
import logging
from core.exceptions import ResourceError, VolunteerError
from core.plugin_usage import (
    USAGE_VOLUNTEER_STATUS, USAGE_REGISTER, USAGE_REGISTER_PARTIAL, USAGE_EDIT, USAGE_DELETE, 
    USAGE_SKILLS, USAGE_FIND, USAGE_ADD_SKILLS
)
from managers.user_states_manager import (
    create_flow, pause_flow, resume_flow, get_flow_state
)
from plugins.commands.formatters import format_deleted_volunteer, format_volunteer

logger = logging.getLogger(__name__)

@plugin('volunteer status', canonical='volunteer status')
def volunteer_status_command(args: str, sender: str, state_machine: BotStateMachine,
                             msg_timestamp: Optional[int] = None) -> str:
    """
    volunteer status - Display the current volunteer status.
    Uses format_volunteer to unify output if desired.
    """
    try:
        all_vols = VOLUNTEER_MANAGER.list_all_volunteers_list()  # returns list of volunteer dicts
        if not all_vols:
            return "No volunteers found."
        return "\n".join(format_volunteer(v) for v in all_vols)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"volunteer_status_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"volunteer_status_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in volunteer_status_command."

@plugin('check in', canonical='check in')
def check_in_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    check in - Marks a volunteer as available.
    """
    try:
        return VOLUNTEER_MANAGER.check_in(sender)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"check_in_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"check_in_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in check_in_command."

@plugin('register', canonical='register')
def register_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    register - Interactive volunteer registration.
    """
    try:
        text = args.strip().lower()
        if text == "cancel":
            pause_flow(sender, "registration")
            return "Cancelled."

        if args.strip() and len(args.strip().split()) < 2 and args.strip().lower() not in SKIP_VALUES:
            return USAGE_REGISTER_PARTIAL

        record = VOLUNTEER_MANAGER.list_all_volunteers().get(sender)
        if args.strip():
            if record:
                return ALREADY_REGISTERED.format(name=record['name'])
            else:
                return VOLUNTEER_MANAGER.register_volunteer(sender, args.strip(), [])
        else:
            if record:
                return ALREADY_REGISTERED.format(name=record['name'])
            else:
                create_flow(sender, "registration", start_step="ask_name")
                return REGISTRATION_WELCOME

    except (ResourceError, VolunteerError) as e:
        logger.error(f"register_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"register_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in register_command."

@plugin(
    [
        'edit','change my name please','change my name to','change my name',
        'can you change my name please','can you change my name to','can you change my name',
        'can i change my name to','can i change my name','not my name',"that's not my name",
        'wrong name','i mispelled'
    ],
    canonical='edit',
    help_visible=False
)
def edit_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    edit - Edit your registered name.
    """
    try:
        if args.strip().lower() == "cancel":
            pause_flow(sender, "edit")
            return "Cancelled."

        record = VOLUNTEER_MANAGER.list_all_volunteers().get(sender)
        if not record:
            create_flow(sender, "registration", start_step="ask_name")
            return REGISTRATION_WELCOME
        if not args.strip():
            create_flow(sender, "edit", start_step="ask_new_name")
            return EDIT_PROMPT.format(name=record['name'])
        # If user typed a name inline, just update
        return VOLUNTEER_MANAGER.register_volunteer(sender, args.strip(), [])
    except (ResourceError, VolunteerError) as e:
        logger.error(f"edit_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"edit_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in edit_command."

@plugin(['delete','del','stop','unsubscribe','remove','opt out'], canonical='delete', help_visible=False)
def delete_command(args: str, sender: str, state_machine: BotStateMachine,
                   msg_timestamp: Optional[int] = None) -> str:
    """
    delete - Handles volunteer deletion flow.
    """
    try:
        user_input = args.strip().lower()
        current_flow = get_flow_state(sender)
        if current_flow == "":
            if user_input == "cancel":
                return "Cancelled."
            create_flow(sender, "deletion", start_step="initial")
            return DELETION_PROMPT
        elif current_flow == "deletion":
            if user_input in {"yes", "y", "yea", "sure"}:
                create_flow(sender, "deletion_confirm", start_step="confirm")
                return DELETION_CONFIRM
            else:
                pause_flow(sender, "deletion")
                return DELETION_CANCELED
        elif current_flow == "deletion_confirm":
            if user_input in {"yes", "delete"}:
                confirmation = VOLUNTEER_MANAGER.delete_volunteer(sender)
                pause_flow(sender, "deletion_confirm")
                return confirmation
            else:
                pause_flow(sender, "deletion_confirm")
                return DELETION_CANCELED
        else:
            pause_flow(sender, current_flow)
            return DELETION_CANCELED
    except (ResourceError, VolunteerError) as e:
        logger.error(f"delete_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"delete_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in delete_command."

@plugin('skills', canonical='skills')
def skills_command(args: str, sender: str, state_machine: BotStateMachine,
                   msg_timestamp: Optional[int] = None) -> str:
    """
    skills - Display your current skills.
    """
    try:
        from db.volunteers import get_volunteer_record
        from core.skill_config import AVAILABLE_SKILLS
        record = get_volunteer_record(sender)
        if not record:
            create_flow(sender, "registration", start_step="ask_name")
            return REGISTRATION_WELCOME
        current_skills = record.get("skills", [])
        current_list = "\n".join(f" - {sk}" for sk in current_skills) if current_skills else " - None"
        all_skills = "\n".join(f" - {s}" for s in AVAILABLE_SKILLS)
        name = record.get("name", "Anonymous")
        msg = f"{name} currently has skills:\n{current_list}\n\n"
        msg += "Here is a list of relevant skills you can add:\n" + all_skills
        return msg
    except (ResourceError, VolunteerError) as e:
        logger.error(f"skills_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"skills_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in skills_command."

@plugin('find', canonical='find')
def find_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    find - Finds volunteers with specified skills.
    """
    from db.volunteers import get_all_volunteers
    try:
        tokens = args.split()
        if not tokens:
            raise PluginArgError(USAGE_FIND)
        data = {"skills": [s.lower() for s in tokens]}
        validated = validate_model(data, VolunteerFindModel, USAGE_FIND)
        volunteers = get_all_volunteers()
        matching = []
        for phone, vol_data in volunteers.items():
            vskills = [s.lower() for s in vol_data.get("skills", [])]
            if all(req in vskills for req in validated.skills):
                matching.append(vol_data.get("name", phone))
        if matching:
            return "Volunteers with specified skills: " + ", ".join(matching)
        return "No volunteers found with the specified skills."
    except PluginArgError as e:
        logger.warning(f"find_command PluginArgError: {e}")
        return str(e)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"find_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"find_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in find_command."

@plugin('add skills', canonical='add skills')
def add_skills_command(args: str, sender: str, state_machine: BotStateMachine,
                       msg_timestamp: Optional[int] = None) -> str:
    """
    add skills - Adds skills to your profile.
    """
    from db.volunteers import get_volunteer_record
    try:
        if not args.strip():
            raise PluginArgError(USAGE_ADD_SKILLS)
        record = get_volunteer_record(sender)
        if not record:
            return "You are not registered. Please register first."
        raw_tokens = [t.strip() for t in args.split(",") if t.strip()]
        if not raw_tokens:
            raise PluginArgError(USAGE_ADD_SKILLS)
        data = {"skills": raw_tokens}
        validated = validate_model(data, VolunteerAddSkillsModel, USAGE_ADD_SKILLS)
        return VOLUNTEER_MANAGER.register_volunteer(sender, "skip", validated.skills)
    except PluginArgError as e:
        logger.warning(f"add_skills_command PluginArgError: {e}")
        return str(e)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"add_skills_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"add_skills_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in add_skills_command."

#
# Updated to use format_deleted_volunteer
#
@plugin('deleted volunteers', canonical='deleted volunteers')
def deleted_volunteers_command(args: str, sender: str, state_machine: BotStateMachine,
                               msg_timestamp: Optional[int] = None) -> str:
    """
    deleted volunteers - Lists all deleted volunteer records, using format_deleted_volunteer.
    """
    try:
        recs = VOLUNTEER_MANAGER.list_deleted_volunteers()
        if not recs:
            return "No deleted volunteers found."
        return "\n".join(format_deleted_volunteer(r) for r in recs)
    except Exception as e:
        logger.error(f"deleted_volunteers_command error: {e}", exc_info=True)
        return "An internal error occurred in deleted_volunteers_command."

# End of plugins/commands/volunteer.py