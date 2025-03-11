#!/usr/bin/env python
"""
plugins/commands/donate.py --- Donation command plugin.
Unified under the new Pydantic approach, reusing the typed models and unified validation helper.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from core.database.donations import add_donation
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import (
    PluginArgError,
    CashDonationArgs,
    InKindDonationArgs,
    RegisterDonationArgs,
    validate_model
)

@plugin('donate', canonical='donate')
def donate_command(args: str, sender: str, state_machine: BotStateMachine,
                   msg_timestamp: Optional[int] = None) -> str:
    """
    donate - Log donation interest or record a donation.

    Subcommands:
      donate <amount> <description>         -> Cash donation.
      donate in-kind <description>          -> In-kind donation.
      donate register <method> [<desc>]     -> Register donation interest.
    """
    try:
        parsed = parse_plugin_arguments(args.strip(), mode='positional')
        tokens = parsed["tokens"]
        if not tokens:
            raise PluginArgError(
                "Usage:\n"
                "  @bot donate <amount> <description>\n"
                "  @bot donate in-kind <description>\n"
                "  @bot donate register <method> [<description>]"
            )

        first = tokens[0].lower()
        if first == "register":
            if len(tokens) < 2:
                raise PluginArgError("Usage: @bot donate register <method> [<description>]")
            data = {
                "method": tokens[1],
                "description": " ".join(tokens[2:]) if len(tokens) > 2 else ""
            }
            validated = validate_model(data, RegisterDonationArgs, "donate register <method> [<description>]")
            combined_description = f"{validated.method} {validated.description}".strip()
            donation_id = add_donation(sender, 0.0, "register", combined_description)
            return f"Donation logged with ID {donation_id}."
        elif first == "in-kind":
            data = {
                "description": " ".join(tokens[1:]) if len(tokens) > 1 else ""
            }
            validated = validate_model(data, InKindDonationArgs, "donate in-kind <description>")
            donation_id = add_donation(sender, 0.0, "in-kind", validated.description)
            return f"Donation logged with ID {donation_id}."
        else:
            try:
                amount = float(tokens[0])
            except ValueError:
                raise PluginArgError(
                    "Invalid donation amount. Provide a numeric value, or use 'in-kind'/'register'."
                )
            data = {
                "amount": amount,
                "description": " ".join(tokens[1:]) if len(tokens) > 1 else ""
            }
            validated = validate_model(data, CashDonationArgs, "donate <amount> <description>")
            donation_id = add_donation(sender, validated.amount, "cash", validated.description)
            return f"Donation logged with ID {donation_id}."
    except PluginArgError as e:
        return str(e)

# End of plugins/commands/donate.py