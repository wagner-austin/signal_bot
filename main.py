"""
main.py
-------
Main entry point for the Signal bot.
Initializes the SignalBotService and starts the asynchronous main loop.
"""

import asyncio
import core.logging_config  # Initialize logging configuration
import logging
from core.signal_bot_service import SignalBotService

logger = logging.getLogger(__name__)

async def main() -> None:
    service = SignalBotService()
    await service.run()

if __name__ == "__main__":
    asyncio.run(main())

# End of main.py