"""Node grouping and chapter system for organizing story sections."""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import json


class GroupType(Enum):
    """Types of node groups."""
    CHAPTER = "chapter"
    SCENE = "scene"
    SUBPLOT = "subplot"
    CHARACTER_ARC = "character_arc"
    LOCATION = "location"
    CUSTOM = "custom"


@dataclass
class NodeGroup:
    """Represents a group of related nodes."""
    
    id: str
    name: str
    group_type: GroupType
    description: str = ""
    color: str = "#4CAF50"
    nodes: Set[str] = field(default_factory=set)
    
    # Visual properties
    show_background: bool = True
    background_color: str = ""
    background_opacity: float = 0.1
    border_color: str = ""
    border_width: int = 2
    border_style: str = "solid"  # solid, dashed, dotted
    
    # Layout properties
    auto_layout: bool = False
    layout_direction: str = "horizontal"  # horizontal, vertical, grid
    padding: int = 20
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    priority: int = 0
    collapsed: bool = False
    
    def add_node(self, node_id: str):
        """Add a node to this group."""
        self.nodes.add(node_id)
    
    def remove_node(self, node_id: str):
        """Remove a node from this group."""
        self.nodes.discard(node_id)
    
    def contains_node(self, node_id: str) -> bool:
        """Check if this group contains a node."""
        return node_id in self.nodes
    
    def get_bounds(self, node_positions: Dict[str, Tuple[float, float]]) -> Tuple[float, float, float, float]:
        """Calculate the bounding box of all nodes in this group."""
        if not self.nodes:
            return 0, 0, 0, 0
        
        positions = [node_positions[node_id] for node_id in self.nodes if node_id in node_positions]
        if not positions:
            return 0, 0, 0, 0
        
        min_x = min(pos[0] for pos in positions) - self.padding
        min_y = min(pos[1] for pos in positions) - self.padding
        max_x = max(pos[0] for pos in positions) + 300 + self.padding  # Assuming node width ~300
        max_y = max(pos[1] for pos in positions) + 200 + self.padding  # Assuming node height ~200
        
        return min_x, min_y, max_x, max_y
    
    def to_dict(self) -> Dict:
        """Serialize group to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "group_type": self.group_type.value,
            "description": self.description,
            "color": self.color,
            "nodes": list(self.nodes),
            "show_background": self.show_background,
            "background_color": self.background_color,
            "background_opacity": self.background_opacity,
            "border_color": self.border_color,
            "border_width": self.border_width,
            "border_style": self.border_style,
            "auto_layout": self.auto_layout,
            "layout_direction": self.layout_direction,
            "padding": self.padding,
            "tags": self.tags,
            "priority": self.priority,
            "collapsed": self.collapsed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NodeGroup':
        """Create group from dictionary."""
        group = cls(
            id=data["id"],
            name=data["name"],
            group_type=GroupType(data["group_type"]),
            description=data.get("description", ""),
            color=data.get("color", "#4CAF50")
        )
        
        group.nodes = set(data.get("nodes", []))
        group.show_background = data.get("show_background", True)
        group.background_color = data.get("background_color", "")
        group.background_opacity = data.get("background_opacity", 0.1)
        group.border_color = data.get("border_color", "")
        group.border_width = data.get("border_width", 2)
        group.border_style = data.get("border_style", "solid")
        group.auto_layout = data.get("auto_layout", False)
        group.layout_direction = data.get("layout_direction", "horizontal")
        group.padding = data.get("padding", 20)
        group.tags = data.get("tags", [])
        group.priority = data.get("priority", 0)
        group.collapsed = data.get("collapsed", False)
        
        return group


class NodeGroupManager:
    """Manages node groups and their visual representation."""
    
    def __init__(self, canvas=None):
        self.canvas = canvas
        self.groups: Dict[str, NodeGroup] = {}
        self.node_to_groups: Dict[str, Set[str]] = {}  # node_id -> set of group_ids
        self.group_visuals: Dict[str, List[int]] = {}  # group_id -> list of canvas item ids
        
        # Visual settings
        self.show_group_backgrounds = True
        self.show_group_borders = True
        self.show_group_labels = True
        
    def create_group(self, group_id: str, name: str, group_type: GroupType, **kwargs) -> NodeGroup:
        """Create a new node group."""
        if group_id in self.groups:
            raise ValueError(f"Group '{group_id}' already exists")
        
        group = NodeGroup(
            id=group_id,
            name=name,
            group_type=group_type,
            **kwargs
        )
        
        self.groups[group_id] = group
        return group
    
    def delete_group(self, group_id: str):
        """Delete a group and remove nodes from it."""
        if group_id not in self.groups:
            return
        
        group = self.groups[group_id]
        
        # Remove nodes from group mappings
        for node_id in group.nodes:
            if node_id in self.node_to_groups:
                self.node_to_groups[node_id].discard(group_id)
                if not self.node_to_groups[node_id]:
                    del self.node_to_groups[node_id]
        
        # Remove visual elements
        self._remove_group_visuals(group_id)
        
        # Delete group
        del self.groups[group_id]
    
    def add_node_to_group(self, node_id: str, group_id: str):
        """Add a node to a group."""
        if group_id not in self.groups:
            raise ValueError(f"Group '{group_id}' does not exist")
        
        group = self.groups[group_id]
        group.add_node(node_id)
        
        # Update mappings
        if node_id not in self.node_to_groups:
            self.node_to_groups[node_id] = set()
        self.node_to_groups[node_id].add(group_id)
        
        # Update visuals
        self._update_group_visuals(group_id)
    
    def remove_node_from_group(self, node_id: str, group_id: str):
        """Remove a node from a group."""
        if group_id not in self.groups:
            return
        
        group = self.groups[group_id]
        group.remove_node(node_id)
        
        # Update mappings
        if node_id in self.node_to_groups:
            self.node_to_groups[node_id].discard(group_id)
            if not self.node_to_groups[node_id]:
                del self.node_to_groups[node_id]
        
        # Update visuals
        self._update_group_visuals(group_id)
    
    def get_node_groups(self, node_id: str) -> List[NodeGroup]:
        """Get all groups that contain a node."""
        if node_id not in self.node_to_groups:
            return []
        
        return [self.groups[group_id] for group_id in self.node_to_groups[node_id]]
    
    def get_groups_by_type(self, group_type: GroupType) -> List[NodeGroup]:
        """Get all groups of a specific type."""
        return [group for group in self.groups.values() if group.group_type == group_type]
    
    def auto_create_chapter_groups(self, nodes: Dict):
        """Automatically create chapter groups based on node chapters."""
        chapter_nodes = {}
        
        # Group nodes by chapter
        for node_id, node in nodes.items():
            if hasattr(node, 'chapter') and node.chapter:
                chapter = str(node.chapter)
                if chapter not in chapter_nodes:
                    chapter_nodes[chapter] = []
                chapter_nodes[chapter].append(node_id)
        
        # Create groups for each chapter
        for chapter, node_ids in chapter_nodes.items():
            group_id = f"chapter_{chapter}"
            
            if group_id not in self.groups:
                self.create_group(
                    group_id=group_id,
                    name=f"Chapter {chapter}",
                    group_type=GroupType.CHAPTER,
                    description=f"Story chapter {chapter}",
                    color=self._get_chapter_color(int(chapter) if chapter.isdigit() else 1)
                )
            
            # Add nodes to group
            for node_id in node_ids:
                self.add_node_to_group(node_id, group_id)
    
    def _get_chapter_color(self, chapter_num: int) -> str:
        """Get a color for a chapter based on its number."""
        colors = [
            "#1976D2",  # Blue
            "#388E3C",  # Green
            "#F57C00",  # Orange
            "#7B1FA2",  # Purple
            "#D32F2F",  # Red
            "#00796B",  # Teal
            "#FBC02D",  # Yellow
            "#5D4037",  # Brown
        ]
        return colors[(chapter_num - 1) % len(colors)]
    
    def draw_group_backgrounds(self, node_positions: Dict[str, Tuple[float, float]]):
        """Draw background visuals for all groups."""
        if not self.canvas or not self.show_group_backgrounds:
            return
        
        # Sort groups by priority (lower priority drawn first)
        sorted_groups = sorted(self.groups.values(), key=lambda g: g.priority)
        
        for group in sorted_groups:
            if group.show_background and group.nodes:
                self._draw_group_background(group, node_positions)
    
    def _draw_group_background(self, group: NodeGroup, node_positions: Dict[str, Tuple[float, float]]):
        """Draw background for a single group."""
        bounds = group.get_bounds(node_positions)
        if bounds == (0, 0, 0, 0):
            return
        
        min_x, min_y, max_x, max_y = bounds
        
        # Remove existing visuals for this group
        self._remove_group_visuals(group.id)
        
        visual_items = []
        
        # Background rectangle
        if group.show_background:
            bg_color = group.background_color or group.color
            bg_rect = self._create_group_rectangle(
                min_x, min_y, max_x, max_y,
                fill=bg_color,
                outline="",
                stipple="gray25" if group.background_opacity < 0.5 else ""
            )
            visual_items.append(bg_rect)
        
        # Border
        if self.show_group_borders and group.border_width > 0:
            border_color = group.border_color or group.color
            border_rect = self._create_group_rectangle(
                min_x, min_y, max_x, max_y,
                fill="",
                outline=border_color,
                width=group.border_width,
                dash=self._get_dash_pattern(group.border_style)
            )
            visual_items.append(border_rect)
        
        # Label
        if self.show_group_labels:
            label_x = min_x + 10
            label_y = min_y + 5
            label_text = self.canvas.create_text(
                label_x, label_y,
                text=group.name,
                fill=group.color,
                font=("Arial", 12, "bold"),
                anchor="nw",
                tags=("group_label", f"group_{group.id}")
            )
            visual_items.append(label_text)
        
        self.group_visuals[group.id] = visual_items
    
    def _create_group_rectangle(self, x1, y1, x2, y2, **kwargs):
        """Create a rectangle for group background/border."""
        return self.canvas.create_rectangle(
            x1, y1, x2, y2,
            tags=("group_background", f"group_{kwargs.get('group_id', 'unknown')}"),
            **kwargs
        )
    
    def _get_dash_pattern(self, border_style: str) -> Optional[Tuple[int, ...]]:
        """Get dash pattern for border style."""
        patterns = {
            "solid": None,
            "dashed": (5, 5),
            "dotted": (2, 2),
            "dash_dot": (5, 5, 2, 5)
        }
        return patterns.get(border_style, None)
    
    def _update_group_visuals(self, group_id: str):
        """Update visuals for a specific group."""
        # This would trigger a redraw of the group background
        # For now, just remove existing visuals
        self._remove_group_visuals(group_id)
    
    def _remove_group_visuals(self, group_id: str):
        """Remove visual elements for a group."""
        if group_id in self.group_visuals:
            for item_id in self.group_visuals[group_id]:
                try:
                    self.canvas.delete(item_id)
                except:
                    pass  # Item might already be deleted
            del self.group_visuals[group_id]
    
    def toggle_group_visibility(self, group_id: str):
        """Toggle visibility of a group's background."""
        if group_id in self.groups:
            group = self.groups[group_id]
            group.show_background = not group.show_background
            self._update_group_visuals(group_id)
    
    def collapse_group(self, group_id: str):
        """Collapse a group (hide its nodes)."""
        if group_id in self.groups:
            self.groups[group_id].collapsed = True
            # Implementation would hide the nodes visually
    
    def expand_group(self, group_id: str):
        """Expand a group (show its nodes)."""
        if group_id in self.groups:
            self.groups[group_id].collapsed = False
            # Implementation would show the nodes visually
    
    def export_groups(self) -> Dict:
        """Export all groups to a dictionary."""
        return {
            group_id: group.to_dict() 
            for group_id, group in self.groups.items()
        }
    
    def import_groups(self, groups_data: Dict):
        """Import groups from a dictionary."""
        self.groups.clear()
        self.node_to_groups.clear()
        
        for group_id, group_data in groups_data.items():
            group = NodeGroup.from_dict(group_data)
            self.groups[group_id] = group
            
            # Rebuild node mappings
            for node_id in group.nodes:
                if node_id not in self.node_to_groups:
                    self.node_to_groups[node_id] = set()
                self.node_to_groups[node_id].add(group_id)
    
    def get_group_hierarchy(self) -> Dict[str, List[str]]:
        """Get a hierarchical view of groups."""
        hierarchy = {
            "chapters": [],
            "scenes": [],
            "subplots": [],
            "character_arcs": [],
            "locations": [],
            "custom": []
        }
        
        for group in self.groups.values():
            type_key = group.group_type.value + "s" if group.group_type.value != "custom" else "custom"
            if type_key in hierarchy:
                hierarchy[type_key].append(group.id)
        
        return hierarchy


# Global group manager instance
group_manager = NodeGroupManager()