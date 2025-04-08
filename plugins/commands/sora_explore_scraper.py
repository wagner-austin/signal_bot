#!/usr/bin/env python3
"""
plugins/commands/sora_explore_scraper.py --- Selenium-based Chrome opener with detailed page info extraction and media download.
Implements a state machine and plugin-based event system with subcommands to start, stop, or check status.
Usage:
  @bot sora explore start
  @bot sora explore stop
  @bot sora explore status
"""

import os
import time
import logging
import requests
from urllib.parse import urlparse, unquote
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
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
BROWSER_STAY_DURATION = 5  # Seconds to keep the browser open after processing (updated from 15 to 5)

# Configuration for using an existing Chrome profile
USE_EXISTING_PROFILE = True
USER_DATA_DIR = r"C:\Users\Test\PROJECTS\sora\ChromeProfiles"
PROFILE_DIRECTORY = "Profile 1"

# Download configuration
DOWNLOAD_DIR = "./explorer_downloads"
DOWNLOAD_FILENAME = "downloaded_media.webp"  # Updated fallback filename

logger = logging.getLogger(__name__)

# -----------------------------
# State Machine Definition
# -----------------------------
class State(Enum):
    INITIAL = auto()
    SETUP = auto()
    NAVIGATING = auto()
    CAPTURING = auto()   # Capturing detailed page info
    DOWNLOADING = auto() # Downloading media from detailed page
    WAITING = auto()
    CLOSING = auto()
    COMPLETED = auto()

# -----------------------------
# Internal Plugin Manager
# -----------------------------
class PluginManagerForSora:
    """
    Manages internal plugins and dispatches state change events.
    """
    def __init__(self):
        self.plugins = []

    def register_plugin(self, plugin):
        self.plugins.append(plugin)
        logger.info(f"(Sora) Plugin {plugin.__class__.__name__} registered.")

    def notify_state_change(self, previous_state, new_state, opener):
        for plugin in self.plugins:
            try:
                plugin.on_state_change(previous_state, new_state, opener)
            except Exception as e:
                logger.error(f"(Sora) Error in plugin {plugin.__class__.__name__}: {e}")

# Optional Logging Plugin for internal state changes
class LoggingPlugin:
    def on_state_change(self, previous_state, new_state, opener):
        logger.info(f"(Sora) State changed from {previous_state.name} to {new_state.name}.")

