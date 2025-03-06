"""
core/logging_config.py
-----------------
Centralized logging configuration for the Signal bot.
"""
import logging

# Configure logging for the entire application
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# End of core/logging_config.py