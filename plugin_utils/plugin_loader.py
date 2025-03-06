"""
plugin_loader.py
----------------
Automatically loads all plugin modules from the 'plugins' directory
(including the __init__.py so that commands can live there).
"""

import os
import importlib.util
import sys

def load_plugins():
    """
    Automatically import all Python modules in the 'plugins' directory.
    """
    # Calculate the base directory, one level up from plugin_utils.
    base_dir = os.path.dirname(os.path.dirname(__file__))
    plugins_dir = os.path.join(base_dir, 'plugins')
    if not os.path.isdir(plugins_dir):
        return
    for filename in os.listdir(plugins_dir):
        if filename.endswith('.py'):
            module_name = filename[:-3]
            file_path = os.path.join(plugins_dir, filename)
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
