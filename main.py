"""
main.py
-------
Main entry point for the Signal bot. Continuously listens for messages and processes commands.
"""

import time
import logging
from core.signal_client import process_incoming
from managers.plugin_manager import get_all_plugins
from plugin_utils.plugin_loader import load_plugins  # Automatically load plugins
from core.config import POLLING_INTERVAL
import core.state as state

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Automatically load all plugins from the 'plugins' folder.
load_plugins()

if __name__ == "__main__":
    logging.info("Signal bot is running. Available commands:")
    for cmd in get_all_plugins().keys():
        logging.info(f" - {cmd}")
    try:
        while state.BOT_CONTROLLER.running:
            process_incoming()
            time.sleep(POLLING_INTERVAL)  # Use configurable polling interval
    except KeyboardInterrupt:
        logging.info("Signal bot has been manually stopped.")
    finally:
        logging.info("Signal bot has been stopped gracefully.")

# End of main.py