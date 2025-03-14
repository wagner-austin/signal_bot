"""
plugins/commands/donate.py - Donation command plugin.
Subcommands:
  register : Register donation interest.
  in-kind  : Log an in-kind donation.
  (default) : Log a cash donation.
USAGE: {USAGE_DONATE}
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from db.donations import add_donation
from parsers.plugin_arg_parser import PluginArgError, CashDonationArgs, InKindDonationArgs, RegisterDonationArgs, validate_model
from core.plugin_usage import USAGE_DONATE

logger = logging.getLogger(__name__)

@plugin('donate', canonical='donate')
def donate_command(args: str, sender: str, state_machine: BotStateMachine,
                   msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/donate.py - Donation command plugin.
    Subcommands:
      register : Register donation interest.
      in-kind  : Log an in-kind donation.
      (default) : Log a cash donation.
    USAGE: {USAGE_DONATE}
    """
    tokens = args.strip().split()
    if not tokens:
        return f"Usage: {USAGE_DONATE}"
    first = tokens[0].lower()
    if first == "register":
        if len(tokens) < 2:
            return f"Usage: {USAGE_DONATE}"
        data = {
            "method": tokens[1],
            "description": " ".join(tokens[2:]) if len(tokens) > 2 else ""
        }
        try:
            validated = validate_model(data, RegisterDonationArgs, USAGE_DONATE)
        except PluginArgError as e:
            logger.warning(f"donate_command PluginArgError: {e}")
            return str(e)
        combined_description = f"{validated.method} {validated.description}".strip()
        donation_id = add_donation(sender, 0.0, "register", combined_description)
        return f"Donation logged with ID {donation_id}."
    elif first == "in-kind":
        data = {
            "description": " ".join(tokens[1:]) if len(tokens) > 1 else ""
        }
        try:
            validated = validate_model(data, InKindDonationArgs, USAGE_DONATE)
        except PluginArgError as e:
            logger.warning(f"donate_command PluginArgError: {e}")
            return str(e)
        donation_id = add_donation(sender, 0.0, "in-kind", validated.description)
        return f"Donation logged with ID {donation_id}."
    else:
        try:
            amount = float(tokens[0])
        except ValueError:
            return f"Unknown subcommand. USAGE: {USAGE_DONATE}"
        data = {
            "amount": amount,
            "description": " ".join(tokens[1:]) if len(tokens) > 1 else ""
        }
        try:
            validated = validate_model(data, CashDonationArgs, USAGE_DONATE)
        except PluginArgError as e:
            logger.warning(f"donate_command PluginArgError: {e}")
            return str(e)
        donation_id = add_donation(sender, validated.amount, "cash", validated.description)
        return f"Donation logged with ID {donation_id}."

# End of plugins/commands/donate.py