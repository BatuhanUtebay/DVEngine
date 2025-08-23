import pytest
import sys
import os

# Add the project root to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from dvge.core.batch_operations import BatchOperationManager, NodeFilter, BatchOperation
from dvge.models.base_node import BaseNode
from dvge.models.dialogue_node import DialogueNode
from unittest.mock import Mock


class TestNodeFilter:
    """Test cases for NodeFilter functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mock nodes
        self.nodes = {
            'node1': Mock(spec=BaseNode),
            'node2': Mock(spec=BaseNode),
            'node3': Mock(spec=BaseNode)
        }
        
        # Set up node attributes
        self.nodes['node1'].NODE_TYPE = 'dialogue'
        self.nodes['node1'].npc = 'Alice'
        self.nodes['node1'].text = 'Hello there!'
        self.nodes['node1'].backgroundTheme = 'forest'
        self.nodes['node1'].chapter = 'Chapter 1'
        self.nodes['node1'].color = '#FF0000'
        
        self.nodes['node2'].NODE_TYPE = 'combat'
        self.nodes['node2'].npc = 'Bob'
        self.nodes['node2'].text = 'Fight!'
        self.nodes['node2'].backgroundTheme = 'dungeon'
        self.nodes['node2'].chapter = 'Chapter 2'
        self.nodes['node2'].color = '#00FF00'
        
        self.nodes['node3'].NODE_TYPE = 'dialogue'
        self.nodes['node3'].npc = 'Alice'
        self.nodes['node3'].text = 'Goodbye!'
        self.nodes['node3'].backgroundTheme = 'forest'
        self.nodes['node3'].chapter = 'Chapter 1'
        self.nodes['node3'].color = '#0000FF'
    
    def test_filter_by_type(self):
        """Test filtering nodes by type."""
        dialogue_nodes = NodeFilter.by_type(self.nodes, 'dialogue')
        assert len(dialogue_nodes) == 2
        
        combat_nodes = NodeFilter.by_type(self.nodes, 'combat')
        assert len(combat_nodes) == 1
    
    def test_filter_by_npc_exact(self):
        """Test filtering nodes by exact NPC name."""
        alice_nodes = NodeFilter.by_npc(self.nodes, 'Alice', exact_match=True)
        assert len(alice_nodes) == 2
        
        bob_nodes = NodeFilter.by_npc(self.nodes, 'Bob', exact_match=True)
        assert len(bob_nodes) == 1
    
    def test_filter_by_npc_partial(self):
        """Test filtering nodes by partial NPC name."""
        a_nodes = NodeFilter.by_npc(self.nodes, 'A', exact_match=False)
        assert len(a_nodes) == 2  # Alice matches
        
        lowercase_alice = NodeFilter.by_npc(self.nodes, 'alice', exact_match=False)
        assert len(lowercase_alice) == 2  # Should be case insensitive
    
    def test_filter_by_text_content(self):
        """Test filtering nodes by text content."""
        hello_nodes = NodeFilter.by_text_content(self.nodes, 'Hello')
        assert len(hello_nodes) == 1
        
        # Case insensitive by default
        hello_lower = NodeFilter.by_text_content(self.nodes, 'hello')
        assert len(hello_lower) == 1
        
        # Case sensitive
        hello_sensitive = NodeFilter.by_text_content(self.nodes, 'hello', case_sensitive=True)
        assert len(hello_sensitive) == 0
    
    def test_filter_by_theme(self):
        """Test filtering nodes by theme."""
        forest_nodes = NodeFilter.by_theme(self.nodes, 'forest')
        assert len(forest_nodes) == 2
        
        dungeon_nodes = NodeFilter.by_theme(self.nodes, 'dungeon')
        assert len(dungeon_nodes) == 1
    
    def test_filter_by_chapter(self):
        """Test filtering nodes by chapter."""
        chapter1_nodes = NodeFilter.by_chapter(self.nodes, 'Chapter 1')
        assert len(chapter1_nodes) == 2
        
        chapter2_nodes = NodeFilter.by_chapter(self.nodes, 'Chapter 2')
        assert len(chapter2_nodes) == 1
    
    def test_filter_by_color(self):
        """Test filtering nodes by color."""
        red_nodes = NodeFilter.by_color(self.nodes, '#FF0000')
        assert len(red_nodes) == 1
    
    def test_orphaned_nodes(self):
        """Test finding orphaned nodes."""
        # Add options to create connections
        self.nodes['node1'].options = [{'nextNode': 'node2'}]
        self.nodes['node2'].options = []
        self.nodes['node3'].options = []
        
        # Override intro detection for this test
        test_nodes = {'intro': self.nodes['node1'], 'node2': self.nodes['node2'], 'node3': self.nodes['node3']}
        
        orphaned = NodeFilter.orphaned_nodes(test_nodes)
        # node3 should be orphaned (not referenced and not intro)
        assert len(orphaned) == 1
        assert orphaned[0] == self.nodes['node3']
    
    def test_dead_end_nodes(self):
        """Test finding dead end nodes."""
        # Set up options
        self.nodes['node1'].options = [{'nextNode': 'node2'}]
        self.nodes['node2'].options = []  # Dead end
        self.nodes['node3'].options = []  # Dead end
        
        dead_ends = NodeFilter.dead_end_nodes(self.nodes)
        assert len(dead_ends) == 2
    
    def test_custom_filter(self):
        """Test custom filter function."""
        # Filter nodes with 'A' in NPC name
        custom_filter = lambda node: 'A' in getattr(node, 'npc', '')
        
        filtered = NodeFilter.by_custom_filter(self.nodes, custom_filter)
        assert len(filtered) == 2  # Alice nodes


class TestBatchOperation:
    """Test cases for BatchOperation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.nodes = [Mock(spec=BaseNode) for _ in range(3)]
        
        for i, node in enumerate(self.nodes):
            node.id = f'node{i}'
            node.text = f'Text {i}'
    
    def test_successful_operation(self):
        """Test successful batch operation."""
        def test_op(node, multiplier=2):
            return f"Processed {node.id} with {multiplier}"
        
        operation = BatchOperation("test_op", test_op)
        result = operation.apply(self.nodes, multiplier=3)
        
        assert result['operation'] == 'test_op'
        assert result['total'] == 3
        assert result['successful'] == 3
        assert result['failed'] == 0
        assert len(result['results']) == 3
    
    def test_operation_with_failures(self):
        """Test batch operation with some failures."""
        def failing_op(node):
            if node.id == 'node1':
                raise ValueError("Test error")
            return f"Success for {node.id}"
        
        operation = BatchOperation("failing_op", failing_op)
        result = operation.apply(self.nodes)
        
        assert result['total'] == 3
        assert result['successful'] == 2
        assert result['failed'] == 1
        
        # Check that failure is recorded
        failed_results = [r for r in result['results'] if not r['success']]
        assert len(failed_results) == 1
        assert failed_results[0]['node_id'] == 'node1'
        assert 'Test error' in failed_results[0]['error']


