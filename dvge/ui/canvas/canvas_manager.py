# dvge/ui/canvas/canvas_manager.py

"""Canvas management for the node editor."""

from tkinter import messagebox
from ...constants import *
from ...models import DialogueNode, DiceRollNode
from .node_renderer import NodeRenderer
from .connection_renderer import ConnectionRenderer
from .interaction_handler import InteractionHandler


class CanvasManager:
    """Manages the canvas and coordinates rendering and interaction."""
    
    def __init__(self, app):
        self.app = app
        self.canvas = app.canvas
        self.placeholder_id = None
        
        # Initialize components
        self.node_renderer = NodeRenderer(self.canvas)
        self.connection_renderer = ConnectionRenderer(self.canvas)
        self.interaction_handler = InteractionHandler(app, self.canvas)

    def draw_grid(self):
        """Draws the background grid on the canvas."""
        self.canvas.delete("grid_line")
        for i in range(0, 10000, GRID_SIZE):
            self.canvas.create_line(
                [(i, 0), (i, 10000)], 
                tag="grid_line", fill=COLOR_GRID_LINES, width=1
            )
            self.canvas.create_line(
                [(0, i), (10000, i)], 
                tag="grid_line", fill=COLOR_GRID_LINES, width=1
            )
        self.canvas.tag_lower("grid_line")

    def draw_placeholder_if_empty(self):
        """Draws a placeholder message if the canvas is empty."""
        if self.placeholder_id:
            self.canvas.delete(self.placeholder_id)
            self.placeholder_id = None
        
        if not self.app.nodes:
            self.app.after(50, self._create_placeholder_text)

    def _create_placeholder_text(self):
        """Helper to create the placeholder text widget."""
        if not self.app.nodes:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            self.placeholder_id = self.canvas.create_text(
                canvas_width / 2, canvas_height / 2,
                text="Right-click to add a new node",
                font=(FONT_FAMILY, 16, "italic"),
                fill=COLOR_TEXT_MUTED,
                tags="placeholder"
            )

    def redraw_all_nodes(self):
        """Clears and redraws the entire canvas, including grid, nodes, and connections."""
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_placeholder_if_empty()
        
        for node in self.app.nodes.values():
            self.create_node_visual(node)
        
        self.update_selection_visuals()
        self.draw_connections()

    def redraw_node(self, node_id):
        """Redraws a single node, which is more efficient than redrawing everything."""
        node = self.app.nodes.get(node_id)
        if not node:
            return
        
        # Remove existing visual elements
        for item_id in node.canvas_item_ids.values():
            if self.canvas.find_withtag(item_id):
                self.canvas.delete(item_id)
        node.canvas_item_ids.clear()
        
        # Recreate visual elements
        self.create_node_visual(node)
        self.update_selection_visuals()
        self.draw_connections()

    def create_node_visual(self, node):
        """Creates all the visual components for a single node on the canvas."""
        self.node_renderer.create_node_visual(node)

    def update_selection_visuals(self):
        """Updates the highlight state of all nodes based on the current selection."""
        self.node_renderer.update_selection_visuals(self.app.nodes, self.app.selected_node_ids)

    def draw_connections(self):
        """Draws all the connection arrows between nodes."""
        self.connection_renderer.draw_connections(self.app.nodes)

    def add_node(self, x, y, node_type="dialogue"):
        """Creates a new node in the data model and on the canvas."""
        self.app._save_state_for_undo("Add Node")
    
        if self.placeholder_id:
            self.canvas.delete(self.placeholder_id)
            self.placeholder_id = None
    
    # Generate unique node ID
        while f"node_{self.app.node_id_counter}" in self.app.nodes:
            self.app.node_id_counter += 1
    
        node_id_str = f"node_{self.app.node_id_counter}"
        self.app.node_id_counter += 1
    
    # Import all node types
        from ...models import (DialogueNode, DiceRollNode, CombatNode, 
                          ShopNode, RandomEventNode, TimerNode, InventoryNode)
    
    # Create appropriate node type
        if node_type == "dice_roll":
            new_node = DiceRollNode(x=x, y=y, node_id=node_id_str)
        elif node_type == "combat":
            new_node = CombatNode(x=x, y=y, node_id=node_id_str)
        elif node_type == "shop":
            new_node = ShopNode(x=x, y=y, node_id=node_id_str)
        elif node_type == "random_event":
            new_node = RandomEventNode(x=x, y=y, node_id=node_id_str)
        elif node_type == "timer":
            new_node = TimerNode(x=x, y=y, node_id=node_id_str)
        elif node_type == "inventory":
            new_node = InventoryNode(x=x, y=y, node_id=node_id_str)
        else:  # Default to dialogue
            new_node = DialogueNode(x=x, y=y, node_id=node_id_str)
        
        self.app.nodes[node_id_str] = new_node
        self.create_node_visual(new_node)
        self.app.set_selection([node_id_str], node_id_str)

    def delete_selected_nodes(self, event=None):
        """Deletes all currently selected nodes."""
        if not self.app.selected_node_ids:
            return
        
        confirm = messagebox.askyesno(
            "Delete Nodes", 
            f"Are you sure you want to delete {len(self.app.selected_node_ids)} selected node(s)?"
        )
        if not confirm:
            return

        self.app._save_state_for_undo("Delete Nodes")
        nodes_to_delete = list(self.app.selected_node_ids)
        
        for node_to_delete_id in nodes_to_delete:
            if node_to_delete_id == "intro":
                messagebox.showwarning("Cannot Delete", "The 'intro' node cannot be deleted.")
                continue

            self._clean_up_node_references(node_to_delete_id)
            self._remove_node_visual(node_to_delete_id)
            
            # Remove from data model
            self.app.nodes.pop(node_to_delete_id, None)
        
        self.app.set_selection([])
        self.draw_connections()
        self.draw_placeholder_if_empty()

    def _clean_up_node_references(self, node_id):
        """Removes references to a node from all other nodes."""
        for node in self.app.nodes.values():
            # Clean up regular dialogue options
            for option in getattr(node, 'options', []):
                if option.get('nextNode') == node_id:
                    option['nextNode'] = ""
            
            # Clean up special node types
            if hasattr(node, 'success_node') and node.success_node == node_id:
                node.success_node = ""
            if hasattr(node, 'failure_node') and node.failure_node == node_id:
                node.failure_node = ""

    def _remove_node_visual(self, node_id):
        """Removes the visual elements of a node from the canvas."""
        if node_id in self.app.nodes:
            node_to_delete = self.app.nodes[node_id]
            for item_id in node_to_delete.canvas_item_ids.values():
                if self.canvas.find_withtag(item_id):
                    self.canvas.delete(item_id)

    def pan_to_node(self, node_id):
        """Pans the main canvas to center on a specific node."""
        node = self.app.nodes.get(node_id)
        if not node:
            return
        
        self.app.set_selection([node_id], node_id)
        
        x, y = node.x, node.y
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        target_x = x - canvas_width / 2 + NODE_WIDTH / 2
        target_y = y - canvas_height / 2 + node.get_height() / 2
        
        self.canvas.xview_moveto(target_x / 10000)
        self.canvas.yview_moveto(target_y / 10000)

    def zoom_to_fit(self):
        """Zooms the canvas to fit all nodes."""
        if not self.app.nodes:
            return
        
        # Find bounds of all nodes
        min_x = min(node.x for node in self.app.nodes.values())
        max_x = max(node.x + NODE_WIDTH for node in self.app.nodes.values())
        min_y = min(node.y for node in self.app.nodes.values())
        max_y = max(node.y + node.get_height() for node in self.app.nodes.values())
        
        # Add padding
        padding = 100
        min_x -= padding
        max_x += padding
        min_y -= padding
        max_y += padding
        
        # Calculate scale factor
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        content_width = max_x - min_x
        content_height = max_y - min_y
        
        scale_x = canvas_width / content_width if content_width > 0 else 1
        scale_y = canvas_height / content_height if content_height > 0 else 1
        scale = min(scale_x, scale_y, 1.0)  # Don't zoom in beyond 100%
        
        if scale < 1.0:
            # Calculate center point
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            
            # Scale all elements
            self.canvas.scale("all", center_x, center_y, scale, scale)

    def center_view(self):
        """Centers the canvas view on all nodes."""
        if not self.app.nodes:
            return
        
        # Find center of all nodes
        center_x = sum(node.x + NODE_WIDTH/2 for node in self.app.nodes.values()) / len(self.app.nodes)
        center_y = sum(node.y + node.get_height()/2 for node in self.app.nodes.values()) / len(self.app.nodes)
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        target_x = center_x - canvas_width / 2
        target_y = center_y - canvas_height / 2
        
        self.canvas.xview_moveto(target_x / 10000)
        self.canvas.yview_moveto(target_y / 10000)