# dvge/__init__.py

"""
Dialogue Venture Game Engine (DVGE)
A powerful, intuitive, node-based editor for creating branching dialogue and narrative-driven experiences.
"""

__version__ = "1.0.0"
__author__ = "Dice Verce"

# Import main components for easier access
from .core.application import DVGApp

from .models import DialogueNode, CombatNode, DiceRollNode, Quest, GameTimer, Enemy

__all__ = [
    'DVGApp',
    'DialogueNode', 
    'CombatNode', 
    'DiceRollNode', 
    'Quest', 
    'GameTimer',
    'Enemy'
]