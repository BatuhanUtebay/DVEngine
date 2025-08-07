# dvge/data_models.py
from .constants import *
from .game_mechanics import Enemy # Import the new Enemy class

class DialogueNode:
    """
    Represents a single node in the dialogue graph. This class holds all the
    data for a node, both for the game logic (like text and choices) and for
    the editor's visual representation (like position and canvas item IDs).
    """
    NODE_TYPE = "Dialogue"

    def __init__(self, x, y, node_id, npc="Narrator", text="", options=None, theme="", chapter="", color=NODE_DEFAULT_COLOR, backgroundImage="", audio="", music="", auto_advance=False, auto_advance_delay=0):
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
        self.options = options if options else []
        self.backgroundTheme = theme
        self.chapter = chapter
        self.color = color
        self.backgroundImage = backgroundImage
        self.audio = audio
        self.music = music
        self.auto_advance = auto_advance
        self.auto_advance_delay = auto_advance_delay

    def to_dict(self):
        """
        Serializes the node's data into a dictionary format.
        """
        return {
            "node_type": self.NODE_TYPE,
            "game_data": {
                "npc": self.npc, "text": self.text, "options": self.options,
                "backgroundTheme": self.backgroundTheme, "chapter": self.chapter,
                "backgroundImage": self.backgroundImage, "audio": self.audio,
                "music": self.music, "auto_advance": self.auto_advance,
                "auto_advance_delay": self.auto_advance_delay
            },
            "editor_data": {"x": self.x, "y": self.y, "id": self.id, "color": self.color}
        }

    @staticmethod
    def from_dict(data):
        """
        Creates a DialogueNode or CombatNode instance from a dictionary.
        This now acts as a factory for all node types.
        """
        node_type = data.get("node_type", "Dialogue")
        if node_type == "Combat":
            return CombatNode.from_dict(data)
        if node_type == "DiceRoll":
            return DiceRollNode.from_dict(data)
        
        # Default to DialogueNode
        game_data = data['game_data']
        editor_data = data['editor_data']
        return DialogueNode(
            x=editor_data['x'], y=editor_data['y'], node_id=editor_data['id'],
            npc=game_data.get('npc', 'Narrator'), text=game_data.get('text', ''),
            options=game_data.get('options', []), theme=game_data.get('backgroundTheme', ''),
            chapter=game_data.get('chapter', ''), color=editor_data.get('color', NODE_DEFAULT_COLOR),
            backgroundImage=game_data.get('backgroundImage', ''),
            audio=game_data.get('audio', ''),
            music=game_data.get('music', ''),
            auto_advance=game_data.get('auto_advance', False),
            auto_advance_delay=game_data.get('auto_advance_delay', 0)
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

class CombatNode(DialogueNode):
    """
    A special type of node for handling combat encounters.
    """
    NODE_TYPE = "Combat"

    def __init__(self, x, y, node_id, text="A battle begins!", enemies=None, successNode="", failNode="", **kwargs):
        super().__init__(x, y, node_id, npc="Combat", text=text, **kwargs)
        self.enemies = enemies if enemies else [] # List of enemy IDs
        self.successNode = successNode # Node to go to on victory
        self.failNode = failNode # Node to go to on defeat (e.g., game over)

    def to_dict(self):
        """Serializes the combat node's data."""
        data = super().to_dict()
        data["node_type"] = self.NODE_TYPE
        data["game_data"]["enemies"] = self.enemies
        data["game_data"]["successNode"] = self.successNode
        data["game_data"]["failNode"] = self.failNode
        # Remove options as they are not used in combat nodes
        data["game_data"].pop("options", None)
        return data

    @staticmethod
    def from_dict(data):
        """Creates a CombatNode instance from a dictionary."""
        game_data = data['game_data']
        editor_data = data['editor_data']
        return CombatNode(
            x=editor_data['x'], y=editor_data['y'], node_id=editor_data['id'],
            text=game_data.get('text', 'A battle begins!'),
            enemies=game_data.get('enemies', []),
            successNode=game_data.get('successNode', ''),
            failNode=game_data.get('failNode', ''),
            theme=game_data.get('backgroundTheme', ''),
            chapter=game_data.get('chapter', ''),
            color=editor_data.get('color', NODE_DEFAULT_COLOR),
            backgroundImage=game_data.get('backgroundImage', ''),
            audio=game_data.get('audio', '')
        )
    
    def get_height(self):
        """Combat nodes have a fixed height for simplicity."""
        return NODE_HEADER_HEIGHT + NODE_BASE_BODY_HEIGHT + NODE_FOOTER_HEIGHT

class DiceRollNode(DialogueNode):
    """
    A special type of node for handling dice rolls.
    """
    NODE_TYPE = "DiceRoll"

    def __init__(self, x, y, node_id, text="A challenge appears!", num_dice=1, num_sides=6, success_threshold=4, success_node="", failure_node="", **kwargs):
        super().__init__(x, y, node_id, npc="Dice Roll", text=text, **kwargs)
        self.num_dice = num_dice
        self.num_sides = num_sides
        self.success_threshold = success_threshold
        self.success_node = success_node
        self.failure_node = failure_node

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

    @staticmethod
    def from_dict(data):
        """Creates a DiceRollNode instance from a dictionary."""
        game_data = data['game_data']
        editor_data = data['editor_data']
        return DiceRollNode(
            x=editor_data['x'], y=editor_data['y'], node_id=editor_data['id'],
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

class Quest:
    """Represents a single quest or journal entry."""
    def __init__(self, quest_id, name="New Quest", description="", state="inactive"):
        self.id = quest_id
        self.name = name
        self.description = description
        self.state = state  # inactive, active, completed, failed

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description, "state": self.state}

    @staticmethod
    def from_dict(data):
        return Quest(quest_id=data.get('id', ''), name=data.get('name', 'New Quest'),
                     description=data.get('description', ''), state=data.get('state', 'inactive'))

class GameTimer:
    """Represents a timer for timed events."""
    def __init__(self, timer_id, duration=60):
        self.id = timer_id
        self.duration = duration # in seconds

    def to_dict(self):
        return {"id": self.id, "duration": self.duration}

    @staticmethod
    def from_dict(data):
        return GameTimer(timer_id=data.get('id', ''), duration=data.get('duration', 60))
