"""
signal_bot_service.py
----------------------
Provides the SignalBotService class that encapsulates the main asynchronous loop.
Handles processing of incoming messages while respecting the bot's state machine.
"""

import asyncio
import logging
from core.config import POLLING_INTERVAL
from core.signal_client import process_incoming
from core.state import BotStateMachine
from plugins.manager import get_all_plugins

logger = logging.getLogger(__name__)

class SignalBotService:
    def __init__(self, state_machine: BotStateMachine = None):
        self.state_machine = state_machine or BotStateMachine()

    async def run(self) -> None:
        """
        Runs the main asynchronous loop to process incoming messages.
        Logs available commands and gracefully handles shutdown.
        """
        logger.info("Signal bot is running. Available commands:")
        for cmd in get_all_plugins().keys():
            logger.info(f" - {cmd}")
        try:
            while self.state_machine.should_continue():
                await process_incoming(self.state_machine)
                await asyncio.sleep(POLLING_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Signal bot has been manually stopped.")
        finally:
            logger.info("Signal bot has been stopped gracefully.")

# End of core/signal_bot_service.py