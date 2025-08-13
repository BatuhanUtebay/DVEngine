# dvge/models/inventory_node.py

"""Inventory node implementation for item management and crafting."""

from .base_node import BaseNode
from ..constants import *


class InventoryNode(BaseNode):
    """A special type of node for inventory management and item crafting."""
    
    NODE_TYPE = "Inventory"
    
    def __init__(self, x, y, node_id, text="Manage your inventory", 
                 crafting_recipes=None, item_actions=None, continue_node="",
                 auto_open=True, **kwargs):
        super().__init__(x, y, node_id, npc="Inventory", text=text, **kwargs)
        self.crafting_recipes = crafting_recipes if crafting_recipes else []
        self.item_actions = item_actions if item_actions else []  # Use, examine, combine, etc.
        self.continue_node = continue_node  # Where to go when closing inventory
        self.auto_open = auto_open  # Automatically open inventory interface
    
    def to_dict(self):
        """Serializes the inventory node's data."""
        data = super().to_dict()
        data["node_type"] = self.NODE_TYPE
        data["game_data"]["crafting_recipes"] = self.crafting_recipes
        data["game_data"]["item_actions"] = self.item_actions
        data["game_data"]["continue_node"] = self.continue_node
        data["game_data"]["auto_open"] = self.auto_open
        # Remove options as they are handled by inventory interface
        data["game_data"].pop("options", None)
        return data
    
    def get_height(self):
        """Inventory nodes have variable height based on recipes and actions."""
        base_height = NODE_HEADER_HEIGHT + NODE_BASE_BODY_HEIGHT + NODE_FOOTER_HEIGHT
        recipe_count = len(self.crafting_recipes)
        action_count = len(self.item_actions)
        return base_height + ((recipe_count + action_count) * 25) + 60
    
    @classmethod
    def from_dict(cls, data):
        """Creates an InventoryNode instance from a dictionary."""
        game_data = data['game_data']
        editor_data = data['editor_data']
        
        return cls(
            x=editor_data['x'],
            y=editor_data['y'],
            node_id=editor_data['id'],
            text=game_data.get('text', 'Manage your inventory'),
            crafting_recipes=game_data.get('crafting_recipes', []),
            item_actions=game_data.get('item_actions', []),
            continue_node=game_data.get('continue_node', ''),
            auto_open=game_data.get('auto_open', True),
            theme=game_data.get('backgroundTheme', ''),
            chapter=game_data.get('chapter', ''),
            color=editor_data.get('color', NODE_DEFAULT_COLOR),
            backgroundImage=game_data.get('backgroundImage', ''),
            audio=game_data.get('audio', ''),
            music=game_data.get('music', '')
        )