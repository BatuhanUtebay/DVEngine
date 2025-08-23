"""Batch operations system for efficiently managing multiple nodes."""

import re
from typing import List, Dict, Any, Callable, Set, Union
from ..models.base_node import BaseNode


class BatchOperation:
    """Represents a single batch operation that can be applied to multiple nodes."""
    
    def __init__(self, name: str, operation_func: Callable, description: str = ""):
        self.name = name
        self.operation_func = operation_func
        self.description = description
        self.results = []
        
    def apply(self, nodes: List[BaseNode], **kwargs) -> Dict[str, Any]:
        """Apply this operation to a list of nodes."""
        self.results = []
        
        for node in nodes:
            try:
                result = self.operation_func(node, **kwargs)
                self.results.append({
                    'node_id': node.id,
                    'success': True,
                    'result': result,
                    'error': None
                })
            except Exception as e:
                self.results.append({
                    'node_id': node.id,
                    'success': False,
                    'result': None,
                    'error': str(e)
                })
        
        success_count = sum(1 for r in self.results if r['success'])
        return {
            'operation': self.name,
            'total': len(nodes),
            'successful': success_count,
            'failed': len(nodes) - success_count,
            'results': self.results
        }


class NodeFilter:
    """Filter system for selecting nodes based on various criteria."""
    
    @staticmethod
    def by_type(nodes: Dict[str, BaseNode], node_type: str) -> List[BaseNode]:
        """Filter nodes by their type."""
        return [node for node in nodes.values() 
                if hasattr(node, 'NODE_TYPE') and node.NODE_TYPE == node_type]
    
    @staticmethod
    def by_npc(nodes: Dict[str, BaseNode], npc_name: str, exact_match: bool = False) -> List[BaseNode]:
        """Filter nodes by NPC name."""
        if exact_match:
            return [node for node in nodes.values() 
                    if hasattr(node, 'npc') and node.npc == npc_name]
        else:
            pattern = re.compile(npc_name, re.IGNORECASE)
            return [node for node in nodes.values() 
                    if hasattr(node, 'npc') and pattern.search(node.npc or '')]
    
    @staticmethod
    def by_text_content(nodes: Dict[str, BaseNode], search_text: str, case_sensitive: bool = False) -> List[BaseNode]:
        """Filter nodes containing specific text."""
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(search_text, flags)
        
        return [node for node in nodes.values() 
                if hasattr(node, 'text') and pattern.search(node.text or '')]
    
    @staticmethod
    def by_theme(nodes: Dict[str, BaseNode], theme: str) -> List[BaseNode]:
        """Filter nodes by background theme."""
        return [node for node in nodes.values() 
                if hasattr(node, 'backgroundTheme') and node.backgroundTheme == theme]
    
    @staticmethod
    def by_chapter(nodes: Dict[str, BaseNode], chapter: str) -> List[BaseNode]:
        """Filter nodes by chapter."""
        return [node for node in nodes.values() 
                if hasattr(node, 'chapter') and node.chapter == chapter]
    
    @staticmethod
    def by_color(nodes: Dict[str, BaseNode], color: str) -> List[BaseNode]:
        """Filter nodes by color."""
        return [node for node in nodes.values() 
                if hasattr(node, 'color') and node.color == color]
    
    @staticmethod
    def orphaned_nodes(nodes: Dict[str, BaseNode]) -> List[BaseNode]:
        """Find nodes with no incoming connections (except intro)."""
        referenced_ids = set()
        
        for node in nodes.values():
            if hasattr(node, 'options'):
                for option in node.options:
                    next_node = option.get('nextNode')
                    if next_node:
                        referenced_ids.add(next_node)
        
        return [node for node_id, node in nodes.items() 
                if node_id != 'intro' and node_id not in referenced_ids]
    
    @staticmethod
    def dead_end_nodes(nodes: Dict[str, BaseNode]) -> List[BaseNode]:
        """Find nodes with no outgoing connections."""
        return [node for node in nodes.values() 
                if not hasattr(node, 'options') or not node.options]
    
    @staticmethod
    def by_custom_filter(nodes: Dict[str, BaseNode], filter_func: Callable[[BaseNode], bool]) -> List[BaseNode]:
        """Filter nodes using a custom function."""
        return [node for node in nodes.values() if filter_func(node)]


