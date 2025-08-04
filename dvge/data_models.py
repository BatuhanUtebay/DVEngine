# dvge/data_models.py
from .constants import *

class DialogueNode:
    """
    Represents a single node in the dialogue graph. This class holds all the
    data for a node, both for the game logic (like text and choices) and for
    the editor's visual representation (like position and canvas item IDs).
    """
    def __init__(self, x, y, node_id, npc="Narrator", text="", options=None, theme="", chapter="", color="#3A3A3A", backgroundImage="", audio=""):
        # Editor-specific data
        self.x = x
        self.y = y
        self.id = node_id
        self.canvas_item_ids = {}  # Stores the IDs of canvas elements for this node
        self.drag_data = {'x': 0, 'y': 0} # Temporary data for drag operations
        self.calculated_text_height = 0 # For dynamic resizing based on text length

        # Game-specific data
        self.npc = npc
        self.text = text
        self.options = options if options else []
        self.backgroundTheme = theme
        self.chapter = chapter
        self.color = color
        self.backgroundImage = backgroundImage
        self.audio = audio

    def to_dict(self):
        """
        Serializes the node's data into a dictionary format, separating game data
        from editor data. This is used for saving the project to a file.
        """
        return {
            "game_data": {
                "npc": self.npc, "text": self.text, "options": self.options,
                "backgroundTheme": self.backgroundTheme, "chapter": self.chapter,
                "backgroundImage": self.backgroundImage, "audio": self.audio
            },
            "editor_data": {"x": self.x, "y": self.y, "id": self.id, "color": self.color}
        }

    @staticmethod
    def from_dict(data):
        """
        Creates a DialogueNode instance from a dictionary. This is used when
        loading a project from a file.
        """
        game_data = data['game_data']
        editor_data = data['editor_data']
        return DialogueNode(
            x=editor_data['x'], y=editor_data['y'], node_id=editor_data['id'],
            npc=game_data.get('npc', 'Narrator'), text=game_data.get('text', ''),
            options=game_data.get('options', []), theme=game_data.get('backgroundTheme', ''),
            chapter=game_data.get('chapter', ''), color=editor_data.get('color', '#3A3A3A'),
            backgroundImage=game_data.get('backgroundImage', ''),
            audio=game_data.get('audio', '')
        )

    def get_height(self):
        """Calculates the total height of the node based on its content."""
        body_height = max(NODE_BASE_BODY_HEIGHT, self.calculated_text_height + 20)
        return NODE_HEADER_HEIGHT + body_height + (len(self.options) * OPTION_LINE_HEIGHT) + NODE_FOOTER_HEIGHT

    def get_connection_point_in(self):
        """Calculates the coordinates for incoming connection arrows."""
        return self.x, self.y + NODE_HEADER_HEIGHT // 2

    def get_connection_point_out(self, option_index):
        """Calculates the coordinates for outgoing connection arrows from a specific choice."""
        body_height = max(NODE_BASE_BODY_HEIGHT, self.calculated_text_height + 20)
        y_offset = NODE_HEADER_HEIGHT + body_height + (option_index * OPTION_LINE_HEIGHT) + (OPTION_LINE_HEIGHT / 2)
        return self.x + NODE_WIDTH, self.y + y_offset