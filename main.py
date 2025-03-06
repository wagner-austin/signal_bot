"""
main.py
-------
Main entry point for the Signal bot. Continuously listens for messages and processes commands.
"""

import time
from core.signal_client import process_incoming
from managers.plugin_manager import get_all_plugins
from plugin_utils.plugin_loader import load_plugins  # Automatically load plugins
import core.state as state

# Automatically load all plugins from the 'plugins' folder.
load_plugins()

if __name__ == "__main__":
    print("Signal bot is running. Available commands:")
    for cmd in get_all_plugins().keys():
        print(f" - {cmd}")
    try:
        while state.STATE.running:
            process_incoming()
            time.sleep(2)  # Polling interval reduced for faster response.
    except KeyboardInterrupt:
        print("Signal bot has been manually stopped.")
    finally:
        print("Signal bot has been stopped gracefully.")

# End of main.py