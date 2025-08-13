# dvge/ui/canvas/connection_renderer.py

"""Connection rendering functionality for the canvas."""

import tkinter as tk
from ...constants import *
from ...models import DiceRollNode


class ConnectionRenderer:
    """Handles rendering of connections between nodes."""
    
    def __init__(self, canvas):
        self.canvas = canvas
    
    def draw_connections(self, nodes):
        """Draws all the connection arrows between nodes."""
        self.canvas.delete("connection")
        
        for node in nodes.values():
            if isinstance(node, DiceRollNode):
                self._draw_dice_roll_connections(node, nodes)
            else:
                self._draw_dialogue_connections(node, nodes)
        
        # Ensure nodes are drawn on top of connections
        self.canvas.tag_raise("node")

    def _draw_dice_roll_connections(self, node, nodes):
        """Draws connections for dice roll nodes."""
        if node.success_node and node.success_node in nodes:
            self.draw_arrow(
                node, nodes[node.success_node], 0, COLOR_SUCCESS
            )
        
        if node.failure_node and node.failure_node in nodes:
            self.draw_arrow(
                node, nodes[node.failure_node], 1, COLOR_ERROR
            )

    def _draw_dialogue_connections(self, node, nodes):
        """Draws connections for dialogue nodes."""
        for i, option in enumerate(node.options):
            target_id = option.get("nextNode")
            if target_id and target_id in nodes:
                self.draw_arrow(
                    node, nodes[target_id], i, NODE_CONNECTION_COLOR
                )

    def draw_arrow(self, source, target, opt_idx, color):
        """Draws a single Bezier curve arrow between two points."""
        x1, y1 = source.get_connection_point_out(opt_idx)
        x2, y2 = target.get_connection_point_in()
        
        # Calculate control points for smooth curve
        ctrlx1, ctrly1 = x1 + 70, y1
        ctrlx2, ctrly2 = x2 - 70, y2
        
        # Create the curved line with arrow
        line_id = self.canvas.create_line(
            x1, y1, ctrlx1, ctrly1, ctrlx2, ctrly2, x2, y2, 
            smooth=True, arrow=tk.LAST, fill=color, width=2.5, 
            tags="connection"
        )
        
        # Send connections to back
        self.canvas.tag_lower(line_id)

    def draw_temporary_connection(self, start_pos, end_pos, color=COLOR_ACCENT):
        """Draws a temporary connection line during connection creation."""
        return self.canvas.create_line(
            start_pos[0], start_pos[1], end_pos[0], end_pos[1], 
            fill=color, width=2.5, dash=(5, 5), tags="temp_connection"
        )

    def clear_temporary_connections(self):
        """Removes all temporary connection lines."""
        self.canvas.delete("temp_connection")

    def update_temporary_connection(self, line_id, start_pos, end_pos):
        """Updates the coordinates of a temporary connection line."""
        if line_id and self.canvas.find_withtag(line_id):
            self.canvas.coords(line_id, start_pos[0], start_pos[1], end_pos[0], end_pos[1])