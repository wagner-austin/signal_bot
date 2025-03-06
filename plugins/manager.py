"""
manager.py
------------------
Unified plugin manager module that handles registration, loading, and reloading of plugins.
It skips non-plugin files and abstracts common loading logic into a helper function.
"""

import os
import sys
import importlib.util
import importlib

# Registry to hold command plugins.
plugin_registry = {}

def plugin(command: str):
    """
    Decorator to register a function as a command plugin.
    
    Args:
        command (str): The command name to register.
        
    Returns:
        function: The decorator that registers the plugin.
    """
    def decorator(func):
        plugin_registry[command.lower()] = func
        return func
    return decorator

def get_plugin(command: str):
    """
    Retrieve a plugin function by command.
    
    Args:
        command (str): The command name.
        
    Returns:
        function or None: The plugin function if found, else None.
    """
    return plugin_registry.get(command.lower())

def get_all_plugins():
    """
    Return all registered plugins.
    
    Returns:
        dict: Dictionary containing all registered plugins.
    """
    return plugin_registry

def clear_plugins():
    """
    Clear all registered plugins to facilitate dynamic reloading.
    """
    plugin_registry.clear()

def _load_module(module_name: str, file_path: str):
    """
    Helper function to load a module given its module name and file path.
    
    Args:
        module_name (str): The name of the module.
        file_path (str): The file path to the module.
        
    Returns:
        module or None: The loaded module object if successful, else None.
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def _load_plugins_from_dir(reload: bool = False) -> None:
    """
    Helper function to load or reload all plugin modules from the plugins directory,
    skipping non-plugin files such as __init__.py.
    
    Args:
        reload (bool): If True, reloads modules already imported; otherwise, imports modules.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    plugins_dir = os.path.join(base_dir, 'plugins')
    if not os.path.isdir(plugins_dir):
        return
    for filename in os.listdir(plugins_dir):
        # Skip non-plugin files
        if not filename.endswith('.py') or filename == '__init__.py':
            continue
        module_name = "plugins." + filename[:-3]
        file_path = os.path.join(plugins_dir, filename)
        if reload and module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            _load_module(module_name, file_path)

def load_plugins():
    """
    Automatically import all plugin modules in the 'plugins' directory,
    skipping non-plugin files.
    """
    _load_plugins_from_dir(reload=False)

def reload_plugins():
    """
    Reload all plugin modules dynamically by clearing the plugin registry
    and re-importing all plugin modules, skipping non-plugin files.
    """
    clear_plugins()
    _load_plugins_from_dir(reload=True)

# End of plugins/manager.py