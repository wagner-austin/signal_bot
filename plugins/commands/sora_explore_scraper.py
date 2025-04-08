#!/usr/bin/env python3
"""
plugins/commands/sora_explore_scraper.py - Sora Explore plugin command for managing Sora Explore sessions.
Handles start, stop, download, and status commands.
Usage:
  @bot sora explore start   -> Launch browser and open Sora Explore page.
  @bot sora explore stop    -> Close the browser.
  @bot sora explore download -> Download/capture from the first thumbnail.
  @bot sora explore status  -> Check current state.
"""

import logging
import inspect
import asyncio  # For handling async calls
from typing import Optional
from plugins.manager import plugin
from core.permissions import OWNER
from core.state import BotStateMachine
from plugins.abstract import BasePlugin
from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError
from plugins.messages import INTERNAL_ERROR

# Import the updated Sora Explore API
from core.api.sora_explore_api import (
    start_sora_explore_session,
    stop_sora_explore_session,
    download_sora_explore_session,
    get_sora_explore_session_status
)

logger = logging.getLogger(__name__)

@plugin(commands=["sora explore"], canonical="sora explore", required_role=OWNER)
class SoraExploreScraperPlugin(BasePlugin):
    """
    Sora Explore plugin command that calls the stable Sora Explore API 
    to manage a Sora Explore session (start, stop, download, status).

    Usage:
      @bot sora explore start   -> Launch browser and open Sora Explore page.
      @bot sora explore stop    -> Close the browser.
      @bot sora explore download -> Download/capture from the first thumbnail.
      @bot sora explore status  -> Check current state.
    """
    def __init__(self):
        super().__init__(
            "sora explore",
            help_text=(
                "Open a Chrome browser with a Sora Explore session; "
                "use 'download' to capture images or videos, "
                "and 'stop' to close the browser."
            )
        )
        self.logger = logging.getLogger(__name__)
        self.subcommands = {
            "start": self._sub_start,
            "stop": self._sub_stop,
            "download": self._sub_download,  # Async subcommand
            "status": self._sub_status,
        }

    async def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        usage = (
            "Usage:\n"
            "  @bot sora explore start   -> Launch browser and open Sora Explore page.\n"
            "  @bot sora explore stop    -> Close the browser.\n"
            "  @bot sora explore download -> Download/capture from the first thumbnail.\n"
            "  @bot sora explore status  -> Check current state.\n"
        )
        try:
            result = handle_subcommands(
                args,
                subcommands=self.subcommands,
                usage_msg=usage,
                unknown_subcmd_msg="Unknown subcommand. See usage:\n" + usage
            )
            # If the result is a coroutine, await it.
            if asyncio.iscoroutine(result):
                result = await result

            # Ensure the result is a string.
            if not isinstance(result, str):
                logger.warning("Plugin 'sora explore' returned non-string or None. Converting to empty string.")
                result = ""
            return result
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

    async def _sub_download(self, rest_args):
        """
        Executes the download command. It passes the sender to the API
        so the downloaded file can be sent back to the requester.
        """
        try:
            return await download_sora_explore_session(self._sender)
        except Exception as e:
            self.logger.error(f"(Sora) Error during download subcommand: {e}", exc_info=True)
            return "(Sora) An error occurred while processing your download command."

    def _sub_status(self, rest_args):
        return get_sora_explore_session_status()

    @property
    def _sender(self) -> str:
        """
        Retrieves the sender from the local scope of the run_command method.
        Returns:
            The sender identifier if found; otherwise 'Unknown'.
        """
        for frame_info in inspect.stack():
            if frame_info.function == "run_command":
                return frame_info.frame.f_locals.get("sender", "Unknown")
        return "Unknown"

# End of plugins/commands/sora_explore_scraper.py