"""
main.py
-------
Main entry point for the Signal bot. Continuously listens for messages and processes commands.
Uses asynchronous processing for improved scalability and responsiveness.
"""

import asyncio
import core.logging_config  # Import to initialize the logging configuration
import logging
from core.signal_client import process_incoming
from plugins.manager import get_all_plugins, load_plugins  # Updated import from merged plugins manager
from core.config import POLLING_INTERVAL
import core.state as state

logger = logging.getLogger(__name__)

# Automatically load all plugins from the 'plugins' folder.
load_plugins()

async def main() -> None:
    """
    Asynchronous main loop for processing incoming messages.
    
    Uses asyncio.create_subprocess_exec for non-blocking subprocess calls
    and asyncio.sleep() for non-blocking delays.
    """
    logger.info("Signal bot is running. Available commands:")
    for cmd in get_all_plugins().keys():
        logger.info(f" - {cmd}")
    try:
        while state.BOT_CONTROLLER.running:
            await process_incoming()
            await asyncio.sleep(POLLING_INTERVAL)  # Use non-blocking sleep
    except KeyboardInterrupt:
        logger.info("Signal bot has been manually stopped.")
    finally:
        logger.info("Signal bot has been stopped gracefully.")

if __name__ == "__main__":
    asyncio.run(main())

# End of main.py
