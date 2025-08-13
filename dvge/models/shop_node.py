# dvge/models/shop_node.py

"""Shop node implementation for buy/sell mechanics."""

from .base_node import BaseNode
from ..constants import *


class ShopNode(BaseNode):
    """A special type of node for handling item buying and selling."""
    
    NODE_TYPE = "Shop"
    
    def __init__(self, x, y, node_id, text="Welcome to the shop!", 
                 items_for_sale=None, items_to_buy=None, currency_variable="gold",
                 continue_node="", **kwargs):
        super().__init__(x, y, node_id, npc="Shopkeeper", text=text, **kwargs)
        self.items_for_sale = items_for_sale if items_for_sale else []  # Items player can buy
        self.items_to_buy = items_to_buy if items_to_buy else []  # Items shop will buy from player
        self.currency_variable = currency_variable  # Variable used as currency
        self.continue_node = continue_node  # Node to go to when leaving shop
    
    def to_dict(self):
        """Serializes the shop node's data."""
        data = super().to_dict()
        data["node_type"] = self.NODE_TYPE
        data["game_data"]["items_for_sale"] = self.items_for_sale
        data["game_data"]["items_to_buy"] = self.items_to_buy
        data["game_data"]["currency_variable"] = self.currency_variable
        data["game_data"]["continue_node"] = self.continue_node
        # Remove options as they are handled differently in shop nodes
        data["game_data"].pop("options", None)
        return data
    
    def get_height(self):
        """Shop nodes have variable height based on items."""
        base_height = NODE_HEADER_HEIGHT + NODE_BASE_BODY_HEIGHT + NODE_FOOTER_HEIGHT
        item_count = len(self.items_for_sale) + len(self.items_to_buy)
        return base_height + (item_count * 25) + 50  # Extra space for shop interface
    
    @classmethod
    def from_dict(cls, data):
        """Creates a ShopNode instance from a dictionary."""
        game_data = data['game_data']
        editor_data = data['editor_data']
        
        return cls(
            x=editor_data['x'],
            y=editor_data['y'],
            node_id=editor_data['id'],
            text=game_data.get('text', 'Welcome to the shop!'),
            items_for_sale=game_data.get('items_for_sale', []),
            items_to_buy=game_data.get('items_to_buy', []),
            currency_variable=game_data.get('currency_variable', 'gold'),
            continue_node=game_data.get('continue_node', ''),
            theme=game_data.get('backgroundTheme', ''),
            chapter=game_data.get('chapter', ''),
            color=editor_data.get('color', NODE_DEFAULT_COLOR),
            backgroundImage=game_data.get('backgroundImage', ''),
            audio=game_data.get('audio', ''),
            music=game_data.get('music', '')
        )