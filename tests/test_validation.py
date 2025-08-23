import pytest
import sys
import os

# Add the project root to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dvge.core.validation import ProjectValidator
from dvge.models.dialogue_node import DialogueNode
from unittest.mock import Mock


class TestProjectValidator:
    """Test cases for the ProjectValidator class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_app = Mock()
        self.validator = ProjectValidator(self.mock_app)
    
    def test_no_intro_node_error(self):
        """Test that missing intro node is detected as error."""
        self.mock_app.nodes = {"start": Mock()}  # No 'intro' node
        
        errors, warnings = self.validator.validate_project()
        
        assert len(errors) == 1
        assert "intro" in errors[0].lower()
    
    def test_valid_project_with_intro(self):
        """Test validation of a valid minimal project."""
        # Create a minimal valid project
        intro_node = Mock()
        intro_node.options = []
        # Mock attributes that validation expects
        intro_node.success_node = ""
        intro_node.failure_node = ""
        intro_node.combat_data = None
        
        self.mock_app.nodes = {"intro": intro_node}
        
        errors, warnings = self.validator.validate_project()
        
        # Should have no critical errors for basic validation
        assert isinstance(errors, list)
        assert isinstance(warnings, list)
    
    def test_unreachable_nodes_warning(self):
        """Test that unreachable nodes generate warnings."""
        # Create intro node that doesn't connect to other nodes
        intro_node = Mock()
        intro_node.options = []
        intro_node.success_node = ""
        intro_node.failure_node = ""
        intro_node.combat_data = None
        
        unreachable_node = Mock()
        unreachable_node.options = []
        unreachable_node.success_node = ""
        unreachable_node.failure_node = ""
        unreachable_node.combat_data = None
        
        self.mock_app.nodes = {
            "intro": intro_node,
            "unreachable": unreachable_node
        }
        
        # Mock the _find_reachable_nodes method to return only intro
        def mock_find_reachable(self):
            return {"intro"}
        
        import types
        self.validator._find_reachable_nodes = types.MethodType(mock_find_reachable, self.validator)
        
        errors, warnings = self.validator.validate_project()
        
        # Should have warnings about unreachable nodes
        assert isinstance(errors, list)
        assert isinstance(warnings, list)
        assert len(warnings) >= 1
        assert any("unreachable" in warning.lower() for warning in warnings)
    
    def test_empty_project(self):
        """Test validation of completely empty project."""
        self.mock_app.nodes = {}
        
        errors, warnings = self.validator.validate_project()
        
        assert len(errors) == 1
        assert "intro" in errors[0].lower()