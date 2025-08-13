# dvge/ui/panels/__init__.py

"""Panels package for UI components."""

from .properties_panel import PropertiesPanel
from .node_properties import NodePropertiesTab
from .choice_properties import ChoicePropertiesTab
from .player_panel import PlayerPanel
from .flags_panel import FlagsPanel
from .quests_panel import QuestsPanel
from .project_panel import ProjectPanel

__all__ = [
    'PropertiesPanel',
    'NodePropertiesTab',
    'ChoicePropertiesTab', 
    'PlayerPanel',
    'FlagsPanel',
    'QuestsPanel',
    'ProjectPanel'
]