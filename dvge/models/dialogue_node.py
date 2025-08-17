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
        
        # Timed choice system properties
        self.enable_timed_choices = False  # Whether this node uses timed choices
        self.choice_timer_duration = 10.0  # Default timer duration in seconds
        self.default_choice_index = 0  # Index of choice selected when timer expires
        self.allow_silence = True  # Whether "..." silence option is available
        self.silence_text = "..."  # Text for silence option
        self.show_timer = True  # Whether to show countdown visual
        self.timer_warning_time = 3.0  # When to show timer warning (red countdown)
    
    def to_dict(self):
        """Serializes the dialogue node's data."""
        data = super().to_dict()
        data["game_data"].update({
            "options": self.options,
            "enable_timed_choices": self.enable_timed_choices,
            "choice_timer_duration": self.choice_timer_duration,
            "default_choice_index": self.default_choice_index,
            "allow_silence": self.allow_silence,
            "silence_text": self.silence_text,
            "show_timer": self.show_timer,
            "timer_warning_time": self.timer_warning_time
        })
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
        
        node = cls(
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
        
        # Load timed choice properties
        node.enable_timed_choices = game_data.get('enable_timed_choices', False)
        node.choice_timer_duration = game_data.get('choice_timer_duration', 10.0)
        node.default_choice_index = game_data.get('default_choice_index', 0)
        node.allow_silence = game_data.get('allow_silence', True)
        node.silence_text = game_data.get('silence_text', "...")
        node.show_timer = game_data.get('show_timer', True)
        node.timer_warning_time = game_data.get('timer_warning_time', 3.0)
        
        return node