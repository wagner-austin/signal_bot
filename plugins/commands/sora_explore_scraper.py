#!/usr/bin/env python3
"""
plugins/commands/sora_explore_scraper.py
----------------------------------------
Sora Explore plugin command that calls the stable Sora Explore API to start/stop/status 
a Sora Explore session.

Usage:
  @bot sora explore start
  @bot sora explore stop
  @bot sora explore status
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.permissions import OWNER
from core.state import BotStateMachine
from plugins.abstract import BasePlugin
from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError
from plugins.messages import INTERNAL_ERROR

# Import the new Sora Explore API
from core.api.sora_explore_api import (
    start_sora_explore_session,
    stop_sora_explore_session,
    get_sora_explore_session_status
)

logger = logging.getLogger(__name__)

@plugin(commands=["sora explore"], canonical="sora explore", required_role=OWNER)
class SoraExploreScraperPlugin(BasePlugin):
    """
    Sora Explore plugin command that calls the stable Sora Explore API to manage 
    a Sora Explore session (start, stop, status).
    Usage:
      @bot sora explore start
      @bot sora explore stop
      @bot sora explore status
    """
    def __init__(self):
        super().__init__(
            "sora explore",
            help_text="Open a Chrome browser with a Sora Explore session, extract info, and download media."
        )
        self.logger = logging.getLogger(__name__)
        self.subcommands = {
            "start": self._sub_start,
            "stop": self._sub_stop,
            "status": self._sub_status,
        }

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        usage = (
            "Usage:\n"
            "  @bot sora explore start   -> Launch browser and process page.\n"
            "  @bot sora explore stop    -> Close the browser.\n"
            "  @bot sora explore status  -> Check current state.\n"
        )
        try:
            return handle_subcommands(
                args,
                subcommands=self.subcommands,
                usage_msg=usage,
                unknown_subcmd_msg="Unknown subcommand. See usage:\n" + usage
            )
        except PluginArgError as pae:
            self.logger.error(f"(Sora) Arg parsing error: {pae}", exc_info=True)
            return str(pae)
        except Exception as e:
            self.logger.error(f"(Sora) Unexpected error in run_command: {e}", exc_info=True)
            return INTERNAL_ERROR

    def _sub_start(self, rest_args):
        return start_sora_explore_session()

    def _sub_stop(self, rest_args):
        return stop_sora_explore_session()

    def _sub_status(self, rest_args):
        return get_sora_explore_session_status()

# End of plugins/commands/sora_explore_scraper.py