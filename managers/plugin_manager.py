"""
managers/plugin_manager.py
-----------------
Provides a plugin manager to register and manage command plugins.
"""

# Registry to hold command plugins.
plugin_registry = {}

def plugin(command: str):
    """Decorator to register a function as a command plugin."""
    def decorator(func):
        plugin_registry[command.lower()] = func
        return func
    return decorator

def get_plugin(command: str):
    """Retrieve a plugin function by command."""
    return plugin_registry.get(command.lower())

def get_all_plugins():
    """Return all registered plugins."""
    return plugin_registry

# End of managers/plugin_manager.py
