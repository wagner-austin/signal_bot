"""
core/state.py
------------
Encapsulates global state for the Signal bot using a StateManager class.
"""

class StateManager:
    def __init__(self):
        self.running = True

# Module-level instance of StateManager
STATE = StateManager()

# End of state.py