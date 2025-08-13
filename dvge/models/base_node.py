# dvge/models/base_node.py

"""Base node class with common functionality for all node types."""

from ..constants import *


class BaseNode:
    """Base class for all node types with common functionality."""
    
    NODE_TYPE = "Base"
    
    def __init__(self, x, y, node_id, npc="Narrator", text="", theme="", 
                 chapter="", color=NODE_DEFAULT_COLOR, backgroundImage="", 
                 audio="", music="", auto_advance=False, auto_advance_delay=0):
        # Editor-specific data
        self.x = x
        self.y = y
        self.id = node_id
        self.canvas_item_ids = {}
        self.drag_data = {'x': 0, 'y': 0}
        self.calculated_text_height = 0
        
        # Game-specific data
        self.npc = npc
        self.text = text
        self.backgroundTheme = theme
        self.chapter = chapter
        self.color = color
        self.backgroundImage = backgroundImage
        self.audio = audio
        self.music = music
        self.auto_advance = auto_advance
        self.auto_advance_delay = auto_advance_delay
    
    def to_dict(self):
        """Serializes the node's data into a dictionary format."""
        return {
            "node_type": self.NODE_TYPE,
            "game_data": {
                "npc": self.npc,
                "text": self.text,
                "backgroundTheme": self.backgroundTheme,
                "chapter": self.chapter,
                "backgroundImage": self.backgroundImage,
                "audio": self.audio,
                "music": self.music,
                "auto_advance": self.auto_advance,
                "auto_advance_delay": self.auto_advance_delay
            },
            "editor_data": {
                "x": self.x,
                "y": self.y,
                "id": self.id,
                "color": self.color
            }
        }
    
    def get_height(self):
        """Calculates the total height of the node based on its content."""
        return NODE_HEADER_HEIGHT + NODE_BASE_BODY_HEIGHT + NODE_FOOTER_HEIGHT
    
    def get_connection_point_in(self):
        """Calculates the coordinates for incoming connection arrows."""
        return self.x, self.y + NODE_HEADER_HEIGHT // 2
    
    def get_connection_point_out(self, option_index):
        """Calculates the coordinates for outgoing connection arrows."""
        body_height = max(NODE_BASE_BODY_HEIGHT, self.calculated_text_height + 20)
        y_offset = (NODE_HEADER_HEIGHT + body_height + 
                   (option_index * OPTION_LINE_HEIGHT) + (OPTION_LINE_HEIGHT / 2))
        return self.x + NODE_WIDTH, self.y + y_offset
    
    @classmethod
    def from_dict(cls, data):
        """Creates a node instance from a dictionary."""
        game_data = data['game_data']
        editor_data = data['editor_data']
        
        return cls(
            x=editor_data['x'],
            y=editor_data['y'],
            node_id=editor_data['id'],
            npc=game_data.get('npc', 'Narrator'),
            text=game_data.get('text', ''),
            theme=game_data.get('backgroundTheme', ''),
            chapter=game_data.get('chapter', ''),
            color=editor_data.get('color', NODE_DEFAULT_COLOR),
            backgroundImage=game_data.get('backgroundImage', ''),
            audio=game_data.get('audio', ''),
            music=game_data.get('music', ''),
            auto_advance=game_data.get('auto_advance', False),
            auto_advance_delay=game_data.get('auto_advance_delay', 0)
        )