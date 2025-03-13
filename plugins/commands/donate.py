#!/usr/bin/env python
"""
plugins/commands/donate.py - Donation command plugin.
Provides donation logging for cash, in-kind, or donation interest.
Usage: See USAGE_DONATE in core/plugin_usage.py
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
import logging
from core.plugin_usage import USAGE_DONATE

logger = logging.getLogger(__name__)

@plugin('donate', canonical='donate')
def donate_command(args: str, sender: str, state_machine: BotStateMachine,
                   msg_timestamp: Optional[int] = None) -> str:
    """
    donate - Log donation interest or record a donation.
    
    USAGE: {USAGE_DONATE}
    """
    try:
        parsed = parse_plugin_arguments(args.strip(), mode='positional')
        tokens = parsed["tokens"]
        if not tokens:
            raise PluginArgError(USAGE_DONATE)

        first = tokens[0].lower()
        if first == "register":
            if len(tokens) < 2:
                raise PluginArgError(USAGE_DONATE)
            data = {
                "method": tokens[1],
                "description": " ".join(tokens[2:]) if len(tokens) > 2 else ""
            }
            validated = validate_model(data, RegisterDonationArgs, USAGE_DONATE)
            combined_description = f"{validated.method} {validated.description}".strip()
            donation_id = add_donation(sender, 0.0, "register", combined_description)
            return f"Donation logged with ID {donation_id}."
        elif first == "in-kind":
            data = {
                "description": " ".join(tokens[1:]) if len(tokens) > 1 else ""
            }
            validated = validate_model(data, InKindDonationArgs, USAGE_DONATE)
            donation_id = add_donation(sender, 0.0, "in-kind", validated.description)
            return f"Donation logged with ID {donation_id}."
        else:
            try:
                amount = float(tokens[0])
            except ValueError:
                raise PluginArgError(USAGE_DONATE)
            data = {
                "amount": amount,
                "description": " ".join(tokens[1:]) if len(tokens) > 1 else ""
            }
            validated = validate_model(data, CashDonationArgs, USAGE_DONATE)
            donation_id = add_donation(sender, validated.amount, "cash", validated.description)
            return f"Donation logged with ID {donation_id}."
    except PluginArgError as e:
        logger.warning(f"donate_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"donate_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in donate_command."

# End of plugins/commands/donate.py