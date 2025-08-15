import tkinter as tk
from ...constants import *
from ...models import DiceRollNode, CombatNode, ShopNode, RandomEventNode, TimerNode, InventoryNode


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
            elif isinstance(node, CombatNode):
                self._draw_combat_connections(node, nodes)
            elif isinstance(node, ShopNode):
                self._draw_shop_connections(node, nodes)
            elif isinstance(node, RandomEventNode):
                self._draw_random_event_connections(node, nodes)
            elif isinstance(node, TimerNode):
                self._draw_timer_connections(node, nodes)
            elif isinstance(node, InventoryNode):
                self._draw_inventory_connections(node, nodes)
            elif hasattr(node, 'options'):
                self._draw_dialogue_connections(node, nodes)
        
        # Ensure nodes are drawn on top of connections
        self.canvas.tag_raise("node")

    def _draw_dice_roll_connections(self, node, nodes):
        """Draws connections for dice roll nodes."""
        if node.success_node and node.success_node in nodes:
            self.draw_arrow(
                node, nodes[node.success_node], 0, COLOR_SUCCESS
            )
        elif node.success_node == "[End Game]":
            self._draw_end_game_indicator(node, 0, COLOR_SUCCESS)
        
        if node.failure_node and node.failure_node in nodes:
            self.draw_arrow(
                node, nodes[node.failure_node], 1, COLOR_ERROR
            )
        elif node.failure_node == "[End Game]":
            self._draw_end_game_indicator(node, 1, COLOR_ERROR)

    def _draw_combat_connections(self, node, nodes):
        """Draws connections for combat nodes."""
        if node.successNode and node.successNode in nodes:
            self.draw_arrow(
                node, nodes[node.successNode], 0, COLOR_SUCCESS
            )
        elif node.successNode == "[End Game]":
            self._draw_end_game_indicator(node, 0, COLOR_SUCCESS)
        
        if node.failNode and node.failNode in nodes:
            self.draw_arrow(
                node, nodes[node.failNode], 1, COLOR_ERROR
            )
        elif node.failNode == "[End Game]":
            self._draw_end_game_indicator(node, 1, COLOR_ERROR)

    def _draw_shop_connections(self, node, nodes):
        """Draws connections for shop nodes."""
        if node.continue_node and node.continue_node in nodes:
            self.draw_arrow(
                node, nodes[node.continue_node], 0, COLOR_ACCENT
            )
        elif node.continue_node == "[End Game]":
            self._draw_end_game_indicator(node, 0, COLOR_ACCENT)

    def _draw_random_event_connections(self, node, nodes):
        """Draws connections for random event nodes."""
        for i, outcome in enumerate(node.random_outcomes):
            next_node = outcome.get('next_node')
            if next_node and next_node in nodes:
                self.draw_arrow(
                    node, nodes[next_node], i, COLOR_WARNING
                )
            elif next_node == "[End Game]":
                self._draw_end_game_indicator(node, i, COLOR_WARNING)

    def _draw_timer_connections(self, node, nodes):
        """Draws connections for timer nodes."""
        if node.next_node and node.next_node in nodes:
            self.draw_arrow(
                node, nodes[node.next_node], 0, COLOR_ACCENT
            )
        elif node.next_node == "[End Game]":
            self._draw_end_game_indicator(node, 0, COLOR_ACCENT)

    def _draw_inventory_connections(self, node, nodes):
        """Draws connections for inventory nodes."""
        if node.continue_node and node.continue_node in nodes:
            self.draw_arrow(
                node, nodes[node.continue_node], 0, COLOR_ACCENT
            )
        elif node.continue_node == "[End Game]":
            self._draw_end_game_indicator(node, 0, COLOR_ACCENT)

    def _draw_dialogue_connections(self, node, nodes):
        """Draws connections for dialogue nodes."""
        for i, option in enumerate(node.options):
            target_id = option.get("nextNode")
            if target_id and target_id in nodes:
                self.draw_arrow(
                    node, nodes[target_id], i, NODE_CONNECTION_COLOR
                )
            elif target_id == "[End Game]":
                self._draw_end_game_indicator(node, i, NODE_CONNECTION_COLOR)

    def _draw_end_game_indicator(self, node, option_index, color):
        """Draws an indicator for [End Game] connections."""
        x1, y1 = node.get_connection_point_out(option_index)
        x2, y2 = x1 + 60, y1
        
        # Draw short arrow to indicate end game
        self.canvas.create_line(
            x1, y1, x2, y2,
            arrow=tk.LAST, fill=color, width=2.5,
            tags="connection"
        )
        
        # Draw "END" text
        self.canvas.create_text(
            x2 + 10, y2, text="END", 
            fill=color, font=("Arial", 10, "bold"),
            anchor="w", tags="connection"
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