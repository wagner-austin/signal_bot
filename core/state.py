"""
state.py
------------
State management for the Signal bot using a state machine.
Defines the BotStateMachine for managing bot lifecycle states.
"""

class BotStateMachine:
    def __init__(self) -> None:
        # Initial state is RUNNING.
        self.current_state: str = "RUNNING"

    def shutdown(self) -> None:
        """
        Transition the state to shutting down.
        """
        self.current_state = "SHUTTING_DOWN"

    def should_continue(self) -> bool:
        """
        Check if the bot should continue running.
        
        Returns:
            bool: True if state is RUNNING, else False.
        """
        return self.current_state == "RUNNING"

# End of core/state.py