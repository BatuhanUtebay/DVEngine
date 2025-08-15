# dvge/models/dice_roll_node.py

"""Dice roll node implementation for skill checks and random events."""

from .base_node import BaseNode
from ..constants import *


class DiceRollNode(BaseNode):
    """A special type of node for handling dice rolls."""
    
    NODE_TYPE = "DiceRoll"
    
    def __init__(self, x, y, node_id, text="A challenge appears!", 
                 num_dice=1, num_sides=6, success_threshold=4, 
                 success_node="", failure_node="", **kwargs):
        super().__init__(x, y, node_id, npc="Dice Roll", text=text, **kwargs)
        self.num_dice = num_dice
        self.num_sides = num_sides
        self.success_threshold = success_threshold
        self.success_node = success_node
        self.failure_node = failure_node
        self.options = []  # Empty options list for UI compatibility
    
    def to_dict(self):
        """Serializes the dice roll node's data."""
        data = super().to_dict()
        data["node_type"] = self.NODE_TYPE
        data["game_data"]["num_dice"] = self.num_dice
        data["game_data"]["num_sides"] = self.num_sides
        data["game_data"]["success_threshold"] = self.success_threshold
        data["game_data"]["success_node"] = self.success_node
        data["game_data"]["failure_node"] = self.failure_node
        # Remove options as they are not used in dice roll nodes
        data["game_data"].pop("options", None)
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Creates a DiceRollNode instance from a dictionary."""
        game_data = data['game_data']
        editor_data = data['editor_data']
        
        return cls(
            x=editor_data['x'],
            y=editor_data['y'],
            node_id=editor_data['id'],
            text=game_data.get('text', 'A challenge appears!'),
            num_dice=game_data.get('num_dice', 1),
            num_sides=game_data.get('num_sides', 6),
            success_threshold=game_data.get('success_threshold', 4),
            success_node=game_data.get('success_node', ''),
            failure_node=game_data.get('failure_node', ''),
            theme=game_data.get('backgroundTheme', ''),
            chapter=game_data.get('chapter', ''),
            color=editor_data.get('color', NODE_DEFAULT_COLOR),
            backgroundImage=game_data.get('backgroundImage', ''),
            audio=game_data.get('audio', '')
        )