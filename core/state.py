"""
core/state.py
------------
Encapsulates the bot's global state in a BotController class.
"""

class BotController:
    def __init__(self) -> None:
        # Indicates if the bot is running.
        self.running: bool = True

    def shutdown(self) -> None:
        """
        Shut down the bot gracefully by setting the running flag to False.
        
        Returns:
            None
        """
        self.running = False

# Global instance of BotController
BOT_CONTROLLER = BotController()

# End of core/state.py