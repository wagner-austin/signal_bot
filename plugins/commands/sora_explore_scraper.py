#!/usr/bin/env python3
"""
plugins/commands/sora_explore_scraper.py
----------------------------------------
Selenium-based Chrome opener that navigates to https://www.sora.com/explore.
Implements a state machine, plugin-based event system, and optional subcommands
to start, stop, or retrieve status of the web navigation.

Usage:
  @bot sora explore start
  @bot sora explore stop
  @bot sora explore status
"""

import os
import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from enum import Enum, auto

from plugins.manager import plugin
from plugins.abstract import BasePlugin
from core.permissions import OWNER
from core.state import BotStateMachine

from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError

# -----------------------------
# Configuration
# -----------------------------
BASE_URL = "https://www.sora.com/explore"
KEEP_BROWSER_OPEN = True
BROWSER_STAY_DURATION = 15

USE_EXISTING_PROFILE = True
USER_DATA_DIR = r"C:\Users\Test\PROJECTS\sora\ChromeProfiles"
PROFILE_DIRECTORY = "Profile 1"

logger = logging.getLogger(__name__)


# -----------------------------
# State Machine Definition
# -----------------------------
class State(Enum):
    INITIAL = auto()
    SETUP = auto()
    NAVIGATING = auto()
    WAITING = auto()
    CLOSING = auto()
    COMPLETED = auto()


# -----------------------------
# Plugin-like system replaced by the bot's plugin architecture
# -----------------------------
class PluginManagerForSora:
    """
    (Optional) If you want to keep a local plugin manager for
    state change notifications inside the Sora plugin only.
    Otherwise, this can be removed or repurposed.
    """
    def __init__(self):
        self.plugins = []

    def register_plugin(self, plugin):
        self.plugins.append(plugin)
        logger.info(f"(Internal Sora) Plugin {plugin.__class__.__name__} registered.")

    def notify_state_change(self, previous_state, new_state, opener):
        for plugin in self.plugins:
            try:
                plugin.on_state_change(previous_state, new_state, opener)
            except Exception as e:
                logger.error(f"(Internal Sora) Error in plugin {plugin.__class__.__name__}: {e}")


# -----------------------------
# SimpleOpener with a state machine
# -----------------------------
class SimpleOpener:
    """
    SimpleOpener opens Chrome using undetected_chromedriver, navigates to BASE_URL,
    and manages state transitions with an internal plugin manager for demonstration.
    """
    def __init__(self, driver_path=None, plugin_manager=None):
        self.driver = None
        self.wait = None
        self.driver_path = driver_path
        self.state = State.INITIAL
        self.plugin_manager = plugin_manager
        self._state_transition(State.SETUP)
        self.setup_driver()

    def _state_transition(self, new_state):
        previous_state = self.state
        self.state = new_state
        if self.plugin_manager:
            self.plugin_manager.notify_state_change(previous_state, new_state, self)

    def setup_driver(self):
        chrome_options = uc.ChromeOptions()
        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        if USE_EXISTING_PROFILE:
            full_profile_path = os.path.join(USER_DATA_DIR, PROFILE_DIRECTORY)
            if os.path.exists(full_profile_path):
                chrome_options.add_argument(f"--user-data-dir={full_profile_path}")
                logger.info(f"(Sora) Using dedicated profile from '{full_profile_path}'.")
            else:
                logger.warning(f"(Sora) Profile '{full_profile_path}' does not exist; launching default profile.")
        else:
            logger.info("(Sora) Not using an existing profile. Launching with default profile.")

        if self.driver_path:
            self.driver = uc.Chrome(driver_executable_path=self.driver_path, options=chrome_options)
        else:
            self.driver = uc.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def open_url(self):
        self._state_transition(State.NAVIGATING)
        logger.info(f"(Sora) Attempting to navigate to {BASE_URL}")
        self.driver.get(BASE_URL)
        time.sleep(2)  # Potentially block the bot briefly

        # Check if 'sora.com/explore' is in the current URL
        expected_fragment = "sora.com/explore"
        if expected_fragment in self.driver.current_url:
            logger.info(f"(Sora) Navigation successful. Current URL: {self.driver.current_url}")
        else:
            logger.warning(f"(Sora) Navigation may have failed. Current URL: {self.driver.current_url}")

    def wait_for_duration(self, duration):
        self._state_transition(State.WAITING)
        logger.info(f"(Sora) Browser staying open for {duration} second(s).")
        time.sleep(duration)

    def close(self):
        self._state_transition(State.CLOSING)
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.info(f"(Sora) Driver quit encountered an error: {e}")
        self._state_transition(State.COMPLETED)


# -----------------------------
# Actual Bot Plugin
# -----------------------------
@plugin(commands=["sora explore"], canonical="sora explore", required_role=OWNER)
class SoraExploreScraperPlugin(BasePlugin):
    """
    Sora Explore Scraper Plugin
    ---------------------------
    Allows owner to open a Chrome browser (via Selenium), navigate to
    https://www.sora.com/explore, optionally keep it open, then close it.

    Usage:
      @bot sora explore start
      @bot sora explore stop
      @bot sora explore status
    """

    def __init__(self):
        super().__init__(
            "sora explore",
            help_text="Open a Chrome browser with a Sora Explore session and optionally keep it open."
        )
        self.logger = logging.getLogger(__name__)
        self.opener = None
        self.internal_plugin_mgr = PluginManagerForSora()
        self.subcommands = {
            "start": self._sub_start,
            "stop": self._sub_stop,
            "status": self._sub_status,
        }

    def run_command(self, args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: int = None) -> str:
        usage = (
            "Usage:\n"
            "  @bot sora explore start   -> Launch browser & navigate.\n"
            "  @bot sora explore stop    -> Close the browser.\n"
            "  @bot sora explore status  -> Check status.\n"
        )
        from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError

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
            return "An internal error occurred in SoraExploreScraperPlugin."

    def _sub_start(self, rest_args):
        if self.opener is not None:
            return "(Sora) Already started. Use 'stop' first if you want to restart."

        # Create the opener and open URL
        self.opener = SimpleOpener(driver_path='chromedriver.exe', plugin_manager=self.internal_plugin_mgr)
        self.opener.open_url()

        if KEEP_BROWSER_OPEN:
            self.opener.wait_for_duration(BROWSER_STAY_DURATION)
            # Note: This blocks the bot for the duration. For better concurrency,
            # consider an async approach or a background thread.

        return "(Sora) Browser launched and navigation attempted."

    def _sub_stop(self, rest_args):
        if not self.opener:
            return "(Sora) No active session to stop."

        self.opener.close()
        self.opener = None
        return "(Sora) Browser closed."

    def _sub_status(self, rest_args):
        if not self.opener:
            return "(Sora) No active session. Use 'start' to launch one."
        return f"(Sora) Current state: {self.opener.state.name}."


# End of sora_explore_scraper.py