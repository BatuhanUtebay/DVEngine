# dvge/models/character_portrait.py

"""Character portrait system for visual storytelling."""

import os
import json
from typing import Dict, List, Optional


class CharacterPortrait:
    """Represents a character with multiple portrait expressions."""
    
    def __init__(self, character_id: str, name: str = ""):
        self.character_id = character_id
        self.name = name or character_id.replace('_', ' ').title()
        self.portraits = {}  # expression_name -> image_path
        self.default_expression = "neutral"
        self.description = ""
        
        # Visual properties
        self.position = "left"  # left, right, center
        self.size = "medium"    # small, medium, large
        self.offset_x = 0       # Fine positioning
        self.offset_y = 0
        
        # Animation properties
        self.transition_speed = "normal"  # slow, normal, fast, instant
        self.entrance_effect = "fade"     # fade, slide, zoom, none
        self.exit_effect = "fade"
    
    def add_portrait(self, expression: str, image_path: str):
        """Add a portrait for a specific expression."""
        if os.path.exists(image_path):
            self.portraits[expression] = image_path
            if not self.default_expression or expression == "neutral":
                self.default_expression = expression
        else:
            raise FileNotFoundError(f"Portrait image not found: {image_path}")
    
    def remove_portrait(self, expression: str):
        """Remove a portrait expression."""
        if expression in self.portraits:
            del self.portraits[expression]
            if self.default_expression == expression and self.portraits:
                self.default_expression = next(iter(self.portraits.keys()))
    
    def get_portrait_path(self, expression: str = None) -> Optional[str]:
        """Get the image path for a specific expression or default."""
        if expression and expression in self.portraits:
            return self.portraits[expression]
        elif self.default_expression in self.portraits:
            return self.portraits[self.default_expression]
        elif self.portraits:
            return next(iter(self.portraits.values()))
        return None
    
    def get_available_expressions(self) -> List[str]:
        """Get list of available expressions for this character."""
        return list(self.portraits.keys())
    
    def to_dict(self) -> Dict:
        """Serialize character portrait to dictionary."""
        return {
            "character_id": self.character_id,
            "name": self.name,
            "portraits": self.portraits.copy(),
            "default_expression": self.default_expression,
            "description": self.description,
            "position": self.position,
            "size": self.size,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "transition_speed": self.transition_speed,
            "entrance_effect": self.entrance_effect,
            "exit_effect": self.exit_effect
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create character portrait from dictionary."""
        character = cls(data["character_id"], data.get("name", ""))
        character.portraits = data.get("portraits", {})
        character.default_expression = data.get("default_expression", "neutral")
        character.description = data.get("description", "")
        character.position = data.get("position", "left")
        character.size = data.get("size", "medium")
        character.offset_x = data.get("offset_x", 0)
        character.offset_y = data.get("offset_y", 0)
        character.transition_speed = data.get("transition_speed", "normal")
        character.entrance_effect = data.get("entrance_effect", "fade")
        character.exit_effect = data.get("exit_effect", "fade")
        return character


class PortraitManager:
    """Manages all character portraits for a project."""
    
    def __init__(self):
        self.characters = {}  # character_id -> CharacterPortrait
        self.project_path = ""
    
    def set_project_path(self, path: str):
        """Set the project path for relative image paths."""
        self.project_path = path
    
    def add_character(self, character_id: str, name: str = "") -> CharacterPortrait:
        """Add a new character to the portrait system."""
        if character_id not in self.characters:
            self.characters[character_id] = CharacterPortrait(character_id, name)
        return self.characters[character_id]
    
    def remove_character(self, character_id: str):
        """Remove a character from the portrait system."""
        if character_id in self.characters:
            del self.characters[character_id]
    
    def get_character(self, character_id: str) -> Optional[CharacterPortrait]:
        """Get a character portrait by ID."""
        return self.characters.get(character_id)
    
    def get_all_characters(self) -> List[CharacterPortrait]:
        """Get all character portraits."""
        return list(self.characters.values())
    
    def get_character_names(self) -> List[str]:
        """Get list of all character names."""
        return [char.name for char in self.characters.values()]
    
    def get_character_ids(self) -> List[str]:
        """Get list of all character IDs."""
        return list(self.characters.keys())
    
    def find_character_by_name(self, name: str) -> Optional[CharacterPortrait]:
        """Find character by display name."""
        for character in self.characters.values():
            if character.name.lower() == name.lower():
                return character
        return None
    
    def import_character_batch(self, folder_path: str, character_id: str = None):
        """Import multiple portraits from a folder."""
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        if not character_id:
            character_id = os.path.basename(folder_path).lower().replace(' ', '_')
        
        character = self.add_character(character_id)
        
        # Common expression name mappings
        expression_mappings = {
            'neutral': ['neutral', 'normal', 'default', 'base'],
            'happy': ['happy', 'smile', 'joy', 'pleased'],
            'sad': ['sad', 'crying', 'depressed', 'sorrow'],
            'angry': ['angry', 'mad', 'furious', 'rage'],
            'surprised': ['surprised', 'shock', 'amazed', 'wow'],
            'confused': ['confused', 'puzzled', 'wondering'],
            'excited': ['excited', 'enthusiastic', 'energetic'],
            'worried': ['worried', 'concerned', 'anxious'],
            'thinking': ['thinking', 'pondering', 'contemplative']
        }
        
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                file_base = os.path.splitext(filename)[0].lower()
                
                # Try to match filename to expression
                expression = "neutral"
                for expr, keywords in expression_mappings.items():
                    if any(keyword in file_base for keyword in keywords):
                        expression = expr
                        break
                
                image_path = os.path.join(folder_path, filename)
                character.add_portrait(expression, image_path)
        
        return character
    
    def export_character_data(self, character_id: str) -> Optional[Dict]:
        """Export character data for sharing."""
        character = self.get_character(character_id)
        return character.to_dict() if character else None
    
    def import_character_data(self, data: Dict) -> CharacterPortrait:
        """Import character data from export."""
        character = CharacterPortrait.from_dict(data)
        self.characters[character.character_id] = character
        return character
    
    def to_dict(self) -> Dict:
        """Serialize all portrait data."""
        return {
            "characters": {char_id: char.to_dict() for char_id, char in self.characters.items()},
            "project_path": self.project_path
        }
    
    def from_dict(self, data: Dict):
        """Load portrait data from dictionary."""
        self.project_path = data.get("project_path", "")
        self.characters = {}
        
        for char_id, char_data in data.get("characters", {}).items():
            self.characters[char_id] = CharacterPortrait.from_dict(char_data)
    
    def save_to_file(self, filepath: str):
        """Save portrait data to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filepath: str):
        """Load portrait data from JSON file."""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.from_dict(data)


class DialoguePortraitEffect:
    """Represents a portrait change effect during dialogue."""
    
    def __init__(self, character_id: str, expression: str = None, 
                 position: str = None, show: bool = True):
        self.character_id = character_id
        self.expression = expression
        self.position = position  # left, right, center
        self.show = show  # True to show, False to hide
        self.delay = 0    # Delay in milliseconds
        self.duration = None  # Custom animation duration
    
    def to_dict(self) -> Dict:
        """Serialize portrait effect."""
        return {
            "character_id": self.character_id,
            "expression": self.expression,
            "position": self.position,
            "show": self.show,
            "delay": self.delay,
            "duration": self.duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create portrait effect from dictionary."""
        effect = cls(
            data["character_id"],
            data.get("expression"),
            data.get("position"),
            data.get("show", True)
        )
        effect.delay = data.get("delay", 0)
        effect.duration = data.get("duration")
        return effect