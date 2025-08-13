# dvge/ui/canvas/node_renderer.py

"""Node rendering functionality for the canvas."""

from ...constants import *
from ...models import DiceRollNode


class NodeRenderer:
    """Handles rendering of nodes on the canvas."""
    
    def __init__(self, canvas):
        self.canvas = canvas
    
    def create_node_visual(self, node):
        """Creates all the visual components for a single node on the canvas."""
        x, y = node.x, node.y
        tags = ("node", node.id)
        
        # Calculate text height
        temp_text = self.canvas.create_text(
            0, 0, text=node.text, font=FONT_DIALOGUE, 
            anchor="nw", width=NODE_WIDTH - 40, state='hidden'
        )
        bbox = self.canvas.bbox(temp_text)
        node.calculated_text_height = bbox[3] - bbox[1] if bbox else 0
        self.canvas.delete(temp_text)

        height = node.get_height()
        is_start_node = node.id == "intro"
        header_color = self._get_header_color(node, is_start_node)

        # Create visual elements
        self._create_node_shadow(node, x, y, height, tags)
        self._create_node_body(node, x, y, height, tags)
        self._create_node_header(node, x, y, header_color, tags)
        self._create_node_text(node, x, y, is_start_node, tags)
        self._create_node_content(node, x, y, tags)
        self._create_node_footer(node, x, y, height, tags)

    def _get_header_color(self, node, is_start_node):
        """Determines the header color for a node."""
        if is_start_node:
            return NODE_INTRO_COLOR
        elif node.color != NODE_DEFAULT_COLOR:
            return node.color
        else:
            return "#455A64"

    def _create_node_shadow(self, node, x, y, height, tags):
        """Creates the drop shadow for a node."""
        node.canvas_item_ids['shadow'] = self._create_rounded_rectangle(
            x+3, y+3, x + NODE_WIDTH+3, y + height+3, 
            NODE_BORDER_RADIUS, fill="#111111", outline="", tags=tags
        )

    def _create_node_body(self, node, x, y, height, tags):
        """Creates the main body of a node."""
        node.canvas_item_ids['body'] = self._create_rounded_rectangle(
            x, y, x + NODE_WIDTH, y + height, 
            NODE_BORDER_RADIUS, fill=NODE_DEFAULT_COLOR, outline="", tags=tags
        )

    def _create_node_header(self, node, x, y, header_color, tags):
        """Creates the header section of a node."""
        node.canvas_item_ids['header'] = self._create_rounded_rectangle(
            x, y, x + NODE_WIDTH, y + NODE_HEADER_HEIGHT, 
            NODE_BORDER_RADIUS, fill=header_color, outline="", tags=tags
        )

    def _create_node_text(self, node, x, y, is_start_node, tags):
        """Creates the text elements for a node."""
        header_text = f"{'★' if is_start_node else ''} {node.id} | {node.npc}"
        node.canvas_item_ids['npc_text'] = self.canvas.create_text(
            x + 20, y + 20, text=header_text, fill=COLOR_TEXT, 
            anchor="w", font=FONT_NPC, tags=tags
        )
        
        node.canvas_item_ids['dialogue_text'] = self.canvas.create_text(
            x + 20, y + 60, text=node.text, fill=COLOR_TEXT_MUTED, 
            anchor="nw", width=NODE_WIDTH - 40, font=FONT_DIALOGUE, tags=tags
        )

    def _create_node_content(self, node, x, y, tags):
        """Creates the content area (options or special node content)."""
        body_height = max(NODE_BASE_BODY_HEIGHT, node.calculated_text_height + 20)
        
        if isinstance(node, DiceRollNode):
            self._create_dice_roll_content(node, x, y, body_height, tags)
        else:
            self._create_dialogue_options(node, x, y, body_height, tags)

    def _create_dice_roll_content(self, node, x, y, body_height, tags):
        """Creates content for dice roll nodes."""
        dice_text = f"Roll {node.num_dice}d{node.num_sides} vs {node.success_threshold}"
        node.canvas_item_ids['dice_text'] = self.canvas.create_text(
            x + 20, y + 100, text=dice_text, fill=COLOR_TEXT, 
            anchor="nw", font=FONT_OPTION, tags=tags
        )
        
        node.canvas_item_ids['success_text'] = self.canvas.create_text(
            x + 20, y + 130, text=f"Success: {node.success_node}", 
            fill=COLOR_SUCCESS, anchor="nw", font=FONT_OPTION, tags=tags
        )
        
        node.canvas_item_ids['failure_text'] = self.canvas.create_text(
            x + 20, y + 150, text=f"Failure: {node.failure_node}", 
            fill=COLOR_ERROR, anchor="nw", font=FONT_OPTION, tags=tags
        )

    def _create_dialogue_options(self, node, x, y, body_height, tags):
        """Creates dialogue options for regular nodes."""
        for i, option in enumerate(node.options):
            y_pos = y + NODE_HEADER_HEIGHT + body_height + (i * OPTION_LINE_HEIGHT) + 15
            option_text = f"{i+1}. {self._wrap_text(option.get('text', '...'), 35)}"
            
            # Option text
            node.canvas_item_ids[f'option_text_{i}'] = self.canvas.create_text(
                x + 20, y_pos, text=option_text, fill=COLOR_TEXT, 
                anchor="w", font=FONT_OPTION, tags=tags
            )
            
            # Condition/Effect indicators
            indicator_text = ""
            if option.get('conditions'): 
                indicator_text += " [C]"
            if option.get('effects'): 
                indicator_text += " [E]"
            
            if indicator_text:
                node.canvas_item_ids[f'option_indicator_{i}'] = self.canvas.create_text(
                    x + NODE_WIDTH - 45, y_pos, text=indicator_text, 
                    fill=COLOR_ACCENT, anchor="e", font=FONT_OPTION, tags=tags
                )

            # Option handle for connections
            node.canvas_item_ids[f'option_handle_{i}'] = self.canvas.create_oval(
                x + NODE_WIDTH - 20, y_pos - 8, x + NODE_WIDTH-4, y_pos + 8, 
                fill=COLOR_ACCENT, outline="", 
                tags=("handle", node.id, f"opt_{i}", "node")
            )

    def _create_node_footer(self, node, x, y, height, tags):
        """Creates the footer section of a node."""
        if not isinstance(node, DiceRollNode):
            footer_y = y + height - NODE_FOOTER_HEIGHT
            footer_tags = ("node", node.id, "add_option_button")
            
            node.canvas_item_ids['add_button_text'] = self.canvas.create_text(
                x + NODE_WIDTH/2, footer_y + 18, text="+ Add Choice", 
                fill=COLOR_TEXT_MUTED, font=FONT_ADD_BUTTON, 
                tags=footer_tags, activefill=COLOR_ACCENT
            )

    def _wrap_text(self, text, max_chars):
        """Truncates text to a maximum length for display on the node."""
        return text[:max_chars].strip() + "..." if len(text) > max_chars else text

    def _create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        """Helper function to draw a rounded rectangle on the canvas."""
        points = [
            x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1,
            x2, y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius, 
            x2, y2 - radius, x2, y2, x2 - radius, y2, x2 - radius, y2, 
            x1 + radius, y2, x1 + radius, y2, x1, y2, x1, y2 - radius, 
            x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1
        ]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def update_selection_visuals(self, nodes, selected_node_ids):
        """Updates the highlight state of all nodes based on the current selection."""
        for node_id, node in nodes.items():
            if node.canvas_item_ids.get('body'):
                is_selected = node_id in selected_node_ids
                outline_color = NODE_SELECTED_OUTLINE_COLOR if is_selected else ""
                outline_width = 3 if is_selected else 0
                self.canvas.itemconfig(
                    node.canvas_item_ids['body'], 
                    outline=outline_color, 
                    width=outline_width
                )