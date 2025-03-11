#!/usr/bin/env python
"""
plugins/commands/system.py --- System command plugins.
Provides system-level commands such as assign, test, shutdown, info, weekly update, theme, plan theme, and status.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.volunteer_manager import VOLUNTEER_MANAGER
from core.metrics import get_uptime
import core.metrics
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import PluginArgError

@plugin('assign', canonical='assign')
def assign_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    assign - Assign a volunteer based on a required skill.
    Usage: "@bot assign <Skill Name>"
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if not tokens:
            raise PluginArgError("Usage: @bot assign <Skill Name>")
        skill = " ".join(tokens)
        volunteer = VOLUNTEER_MANAGER.assign_volunteer(skill, skill)
        if volunteer:
            return f"{skill} assigned to {volunteer}."
        return f"No available volunteer for {skill}."
    except PluginArgError as e:
        return str(e)

@plugin('test', canonical='test')
def plugin_test_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    test - Test command for verifying bot response.
    Usage: "@bot test"
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if tokens:
            raise PluginArgError("Usage: @bot test")
        return "yes"
    except PluginArgError as e:
        return str(e)

@plugin('shutdown', canonical='shutdown')
def shutdown_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    shutdown - Shut down the bot gracefully.
    If extra arguments are provided, usage error.
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if tokens:
            raise PluginArgError("Usage: @bot shutdown")
        state_machine.shutdown()
        return "Bot is shutting down."
    except PluginArgError as e:
        return str(e)

@plugin('info', canonical='info')
def info_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    info - Provides a brief overview of the 50501 OC Grassroots Movement.
    Usage: "@bot info"
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if tokens:
            raise PluginArgError("Usage: @bot info")
        return (
            "50501 OC Grassroots Movement is dedicated to upholding the Constitution and ending executive overreach.\n\n"
            "We empower citizens to reclaim democracy and hold power accountable through peaceful, visible, and sustained engagement."
        )
    except PluginArgError as e:
        return str(e)

@plugin('weekly update', canonical='weekly update')
def weekly_update_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    weekly update - Provides a summary of Trump's actions and Democrat advances this week.
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if tokens:
            raise PluginArgError("Usage: @bot weekly update")
        return (
            "Weekly Update:\n\n"
            "Trump Actions:\n - Held rallies, executive orders.\n\n"
            "Democrat Advances:\n - Pushed key legislation, local election wins.\n"
        )
    except PluginArgError as e:
        return str(e)

@plugin('theme', canonical='theme')
def theme_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    theme - Displays the important theme for this week.
    Usage: "@bot theme"
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if tokens:
            raise PluginArgError("Usage: @bot theme")
        return (
            "This Week's Theme:\n"
            "Community Engagement & Accountability."
        )
    except PluginArgError as e:
        return str(e)

@plugin('plan theme', canonical='plan theme')
def plan_theme_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    plan theme - Helps set or plan this week's theme.
    Usage: "@bot plan theme"
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if tokens:
            raise PluginArgError("Usage: @bot plan theme")
        return (
            "Plan Theme:\n"
            "Provide the new theme in a format: 'Theme: <description>'."
        )
    except PluginArgError as e:
        return str(e)

@plugin('status', canonical='status')
def status_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    status - Displays system status including messages per hour, total messages sent, and uptime.
    Usage: "@bot status"
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if tokens:
            raise PluginArgError("Usage: @bot status")
        uptime_seconds = get_uptime()
        uptime_hours = uptime_seconds / 3600 if uptime_seconds > 0 else 0
        sent = core.metrics.messages_sent
        mph = sent if uptime_hours < 1 else sent / uptime_hours
        return (
            f"Status:\n"
            f"Messages sent: {sent}\n"
            f"Uptime: {uptime_seconds:.0f} seconds (~{uptime_hours:.2f} hours)\n"
            f"Messages per hour: {mph:.2f}\n"
            f"System: operational."
        )
    except PluginArgError as e:
        return str(e)

# End plugins/commands/system.py