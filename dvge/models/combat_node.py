# dvge/models/combat_node.py

"""Combat node implementation for battle encounters."""

from .base_node import BaseNode
from ..constants import *


class CombatNode(BaseNode):
    """A special type of node for handling combat encounters."""
    
    NODE_TYPE = "Combat"
    
    def __init__(self, x, y, node_id, text="A battle begins!", 
                 enemies=None, successNode="", failNode="", **kwargs):
        super().__init__(x, y, node_id, npc="Combat", text=text, **kwargs)
        self.enemies = enemies if enemies else []  # List of enemy IDs
        self.successNode = successNode  # Node to go to on victory
        self.failNode = failNode  # Node to go to on defeat
        self.options = []  # Empty options list for UI compatibility
    
    def to_dict(self):
        """Serializes the combat node's data."""
        data = super().to_dict()
        data["node_type"] = self.NODE_TYPE
        data["game_data"]["enemies"] = self.enemies
        data["game_data"]["successNode"] = self.successNode
        data["game_data"]["failNode"] = self.failNode
        # Remove options as they are not used in combat nodes
        data["game_data"].pop("options", None)
        return data
    
    def get_height(self):
        """Combat nodes have a fixed height for simplicity."""
        return NODE_HEADER_HEIGHT + NODE_BASE_BODY_HEIGHT + NODE_FOOTER_HEIGHT
    
    @classmethod
    def from_dict(cls, data):
        """Creates a CombatNode instance from a dictionary."""
        game_data = data['game_data']
        editor_data = data['editor_data']
        
        return cls(
            x=editor_data['x'],
            y=editor_data['y'],
            node_id=editor_data['id'],
            text=game_data.get('text', 'A battle begins!'),
            enemies=game_data.get('enemies', []),
            successNode=game_data.get('successNode', ''),
            failNode=game_data.get('failNode', ''),
            theme=game_data.get('backgroundTheme', ''),
            chapter=game_data.get('chapter', ''),
            color=editor_data.get('color', NODE_DEFAULT_COLOR),
            backgroundImage=game_data.get('backgroundImage', ''),
            audio=game_data.get('audio', '')
        )