# dvge/models/dialogue_node.py

"""Dialogue node implementation for standard conversation nodes."""

from .base_node import BaseNode
from ..constants import *


class DialogueNode(BaseNode):
    """Represents a standard dialogue node with choices."""
    
    NODE_TYPE = "Dialogue"
    
    def __init__(self, x, y, node_id, npc="Narrator", text="", options=None, **kwargs):
        super().__init__(x, y, node_id, npc, text, **kwargs)
        self.options = options if options else []
    
    def to_dict(self):
        """Serializes the dialogue node's data."""
        data = super().to_dict()
        data["game_data"]["options"] = self.options
        return data
    
    def get_height(self):
        """Calculates the total height including options."""
        body_height = max(NODE_BASE_BODY_HEIGHT, self.calculated_text_height + 20)
        return (NODE_HEADER_HEIGHT + body_height + 
               (len(self.options) * OPTION_LINE_HEIGHT) + NODE_FOOTER_HEIGHT)
    
    @classmethod
    def from_dict(cls, data):
        """Creates a DialogueNode instance from a dictionary."""
        game_data = data['game_data']
        editor_data = data['editor_data']
        
        return cls(
            x=editor_data['x'],
            y=editor_data['y'],
            node_id=editor_data['id'],
            npc=game_data.get('npc', 'Narrator'),
            text=game_data.get('text', ''),
            options=game_data.get('options', []),
            theme=game_data.get('backgroundTheme', ''),
            chapter=game_data.get('chapter', ''),
            color=editor_data.get('color', NODE_DEFAULT_COLOR),
            backgroundImage=game_data.get('backgroundImage', ''),
            audio=game_data.get('audio', ''),
            music=game_data.get('music', ''),
            auto_advance=game_data.get('auto_advance', False),
            auto_advance_delay=game_data.get('auto_advance_delay', 0)
        )