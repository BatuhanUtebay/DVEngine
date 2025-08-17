"""Enhanced node renderer with theming, icons, and visual states."""

import math
import tkinter as tk
from typing import Dict, List, Tuple, Optional
from ...constants import *
from ...models import DiceRollNode, ShopNode, RandomEventNode, TimerNode, InventoryNode, AdvancedCombatNode
from .node_themes import theme_manager, NodeTheme, NodeVisualState


class EnhancedNodeRenderer:
    """Advanced node renderer with theming and visual effects."""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.node_states: Dict[str, NodeVisualState] = {}
        self.animation_items = {}  # Track items for animations
        
    def create_node_visual(self, node):
        """Creates enhanced visual components for a node."""
        # Clear any existing visual elements first
        for item_id in list(node.canvas_item_ids.values()):
            try:
                if self.canvas.find_withtag(item_id):
                    self.canvas.delete(item_id)
            except (tk.TclError, AttributeError):
                pass
        node.canvas_item_ids.clear()
        
        x, y = node.x, node.y
        tags = ("node", node.id)
        
        # Get theme and visual state
        theme = theme_manager.get_theme_for_node(node)
        state = self.get_node_state(node.id)
        
        # Calculate dimensions
        self._calculate_node_dimensions(node)
        height = node.get_height()
        
        # Create visual layers
        self._create_node_shadow(node, x, y, height, theme, tags)
        self._create_node_body(node, x, y, height, theme, state, tags)
        self._create_node_border(node, x, y, height, theme, state, tags)
        self._create_node_header(node, x, y, theme, tags)
        self._create_node_icon(node, x, y, theme, tags)
        self._create_node_text(node, x, y, theme, tags)
        self._create_node_content(node, x, y, theme, tags)
        self._create_node_footer(node, x, y, height, theme, tags)
        self._create_status_indicators(node, x, y, theme, tags)
        
        # Apply visual effects
        self._apply_visual_effects(node, theme, state)
    
    def get_node_state(self, node_id: str) -> NodeVisualState:
        """Get or create visual state for a node."""
        if node_id not in self.node_states:
            self.node_states[node_id] = NodeVisualState()
        return self.node_states[node_id]
    
    def update_node_state(self, node_id: str, **kwargs):
        """Update visual state of a node."""
        state = self.get_node_state(node_id)
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)
        
        # Trigger visual update if needed
        self._update_node_appearance(node_id)
    
    def _calculate_node_dimensions(self, node):
        """Calculate text height and node dimensions."""
        temp_text = self.canvas.create_text(
            0, 0, text=node.text, font=FONT_DIALOGUE, 
            anchor="nw", width=NODE_WIDTH - 40, state='hidden'
        )
        bbox = self.canvas.bbox(temp_text)
        node.calculated_text_height = bbox[3] - bbox[1] if bbox else 0
        self.canvas.delete(temp_text)
    
    def _create_node_shadow(self, node, x, y, height, theme: NodeTheme, tags):
        """Create drop shadow with theme support."""
        if not theme.shadow_enabled:
            return
            
        shadow_x = x + theme.shadow_offset[0]
        shadow_y = y + theme.shadow_offset[1]
        
        node.canvas_item_ids['shadow'] = self._create_rounded_rectangle(
            shadow_x, shadow_y, shadow_x + NODE_WIDTH, shadow_y + height,
            theme.corner_radius, fill=theme.shadow_color, outline="", tags=tags
        )
    
    def _create_node_body(self, node, x, y, height, theme: NodeTheme, state: NodeVisualState, tags):
        """Create main node body with theme support."""
        body_color = theme.body_color
        
        # Apply state modifications
        if state.is_disabled:
            body_color = self._adjust_color_opacity(body_color, theme.disabled_opacity)
        
        node.canvas_item_ids['body'] = self._create_rounded_rectangle(
            x, y, x + NODE_WIDTH, y + height,
            theme.corner_radius, fill=body_color, outline="", tags=tags
        )
    
    def _create_node_border(self, node, x, y, height, theme: NodeTheme, state: NodeVisualState, tags):
        """Create node border based on theme and state."""
        border_color = theme.border_color
        border_width = theme.border_width
        
        # Override for selection state
        if state.is_selected:
            border_color = theme.selected_border_color
            border_width = theme.selected_border_width
        elif state.is_highlighted and state.highlight_color:
            border_color = state.highlight_color
            border_width = max(border_width, 2)
        
        if border_width > 0 and border_color:
            node.canvas_item_ids['border'] = self._create_rounded_rectangle(
                x, y, x + NODE_WIDTH, y + height,
                theme.corner_radius, fill="", outline=border_color, 
                width=border_width, tags=tags
            )
    
    def _create_node_header(self, node, x, y, theme: NodeTheme, tags):
        """Create node header with theme support."""
        node.canvas_item_ids['header'] = self._create_rounded_rectangle(
            x, y, x + NODE_WIDTH, y + NODE_HEADER_HEIGHT,
            theme.corner_radius, fill=theme.header_color, outline="", tags=tags
        )
    
    def _create_node_icon(self, node, x, y, theme: NodeTheme, tags):
        """Create node icon if specified in theme."""
        if not theme.icon:
            return
            
        # Position icon in top-left of header
        icon_x = x + 10
        icon_y = y + NODE_HEADER_HEIGHT // 2
        
        node.canvas_item_ids['icon'] = self.canvas.create_text(
            icon_x, icon_y, text=theme.icon, fill=theme.icon_color,
            font=(FONT_FAMILY, theme.icon_size, "normal"), anchor="w", tags=tags
        )
    
    def _create_node_text(self, node, x, y, theme: NodeTheme, tags):
        """Create text elements with theme support."""
        # Adjust header text position if icon exists
        text_offset = 30 if theme.icon else 20
        
        # Header text (NPC name and node ID)
        is_start_node = node.id == "intro"
        header_prefix = "★ " if is_start_node else ""
        header_text = f"{header_prefix}{node.id} | {node.npc}"
        
        node.canvas_item_ids['npc_text'] = self.canvas.create_text(
            x + text_offset, y + 20, text=header_text, fill=theme.text_color,
            anchor="w", font=FONT_NPC, tags=tags
        )
        
        # Main dialogue text
        node.canvas_item_ids['dialogue_text'] = self.canvas.create_text(
            x + 20, y + 60, text=node.text, fill=theme.subtitle_color,
            anchor="nw", width=NODE_WIDTH - 40, font=FONT_DIALOGUE, tags=tags
        )
    
    def _create_node_content(self, node, x, y, theme: NodeTheme, tags):
        """Create node content area with enhanced styling."""
        body_height = max(NODE_BASE_BODY_HEIGHT, node.calculated_text_height + 20)
        
        if isinstance(node, DiceRollNode):
            self._create_dice_roll_content(node, x, y, body_height, theme, tags)
        elif isinstance(node, ShopNode):
            self._create_shop_content(node, x, y, body_height, theme, tags)
        elif isinstance(node, (RandomEventNode, TimerNode, InventoryNode)):
            self._create_special_node_content(node, x, y, body_height, theme, tags)
        else:
            self._create_dialogue_options(node, x, y, body_height, theme, tags)
    
    def _create_dice_roll_content(self, node, x, y, body_height, theme: NodeTheme, tags):
        """Create dice roll specific content with enhanced styling."""
        dice_y = y + NODE_HEADER_HEIGHT + body_height + 10
        
        # Dice roll info with themed colors
        dice_text = f"🎲 {node.num_dice}d{node.num_sides} (Target: {node.success_threshold})"
        node.canvas_item_ids['dice_info'] = self.canvas.create_text(
            x + 20, dice_y, text=dice_text, fill=theme.text_color,
            anchor="w", font=FONT_OPTION, tags=tags
        )
        
        # Success/failure paths with colored indicators
        success_text = f"✅ Success → {node.success_node}"
        failure_text = f"❌ Failure → {node.failure_node}"
        
        node.canvas_item_ids['success_path'] = self.canvas.create_text(
            x + 20, dice_y + 25, text=success_text, fill=COLOR_SUCCESS,
            anchor="w", font=FONT_OPTION, tags=tags
        )
        
        node.canvas_item_ids['failure_path'] = self.canvas.create_text(
            x + 20, dice_y + 45, text=failure_text, fill=COLOR_ERROR,
            anchor="w", font=FONT_OPTION, tags=tags
        )
    
    def _create_shop_content(self, node, x, y, body_height, theme: NodeTheme, tags):
        """Create shop specific content with enhanced styling."""
        shop_y = y + NODE_HEADER_HEIGHT + body_height + 10
        
        # Shop info with gold icon
        items_count = len(getattr(node, 'items_for_sale', []))
        shop_text = f"💰 {items_count} items for sale"
        
        node.canvas_item_ids['shop_info'] = self.canvas.create_text(
            x + 20, shop_y, text=shop_text, fill=theme.text_color,
            anchor="w", font=FONT_OPTION, tags=tags
        )
    
    def _create_special_node_content(self, node, x, y, body_height, theme: NodeTheme, tags):
        """Create content for special node types."""
        content_y = y + NODE_HEADER_HEIGHT + body_height + 10
        
        # Add type-specific indicators
        if isinstance(node, TimerNode):
            timer_text = f"⏱️ Timer: {getattr(node, 'duration', 'N/A')}s"
            node.canvas_item_ids['timer_info'] = self.canvas.create_text(
                x + 20, content_y, text=timer_text, fill=theme.text_color,
                anchor="w", font=FONT_OPTION, tags=tags
            )
        elif isinstance(node, InventoryNode):
            inv_text = "🎒 Inventory Management"
            node.canvas_item_ids['inv_info'] = self.canvas.create_text(
                x + 20, content_y, text=inv_text, fill=theme.text_color,
                anchor="w", font=FONT_OPTION, tags=tags
            )
    
    def _create_dialogue_options(self, node, x, y, body_height, theme: NodeTheme, tags):
        """Create dialogue options with enhanced styling and proper interaction elements."""
        if not hasattr(node, 'options') or not node.options:
            return
            
        for i, option in enumerate(node.options):
            y_pos = y + NODE_HEADER_HEIGHT + body_height + (i * OPTION_LINE_HEIGHT) + 15
            option_text = f"{i+1}. {self._wrap_text(option.get('text', '...'), 35)}"
            
            # Color code options based on effects or conditions
            text_color = theme.text_color
            if option.get('effects'):
                text_color = COLOR_ACCENT  # Highlight options with effects
            elif option.get('conditions'):
                text_color = COLOR_WARNING  # Highlight conditional options
            
            # Option text
            node.canvas_item_ids[f'option_text_{i}'] = self.canvas.create_text(
                x + 20, y_pos, text=option_text, fill=text_color,
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

            # CRITICAL: Option handle for connections
            node.canvas_item_ids[f'option_handle_{i}'] = self.canvas.create_oval(
                x + NODE_WIDTH - 20, y_pos - 8, x + NODE_WIDTH-4, y_pos + 8, 
                fill=COLOR_ACCENT, outline="", 
                tags=("handle", node.id, f"opt_{i}", "node")
            )
    
    def _create_node_footer(self, node, x, y, height, theme: NodeTheme, tags):
        """Create node footer with Add Choice button."""
        # Only add the footer for dialogue nodes (not dice roll or special nodes)
        if not isinstance(node, DiceRollNode):
            footer_y = y + height - NODE_FOOTER_HEIGHT
            footer_tags = ("node", node.id, "add_option_button")
            
            # CRITICAL: Add Choice button
            node.canvas_item_ids['add_button_text'] = self.canvas.create_text(
                x + NODE_WIDTH/2, footer_y + 18, text="+ Add Choice", 
                fill=COLOR_TEXT_MUTED, font=FONT_ADD_BUTTON, 
                tags=footer_tags, activefill=COLOR_ACCENT
            )
    
    def _create_status_indicators(self, node, x, y, theme: NodeTheme, tags):
        """Create status indicators for conditions, effects, etc."""
        indicators = []
        indicator_x = x + NODE_WIDTH - 25
        indicator_y = y + 5
        
        # Add indicators based on node properties
        if hasattr(node, 'conditions') and node.conditions:
            indicators.append("🔒")  # Has conditions
        
        if hasattr(node, 'effects') and node.effects:
            indicators.append("⚡")  # Has effects
            
        if hasattr(node, 'chapter') and node.chapter:
            indicators.append("📖")  # Part of chapter
        
        # Draw indicators
        for i, indicator in enumerate(indicators):
            self.canvas.create_text(
                indicator_x - (i * 20), indicator_y, text=indicator,
                fill=theme.icon_color, font=(FONT_FAMILY, 12, "normal"),
                anchor="center", tags=tags
            )
    
    def _apply_visual_effects(self, node, theme: NodeTheme, state: NodeVisualState):
        """Apply visual effects like hover, glow, pulse."""
        if state.is_hovered and theme.hover_scale != 1.0:
            self._apply_hover_scale(node, theme.hover_scale)
        
        if theme.hover_glow and (state.is_hovered or state.is_highlighted):
            self._apply_glow_effect(node, theme.header_color)
        
        if theme.pulse_enabled:
            self._apply_pulse_effect(node, theme.header_color)
    
    def _apply_hover_scale(self, node, scale: float):
        """Apply hover scaling effect."""
        # This would implement canvas item scaling
        pass
    
    def _apply_glow_effect(self, node, color: str):
        """Apply glow effect around node."""
        # This would create additional glow rectangles
        pass
    
    def _apply_pulse_effect(self, node, color: str):
        """Apply pulsing animation effect."""
        # This would implement color pulsing animation
        pass
    
    def _update_node_appearance(self, node_id: str):
        """Update node appearance based on current state."""
        # Try to find the node through canvas master (for real app)
        node = None
        try:
            if hasattr(self.canvas, 'master') and hasattr(self.canvas.master, 'app'):
                for app_node in self.canvas.master.app.nodes.values():
                    if app_node.id == node_id:
                        node = app_node
                        break
        except (AttributeError, TypeError):
            # In test environment or different setup, skip the update
            return
        
        if not node or 'border' not in node.canvas_item_ids:
            return
            
        state = self.get_node_state(node_id)
        theme = theme_manager.get_theme_for_node(node)
        
        # Update border based on selection state
        if state.is_selected:
            border_color = theme.selected_border_color
            border_width = theme.selected_border_width
        else:
            border_color = theme.border_color
            border_width = theme.border_width
        
        # Update the border canvas item
        try:
            self.canvas.itemconfig(
                node.canvas_item_ids['border'], 
                outline=border_color, 
                width=border_width
            )
        except (tk.TclError, AttributeError):
            # Canvas item might not exist in test environment
            pass
    
    def _create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle on the canvas using the same approach as original renderer."""
        points = [
            x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1,
            x2, y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius, 
            x2, y2 - radius, x2, y2, x2 - radius, y2, x2 - radius, y2, 
            x1 + radius, y2, x1 + radius, y2, x1, y2, x1, y2 - radius, 
            x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)
    
    def _adjust_color_opacity(self, color: str, opacity: float) -> str:
        """Adjust color opacity (simplified implementation)."""
        # For now, just return the original color
        # A full implementation would convert to RGBA and adjust alpha
        return color

    def _wrap_text(self, text, max_chars):
        """Truncates text to a maximum length for display on the node."""
        return text[:max_chars].strip() + "..." if len(text) > max_chars else text


# Utility functions for color manipulation
def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB tuple to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


def lighten_color(hex_color: str, factor: float = 0.2) -> str:
    """Lighten a hex color by a factor."""
    r, g, b = hex_to_rgb(hex_color)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return rgb_to_hex(r, g, b)


def darken_color(hex_color: str, factor: float = 0.2) -> str:
    """Darken a hex color by a factor."""
    r, g, b = hex_to_rgb(hex_color)
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return rgb_to_hex(r, g, b)