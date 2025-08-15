# dvge/models/timer_node.py

"""Timer node implementation for time-based events and delays."""

from .base_node import BaseNode
from ..constants import *


class TimerNode(BaseNode):
    """A special type of node for handling time-based delays and events."""
    
    NODE_TYPE = "Timer"
    
    def __init__(self, x, y, node_id, text="Please wait...", 
                 wait_time=5, time_unit="seconds", next_node="",
                 show_countdown=True, allow_skip=False, **kwargs):
        super().__init__(x, y, node_id, npc="System", text=text, **kwargs)
        self.wait_time = wait_time  # Time to wait
        self.time_unit = time_unit  # "seconds", "minutes", "hours", "days"
        self.next_node = next_node  # Where to go after timer expires
        self.show_countdown = show_countdown  # Show countdown timer
        self.allow_skip = allow_skip  # Allow player to skip waiting
        self.options = []  # Empty options list for UI compatibility
    
    def to_dict(self):
        """Serializes the timer node's data."""
        data = super().to_dict()
        data["node_type"] = self.NODE_TYPE
        data["game_data"]["wait_time"] = self.wait_time
        data["game_data"]["time_unit"] = self.time_unit
        data["game_data"]["next_node"] = self.next_node
        data["game_data"]["show_countdown"] = self.show_countdown
        data["game_data"]["allow_skip"] = self.allow_skip
        # Remove options as they are not used in timer nodes
        data["game_data"].pop("options", None)
        return data
    
    def get_height(self):
        """Timer nodes have a standard height."""
        return NODE_HEADER_HEIGHT + NODE_BASE_BODY_HEIGHT + NODE_FOOTER_HEIGHT + 30
    
    @classmethod
    def from_dict(cls, data):
        """Creates a TimerNode instance from a dictionary."""
        game_data = data['game_data']
        editor_data = data['editor_data']
        
        return cls(
            x=editor_data['x'],
            y=editor_data['y'],
            node_id=editor_data['id'],
            text=game_data.get('text', 'Please wait...'),
            wait_time=game_data.get('wait_time', 5),
            time_unit=game_data.get('time_unit', 'seconds'),
            next_node=game_data.get('next_node', ''),
            show_countdown=game_data.get('show_countdown', True),
            allow_skip=game_data.get('allow_skip', False),
            theme=game_data.get('backgroundTheme', ''),
            chapter=game_data.get('chapter', ''),
            color=editor_data.get('color', NODE_DEFAULT_COLOR),
            backgroundImage=game_data.get('backgroundImage', ''),
            audio=game_data.get('audio', ''),
            music=game_data.get('music', '')
        )