#!/usr/bin/env python
"""
plugins/commands/volunteer.py --- Volunteer command plugins.
Handles volunteer registration, editing, deletion, and skill management.
USAGE: Refer to usage constants in core/plugin_usage.py (USAGE_VOLUNTEER_STATUS, USAGE_REGISTER, USAGE_REGISTER_PARTIAL, USAGE_EDIT, USAGE_DELETE, 
USAGE_SKILLS, USAGE_FIND, USAGE_ADD_SKILLS)
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
from managers.user_states_manager import set_flow_state, get_flow_state, clear_flow_state

logger = logging.getLogger(__name__)

@plugin('volunteer status', canonical='volunteer status')
def volunteer_status_command(args: str, sender: str, state_machine: BotStateMachine,
                             msg_timestamp: Optional[int] = None) -> str:
    """
    volunteer status - Display the current volunteer status.
    
    USAGE: {USAGE_VOLUNTEER_STATUS}
    """
    try:
        return VOLUNTEER_MANAGER.volunteer_status()
    except (ResourceError, VolunteerError) as e:
        logger.error(f"volunteer_status_command domain error: {e}", exc_info=True)
        error_msg = str(e)
        if ":" in error_msg:
            error_msg = error_msg.split(":", 1)[1].strip()
        return f"An error occurred: {error_msg}"
    except Exception as e:
        logger.error(f"volunteer_status_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in volunteer_status_command."

@plugin('check in', canonical='check in')
def check_in_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    check in - Marks a volunteer as available.
    
    USAGE: {USAGE_VOLUNTEER_STATUS}
    """
    try:
        return VOLUNTEER_MANAGER.check_in(sender)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"check_in_command domain error: {e}", exc_info=True)
        error_msg = str(e)
        if ":" in error_msg:
            error_msg = error_msg.split(":", 1)[1].strip()
        return f"An error occurred: {error_msg}"
    except Exception as e:
        logger.error(f"check_in_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in check_in_command."

@plugin('register', canonical='register')
def register_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    register - Interactive volunteer registration.
    
    USAGE: {USAGE_REGISTER}
    """
    try:
        if args.strip().lower() == "cancel":
            clear_flow_state(sender)
            return "Cancelled."
        
        if args.strip() and len(args.strip().split()) < 2 and args.strip().lower() not in SKIP_VALUES:
            return USAGE_REGISTER_PARTIAL

        record = VOLUNTEER_MANAGER.list_all_volunteers().get(sender)
        if args.strip():
            if record:
                return ALREADY_REGISTERED.format(name=record['name'])
            else:
                clear_flow_state(sender)
                return VOLUNTEER_MANAGER.register_volunteer(sender, args.strip(), [])
        else:
            if record:
                return ALREADY_REGISTERED.format(name=record['name'])
            else:
                set_flow_state(sender, "registration")
                return REGISTRATION_WELCOME
    except (ResourceError, VolunteerError) as e:
        logger.error(f"register_command domain error: {e}", exc_info=True)
        error_msg = str(e)
        if ":" in error_msg:
            error_msg = error_msg.split(":", 1)[1].strip()
        return f"An error occurred: {error_msg}"
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
    
    USAGE: {USAGE_EDIT}
    """
    try:
        if args.strip().lower() == "cancel":
            clear_flow_state(sender)
            return "Cancelled."
        
        record = VOLUNTEER_MANAGER.list_all_volunteers().get(sender)
        if not record:
            set_flow_state(sender, "registration")
            return REGISTRATION_WELCOME
        if not args.strip():
            set_flow_state(sender, "edit")
            return EDIT_PROMPT.format(name=record['name'])
        clear_flow_state(sender)
        return VOLUNTEER_MANAGER.register_volunteer(sender, args.strip(), [])
    except (ResourceError, VolunteerError) as e:
        logger.error(f"edit_command domain error: {e}", exc_info=True)
        error_msg = str(e)
        if ":" in error_msg:
            error_msg = error_msg.split(":", 1)[1].strip()
        return f"An error occurred: {error_msg}"
    except Exception as e:
        logger.error(f"edit_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in edit_command."

@plugin(['delete','del','stop','unsubscribe','remove','opt out'], canonical='delete', help_visible=False)
def delete_command(args: str, sender: str, state_machine: BotStateMachine,
                   msg_timestamp: Optional[int] = None) -> str:
    """
    delete - Handles volunteer deletion flow.
    On initial invocation (no deletion flow active), it sets the flow state to "deletion"
    and returns a prompt asking if the user wants to delete their registration.
    If already in the "deletion" flow and the user replies affirmatively (e.g., "yes", "y", "yea", "sure"),
    the flow state is updated to "deletion_confirm" and a confirmation prompt is returned.
    If in the "deletion_confirm" state and the user confirms with "yes" or "delete",
    the volunteer record is deleted and the flow state cleared.
    Any non-affirmative response cancels the deletion flow.
    
    USAGE: {USAGE_DELETE}
    """
    try:
        user_input = args.strip().lower()
        current_flow = get_flow_state(sender)
        if current_flow == "":
            # No deletion flow active; start it.
            if user_input == "cancel":
                return "Cancelled."
            set_flow_state(sender, "deletion")
            return DELETION_PROMPT
        elif current_flow == "deletion":
            # In initial deletion step.
            if user_input in {"yes", "y", "yea", "sure"}:
                set_flow_state(sender, "deletion_confirm")
                return DELETION_CONFIRM
            else:
                clear_flow_state(sender)
                return DELETION_CANCELED
        elif current_flow == "deletion_confirm":
            # In confirmation step.
            if user_input in {"yes", "delete"}:
                confirmation = VOLUNTEER_MANAGER.delete_volunteer(sender)
                clear_flow_state(sender)
                return confirmation
            else:
                clear_flow_state(sender)
                return DELETION_CANCELED
        else:
            clear_flow_state(sender)
            return DELETION_CANCELED
    except (ResourceError, VolunteerError) as e:
        logger.error(f"delete_command domain error: {e}", exc_info=True)
        error_msg = str(e)
        if ":" in error_msg:
            error_msg = error_msg.split(":", 1)[1].strip()
        return f"An error occurred: {error_msg}"
    except Exception as e:
        logger.error(f"delete_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in delete_command."

@plugin('skills', canonical='skills')
def skills_command(args: str, sender: str, state_machine: BotStateMachine,
                   msg_timestamp: Optional[int] = None) -> str:
    """
    skills - Display your current skills.
    
    USAGE: {USAGE_SKILLS}
    """
    try:
        from core.database import get_volunteer_record
        from core.skill_config import AVAILABLE_SKILLS
        record = get_volunteer_record(sender)
        if not record:
            set_flow_state(sender, "registration")
            return REGISTRATION_WELCOME
        else:
            current_skills = record.get("skills", [])
            current_skills_formatted = "\n".join([f" - {skill}" for skill in current_skills]) if current_skills else " - None"
            available_skills_formatted = "\n".join([f" - {skill}" for skill in AVAILABLE_SKILLS])
            name = record.get("name", "Anonymous")
            message = f"{name} currently has skills:\n{current_skills_formatted}\n\n"
            message += "Here is a list of relevant skills you can add:\n" + available_skills_formatted
            return message
    except (ResourceError, VolunteerError) as e:
        logger.error(f"skills_command domain error: {e}", exc_info=True)
        error_msg = str(e)
        if ":" in error_msg:
            error_msg = error_msg.split(":", 1)[1].strip()
        return f"An error occurred: {error_msg}"
    except Exception as e:
        logger.error(f"skills_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in skills_command."

@plugin('find', canonical='find')
def find_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    find - Finds volunteers with specified skills.
    
    USAGE: {USAGE_FIND}
    """
    try:
        from core.database import get_all_volunteers
        raw_tokens = args.split()
        if not raw_tokens:
            raise PluginArgError(USAGE_FIND)
        data = {"skills": [s.lower() for s in raw_tokens]}
        validated = validate_model(data, VolunteerFindModel, USAGE_FIND)
        volunteers = get_all_volunteers()
        matching_volunteers = []
        for phone, data_v in volunteers.items():
            volunteer_skills = [s.lower() for s in data_v.get("skills", [])]
            if all(req in volunteer_skills for req in validated.skills):
                matching_volunteers.append(data_v.get("name", phone))
        if matching_volunteers:
            return "Volunteers with specified skills: " + ", ".join(matching_volunteers)
        else:
            return "No volunteers found with the specified skills."
    except PluginArgError as e:
        logger.warning(f"find_command PluginArgError: {e}")
        return str(e)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"find_command domain error: {e}", exc_info=True)
        error_msg = str(e)
        if ":" in error_msg:
            error_msg = error_msg.split(":", 1)[1].strip()
        return f"An error occurred: {error_msg}"
    except Exception as e:
        logger.error(f"find_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in find_command."

@plugin('add skills', canonical='add skills')
def add_skills_command(args: str, sender: str, state_machine: BotStateMachine,
                       msg_timestamp: Optional[int] = None) -> str:
    """
    add skills - Adds skills to your profile.
    
    USAGE: {USAGE_ADD_SKILLS}
    """
    try:
        if not args.strip():
            raise PluginArgError(USAGE_ADD_SKILLS)
        from core.database import get_volunteer_record
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
        error_msg = str(e)
        if ":" in error_msg:
            error_msg = error_msg.split(":", 1)[1].strip()
        return f"An error occurred: {error_msg}"
    except Exception as e:
        logger.error(f"add_skills_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in add_skills_command."

# End of plugins/commands/volunteer.py