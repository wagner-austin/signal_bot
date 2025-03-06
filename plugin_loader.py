"""
plugin_loader.py
----------------
Automatically loads all plugin modules from the 'plugins' directory
(including the __init__.py now, so commands can live there).
"""

import os
import importlib.util
import sys

def load_plugins():
    """
    Automatically import all Python modules in the 'plugins' directory.
    """
    plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    if not os.path.isdir(plugins_dir):
        return
    for filename in os.listdir(plugins_dir):
        # Removed "and filename != '__init__.py'" so we also load __init__.py
        if filename.endswith('.py'):
            module_name = filename[:-3]
            file_path = os.path.join(plugins_dir, filename)
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
