# dvge/ui/dialogs/__init__.py

"""Dialogs package for modal dialogs."""

from .search_dialog import SearchDialog
from .template_selection_dialog import TemplateSelectionDialog
from .visual_style_dialog import VisualStyleDialog

__all__ = [
    'SearchDialog',
    'TemplateSelectionDialog',
    'VisualStyleDialog'
]