"""
plugin_utils/plugin_loader.py
----------------
Automatically loads or reloads all plugin modules from the 'plugins' directory.
Supports dynamic reloading of plugins without restarting the bot.
"""

import os
import importlib.util
import sys
import importlib
from managers import plugin_manager

def _load_module(module_name: str, file_path: str):
    """
    Helper function to load a module given its module name and file path.
    Returns the module object if loaded successfully, otherwise None.
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def load_plugins():
    """
    Automatically import all Python modules in the 'plugins' directory.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    plugins_dir = os.path.join(base_dir, 'plugins')
    if not os.path.isdir(plugins_dir):
        return
    for filename in os.listdir(plugins_dir):
        if filename.endswith('.py'):
            module_name = "plugins." + filename[:-3]
            file_path = os.path.join(plugins_dir, filename)
            _load_module(module_name, file_path)

def reload_plugins():
    """
    Reload all plugins dynamically by clearing the plugin registry and re-importing all plugin modules.
    """
    plugin_manager.clear_plugins()
    base_dir = os.path.dirname(os.path.dirname(__file__))
    plugins_dir = os.path.join(base_dir, 'plugins')
    if not os.path.isdir(plugins_dir):
        return
    for filename in os.listdir(plugins_dir):
        if filename.endswith('.py'):
            module_name = "plugins." + filename[:-3]
            file_path = os.path.join(plugins_dir, filename)
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            else:
                _load_module(module_name, file_path)

# End of plugin_utils/plugin_loader.py