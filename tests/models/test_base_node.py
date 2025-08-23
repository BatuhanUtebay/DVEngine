import pytest
import sys
import os

# Add the project root to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from dvge.models.base_node import BaseNode
from dvge.constants import NODE_DEFAULT_COLOR


class TestBaseNode:
    """Test cases for the BaseNode class."""
    
    def test_initialization_defaults(self):
        """Test that BaseNode initializes with correct default values."""
        node = BaseNode(100, 200, "test_id")
        
        assert node.x == 100
        assert node.y == 200
        assert node.id == "test_id"
        assert node.npc == "Narrator"
        assert node.text == ""
        assert node.color == NODE_DEFAULT_COLOR
        assert node.auto_advance is False
        assert node.auto_advance_delay == 0
        assert isinstance(node.canvas_item_ids, dict)
        assert isinstance(node.drag_data, dict)
    
    def test_initialization_custom_values(self):
        """Test BaseNode initialization with custom values."""
        node = BaseNode(
            x=50,
            y=75,
            node_id="custom_id",
            npc="TestNPC",
            text="Custom text",
            theme="dark",
            chapter="Chapter 1",
            color="#FF0000",
            auto_advance=True,
            auto_advance_delay=5
        )
        
        assert node.x == 50
        assert node.y == 75
        assert node.id == "custom_id"
        assert node.npc == "TestNPC"
        assert node.text == "Custom text"
        assert node.backgroundTheme == "dark"
        assert node.chapter == "Chapter 1"
        assert node.color == "#FF0000"
        assert node.auto_advance is True
        assert node.auto_advance_delay == 5
    
    def test_portrait_system_defaults(self):
        """Test that portrait system fields have correct defaults."""
        node = BaseNode(0, 0, "test")
        
        assert node.character_id == ""
        assert node.expression == ""
        assert node.portrait_position == "left"
        assert isinstance(node.portrait_effects, list)
        assert len(node.portrait_effects) == 0
    
    def test_music_system_defaults(self):
        """Test that music/mood system fields have correct defaults."""
        node = BaseNode(0, 0, "test")
        
        assert node.mood == "neutral"
        assert node.intensity == "medium"
        assert node.scene_type == "dialogue"
        assert isinstance(node.tags, list)
        assert len(node.tags) == 0
    
    def test_media_system_defaults(self):
        """Test that media system fields have correct defaults."""
        node = BaseNode(0, 0, "test")
        
        assert isinstance(node.media_assets, list)
        assert len(node.media_assets) == 0
        assert node.media_enabled is True