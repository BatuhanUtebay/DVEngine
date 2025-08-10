# dvge/core/validation.py
class ProjectValidator:
    """Validates project integrity and finds issues."""
    
    def __init__(self, app):
        self.app = app
    
    def validate_project(self):
        """Checks the project for common errors before exporting."""
        errors = []
        warnings = []
        
        # Check for intro node
        if "intro" not in self.app.nodes:
            errors.append("Project must contain a node with the ID 'intro' to start.")
            return errors, warnings  # Fatal error, no point in checking more

        # Find reachable nodes
        reachable_nodes = self._find_reachable_nodes()
        
        # Check for unreachable nodes
        all_node_ids = set(self.app.nodes.keys())
        unreachable = all_node_ids - reachable_nodes
        if unreachable: 
            warnings.append(f"Unreachable nodes found: {', '.join(unreachable)}")

        # Check for broken links
        self._check_broken_links(errors)
        
        # Check for empty required fields
        self._check_empty_fields(warnings)
        
        return errors, warnings
    
    def _find_reachable_nodes(self):
        """Find all nodes reachable from the intro node."""
        reachable_nodes = set(["intro"])
        node_queue = ["intro"]
        
        head = 0
        while head < len(node_queue):
            current_id = node_queue[head]
            head += 1
            node = self.app.nodes.get(current_id)
            if not node: 
                continue
            
            # Check regular options
            for option in getattr(node, 'options', []):
                target_id = option.get("nextNode")
                if target_id and target_id in self.app.nodes and target_id not in reachable_nodes:
                    reachable_nodes.add(target_id)
                    node_queue.append(target_id)
            
            # Check special node types
            if hasattr(node, 'success_node') and node.success_node:
                if node.success_node in self.app.nodes and node.success_node not in reachable_nodes:
                    reachable_nodes.add(node.success_node)
                    node_queue.append(node.success_node)
            
            if hasattr(node, 'failure_node') and node.failure_node:
                if node.failure_node in self.app.nodes and node.failure_node not in reachable_nodes:
                    reachable_nodes.add(node.failure_node)
                    node_queue.append(node.failure_node)
        
        return reachable_nodes
    
    def _check_broken_links(self, errors):
        """Check for broken node links."""
        all_node_ids = set(self.app.nodes.keys())
        
        for node_id, node in self.app.nodes.items():
            # Check regular options
            for i, option in enumerate(getattr(node, 'options', [])):
                target_id = option.get('nextNode')
                if target_id and target_id not in all_node_ids and target_id != "[End Game]":
                    errors.append(f"Node '{node_id}', Choice #{i+1}: Links to non-existent node '{target_id}'.")
            
            # Check special node types
            if hasattr(node, 'success_node') and node.success_node:
                if node.success_node not in all_node_ids and node.success_node != "[End Game]":
                    errors.append(f"Node '{node_id}': Success node '{node.success_node}' does not exist.")
            
            if hasattr(node, 'failure_node') and node.failure_node:
                if node.failure_node not in all_node_ids and node.failure_node != "[End Game]":
                    errors.append(f"Node '{node_id}': Failure node '{node.failure_node}' does not exist.")
    
    def _check_empty_fields(self, warnings):
        """Check for empty important fields."""
        for node_id, node in self.app.nodes.items():
            if not getattr(node, 'text', '').strip():
                warnings.append(f"Node '{node_id}' has empty dialogue text.")
            
            if not getattr(node, 'npc', '').strip():
                warnings.append(f"Node '{node_id}' has empty NPC name.")