class BatchOperationManager:
    """Main manager for batch operations on nodes."""
    
    def __init__(self, app):
        self.app = app
        self.operations = {}
        self.history = []
        self._register_default_operations()
    
    def _register_default_operations(self):
        """Register the default set of batch operations."""
        
        # Text operations
        self.register_operation(
            "find_replace_text",
            self._find_replace_text,
            "Find and replace text in dialogue"
        )
        
        self.register_operation(
            "append_text",
            self._append_text,
            "Append text to dialogue"
        )
        
        self.register_operation(
            "prepend_text", 
            self._prepend_text,
            "Prepend text to dialogue"
        )
        
        # Styling operations
        self.register_operation(
            "change_color",
            self._change_color,
            "Change node color"
        )
        
        self.register_operation(
            "change_theme",
            self._change_theme,
            "Change background theme"
        )
        
        self.register_operation(
            "change_chapter",
            self._change_chapter,
            "Change chapter assignment"
        )
        
        # NPC operations
        self.register_operation(
            "change_npc",
            self._change_npc,
            "Change NPC speaker"
        )
        
        self.register_operation(
            "normalize_npc_names",
            self._normalize_npc_names,
            "Normalize NPC name formatting"
        )
        
        # Validation operations
        self.register_operation(
            "validate_nodes",
            self._validate_nodes,
            "Validate node data integrity"
        )
        
        self.register_operation(
            "fix_empty_text",
            self._fix_empty_text,
            "Add placeholder text to empty nodes"
        )
        
        # Connection operations
        self.register_operation(
            "remove_broken_connections",
            self._remove_broken_connections,
            "Remove connections to non-existent nodes"
        )
        
        # Advanced operations
        self.register_operation(
            "auto_arrange_by_chapter",
            self._auto_arrange_by_chapter,
            "Auto-arrange nodes by chapter"
        )
    
    def register_operation(self, name: str, operation_func: Callable, description: str = ""):
        """Register a new batch operation."""
        self.operations[name] = BatchOperation(name, operation_func, description)
    
    def get_available_operations(self) -> Dict[str, str]:
        """Get list of available operations with descriptions."""
        return {name: op.description for name, op in self.operations.items()}
    
    def execute_operation(self, operation_name: str, node_filter: Union[str, List[BaseNode]], **kwargs) -> Dict[str, Any]:
        """Execute a batch operation on filtered nodes."""
        if operation_name not in self.operations:
            raise ValueError(f"Unknown operation: {operation_name}")
        
        # Get nodes to operate on
        if isinstance(node_filter, str):
            nodes = self._apply_filter(node_filter, **kwargs.get('filter_params', {}))
        elif isinstance(node_filter, list):
            nodes = node_filter
        else:
            raise ValueError("node_filter must be a filter name string or list of nodes")
        
        if not nodes:
            return {
                'operation': operation_name,
                'total': 0,
                'successful': 0,
                'failed': 0,
                'results': [],
                'message': 'No nodes matched the filter criteria'
            }
        
        # Execute operation
        operation = self.operations[operation_name]
        result = operation.apply(nodes, **kwargs)
        
        # Save state for undo if any changes were made
        if result['successful'] > 0:
            self.app.state_manager.save_state(f"Batch: {operation_name}")
        
        # Add to history
        self.history.append(result)
        
        return result
    
    def _apply_filter(self, filter_name: str, **filter_params) -> List[BaseNode]:
        """Apply a named filter to get nodes."""
        nodes = self.app.nodes
        
        filter_map = {
            'all': lambda: list(nodes.values()),
            'by_type': lambda: NodeFilter.by_type(nodes, filter_params.get('node_type', 'dialogue')),
            'by_npc': lambda: NodeFilter.by_npc(nodes, filter_params.get('npc_name', ''), filter_params.get('exact_match', False)),
            'by_text': lambda: NodeFilter.by_text_content(nodes, filter_params.get('search_text', ''), filter_params.get('case_sensitive', False)),
            'by_theme': lambda: NodeFilter.by_theme(nodes, filter_params.get('theme', '')),
            'by_chapter': lambda: NodeFilter.by_chapter(nodes, filter_params.get('chapter', '')),
            'by_color': lambda: NodeFilter.by_color(nodes, filter_params.get('color', '')),
            'orphaned': lambda: NodeFilter.orphaned_nodes(nodes),
            'dead_end': lambda: NodeFilter.dead_end_nodes(nodes),
            'selected': lambda: [nodes[node_id] for node_id in self.app.selected_node_ids if node_id in nodes]
        }
        
        if filter_name not in filter_map:
            raise ValueError(f"Unknown filter: {filter_name}")
        
        return filter_map[filter_name]()
    
    # Operation implementations
    def _find_replace_text(self, node: BaseNode, find_text: str, replace_text: str, case_sensitive: bool = False, **kwargs):
        """Find and replace text in a node."""
        if not hasattr(node, 'text') or not node.text:
            return "No text to modify"
        
        flags = 0 if case_sensitive else re.IGNORECASE
        old_text = node.text
        node.text = re.sub(find_text, replace_text, node.text, flags=flags)
        
        return f"Replaced {len(re.findall(find_text, old_text, flags=flags))} occurrences"
    
    def _append_text(self, node: BaseNode, append_text: str, **kwargs):
        """Append text to a node."""
        if not hasattr(node, 'text'):
            node.text = ""
        
        node.text = (node.text or "") + append_text
        return f"Appended text"
    
    def _prepend_text(self, node: BaseNode, prepend_text: str, **kwargs):
        """Prepend text to a node."""
        if not hasattr(node, 'text'):
            node.text = ""
        
        node.text = prepend_text + (node.text or "")
        return f"Prepended text"
    
    def _change_color(self, node: BaseNode, new_color: str, **kwargs):
        """Change node color."""
        old_color = getattr(node, 'color', None)
        node.color = new_color
        return f"Changed color from {old_color} to {new_color}"
    
    def _change_theme(self, node: BaseNode, new_theme: str, **kwargs):
        """Change background theme."""
        old_theme = getattr(node, 'backgroundTheme', '')
        node.backgroundTheme = new_theme
        return f"Changed theme from '{old_theme}' to '{new_theme}'"
    
    def _change_chapter(self, node: BaseNode, new_chapter: str, **kwargs):
        """Change chapter assignment."""
        old_chapter = getattr(node, 'chapter', '')
        node.chapter = new_chapter
        return f"Changed chapter from '{old_chapter}' to '{new_chapter}'"
    
    def _change_npc(self, node: BaseNode, new_npc: str, **kwargs):
        """Change NPC speaker."""
        old_npc = getattr(node, 'npc', 'Narrator')
        node.npc = new_npc
        return f"Changed NPC from '{old_npc}' to '{new_npc}'"
    
    def _normalize_npc_names(self, node: BaseNode, **kwargs):
        """Normalize NPC name formatting."""
        if hasattr(node, 'npc') and node.npc:
            old_name = node.npc
            # Normalize to Title Case
            node.npc = node.npc.strip().title()
            return f"Normalized '{old_name}' to '{node.npc}'"
        return "No NPC name to normalize"
    
    def _validate_nodes(self, node: BaseNode, **kwargs):
        """Validate node data integrity."""
        issues = []
        
        # Check required fields
        if not hasattr(node, 'id') or not node.id:
            issues.append("Missing node ID")
        
        if not hasattr(node, 'text') or not node.text:
            issues.append("Empty dialogue text")
        
        # Check for broken connections
        if hasattr(node, 'options'):
            for i, option in enumerate(node.options):
                next_node = option.get('nextNode')
                if next_node and next_node not in self.app.nodes:
                    issues.append(f"Broken connection in option {i}: {next_node}")
        
        return f"Found {len(issues)} issues: {', '.join(issues)}" if issues else "Valid"
    
    def _fix_empty_text(self, node: BaseNode, placeholder_text: str = "[Empty dialogue - please add content]", **kwargs):
        """Add placeholder text to empty nodes."""
        if not hasattr(node, 'text') or not node.text or node.text.strip() == "":
            node.text = placeholder_text
            return "Added placeholder text"
        return "Text already present"
    
    def _remove_broken_connections(self, node: BaseNode, **kwargs):
        """Remove connections to non-existent nodes."""
        if not hasattr(node, 'options'):
            return "No options to check"
        
        removed_count = 0
        valid_options = []
        
        for option in node.options:
            next_node = option.get('nextNode')
            if not next_node or next_node in self.app.nodes:
                valid_options.append(option)
            else:
                removed_count += 1
        
        node.options = valid_options
        return f"Removed {removed_count} broken connections"
    
    def _auto_arrange_by_chapter(self, node: BaseNode, **kwargs):
        """Auto-arrange nodes by chapter (position-based)."""
        if not hasattr(node, 'chapter') or not node.chapter:
            return "No chapter assigned"
        
        # Simple arrangement: chapters in columns
        chapter_positions = {
            'Chapter 1': (100, 100),
            'Chapter 2': (400, 100), 
            'Chapter 3': (700, 100),
            'Chapter 4': (1000, 100)
        }
        
        if node.chapter in chapter_positions:
            base_x, base_y = chapter_positions[node.chapter]
            # Add some vertical offset based on node ID hash for variety
            offset_y = hash(node.id) % 200
            node.x = base_x
            node.y = base_y + offset_y
            return f"Arranged in {node.chapter} column"
        
        return "Unknown chapter for arrangement"
    
    def get_operation_history(self) -> List[Dict[str, Any]]:
        """Get history of batch operations."""
        return self.history.copy()
    
    def clear_history(self):
        """Clear operation history."""
        self.history.clear()


class BatchOperationDialog:
    """Dialog for configuring and executing batch operations."""
    
    def __init__(self, app):
        self.app = app
        self.batch_manager = BatchOperationManager(app)
    
    def show_dialog(self):
        """Show the batch operations dialog."""
        # This would be implemented as a GUI dialog
        # For now, we'll provide a simple interface through the existing menu system
        pass
    
    def quick_operations_menu(self):
        """Return quick operations for menu integration."""
        return {
            "Find & Replace Text in All Nodes": {
                'operation': 'find_replace_text',
                'filter': 'all',
                'params': {}
            },
            "Change Color of Selected Nodes": {
                'operation': 'change_color', 
                'filter': 'selected',
                'params': {}
            },
            "Fix Empty Dialogue Text": {
                'operation': 'fix_empty_text',
                'filter': 'all',
                'params': {}
            },
            "Remove Broken Connections": {
                'operation': 'remove_broken_connections',
                'filter': 'all', 
                'params': {}
            },
            "Find Orphaned Nodes": {
                'operation': 'validate_nodes',
                'filter': 'orphaned',
                'params': {}
            }
        }