# dvge/ui/canvas_widget.py - Fully fixed version with no duplication bug
from PySide6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsRectItem, 
    QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsLineItem,
    QGraphicsPathItem, QMenu, QMessageBox, QGraphicsItem,
    QGraphicsProxyWidget, QLabel, QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QTimer
from PySide6.QtGui import (
    QFont, QColor, QPen, QBrush, QPainter, QPainterPath, 
    QFontMetrics, QPolygonF, QLinearGradient, QRadialGradient
)

from ..constants import *
from ..data_models import DialogueNode, DiceRollNode

class NodeGraphicsItem(QGraphicsRectItem):
    """Custom graphics item for dialogue nodes with modern styling."""
    
    def __init__(self, node, canvas_widget):
        super().__init__()
        self.node = node
        self.canvas_widget = canvas_widget
        self.option_handles = []
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setCursor(Qt.PointingHandCursor)
        
        # Track movement state
        self._is_being_dragged = False
        self._last_valid_pos = QPointF(node.x, node.y)
        
        self.update_appearance()

    def update_appearance(self):
        """Update the visual appearance of the node."""
        # Calculate node dimensions
        font_metrics = QFontMetrics(QFont("Segoe UI", 9))
        text_width = NODE_WIDTH - 40
        
        # Calculate text height
        text_rect = font_metrics.boundingRect(
            0, 0, text_width, 1000, 
            Qt.TextWordWrap, self.node.text
        )
        self.node.calculated_text_height = text_rect.height()
        
        height = self.node.get_height()
        
        # Set position and size
        self.setRect(0, 0, NODE_WIDTH, height)
        self.setPos(self.node.x, self.node.y)
        
        # Clear existing handles
        for handle in self.option_handles:
            if handle.scene():
                handle.scene().removeItem(handle)
        self.option_handles.clear()
        
        # Create option handles for regular dialogue nodes
        if not isinstance(self.node, DiceRollNode):
            for i, option in enumerate(self.node.options):
                handle = OptionHandle(self, i)
                self.option_handles.append(handle)
                if self.scene():
                    self.scene().addItem(handle)

    def paint(self, painter, option, widget=None):
        """Custom painting for modern node appearance."""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Node bounds
        rect = self.rect()
        
        # Determine colors
        is_intro = self.node.id == "intro"
        is_selected = self.isSelected()
        
        if is_intro:
            base_color = QColor("#006400")
        elif isinstance(self.node, DiceRollNode):
            base_color = QColor("#8B4513")
        else:
            base_color = QColor(self.node.color) if self.node.color != NODE_DEFAULT_COLOR else QColor("#455A64")
        
        # Draw shadow
        shadow_rect = rect.adjusted(3, 3, 3, 3)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 100))
        
        # Create gradient for main body
        gradient = QLinearGradient(0, rect.top(), 0, rect.bottom())
        gradient.setColorAt(0, QColor("#3A3A3A"))
        gradient.setColorAt(1, QColor("#2A2A2A"))
        
        # Draw main body
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor("#555555"), 1))
        painter.drawRoundedRect(rect, NODE_BORDER_RADIUS, NODE_BORDER_RADIUS)
        
        # Draw header
        header_rect = QRectF(0, 0, NODE_WIDTH, NODE_HEADER_HEIGHT)
        header_gradient = QLinearGradient(0, 0, 0, NODE_HEADER_HEIGHT)
        header_gradient.setColorAt(0, base_color.lighter(120))
        header_gradient.setColorAt(1, base_color)
        
        painter.setBrush(QBrush(header_gradient))
        painter.setPen(QPen(base_color.darker(120), 1))
        painter.drawRoundedRect(header_rect, NODE_BORDER_RADIUS, NODE_BORDER_RADIUS)
        
        # Draw selection outline
        if is_selected:
            selection_pen = QPen(QColor(NODE_SELECTED_OUTLINE_COLOR), 3)
            painter.setPen(selection_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(rect.adjusted(-2, -2, 2, 2), NODE_BORDER_RADIUS + 2, NODE_BORDER_RADIUS + 2)
        
        # Draw text content
        self._draw_text_content(painter, rect)

    def _draw_text_content(self, painter, rect):
        """Draw the text content of the node."""
        painter.setPen(QColor("#FFFFFF"))
        
        # Header text
        is_intro = self.node.id == "intro"
        header_text = f"{'* ' if is_intro else ''}{self.node.id} | {self.node.npc}"
        
        header_font = QFont("Segoe UI", 10, QFont.Bold)
        painter.setFont(header_font)
        header_rect = QRectF(20, 8, NODE_WIDTH - 40, NODE_HEADER_HEIGHT - 16)
        painter.drawText(header_rect, Qt.AlignLeft | Qt.AlignVCenter, header_text)
        
        # Dialogue text
        dialogue_font = QFont("Segoe UI", 9)
        painter.setFont(dialogue_font)
        painter.setPen(QColor("#CCCCCC"))
        
        dialogue_rect = QRectF(20, NODE_HEADER_HEIGHT + 10, NODE_WIDTH - 40, self.node.calculated_text_height)
        painter.drawText(dialogue_rect, Qt.TextWordWrap, self.node.text)
        
        # Options or dice roll content
        if isinstance(self.node, DiceRollNode):
            self._draw_dice_roll_content(painter)
        else:
            self._draw_options_content(painter)

    def _draw_dice_roll_content(self, painter):
        """Draw dice roll specific content."""
        y_offset = NODE_HEADER_HEIGHT + max(NODE_BASE_BODY_HEIGHT, self.node.calculated_text_height + 20)
        
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.setPen(QColor("#FFD700"))
        
        dice_text = f"[DICE] Roll {self.node.num_dice}d{self.node.num_sides} vs {self.node.success_threshold}"
        painter.drawText(20, y_offset + 20, dice_text)
        
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor("#90EE90"))
        painter.drawText(20, y_offset + 40, f"[OK] Success: {self.node.success_node or '[Not Set]'}")
        
        painter.setPen(QColor("#F08080"))
        painter.drawText(20, y_offset + 60, f"[X] Failure: {self.node.failure_node or '[Not Set]'}")

    def _draw_options_content(self, painter):
        """Draw dialogue options."""
        y_offset = NODE_HEADER_HEIGHT + max(NODE_BASE_BODY_HEIGHT, self.node.calculated_text_height + 20)
        
        painter.setFont(QFont("Segoe UI", 8))
        
        for i, option in enumerate(self.node.options):
            option_y = y_offset + (i * OPTION_LINE_HEIGHT) + 15
            
            # Option text
            painter.setPen(QColor("#FFFFFF"))
            option_text = f"{i+1}. {self._wrap_text(option.get('text', '...'), 35)}"
            painter.drawText(20, option_y, option_text)
            
            # Condition/Effect indicators
            indicators = []
            if option.get('conditions'):
                indicators.append("[C]")
            if option.get('effects'):
                indicators.append("[E]")
            
            if indicators:
                painter.setPen(QColor("#007ACC"))
                indicator_text = " ".join(indicators)
                painter.drawText(NODE_WIDTH - 45, option_y, indicator_text)

    def _wrap_text(self, text, max_chars):
        """Truncate text to a maximum length for display."""
        return text[:max_chars].strip() + "..." if len(text) > max_chars else text

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self._is_being_dragged = True
            self._last_valid_pos = self.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move events during dragging."""
        if self._is_being_dragged:
            # Update handle positions during drag
            for handle in self.option_handles:
                handle.update_position_during_drag()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        super().mouseReleaseEvent(event)
        
        if event.button() == Qt.LeftButton and self._is_being_dragged:
            self._is_being_dragged = False
            
            # Get final position
            current_pos = self.pos()
            
            # Snap to grid
            grid_x = round(current_pos.x() / GRID_SIZE) * GRID_SIZE
            grid_y = round(current_pos.y() / GRID_SIZE) * GRID_SIZE
            
            # Update position
            self.setPos(grid_x, grid_y)
            self.node.x = grid_x
            self.node.y = grid_y
            
            # Update handles to final positions
            for handle in self.option_handles:
                handle.update_position_final()
            
            # Update connections only once at the end
            self.canvas_widget.update_connections()

    def itemChange(self, change, value):
        """Handle item changes - MINIMAL implementation to prevent loops."""
        if change == QGraphicsItem.ItemPositionChange and self._is_being_dragged:
            # Only update data model position, nothing else
            new_pos = value
            self.node.x = new_pos.x()
            self.node.y = new_pos.y()
        
        return super().itemChange(change, value)

class OptionHandle(QGraphicsEllipseItem):
    """Handle for connecting dialogue options."""
    
    def __init__(self, node_item, option_index):
        super().__init__()
        self.node_item = node_item
        self.option_index = option_index
        
        # Set up handle appearance
        self.setRect(-8, -8, 16, 16)
        self.setBrush(QBrush(QColor("#007ACC")))
        self.setPen(QPen(QColor("#005A9E"), 2))
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        self.setCursor(Qt.CrossCursor)
        
        self.update_position_final()

    def update_position_during_drag(self):
        """Update position during node dragging - smooth but may be approximate."""
        if not self.node_item or not self.node_item.node:
            return
        
        node = self.node_item.node
        body_height = max(NODE_BASE_BODY_HEIGHT, node.calculated_text_height + 20)
        y_offset = NODE_HEADER_HEIGHT + body_height + (self.option_index * OPTION_LINE_HEIGHT) + (OPTION_LINE_HEIGHT / 2)
        
        # Use current visual position of node for smooth dragging
        node_pos = self.node_item.pos()
        self.setPos(node_pos.x() + NODE_WIDTH - 12, node_pos.y() + y_offset)

    def update_position_final(self):
        """Update to final position - precise positioning."""
        if not self.node_item or not self.node_item.node:
            return
        
        node = self.node_item.node
        body_height = max(NODE_BASE_BODY_HEIGHT, node.calculated_text_height + 20)
        y_offset = NODE_HEADER_HEIGHT + body_height + (self.option_index * OPTION_LINE_HEIGHT) + (OPTION_LINE_HEIGHT / 2)
        
        # Use data model position for precise final positioning
        self.setPos(node.x + NODE_WIDTH - 12, node.y + y_offset)

    def mousePressEvent(self, event):
        """Handle mouse press to start connection."""
        if event.button() == Qt.LeftButton:
            self.node_item.canvas_widget.start_connection(self.node_item.node.id, self.option_index)
            event.accept()

class ConnectionLine(QGraphicsPathItem):
    """Curved connection line between nodes."""
    
    def __init__(self, start_pos, end_pos, color=QColor("#007ACC")):
        super().__init__()
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        
        self.setPen(QPen(color, 2.5))
        self.setBrush(Qt.NoBrush)
        
        self.update_path()

    def update_path(self):
        """Update the curved path between points."""
        path = QPainterPath()
        path.moveTo(self.start_pos)
        
        # Create bezier curve
        ctrl1_x = self.start_pos.x() + 70
        ctrl1_y = self.start_pos.y()
        ctrl2_x = self.end_pos.x() - 70
        ctrl2_y = self.end_pos.y()
        
        path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, self.end_pos.x(), self.end_pos.y())
        
        # Add arrow head
        self._add_arrow_head(path)
        
        self.setPath(path)

    def _add_arrow_head(self, path):
        """Add an arrow head to the end of the path."""
        # Calculate arrow direction from control point to end
        dx = self.end_pos.x() - (self.end_pos.x() - 70)
        dy = self.end_pos.y() - self.end_pos.y()
        
        # If no direction, use horizontal
        if dx == 0 and dy == 0:
            dx = -1
        
        # Normalize
        length = (dx*dx + dy*dy) ** 0.5
        if length > 0:
            dx /= length
            dy /= length
        
        # Arrow points
        arrow_length = 12
        arrow_width = 6
        
        p1 = QPointF(
            self.end_pos.x() - arrow_length * dx + arrow_width * dy,
            self.end_pos.y() - arrow_length * dy - arrow_width * dx
        )
        p2 = QPointF(
            self.end_pos.x() - arrow_length * dx - arrow_width * dy,
            self.end_pos.y() - arrow_length * dy + arrow_width * dx
        )
        
        # Draw arrow
        arrow = QPainterPath()
        arrow.moveTo(self.end_pos)
        arrow.lineTo(p1)
        arrow.moveTo(self.end_pos)
        arrow.lineTo(p2)
        
        path.addPath(arrow)

class CustomGraphicsView(QGraphicsView):
    """Custom graphics view that handles context menu properly."""
    
    context_menu_requested = Signal(QPointF)  # scene position
    
    def __init__(self, scene):
        super().__init__(scene)
        
    def contextMenuEvent(self, event):
        """Handle context menu events."""
        # Convert to scene coordinates
        scene_pos = self.mapToScene(event.pos())
        
        # Check if we clicked on a graphics item
        item_at_pos = self.scene().itemAt(scene_pos, self.transform())
        
        # Only show context menu if we clicked on empty space
        if not item_at_pos or not isinstance(item_at_pos, (NodeGraphicsItem, OptionHandle)):
            self.context_menu_requested.emit(scene_pos)
        
        # Don't call super() to prevent default context menu

class ModernCanvasWidget(QWidget):
    """Modern canvas widget for the node editor."""
    
    node_selected = Signal(list)
    nodes_changed = Signal()
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.node_items = {}
        self.connection_items = []
        self.is_connecting = False
        self.connection_start = None
        self.temp_connection = None
        
        # Track last context menu position
        self.last_context_pos = QPointF(0, 0)
        
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Graphics view and scene
        self.scene = QGraphicsScene()
        self.view = CustomGraphicsView(self.scene)
        
        # Configure view
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setBackgroundBrush(QBrush(QColor(COLOR_CANVAS_BACKGROUND)))
        
        # Connect context menu signal
        self.view.context_menu_requested.connect(self._on_context_menu_requested)
        
        # Custom styling for the view
        self.view.setStyleSheet("""
            QGraphicsView {
                border: 1px solid #3e3e40;
                border-radius: 8px;
                background-color: #1a1a1a;
            }
        """)
        
        layout.addWidget(self.view)
        
        # Setup scene
        self.scene.setSceneRect(0, 0, 10000, 10000)
        self.draw_grid()
        
        # Connect signals
        self.scene.selectionChanged.connect(self._on_selection_changed)
        
        # Context menu
        self.context_menu = QMenu(self)
        self._setup_context_menu()

    def _on_context_menu_requested(self, scene_pos):
        """Handle context menu request from view."""
        self.last_context_pos = scene_pos
        
        # Show context menu at cursor position
        cursor_pos = self.mapToGlobal(self.mapFromScene(scene_pos))
        self._show_context_menu_at_pos(cursor_pos)

    def mapFromScene(self, scene_pos):
        """Convert scene position to widget coordinates."""
        return self.view.mapFromScene(scene_pos)

    def _setup_context_menu(self):
        """Setup the context menu."""
        self.context_menu.addAction("Add Dialogue Node", self._add_dialogue_node)
        self.context_menu.addAction("Add Dice Roll Node", self._add_dice_roll_node)
        self.context_menu.addSeparator()
        
        self.delete_action = self.context_menu.addAction("Delete Selected", self._delete_selected)
        self.delete_action.setEnabled(False)

    def draw_grid(self):
        """Draw the background grid."""
        pen = QPen(QColor(COLOR_GRID_LINES), 1, Qt.DotLine)
        
        # Draw vertical lines
        for x in range(0, 10000, GRID_SIZE):
            line = self.scene.addLine(x, 0, x, 10000, pen)
            line.setZValue(-1000)  # Send to back
        
        # Draw horizontal lines
        for y in range(0, 10000, GRID_SIZE):
            line = self.scene.addLine(0, y, 10000, y, pen)
            line.setZValue(-1000)  # Send to back

    def _show_context_menu_at_pos(self, global_pos):
        """Show context menu at the given global position."""
        # Update delete action state
        self.delete_action.setEnabled(bool(self.app.selected_node_ids))
        
        # Show menu
        self.context_menu.exec(global_pos)

    def _add_dialogue_node(self):
        """Add a new dialogue node at the context menu position."""
        self.add_node_at_position(self.last_context_pos.x(), self.last_context_pos.y())

    def _add_dice_roll_node(self):
        """Add a new dice roll node at the context menu position."""
        self.add_node_at_position(self.last_context_pos.x(), self.last_context_pos.y(), "dice_roll")

    def _delete_selected(self):
        """Delete selected nodes."""
        if not self.app.selected_node_ids:
            return
            
        reply = QMessageBox.question(
            self, "Delete Nodes",
            f"Are you sure you want to delete {len(self.app.selected_node_ids)} selected node(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_nodes(self.app.selected_node_ids)

    def add_node_at_position(self, x, y, node_type="dialogue"):
        """Add a new node at the specified position."""
        self.app._save_state_for_undo("Add Node")
        
        # Generate unique ID
        while f"node_{self.app.node_id_counter}" in self.app.nodes:
            self.app.node_id_counter += 1
        
        node_id = f"node_{self.app.node_id_counter}"
        self.app.node_id_counter += 1
        
        # Create node
        if node_type == "dice_roll":
            new_node = DiceRollNode(x=x, y=y, node_id=node_id)
        else:
            new_node = DialogueNode(x=x, y=y, node_id=node_id)
        
        self.app.nodes[node_id] = new_node
        
        # Create visual representation
        self.create_node_item(new_node)
        
        # Select the new node
        self.app.set_selection([node_id], node_id)
        self.nodes_changed.emit()

    def create_node_item(self, node):
        """Create a visual item for a node."""
        item = NodeGraphicsItem(node, self)
        self.scene.addItem(item)
        self.node_items[node.id] = item
        return item

    def delete_nodes(self, node_ids):
        """Delete the specified nodes."""
        self.app._save_state_for_undo("Delete Nodes")
        
        for node_id in node_ids:
            if node_id == "intro":
                QMessageBox.warning(self, "Cannot Delete", "The 'intro' node cannot be deleted.")
                continue
            
            # Clean up references in other nodes
            for node in self.app.nodes.values():
                for option in getattr(node, 'options', []):
                    if option.get('nextNode') == node_id:
                        option['nextNode'] = ""
            
            # Remove from scene
            if node_id in self.node_items:
                item = self.node_items[node_id]
                # Remove handles first
                for handle in item.option_handles:
                    if handle.scene():
                        handle.scene().removeItem(handle)
                # Remove main item
                self.scene.removeItem(item)
                del self.node_items[node_id]
            
            # Remove from data
            if node_id in self.app.nodes:
                del self.app.nodes[node_id]
        
        # Clear selection
        self.app.set_selection([])
        self.update_connections()
        self.nodes_changed.emit()

    def redraw_all_nodes(self):
        """Redraw all nodes."""
        # Clear existing items
        for item in list(self.node_items.values()):
            # Remove handles first
            for handle in item.option_handles:
                if handle.scene():
                    handle.scene().removeItem(handle)
            # Remove main item
            if item.scene():
                self.scene.removeItem(item)
        self.node_items.clear()
        
        # Clear connections
        self.clear_connections()
        
        # Recreate node items
        for node in self.app.nodes.values():
            self.create_node_item(node)
        
        # Update connections
        self.update_connections()
        self.update_selection_visuals()

    def update_selection_visuals(self):
        """Update the visual selection state of nodes."""
        for node_id, item in self.node_items.items():
            item.setSelected(node_id in self.app.selected_node_ids)

    def start_connection(self, source_node_id, option_index):
        """Start creating a connection from a node option."""
        self.is_connecting = True
        self.connection_start = (source_node_id, option_index)
        
        # Create temporary connection line
        source_node = self.app.nodes[source_node_id]
        start_pos = self._get_option_connection_point(source_node, option_index)
        
        self.temp_connection = ConnectionLine(start_pos, start_pos, QColor("#007ACC"))
        self.temp_connection.setOpacity(0.7)
        self.scene.addItem(self.temp_connection)
        
        # Set cursor
        self.view.setCursor(Qt.CrossCursor)

    def _get_option_connection_point(self, node, option_index):
        """Get the connection point for a node option."""
        body_height = max(NODE_BASE_BODY_HEIGHT, node.calculated_text_height + 20)
        y_offset = NODE_HEADER_HEIGHT + body_height + (option_index * OPTION_LINE_HEIGHT) + (OPTION_LINE_HEIGHT / 2)
        return QPointF(node.x + NODE_WIDTH, node.y + y_offset)

    def _get_node_input_point(self, node):
        """Get the input connection point for a node."""
        return QPointF(node.x, node.y + NODE_HEADER_HEIGHT // 2)

    def finish_connection(self, target_node_id):
        """Finish creating a connection to a target node."""
        if not self.is_connecting or not self.connection_start:
            return
        
        source_node_id, option_index = self.connection_start
        
        # Update the option's next node
        if source_node_id in self.app.nodes:
            source_node = self.app.nodes[source_node_id]
            if option_index < len(source_node.options):
                self.app._save_state_for_undo("Create Connection")
                source_node.options[option_index]['nextNode'] = target_node_id
        
        self._end_connection()
        self.update_connections()

    def _end_connection(self):
        """End the connection process."""
        self.is_connecting = False
        self.connection_start = None
        
        if self.temp_connection:
            self.scene.removeItem(self.temp_connection)
            self.temp_connection = None
        
        self.view.setCursor(Qt.ArrowCursor)

    def clear_connections(self):
        """Clear all connection lines."""
        for item in list(self.connection_items):
            if item.scene():
                self.scene.removeItem(item)
        self.connection_items.clear()

    def update_connections(self):
        """Update all connection lines."""
        self.clear_connections()
        
        for node in self.app.nodes.values():
            if isinstance(node, DiceRollNode):
                # Handle dice roll connections
                if node.success_node and node.success_node in self.app.nodes:
                    target_node = self.app.nodes[node.success_node]
                    start_pos = self._get_option_connection_point(node, 0)
                    end_pos = self._get_node_input_point(target_node)
                    
                    connection = ConnectionLine(start_pos, end_pos, QColor("#90EE90"))
                    self.scene.addItem(connection)
                    self.connection_items.append(connection)
                
                if node.failure_node and node.failure_node in self.app.nodes:
                    target_node = self.app.nodes[node.failure_node]
                    start_pos = self._get_option_connection_point(node, 1)
                    end_pos = self._get_node_input_point(target_node)
                    
                    connection = ConnectionLine(start_pos, end_pos, QColor("#F08080"))
                    self.scene.addItem(connection)
                    self.connection_items.append(connection)
            else:
                # Handle regular dialogue connections
                for i, option in enumerate(node.options):
                    target_id = option.get("nextNode")
                    if target_id and target_id in self.app.nodes:
                        target_node = self.app.nodes[target_id]
                        start_pos = self._get_option_connection_point(node, i)
                        end_pos = self._get_node_input_point(target_node)
                        
                        connection = ConnectionLine(start_pos, end_pos, QColor("#007ACC"))
                        self.scene.addItem(connection)
                        self.connection_items.append(connection)

    def _on_selection_changed(self):
        """Handle scene selection changes."""
        selected_items = self.scene.selectedItems()
        selected_node_ids = []
        
        for item in selected_items:
            if isinstance(item, NodeGraphicsItem):
                selected_node_ids.append(item.node.id)
        
        self.node_selected.emit(selected_node_ids)

    def pan_to_node(self, node_id):
        """Pan the view to center on a specific node."""
        if node_id in self.node_items:
            item = self.node_items[node_id]
            self.view.centerOn(item)
            
            # Select the node
            self.app.set_selection([node_id], node_id)