class TestBatchOperationManager:
    """Test cases for BatchOperationManager functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_app = Mock()
        self.mock_app.nodes = {}
        self.mock_app.selected_node_ids = []
        self.mock_app.state_manager = Mock()
        
        # Create test nodes
        for i in range(3):
            node = Mock(spec=BaseNode)
            node.id = f'node{i}'
            node.text = f'Original text {i}'
            node.npc = 'TestNPC'
            node.color = '#FFFFFF'
            self.mock_app.nodes[f'node{i}'] = node
        
        self.manager = BatchOperationManager(self.mock_app)
    
    def test_initialization(self):
        """Test manager initialization."""
        assert self.manager.app == self.mock_app
        assert len(self.manager.operations) > 0  # Should have default operations
        assert isinstance(self.manager.history, list)
    
    def test_register_operation(self):
        """Test registering custom operations."""
        def custom_op(node):
            return "custom result"
        
        self.manager.register_operation("custom", custom_op, "Custom operation")
        
        assert "custom" in self.manager.operations
        assert self.manager.operations["custom"].description == "Custom operation"
    
    def test_get_available_operations(self):
        """Test getting list of available operations."""
        operations = self.manager.get_available_operations()
        
        assert isinstance(operations, dict)
        assert len(operations) > 0
        assert "find_replace_text" in operations
    
    def test_execute_find_replace_operation(self):
        """Test executing find and replace operation."""
        # Set up test data
        self.mock_app.nodes['node0'].text = "Hello world"
        self.mock_app.nodes['node1'].text = "Hello there"
        self.mock_app.nodes['node2'].text = "Goodbye world"
        
        result = self.manager.execute_operation(
            "find_replace_text",
            "all",
            find_text="Hello",
            replace_text="Hi",
            case_sensitive=False
        )
        
        assert result['operation'] == 'find_replace_text'
        assert result['successful'] >= 2  # At least 2 nodes should be affected
        
        # Check that text was actually replaced
        assert self.mock_app.nodes['node0'].text == "Hi world"
        assert self.mock_app.nodes['node1'].text == "Hi there"
        assert self.mock_app.nodes['node2'].text == "Goodbye world"  # Unchanged
    
    def test_execute_change_color_operation(self):
        """Test executing color change operation."""
        result = self.manager.execute_operation(
            "change_color",
            "all",
            new_color="#FF0000"
        )
        
        assert result['operation'] == 'change_color'
        assert result['successful'] == 3
        
        # Check that colors were changed
        for node in self.mock_app.nodes.values():
            assert node.color == "#FF0000"
    
    def test_execute_with_selected_filter(self):
        """Test executing operation with selected nodes filter."""
        self.mock_app.selected_node_ids = ['node0', 'node1']
        
        result = self.manager.execute_operation(
            "change_color", 
            "selected",
            new_color="#00FF00"
        )
        
        assert result['successful'] == 2
        assert self.mock_app.nodes['node0'].color == "#00FF00"
        assert self.mock_app.nodes['node1'].color == "#00FF00"
        assert self.mock_app.nodes['node2'].color == "#FFFFFF"  # Unchanged
    
    def test_execute_with_empty_filter(self):
        """Test executing operation with filter that matches no nodes."""
        result = self.manager.execute_operation(
            "change_color",
            "selected",  # No selected nodes
            new_color="#0000FF"
        )
        
        assert result['total'] == 0
        assert result['successful'] == 0
        assert 'message' in result
    
    def test_state_saving(self):
        """Test that state is saved after successful operations."""
        self.manager.execute_operation(
            "change_color",
            "all",
            new_color="#123456"
        )
        
        # Should have called save_state
        self.mock_app.state_manager.save_state.assert_called_once()
    
    def test_history_tracking(self):
        """Test that operation history is tracked."""
        initial_history_length = len(self.manager.history)
        
        self.manager.execute_operation(
            "change_color",
            "all", 
            new_color="#ABCDEF"
        )
        
        assert len(self.manager.history) == initial_history_length + 1
        
        # Check history entry
        last_entry = self.manager.history[-1]
        assert last_entry['operation'] == 'change_color'
    
    def test_fix_empty_text_operation(self):
        """Test fix empty text operation."""
        # Set up nodes with empty text
        self.mock_app.nodes['node0'].text = ""
        self.mock_app.nodes['node1'].text = "   "  # Whitespace only
        self.mock_app.nodes['node2'].text = "Valid text"
        
        result = self.manager.execute_operation(
            "fix_empty_text",
            "all",
            placeholder_text="[PLACEHOLDER]"
        )
        
        assert result['successful'] >= 2
        assert self.mock_app.nodes['node0'].text == "[PLACEHOLDER]"
        assert self.mock_app.nodes['node1'].text == "[PLACEHOLDER]"
        assert self.mock_app.nodes['node2'].text == "Valid text"  # Should remain unchanged
    
    def test_invalid_operation_name(self):
        """Test executing invalid operation name."""
        with pytest.raises(ValueError, match="Unknown operation"):
            self.manager.execute_operation("invalid_operation", "all")
    
    def test_invalid_filter_name(self):
        """Test executing with invalid filter name."""
        with pytest.raises(ValueError, match="Unknown filter"):
            result = self.manager.execute_operation("change_color", "invalid_filter")
    
    def test_clear_history(self):
        """Test clearing operation history."""
        # Add some operations to history
        self.manager.execute_operation("change_color", "all", new_color="#111111")
        self.manager.execute_operation("change_color", "all", new_color="#222222")
        
        assert len(self.manager.history) > 0
        
        self.manager.clear_history()
        assert len(self.manager.history) == 0