#!/usr/bin/env python
"""
plugins/commands/donate.py - Donation command plugin.
Provides a command to log donation interest or record a donation.
Usage:
  "@bot donate <amount> <description>"
  "@bot donate in-kind <description>"
  "@bot donate register <method> [<description>]"
The donation is recorded in the Donations table.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from core.database.donations import add_donation
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import PluginArgError

@plugin('donate', canonical='donate')
def donate_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    donate - Log donation interest or record a donation.
    
    Subcommands:
      donate <amount> <description>        : Log a cash donation (amount is numeric).
      donate in-kind <description>           : Log an in-kind donation.
      donate register <method> [<description>]: Log donation interest using a specific method (e.g., venmo).
    
    Usage Examples:
      "@bot donate 25 Great cause!"
      "@bot donate in-kind 50 folding tables"
      "@bot donate register venmo"
    """
    try:
        args = args.strip()
        if not args:
            return ("Usage:\n"
                    "  @bot donate <amount> <description>\n"
                    "  @bot donate in-kind <description>\n"
                    "  @bot donate register <method> [<description>]")
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        donation_type = "cash"
        amount = 0.0
        description = ""
    
        if tokens[0].lower() == "register":
            if len(tokens) < 2:
                raise PluginArgError("Usage: @bot donate register <method> [<description>]")
            donation_type = tokens[1].lower()
            description = " ".join(tokens[2:]) if len(tokens) > 2 else ""
        elif tokens[0].lower() == "in-kind":
            donation_type = "in-kind"
            description = " ".join(tokens[1:]) if len(tokens) > 1 else ""
        else:
            try:
                amount = float(tokens[0])
                donation_type = "cash"
                description = " ".join(tokens[1:]) if len(tokens) > 1 else ""
            except ValueError:
                raise PluginArgError("Invalid donation amount. Please provide a numeric value for amount, or use the 'in-kind' or 'register' options.")
    
        donation_id = add_donation(sender, amount, donation_type, description)
        return f"Donation logged with ID {donation_id}."
    except PluginArgError as e:
        return f"Usage error: {e}"

# End of plugins/commands/donate.py