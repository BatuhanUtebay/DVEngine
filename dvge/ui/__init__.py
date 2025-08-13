# dvge/ui/__init__.py

"""User interface package for DVGE."""

from .main_window import setup_main_window
from .menus import create_menu
from .panels.properties_panel import PropertiesPanel
from .canvas.canvas_manager import CanvasManager
from .dialogs.search_dialog import SearchDialog

__all__ = [
    'setup_main_window',
    'create_menu',
    'PropertiesPanel',
    'CanvasManager',
    'SearchDialog'
]