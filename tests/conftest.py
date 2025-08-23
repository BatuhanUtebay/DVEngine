"""Test configuration and fixtures for DVGE tests."""

import pytest
import sys
import os

# Add the project root to Python path for all tests
project_root = os.path.join(os.path.dirname(__file__), '..')
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def mock_app():
    """Create a mock application instance for testing."""
    from unittest.mock import Mock
    
    app = Mock()
    app.nodes = {}
    app.player_stats = {"health": 100, "strength": 10, "defense": 5}
    app.player_inventory = []
    app.story_flags = {}
    app.variables = {"gold": 50}
    app.quests = {}
    app.enemies = {}
    app.timers = {}
    app.active_node_id = None
    app.selected_node_ids = []
    
    return app


@pytest.fixture
def sample_dialogue_node():
    """Create a sample dialogue node for testing."""
    from dvge.models.dialogue_node import DialogueNode
    
    return DialogueNode(
        x=100,
        y=200, 
        node_id="test_dialogue",
        npc="Test Character",
        text="This is a test dialogue."
    )