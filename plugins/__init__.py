"""
__init__.py
-----------
Plugin definitions for the Signal bot.
Each plugin is registered via the @plugin decorator from the unified plugins/manager.
This module exports the public plugin commands for use in the bot.
"""

from typing import Optional
from plugins.manager import plugin
from managers.volunteer_manager import VOLUNTEER_MANAGER
from core.state import BotStateMachine

@plugin('assign')
def assign_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command to assign a volunteer based on a skill.
    Expected format: "@bot assign <Skill Name>"
    
    Args:
        args (str): The arguments provided by the user.
        sender (str): The sender's phone number.
        state_machine (BotStateMachine): The bot's state machine.
        msg_timestamp (Optional[int]): The timestamp of the message.
        
    Returns:
        str: The result of the volunteer assignment.
    """
    skill = args.strip()
    if not skill:
        return "Usage: @bot assign <Skill Name>"
    volunteer = VOLUNTEER_MANAGER.assign_volunteer(skill, skill)
    if volunteer:
        return f"{skill} assigned to {volunteer}."
    else:
        return f"No available volunteer for {skill}."

@plugin('test')
def test_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command for testing.
    Expected format: "test" or "@bot test"
    Responds with "yes".
    
    Args:
        args (str): The arguments provided by the user.
        sender (str): The sender's phone number.
        state_machine (BotStateMachine): The bot's state machine.
        msg_timestamp (Optional[int]): The timestamp of the message.
        
    Returns:
        str: A confirmation response.
    """
    return "yes"

@plugin('shutdown')
def shutdown_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command to shut down the bot gracefully.
    Expected format: "@bot shutdown"
    
    Args:
        args (str): The arguments provided by the user.
        sender (str): The sender's phone number.
        state_machine (BotStateMachine): The bot's state machine.
        msg_timestamp (Optional[int]): The timestamp of the message.
        
    Returns:
        str: A shutdown confirmation message.
    """
    state_machine.shutdown()
    return "Bot is shutting down."
