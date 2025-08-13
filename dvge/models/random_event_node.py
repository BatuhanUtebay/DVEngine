# dvge/models/random_event_node.py

"""Random event node implementation for weighted random outcomes."""

from .base_node import BaseNode
from ..constants import *


class RandomEventNode(BaseNode):
    """A special type of node that randomly selects from multiple outcomes."""
    
    NODE_TYPE = "RandomEvent"
    
    def __init__(self, x, y, node_id, text="Something unexpected happens...", 
                 random_outcomes=None, auto_trigger=True, **kwargs):
        super().__init__(x, y, node_id, npc="Fate", text=text, **kwargs)
        self.random_outcomes = random_outcomes if random_outcomes else []
        self.auto_trigger = auto_trigger  # If True, triggers immediately; if False, shows button
    
    def to_dict(self):
        """Serializes the random event node's data."""
        data = super().to_dict()
        data["node_type"] = self.NODE_TYPE
        data["game_data"]["random_outcomes"] = self.random_outcomes
        data["game_data"]["auto_trigger"] = self.auto_trigger
        # Remove options as they are handled by random outcomes
        data["game_data"].pop("options", None)
        return data
    
    def get_height(self):
        """Random event nodes have variable height based on outcomes."""
        base_height = NODE_HEADER_HEIGHT + NODE_BASE_BODY_HEIGHT + NODE_FOOTER_HEIGHT
        outcome_count = len(self.random_outcomes)
        return base_height + (outcome_count * 30) + 40
    
    @classmethod
    def from_dict(cls, data):
        """Creates a RandomEventNode instance from a dictionary."""
        game_data = data['game_data']
        editor_data = data['editor_data']
        
        return cls(
            x=editor_data['x'],
            y=editor_data['y'],
            node_id=editor_data['id'],
            text=game_data.get('text', 'Something unexpected happens...'),
            random_outcomes=game_data.get('random_outcomes', []),
            auto_trigger=game_data.get('auto_trigger', True),
            theme=game_data.get('backgroundTheme', ''),
            chapter=game_data.get('chapter', ''),
            color=editor_data.get('color', NODE_DEFAULT_COLOR),
            backgroundImage=game_data.get('backgroundImage', ''),
            audio=game_data.get('audio', ''),
            music=game_data.get('music', '')
        )