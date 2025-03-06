"""
main.py
-------
Main entry point for the Signal bot. Continuously listens for messages and processes commands.
"""

import time
from signal_client import process_incoming
from plugin_manager import get_all_plugins
import plugin_loader  # Automatically load plugins
import state  # Import global state

# Automatically load all plugins from the 'plugins' folder.
plugin_loader.load_plugins()

if __name__ == "__main__":
    print("Signal bot is running. Available commands:")
    for cmd in get_all_plugins().keys():
        print(f" - {cmd}")
    try:
        while state.RUNNING:
            process_incoming()
            time.sleep(2)  # Polling interval reduced for faster response.
    except KeyboardInterrupt:
        print("Signal bot has been manually stopped.")
    finally:
        print("Signal bot has been stopped gracefully.")
