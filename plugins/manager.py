"""
plugins/manager.py - Unified plugin manager for registering and loading plugins.
Handles registration, loading, and reloading of plugins by explicitly importing all submodules
under the plugins.commands package to ensure plugin decorators are executed.
"""

import sys
import importlib
import pkgutil
from typing import Callable, Any, Optional, Dict, List, Union

# Registry to hold command plugins.
plugin_registry: Dict[str, Callable[..., Any]] = {}

def plugin(commands: Union[str, List[str]]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    plugin - Decorator to register a function as a command plugin with one or more aliases.
    
    Args:
        commands (Union[str, List[str]]): A command name or a list of command aliases.
        
    Returns:
        Callable: A decorator that registers the plugin function.
        
    Note:
        Instead of raising an error for duplicate registrations, the new registration
        overrides any existing one. This facilitates module reloading.
    """
    if isinstance(commands, str):
        commands = [commands]
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        for command in commands:
            key = command.lower()
            # Override any existing registration to support reloads.
            plugin_registry[key] = func
        return func
    return decorator

def get_plugin(command: str) -> Optional[Callable[..., Any]]:
    """
    get_plugin - Retrieve a plugin function by command.
    
    Args:
        command (str): The command name.
        
    Returns:
        Optional[Callable]: The plugin function if found, else None.
    """
    return plugin_registry.get(command.lower())

def get_all_plugins() -> Dict[str, Callable[..., Any]]:
    """
    get_all_plugins - Return all registered plugins.
    
    Returns:
        Dict[str, Callable]: Dictionary containing all registered plugins.
    """
    return plugin_registry

def clear_plugins() -> None:
    """
    clear_plugins - Clear all registered plugins to facilitate dynamic reloading.
    """
    plugin_registry.clear()

def load_plugins() -> None:
    """
    load_plugins - Automatically import (or reload) all plugin modules in the 'plugins.commands'
    package to register all plugins.
    
    Returns:
        None
    """
    import plugins.commands  # Ensure the package is imported.
    # Collect module names from plugins.commands submodules, deduplicated.
    module_names = {module_info.name for module_info in pkgutil.walk_packages(plugins.commands.__path__, plugins.commands.__name__ + ".")}
    for module_name in module_names:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)

def reload_plugins() -> None:
    """
    reload_plugins - Reload all plugin modules dynamically by clearing the plugin registry
    and re-importing all plugin modules.
    
    Returns:
        None
    """
    clear_plugins()
    load_plugins()

# End of plugins/manager.py