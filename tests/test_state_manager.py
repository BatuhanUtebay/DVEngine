import pytest
import sys
import os

# Add the project root to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dvge.core.state_manager import StateManager
from unittest.mock import Mock


class TestStateManager:
    """Test cases for the StateManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a mock app object
        self.mock_app = Mock()
        self.mock_app.nodes = {"intro": Mock()}
        self.mock_app.player_stats = {"health": 100}
        self.mock_app.player_inventory = []
        self.mock_app.story_flags = {}
        self.mock_app.variables = {"gold": 50}
        self.mock_app.quests = {}
        self.mock_app.enemies = {}
        self.mock_app.timers = {}
        
        self.state_manager = StateManager(self.mock_app)
    
    def test_initialization(self):
        """Test that StateManager initializes correctly."""
        assert self.state_manager.app == self.mock_app
        assert len(self.state_manager.undo_stack) == 0
        assert len(self.state_manager.redo_stack) == 0
    
    def test_save_state(self):
        """Test that save_state adds to undo stack."""
        initial_stack_size = len(self.state_manager.undo_stack)
        self.state_manager.save_state("Test Action")
        
        assert len(self.state_manager.undo_stack) == initial_stack_size + 1
        assert len(self.state_manager.redo_stack) == 0
    
    def test_undo_empty_stack(self):
        """Test that undo does nothing when stack is empty."""
        result = self.state_manager.undo()
        assert result is False
    
    def test_redo_empty_stack(self):
        """Test that redo does nothing when stack is empty.""" 
        result = self.state_manager.redo()
        assert result is False
    
    def test_clear_history(self):
        """Test that clear_history empties both stacks."""
        # Add some states
        self.state_manager.save_state("Action 1")
        self.state_manager.save_state("Action 2")
        
        assert len(self.state_manager.undo_stack) > 0
        
        self.state_manager.clear_history()
        
        assert len(self.state_manager.undo_stack) == 0
        assert len(self.state_manager.redo_stack) == 0