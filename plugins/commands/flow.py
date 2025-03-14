#!/usr/bin/env python
"""
plugins/commands/flow.py
------------------------
Flow management plugin commands.
Allows listing, switching, pausing, and resuming flows.

CHANGES:
 - New plugin for multi-flow approach.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.user_states_manager import list_flows, resume_flow, pause_flow, create_flow

@plugin(commands=["flow"], canonical="flow")
def flow_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    flow - Manage your flows. Subcommands:
      list                   : Show all flows and current active_flow
      switch <flow_name>     : Resume an existing flow
      pause [<flow_name>]    : Pause a flow (defaults to active_flow)
      create <flow_name>     : Create/reset a flow (for demonstration)
    """
    tokens = args.strip().split()
    if not tokens:
        return "Usage: @bot flow <list|switch|pause|create> ..."

    subcmd = tokens[0].lower()
    remainder = tokens[1:] if len(tokens) > 1 else []

    if subcmd == "list":
        info = list_flows(sender)
        lines = [f"Active Flow: {info['active_flow'] or 'None'}"]
        for fname, details in info["flows"].items():
            lines.append(f"- {fname} (step={details['step']}, data_count={details['data_count']})")
        return "\n".join(lines)

    elif subcmd == "switch":
        if not remainder:
            return "Usage: @bot flow switch <flow_name>"
        flow_name = remainder[0]
        resume_flow(sender, flow_name)
        return f"Switched to flow '{flow_name}'."

    elif subcmd == "pause":
        if remainder:
            flow_name = remainder[0]
        else:
            # If no flow name given, assume active_flow
            info = list_flows(sender)
            flow_name = info["active_flow"]
            if not flow_name:
                return "No active flow to pause."
        pause_flow(sender, flow_name)
        return f"Paused flow '{flow_name}'."

    elif subcmd == "create":
        if not remainder:
            return "Usage: @bot flow create <flow_name>"
        flow_name = remainder[0]
        create_flow(sender, flow_name)
        return f"Flow '{flow_name}' created and set active."
    else:
        return "Unknown subcommand. Try: list, switch, pause, create."

# End of plugins/commands/flow.py