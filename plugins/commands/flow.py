"""
plugins/commands/flow.py - Flow management plugin commands.
Allows listing, switching, pausing, and creating flows using a unified subcommand dispatcher.
"""

from typing import Optional, List
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.user_states_manager import list_flows, resume_flow, pause_flow, create_flow
from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError

@plugin(commands=["flow"], canonical="flow")
def flow_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/flow.py - Flow management plugin.
    Subcommands:
      list                   : Show all flows and current active flow.
      switch <flow_name>     : Resume an existing flow.
      pause [<flow_name>]    : Pause a flow (defaults to active flow).
      create <flow_name>     : Create or reset a flow.
    USAGE: @bot flow <list|switch|pause|create> ...
    """
    usage = "Usage: @bot flow <list|switch|pause|create> ..."

    def sub_list(rest: List[str]) -> str:
        info = list_flows(sender)
        lines = [f"Active Flow: {info['active_flow'] or 'None'}"]
        for fname, details in info["flows"].items():
            lines.append(f"- {fname} (step={details['step']}, data_count={details['data_count']})")
        return "\n".join(lines)

    def sub_switch(rest: List[str]) -> str:
        if not rest:
            return "Usage: @bot flow switch <flow_name>"
        flow_name = rest[0]
        resume_flow(sender, flow_name)
        return f"Switched to flow '{flow_name}'."

    def sub_pause(rest: List[str]) -> str:
        if rest:
            flow_name = rest[0]
        else:
            info = list_flows(sender)
            flow_name = info["active_flow"]
            if not flow_name:
                return "No active flow to pause."
        pause_flow(sender, flow_name)
        return f"Paused flow '{flow_name}'."

    def sub_create(rest: List[str]) -> str:
        if not rest:
            return "Usage: @bot flow create <flow_name>"
        flow_name = rest[0]
        create_flow(sender, flow_name)
        return f"Flow '{flow_name}' created and set active."

    subcommands = {
        "list": sub_list,
        "switch": sub_switch,
        "pause": sub_pause,
        "create": sub_create
    }

    try:
        return handle_subcommands(
            args,
            subcommands,
            usage_msg=usage,
            unknown_subcmd_msg="Unknown subcommand"
        )
    except PluginArgError as e:
        return str(e)
    except Exception as e:
        return f"An internal error occurred in flow_command: {e}"

# End of plugins/commands/flow.py