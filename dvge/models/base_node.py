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
        
        # Portrait system data
        self.character_id = ""  # ID of character for portrait lookup
        self.expression = ""    # Specific expression to show
        self.portrait_position = "left"  # left, right, center
        self.portrait_effects = []  # List of portrait effect changes
        
        # Music and emotional context data
        self.mood = "neutral"  # neutral, happy, sad, tense, mysterious, romantic, action
        self.intensity = "medium"  # low, medium, high
        self.scene_type = "dialogue"  # dialogue, combat, exploration, cutscene, shop
        self.tags = []  # Custom tags for additional context
    
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
                "auto_advance_delay": self.auto_advance_delay,
                "character_id": getattr(self, 'character_id', ''),
                "expression": getattr(self, 'expression', ''),
                "portrait_position": getattr(self, 'portrait_position', 'left'),
                "portrait_effects": getattr(self, 'portrait_effects', []),
                "mood": getattr(self, 'mood', 'neutral'),
                "intensity": getattr(self, 'intensity', 'medium'),
                "scene_type": getattr(self, 'scene_type', 'dialogue'),
                "tags": getattr(self, 'tags', [])
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
    
    def update_from_dict(self, data):
        """Update node properties from dictionary data."""
        # Handle both old format (game_data/editor_data) and new format (flat)
        if 'game_data' in data and 'editor_data' in data:
            # Old format
            game_data = data['game_data']
            editor_data = data['editor_data']
            
            self.x = editor_data.get('x', self.x)
            self.y = editor_data.get('y', self.y)
            self.id = editor_data.get('id', self.id)
            self.color = editor_data.get('color', self.color)
            
            self.npc = game_data.get('npc', self.npc)
            self.text = game_data.get('text', self.text)
            self.backgroundTheme = game_data.get('backgroundTheme', self.backgroundTheme)
            self.chapter = game_data.get('chapter', self.chapter)
            self.backgroundImage = game_data.get('backgroundImage', self.backgroundImage)
            self.audio = game_data.get('audio', self.audio)
            self.music = game_data.get('music', self.music)
            self.auto_advance = game_data.get('auto_advance', self.auto_advance)
            self.auto_advance_delay = game_data.get('auto_advance_delay', self.auto_advance_delay)
        else:
            # New flat format
            self.x = data.get('x', self.x)
            self.y = data.get('y', self.y)
            self.id = data.get('id', self.id)
            self.color = data.get('color', self.color)
            self.npc = data.get('npc', self.npc)
            self.text = data.get('text', self.text)
            self.backgroundTheme = data.get('backgroundTheme', self.backgroundTheme)
            self.chapter = data.get('chapter', self.chapter)
            self.backgroundImage = data.get('backgroundImage', self.backgroundImage)
            self.audio = data.get('audio', self.audio)
            self.music = data.get('music', self.music)
            self.auto_advance = data.get('auto_advance', self.auto_advance)
            self.auto_advance_delay = data.get('auto_advance_delay', self.auto_advance_delay)
    
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
    
    def analyze_emotional_context(self):
        """Automatically analyzes the text content to determine emotional context."""
        text_lower = self.text.lower()
        
        # Mood detection based on keywords
        mood_keywords = {
            'happy': ['happy', 'joy', 'smile', 'laugh', 'excited', 'wonderful', 'great', 'amazing', 'celebrate'],
            'sad': ['sad', 'cry', 'weep', 'mourn', 'sorrow', 'grief', 'tragic', 'devastating', 'heartbroken'],
            'tense': ['danger', 'threat', 'warning', 'careful', 'watch out', 'enemy', 'trap', 'urgent', 'hurry'],
            'mysterious': ['strange', 'weird', 'mysterious', 'unknown', 'secret', 'hidden', 'whisper', 'shadow'],
            'romantic': ['love', 'romance', 'heart', 'kiss', 'romantic', 'darling', 'beloved', 'affection'],
            'action': ['fight', 'battle', 'attack', 'run', 'quick', 'fast', 'charge', 'strike', 'combat']
        }
        
        mood_scores = {}
        for mood, keywords in mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                mood_scores[mood] = score
        
        if mood_scores:
            self.mood = max(mood_scores, key=mood_scores.get)
        
        # Intensity detection based on punctuation and capitalization
        exclamation_count = text_lower.count('!')
        question_count = text_lower.count('?')
        caps_ratio = sum(1 for c in self.text if c.isupper()) / len(self.text) if self.text else 0
        
        if exclamation_count >= 2 or caps_ratio > 0.3:
            self.intensity = "high"
        elif exclamation_count == 0 and question_count == 0 and caps_ratio < 0.05:
            self.intensity = "low"
        else:
            self.intensity = "medium"
        
        # Scene type detection based on NPC and content
        if self.npc.lower() in ['narrator', 'system']:
            if any(word in text_lower for word in ['enters', 'leaves', 'walks', 'moves']):
                self.scene_type = "exploration"
            else:
                self.scene_type = "cutscene"
        elif any(word in text_lower for word in ['buy', 'sell', 'shop', 'merchant', 'gold', 'price']):
            self.scene_type = "shop"
        elif any(word in text_lower for word in ['fight', 'battle', 'attack', 'combat', 'enemy']):
            self.scene_type = "combat"
        else:
            self.scene_type = "dialogue"
        
        # Generate contextual tags
        self.tags = []
        if exclamation_count > 0:
            self.tags.append("emotional")
        if question_count > 0:
            self.tags.append("questioning")
        if any(word in text_lower for word in ['remember', 'past', 'before', 'long ago']):
            self.tags.append("memory")
        if any(word in text_lower for word in ['will', 'future', 'tomorrow', 'soon', 'plan']):
            self.tags.append("future")
    
    def set_text(self, new_text):
        """Sets new text and automatically analyzes emotional context."""
        self.text = new_text
        self.analyze_emotional_context()