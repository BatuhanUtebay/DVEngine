"""Node theming system for visual customization of nodes."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from ...constants import *


@dataclass
class NodeTheme:
    """Defines the visual appearance of a node."""
    
    # Basic colors
    header_color: str = NODE_DEFAULT_COLOR
    body_color: str = NODE_DEFAULT_COLOR
    border_color: str = ""
    text_color: str = COLOR_TEXT
    subtitle_color: str = COLOR_TEXT_MUTED
    
    # Visual effects
    shadow_enabled: bool = True
    shadow_color: str = "#111111"
    shadow_offset: tuple = (3, 3)
    border_width: int = 0
    corner_radius: int = NODE_BORDER_RADIUS
    
    # Icon and decorations
    icon: str = ""  # Unicode icon or emoji
    icon_color: str = COLOR_TEXT
    icon_size: int = 16
    header_pattern: str = ""  # Optional background pattern
    
    # Animation properties
    hover_scale: float = 1.0
    hover_glow: bool = False
    pulse_enabled: bool = False
    
    # State variations
    selected_border_color: str = NODE_SELECTED_OUTLINE_COLOR
    selected_border_width: int = 3
    disabled_opacity: float = 0.5


@dataclass 
class NodeVisualState:
    """Represents the current visual state of a node."""
    
    is_selected: bool = False
    is_hovered: bool = False
    is_disabled: bool = False
    is_highlighted: bool = False
    highlight_color: str = ""
    custom_properties: Dict[str, Any] = field(default_factory=dict)


class NodeThemeManager:
    """Manages node themes and visual styling."""
    
    def __init__(self):
        self.themes = {}
        self.node_type_themes = {}
        self.conditional_themes = {}
        self._initialize_default_themes()
    
    def _initialize_default_themes(self):
        """Create default themes for different node types."""
        
        # Default dialogue theme
        self.themes["default"] = NodeTheme(
            header_color="#455A64",
            body_color=NODE_DEFAULT_COLOR,
            icon="💬",
            icon_color=COLOR_TEXT
        )
        
        # Start node theme
        self.themes["start"] = NodeTheme(
            header_color=NODE_INTRO_COLOR,
            body_color=NODE_DEFAULT_COLOR,
            icon="⭐",
            icon_color="#FFD700",
            hover_glow=True,
            pulse_enabled=True
        )
        
        # Combat node theme
        self.themes["combat"] = NodeTheme(
            header_color=NODE_COMBAT_COLOR,
            body_color="#2C1810",
            border_color="#8B0000",
            border_width=2,
            icon="⚔️",
            icon_color="#FF6B6B",
            hover_scale=1.02
        )
        
        # Advanced combat theme
        self.themes["advanced_combat"] = NodeTheme(
            header_color="#8B0000",
            body_color="#1A0A0A",
            border_color="#DC143C",
            border_width=3,
            icon="🛡️",
            icon_color="#FFD700",
            hover_scale=1.05,
            hover_glow=True,
            pulse_enabled=True,
            shadow_color="#8B0000",
            shadow_offset=(4, 4)
        )
        
        # Shop node theme
        self.themes["shop"] = NodeTheme(
            header_color="#8E6A3A",
            body_color="#3D2F1F",
            border_color="#DAA520",
            border_width=1,
            icon="🛒",
            icon_color="#FFD700",
            shadow_color="#2F1B0C"
        )
        
        # Dice roll theme
        self.themes["dice_roll"] = NodeTheme(
            header_color="#4A148C",
            body_color="#1A0A2E",
            border_color="#7B1FA2",
            border_width=1,
            icon="🎲",
            icon_color="#E1BEE7",
            hover_glow=True
        )
        
        # Random event theme
        self.themes["random_event"] = NodeTheme(
            header_color="#FF6F00",
            body_color="#331900",
            border_color="#FF8F00",
            border_width=1,
            icon="❓",
            icon_color="#FFB74D",
            pulse_enabled=True
        )
        
        # Timer node theme
        self.themes["timer"] = NodeTheme(
            header_color="#D32F2F",
            body_color="#1A0000",
            border_color="#F44336",
            border_width=2,
            icon="⏰",
            icon_color="#FFCDD2",
            pulse_enabled=True
        )
        
        # Inventory node theme
        self.themes["inventory"] = NodeTheme(
            header_color="#5D4037",
            body_color="#2E1A16",
            border_color="#8D6E63",
            border_width=1,
            icon="🎒",
            icon_color="#BCAAA4"
        )
        
        # Chapter/group themes
        self.themes["chapter_1"] = NodeTheme(
            header_color="#1976D2",
            body_color="#0D1421",
            border_color="#42A5F5",
            border_width=1,
            icon="📖",
            icon_color="#90CAF9"
        )
        
        self.themes["chapter_2"] = NodeTheme(
            header_color="#388E3C",
            body_color="#0A1F0A",
            border_color="#66BB6A",
            border_width=1,
            icon="📚",
            icon_color="#A5D6A7"
        )
        
        self.themes["chapter_3"] = NodeTheme(
            header_color="#F57C00",
            body_color="#331500",
            border_color="#FFB74D",
            border_width=1,
            icon="📜",
            icon_color="#FFCC02"
        )
        
        # Conditional state themes
        self.themes["quest_active"] = NodeTheme(
            header_color=COLOR_QUEST_ACTIVE,
            body_color="#332C00",
            border_color="#FDD835",
            border_width=2,
            icon="📋",
            icon_color="#FFF59D",
            hover_glow=True
        )
        
        self.themes["quest_completed"] = NodeTheme(
            header_color=COLOR_QUEST_COMPLETED,
            body_color="#0A2E0A",
            border_color="#4CAF50",
            border_width=2,
            icon="✅",
            icon_color="#C8E6C9"
        )
        
        self.themes["locked"] = NodeTheme(
            header_color="#424242",
            body_color="#1A1A1A",
            border_color="#616161",
            border_width=1,
            icon="🔒",
            icon_color="#9E9E9E"
        )
        
        # Map node types to default themes
        self.node_type_themes = {
            "DialogueNode": "default",
            "CombatNode": "combat",
            "AdvancedCombatNode": "advanced_combat",
            "ShopNode": "shop",
            "DiceRollNode": "dice_roll",
            "RandomEventNode": "random_event",
            "TimerNode": "timer",
            "InventoryNode": "inventory"
        }
    
    def get_theme_for_node(self, node) -> NodeTheme:
        """Get the appropriate theme for a node."""
        # Check for custom theme on node
        if hasattr(node, 'theme') and node.theme in self.themes:
            return self.themes[node.theme]
        
        # Check for chapter/group theme
        if hasattr(node, 'chapter') and node.chapter:
            chapter_theme = f"chapter_{node.chapter}"
            if chapter_theme in self.themes:
                return self.themes[chapter_theme]
        
        # Check for conditional themes
        conditional_theme = self._get_conditional_theme(node)
        if conditional_theme:
            return conditional_theme
            
        # Check for node type theme
        node_type = type(node).__name__
        if node_type in self.node_type_themes:
            theme_name = self.node_type_themes[node_type]
            return self.themes[theme_name]
        
        # Special case for start node
        if hasattr(node, 'id') and node.id == "intro":
            return self.themes["start"]
            
        # Default theme
        return self.themes["default"]
    
    def _get_conditional_theme(self, node) -> Optional[NodeTheme]:
        """Get theme based on node conditions or flags."""
        # This would be expanded to check story flags, quest states, etc.
        # For now, return None
        return None
    
    def register_theme(self, name: str, theme: NodeTheme):
        """Register a custom theme."""
        self.themes[name] = theme
    
    def set_node_type_theme(self, node_type: str, theme_name: str):
        """Set the default theme for a node type."""
        self.node_type_themes[node_type] = theme_name
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return list(self.themes.keys())
    
    def create_custom_theme(self, base_theme: str = "default", **kwargs) -> NodeTheme:
        """Create a custom theme based on an existing theme."""
        if base_theme not in self.themes:
            base_theme = "default"
            
        base = self.themes[base_theme]
        
        # Create new theme with overrides
        theme_dict = base.__dict__.copy()
        theme_dict.update(kwargs)
        
        return NodeTheme(**theme_dict)


# Global theme manager instance
theme_manager = NodeThemeManager()