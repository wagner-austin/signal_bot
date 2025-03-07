"""
main.py - Main entry point for the Signal bot.
Initializes logging, metrics, and the database, then starts the SignalBotService.
Optionally runs the test suite if the --test flag is provided.
"""

import sys
import asyncio
import core.logging_config  # Initialize logging configuration
import core.database        # Import the database module
import core.metrics         # Initialize metrics tracking (starts timer)
import logging
from core.signal_bot_service import SignalBotService

logger = logging.getLogger(__name__)

async def main() -> None:
    # Initialize the SQLite database (creates tables if they do not exist)
    core.database.init_db()
    service = SignalBotService()
    await service.run()

if __name__ == "__main__":
    if '--test' in sys.argv:
        from tests.test_all import run_all_tests
        run_all_tests()
    else:
        asyncio.run(main())

# End of main.py
