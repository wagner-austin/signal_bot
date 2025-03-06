"""
plugins/commands.py
-------------------
Contains the implementation of command plugins for the Signal bot.
Each command is registered using the @plugin decorator from the unified plugins/manager.
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
        state_machine (BotStateMachine): The bot's state machine instance.
        msg_timestamp (Optional[int]): The timestamp of the message.

    Returns:
        str: A message indicating the result of the volunteer assignment.
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
        args (str): The arguments provided by the user (ignored).
        sender (str): The sender's phone number.
        state_machine (BotStateMachine): The bot's state machine instance.
        msg_timestamp (Optional[int]): The timestamp of the message.

    Returns:
        str: The string "yes".
    """
    return "yes"

@plugin('shutdown')
def shutdown_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command to shut down the bot gracefully.
    Expected format: "@bot shutdown"

    Args:
        args (str): The arguments provided by the user (ignored).
        sender (str): The sender's phone number.
        state_machine (BotStateMachine): The bot's state machine instance.
        msg_timestamp (Optional[int]): The timestamp of the message.

    Returns:
        str: A message confirming that the bot is shutting down.
    """
    state_machine.shutdown()
    return "Bot is shutting down."

@plugin('test_all')
async def test_all_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command to run all integration tests.
    Invokes tests for message parsing, volunteer assignment, state transitions,
    and simulated message sending. Returns a summary of test results.
    
    Args:
        args (str): The arguments provided by the user (ignored).
        sender (str): The sender's phone number.
        state_machine (BotStateMachine): The bot's state machine instance.
        msg_timestamp (Optional[int]): The timestamp of the message.
    
    Returns:
        str: Summary of integration test results.
    """
    from tests.test_all import run_tests
    summary = await run_tests()
    return summary

# End of plugins/commands.py