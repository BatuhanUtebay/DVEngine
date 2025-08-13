# dvge/models/__init__.py

"""Models package for DVGE data structures."""

from .base_node import BaseNode
from .dialogue_node import DialogueNode
from .combat_node import CombatNode
from .dice_roll_node import DiceRollNode
from .shop_node import ShopNode
from .random_event_node import RandomEventNode
from .timer_node import TimerNode
from .inventory_node import InventoryNode
from .quest import Quest
from .game_timer import GameTimer
from .enemy import Enemy

# Factory function for creating nodes from dictionaries
def create_node_from_dict(data):
    """Creates the appropriate node type from a dictionary."""
    node_type = data.get("node_type", "Dialogue")
    
    if node_type == "Combat":
        return CombatNode.from_dict(data)
    elif node_type == "DiceRoll":
        return DiceRollNode.from_dict(data)
    elif node_type == "Shop":
        return ShopNode.from_dict(data)
    elif node_type == "RandomEvent":
        return RandomEventNode.from_dict(data)
    elif node_type == "Timer":
        return TimerNode.from_dict(data)
    elif node_type == "Inventory":
        return InventoryNode.from_dict(data)
    else:
        return DialogueNode.from_dict(data)

__all__ = [
    'BaseNode',
    'DialogueNode', 
    'CombatNode', 
    'DiceRollNode',
    'ShopNode',
    'RandomEventNode', 
    'TimerNode',
    'InventoryNode',
    'Quest', 
    'GameTimer',
    'Enemy',
    'create_node_from_dict'
]