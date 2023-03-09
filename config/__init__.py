import os
from importlib import import_module

os.environ.setdefault("GESTOR_MODULE_SETTINGS", "config.local")
mod = import_module(os.getenv("GESTOR_MODULE_SETTINGS"))

settings = mod.settings