# -----------------------------
# SimpleOpener with Download and Detailed Info Extraction
# -----------------------------
class SimpleOpener:
    """
    Opens Chrome using undetected_chromedriver, navigates to the Sora Explore page,
    captures detailed page information (media URL, artist, prompt, summary), downloads the media,
    and manages state transitions.
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
        time.sleep(2)  # Allow time for navigation to complete

        current_url = self.driver.current_url
        if "sora.com/explore" in current_url:
            logger.info(f"(Sora) Navigation successful. Current URL: {current_url}")
            self.capture_detailed_info()
        else:
            logger.warning(f"(Sora) Navigation may have failed. Current URL: {current_url}")

    def capture_detailed_info(self):
        self._state_transition(State.CAPTURING)
        try:
            thumbnail = self.wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "a[href^='/g/']"))
        except Exception as e:
            logger.warning(f"(Sora) Detailed page link not found: {e}")
            return

        detailed_path = thumbnail.get_attribute("href")
        if detailed_path.startswith("/"):
            detailed_url = "https://sora.com" + detailed_path
        else:
            detailed_url = detailed_path

        # Capture artist information from the thumbnail container (if available)
        artist = ""
        try:
            container = thumbnail.find_element(By.XPATH, "..")
            artist_element = container.find_element(By.CSS_SELECTOR, "button span.truncate")
            artist = artist_element.text.strip()
        except Exception as e:
            logger.warning(f"(Sora) Artist not found: {e}")

        logger.info(f"(Sora) Navigating to detailed page: {detailed_url}")
        self.driver.get(detailed_url)

        try:
            # Attempt to locate an image element; if not found, then try for a video element.
            try:
                media_element = self.wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "img[alt='Generated image']"))
                media_type = "image"
            except Exception:
                media_element = self.wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "video[src]"))
                media_type = "video"

            media_url = media_element.get_attribute("src")
            logger.info(f"(Sora) Detailed page {media_type} URL: {media_url}")
            self._state_transition(State.DOWNLOADING)

            # Extract and clean the original filename from the media URL
            parsed_url = urlparse(media_url)
            decoded_path = unquote(parsed_url.path)
            prefix = "/vg-assets/"
            if decoded_path.startswith(prefix):
                decoded_path = decoded_path[len(prefix):]
            name_without_ext, ext = os.path.splitext(decoded_path)
            if not ext:
                ext = ".webp" if media_type == "image" else ".mp4"
            final_filename = name_without_ext.replace("/", "_") + ext

            self._save_image(media_url, final_filename)
        except Exception as e:
            logger.warning(f"(Sora) Error while processing detailed page media: {e}")
            media_url = ""
            final_filename = DOWNLOAD_FILENAME

        # Capture prompt text
        prompt = ""
        try:
            prompt_button = self.wait.until(
                lambda d: d.find_element(By.XPATH, "//div[contains(text(),'Prompt')]/following-sibling::button")
            )
            prompt = prompt_button.text.strip()
        except Exception as e:
            logger.warning(f"(Sora) Prompt text not found: {e}")

        # Capture summary text
        try:
            summary_element = self.wait.until(
                lambda d: d.find_element(By.XPATH, "//div[contains(@class, 'surface-nav-element')]//div[contains(@class, 'truncate') and not(ancestor::a)]")
            )
            summary = summary_element.text.strip()
        except Exception as e:
            logger.warning(f"(Sora) Summary text not found: {e}")
            summary = self.driver.title.strip()

        detailed_info = {
            "detailed_url": self.driver.current_url,
            "artist": artist,
            "summary": summary,
            "prompt": prompt,
            "media_url": media_url,
            "downloaded_media": final_filename
        }
        logger.info(f"(Sora) Captured detailed info: {detailed_info}")
        logger.info("(Sora) Returning to the previous page.")
        self.driver.back()

    def _save_image(self, media_url, filename):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        try:
            response = requests.get(media_url, stream=True)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"(Sora) Media saved to: {file_path}")
        except Exception as e:
            logger.error(f"(Sora) Failed to download media: {e}")

    def wait_for_duration(self, duration):
        self._state_transition(State.WAITING)
        logger.info(f"(Sora) Browser remaining open for {duration} second(s).")
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
# Bot Plugin Implementation
# -----------------------------
@plugin(commands=["sora explore"], canonical="sora explore", required_role=OWNER)
class SoraExploreScraperPlugin(BasePlugin):
    """
    sora_explore_scraper.py --- Selenium-based Chrome opener with detailed page info extraction and media download.
    Implements a state machine and plugin-based event system to open a Chrome browser, navigate to a Sora Explore session,
    extract detailed info (artist, prompt, summary), and download the media.
    
    Usage:
      @bot sora explore start   -> Launch browser and process page.
      @bot sora explore stop    -> Close the browser.
      @bot sora explore status  -> Check current state.
    """
    def __init__(self):
        super().__init__(
            "sora explore",
            help_text="Open a Chrome browser with a Sora Explore session, extract detailed info, and download media."
        )
        self.logger = logging.getLogger(__name__)
        self.opener = None
        self.internal_plugin_mgr = PluginManagerForSora()
        # Optionally register the LoggingPlugin to log state transitions
        self.internal_plugin_mgr.register_plugin(LoggingPlugin())
        self.subcommands = {
            "start": self._sub_start,
            "stop": self._sub_stop,
            "status": self._sub_status,
        }

    def run_command(self, args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: int = None) -> str:
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
            return "An internal error occurred in SoraExploreScraperPlugin."

    def _sub_start(self, rest_args):
        if self.opener is not None:
            return "(Sora) Already started. Use 'stop' first if you want to restart."
        self.opener = SimpleOpener(driver_path='chromedriver.exe', plugin_manager=self.internal_plugin_mgr)
        self.opener.open_url()
        if KEEP_BROWSER_OPEN:
            self.opener.wait_for_duration(BROWSER_STAY_DURATION)
        return "(Sora) Browser launched, navigation and processing attempted."

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

# End of plugins/commands/sora_explore_scraper.py