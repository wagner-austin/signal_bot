#!/usr/bin/env python
"""
plugins/commands/donate.py --- Donation command plugin.
Provides a command to log donation interest or record a donation.
Uses typed Pydantic models to reduce repetitive argument check logic.
Usage:
  "@bot donate <amount> <description>"
  "@bot donate in-kind <description>"
  "@bot donate register <method> [<description>]"
"""

from typing import Optional, Union, Literal
from plugins.manager import plugin
from core.state import BotStateMachine
from core.database.donations import add_donation
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import PluginArgError
from pydantic import BaseModel, ValidationError

class CashDonationArgs(BaseModel):
    donation_type: Literal["cash"]
    amount: float
    description: str

class InKindDonationArgs(BaseModel):
    donation_type: Literal["in-kind"]
    description: str

class RegisterDonationArgs(BaseModel):
    donation_type: Literal["register"]
    method: str
    description: Optional[str] = ""

DonationArgs = Union[CashDonationArgs, InKindDonationArgs, RegisterDonationArgs]

def parse_donation_args(tokens: list[str]) -> DonationArgs:
    """
    Parses tokens into a typed DonationArgs object.
    Raises PluginArgError on usage problems.
    """
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
            "donation_type": "register",
            "method": tokens[1],
            "description": " ".join(tokens[2:]) if len(tokens) > 2 else ""
        }
        return RegisterDonationArgs(**data)
    elif first == "in-kind":
        data = {
            "donation_type": "in-kind",
            "description": " ".join(tokens[1:]) if len(tokens) > 1 else ""
        }
        return InKindDonationArgs(**data)
    else:
        try:
            amount = float(tokens[0])
        except ValueError:
            raise PluginArgError(
                "Invalid donation amount. Provide a numeric value for amount, or use 'in-kind'/'register'."
            )
        data = {
            "donation_type": "cash",
            "amount": amount,
            "description": " ".join(tokens[1:]) if len(tokens) > 1 else ""
        }
        return CashDonationArgs(**data)

@plugin('donate', canonical='donate')
def donate_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
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

        donation_args = parse_donation_args(tokens)
        if donation_args.donation_type == "cash":
            donation_id = add_donation(sender, donation_args.amount, "cash", donation_args.description)
        elif donation_args.donation_type == "in-kind":
            donation_id = add_donation(sender, 0.0, "in-kind", donation_args.description)
        elif donation_args.donation_type == "register":
            combined_description = donation_args.method
            if donation_args.description:
                combined_description += f" {donation_args.description}"
            donation_id = add_donation(sender, 0.0, "register", combined_description)
        else:
            raise PluginArgError("Unrecognized donation type.")

        return f"Donation logged with ID {donation_id}."
    except (PluginArgError, ValidationError) as e:
        return str(e)

# End of plugins/commands/donate.py