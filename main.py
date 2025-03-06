"""
main.py
-------
Main entry point for the Signal bot. Continuously listens for messages and processes commands.
Uses asynchronous processing for improved scalability and responsiveness.
"""

import asyncio
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

async def main() -> None:
    """
    Asynchronous main loop for processing incoming messages.
    
    Uses asyncio.to_thread() to run blocking operations (process_incoming)
    in a separate thread and asyncio.sleep() for non-blocking delays.
    """
    logging.info("Signal bot is running. Available commands:")
    for cmd in get_all_plugins().keys():
        logging.info(f" - {cmd}")
    try:
        while state.BOT_CONTROLLER.running:
            # Run process_incoming in a separate thread to prevent blocking the event loop.
            await asyncio.to_thread(process_incoming)
            await asyncio.sleep(POLLING_INTERVAL)  # Use non-blocking sleep
    except KeyboardInterrupt:
        logging.info("Signal bot has been manually stopped.")
    finally:
        logging.info("Signal bot has been stopped gracefully.")

if __name__ == "__main__":
    asyncio.run(main())

# End of main.py