# dvge/ui/pyside_wrapper.py

"""
PySide6 wrapper for enhanced UI/UX while maintaining existing code structure.
This provides a modern, native-looking interface without changing the core engine.
"""

import sys
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QTextEdit, QTreeWidget, QTreeWidgetItem,
    QLabel, QPushButton, QMenuBar, QToolBar, QStatusBar, QScrollArea,
    QFrame, QGroupBox, QComboBox, QSpinBox, QCheckBox, QLineEdit,
    QSlider, QProgressBar, QListWidget, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QAction, QIcon, QFont, QPalette, QColor, QPainter


class ModernCanvasWidget(QWidget):
    """Modern OpenGL-accelerated canvas widget for better performance."""
    
    node_clicked = Signal(str)
    canvas_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.nodes = {}
        self.connections = []
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.selected_node = None
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
    def add_node(self, node_id: str, x: float, y: float, node_data: Dict[str, Any]):
        """Add a node to the canvas."""
        self.nodes[node_id] = {
            'x': x,
            'y': y,
            'data': node_data,
            'selected': False
        }
        self.update()
        
    def remove_node(self, node_id: str):
        """Remove a node from the canvas."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.update()
            
    def select_node(self, node_id: str):
        """Select a node."""
        # Deselect all nodes
        for node in self.nodes.values():
            node['selected'] = False
            
        # Select the specified node
        if node_id in self.nodes:
            self.nodes[node_id]['selected'] = True
            self.selected_node = node_id
            self.node_clicked.emit(node_id)
            
        self.update()
        
    def paintEvent(self, event):
        """Paint the canvas."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Clear background
        painter.fillRect(self.rect(), QColor(45, 45, 45))
        
        # Draw grid
        self._draw_grid(painter)
        
        # Draw connections
        self._draw_connections(painter)
        
        # Draw nodes
        self._draw_nodes(painter)
        
    def _draw_grid(self, painter: QPainter):
        """Draw grid lines."""
        painter.setPen(QColor(70, 70, 70))
        
        grid_size = 50 * self.zoom_level
        width = self.width()
        height = self.height()
        
        # Vertical lines
        x = self.pan_x % grid_size
        while x < width:
            painter.drawLine(int(x), 0, int(x), height)
            x += grid_size
            
        # Horizontal lines
        y = self.pan_y % grid_size
        while y < height:
            painter.drawLine(0, int(y), width, int(y))
            y += grid_size
            
    def _draw_nodes(self, painter: QPainter):
        """Draw all nodes."""
        for node_id, node in self.nodes.items():
            x = node['x'] * self.zoom_level + self.pan_x
            y = node['y'] * self.zoom_level + self.pan_y
            
            # Node rectangle
            node_width = 200 * self.zoom_level
            node_height = 100 * self.zoom_level
            
            # Draw shadow
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, 100))
            painter.drawRoundedRect(x + 3, y + 3, node_width, node_height, 10, 10)
            
            # Draw main node
            if node['selected']:
                painter.setBrush(QColor(100, 150, 250))
            else:
                painter.setBrush(QColor(80, 80, 90))
            painter.setPen(QColor(150, 150, 150))
            painter.drawRoundedRect(x, y, node_width, node_height, 10, 10)
            
            # Draw text
            painter.setPen(QColor(255, 255, 255))
            font = QFont("Arial", max(10, int(12 * self.zoom_level)))
            painter.setFont(font)
            
            title = node['data'].get('title', f'Node {node_id}')
            painter.drawText(x + 10, y + 20, node_width - 20, 30, Qt.AlignLeft, title)
            
    def _draw_connections(self, painter: QPainter):
        """Draw connections between nodes."""
        painter.setPen(QColor(150, 150, 150, 200))
        for connection in self.connections:
            start_node = self.nodes.get(connection['from'])
            end_node = self.nodes.get(connection['to'])
            
            if start_node and end_node:
                start_x = start_node['x'] * self.zoom_level + self.pan_x + 100
                start_y = start_node['y'] * self.zoom_level + self.pan_y + 50
                end_x = end_node['x'] * self.zoom_level + self.pan_x + 100
                end_y = end_node['y'] * self.zoom_level + self.pan_y + 50
                
                painter.drawLine(start_x, start_y, end_x, end_y)
                
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            # Check if clicking on a node
            for node_id, node in self.nodes.items():
                x = node['x'] * self.zoom_level + self.pan_x
                y = node['y'] * self.zoom_level + self.pan_y
                width = 200 * self.zoom_level
                height = 100 * self.zoom_level
                
                if (x <= event.x() <= x + width and 
                    y <= event.y() <= y + height):
                    self.select_node(node_id)
                    break
                    
        super().mousePressEvent(event)
        
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
        self.zoom_level = max(0.1, min(3.0, self.zoom_level * zoom_factor))
        self.update()


class ModernPropertiesPanel(QWidget):
    """Modern properties panel with enhanced UI."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the properties panel UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Inspector")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #FFFFFF;
                padding: 10px;
                background-color: #3C3C3C;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2B2B2B;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #FFFFFF;
                padding: 8px 12px;
                margin: 2px;
                border-radius: 3px;
            }
            QTabBar::tab:selected {
                background-color: #0078D4;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
        """)
        
        # Add tabs
        self.setup_node_tab()
        self.setup_advanced_tab()
        self.setup_features_tab()
        self.setup_project_tab()
        
        layout.addWidget(self.tab_widget)
        
    def setup_node_tab(self):
        """Setup the node properties tab."""
        node_widget = QWidget()
        layout = QVBoxLayout(node_widget)
        
        # Node ID
        id_group = QGroupBox("Node Information")
        id_layout = QVBoxLayout(id_group)
        
        self.node_id_label = QLabel("No node selected")
        self.node_id_label.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        id_layout.addWidget(self.node_id_label)
        
        layout.addWidget(id_group)
        
        # Node title
        title_group = QGroupBox("Title")
        title_layout = QVBoxLayout(title_group)
        
        self.title_edit = QLineEdit()
        self.title_edit.setStyleSheet("""
            QLineEdit {
                background-color: #404040;
                color: #FFFFFF;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        title_layout.addWidget(self.title_edit)
        
        layout.addWidget(title_group)
        
        # Node content
        content_group = QGroupBox("Content")
        content_layout = QVBoxLayout(content_group)
        
        self.content_edit = QTextEdit()
        self.content_edit.setStyleSheet("""
            QTextEdit {
                background-color: #404040;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 3px;
            }
        """)
        content_layout.addWidget(self.content_edit)
        
        layout.addWidget(content_group)
        
        # Apply dark theme to group boxes
        for group in [id_group, title_group, content_group]:
            group.setStyleSheet("""
                QGroupBox {
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    margin: 5px;
                    padding-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
        
        self.tab_widget.addTab(node_widget, "Node")
        
    def setup_advanced_tab(self):
        """Setup the advanced properties tab."""
        advanced_widget = QWidget()
        layout = QVBoxLayout(advanced_widget)
        
        # Node type selector
        type_group = QGroupBox("Node Type")
        type_layout = QVBoxLayout(type_group)
        
        self.node_type_combo = QComboBox()
        self.node_type_combo.addItems([
            "Standard Node",
            "Dice Roll Node", 
            "Combat Node",
            "Shop Node",
            "Timer Node",
            "Random Event Node"
        ])
        self.node_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #404040;
                color: #FFFFFF;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        type_layout.addWidget(self.node_type_combo)
        
        layout.addWidget(type_group)
        
        # Advanced settings
        settings_group = QGroupBox("Advanced Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Timer settings
        timer_frame = QFrame()
        timer_layout = QHBoxLayout(timer_frame)
        timer_layout.addWidget(QLabel("Timer Duration:"))
        
        self.timer_spin = QSpinBox()
        self.timer_spin.setRange(1, 300)
        self.timer_spin.setValue(30)
        self.timer_spin.setStyleSheet("""
            QSpinBox {
                background-color: #404040;
                color: #FFFFFF;
                border: 1px solid #555555;
                padding: 3px;
                border-radius: 3px;
            }
        """)
        timer_layout.addWidget(self.timer_spin)
        timer_layout.addWidget(QLabel("seconds"))
        
        settings_layout.addWidget(timer_frame)
        
        # Auto-advance checkbox
        self.auto_advance_check = QCheckBox("Auto-advance")
        self.auto_advance_check.setStyleSheet("color: #FFFFFF;")
        settings_layout.addWidget(self.auto_advance_check)
        
        layout.addWidget(settings_group)
        
        # Apply styling to group boxes
        for group in [type_group, settings_group]:
            group.setStyleSheet("""
                QGroupBox {
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    margin: 5px;
                    padding-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
        
        self.tab_widget.addTab(advanced_widget, "Advanced")
        
    def setup_features_tab(self):
        """Setup the features tab."""
        features_widget = QWidget()
        layout = QVBoxLayout(features_widget)
        
        # Feature selector
        feature_group = QGroupBox("Feature Type")
        feature_layout = QVBoxLayout(feature_group)
        
        self.feature_combo = QComboBox()
        self.feature_combo.addItems([
            "Skill Checks",
            "Loot Tables", 
            "Reputation System",
            "Puzzles",
            "Minigames"
        ])
        self.feature_combo.setStyleSheet("""
            QComboBox {
                background-color: #404040;
                color: #FFFFFF;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        feature_layout.addWidget(self.feature_combo)
        
        layout.addWidget(feature_group)
        
        # Feature content area
        self.feature_content = QScrollArea()
        self.feature_content.setStyleSheet("""
            QScrollArea {
                background-color: #2B2B2B;
                border: 1px solid #555555;
                border-radius: 5px;
            }
        """)
        
        # Default content
        default_content = QLabel("Select a feature type to configure advanced properties")
        default_content.setAlignment(Qt.AlignCenter)
        default_content.setStyleSheet("color: #888888; font-size: 14px;")
        self.feature_content.setWidget(default_content)
        
        layout.addWidget(self.feature_content)
        
        # Apply styling
        feature_group.setStyleSheet("""
            QGroupBox {
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        self.tab_widget.addTab(features_widget, "Features")
        
    def setup_project_tab(self):
        """Setup the project tab."""
        project_widget = QWidget()
        layout = QVBoxLayout(project_widget)
        
        # Project info
        info_group = QGroupBox("Project Information")
        info_layout = QVBoxLayout(info_group)
        
        self.project_name_label = QLabel("Project Name: New Project")
        self.project_name_label.setStyleSheet("color: #CCCCCC;")
        info_layout.addWidget(self.project_name_label)
        
        self.project_path_label = QLabel("Path: Not saved")
        self.project_path_label.setStyleSheet("color: #CCCCCC;")
        info_layout.addWidget(self.project_path_label)
        
        layout.addWidget(info_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.node_count_label = QLabel("Nodes: 0")
        self.node_count_label.setStyleSheet("color: #CCCCCC;")
        stats_layout.addWidget(self.node_count_label)
        
        self.connection_count_label = QLabel("Connections: 0")
        self.connection_count_label.setStyleSheet("color: #CCCCCC;")
        stats_layout.addWidget(self.connection_count_label)
        
        layout.addWidget(stats_group)
        
        # Apply styling
        for group in [info_group, stats_group]:
            group.setStyleSheet("""
                QGroupBox {
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    margin: 5px;
                    padding-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
        
        self.tab_widget.addTab(project_widget, "Project")


class ModernDVGEMainWindow(QMainWindow):
    """Modern main window for DVGE with enhanced UI/UX."""
    
    def __init__(self, original_app, parent=None):
        super().__init__(parent)
        self.original_app = original_app
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the main window UI."""
        self.setWindowTitle("Dialogue Venture Game Engine - Enhanced")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
        """)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Canvas area
        self.canvas_widget = ModernCanvasWidget()
        splitter.addWidget(self.canvas_widget)
        
        # Properties panel
        self.properties_panel = ModernPropertiesPanel()
        self.properties_panel.setMinimumWidth(350)
        self.properties_panel.setMaximumWidth(450)
        splitter.addWidget(self.properties_panel)
        
        # Set splitter sizes
        splitter.setSizes([1000, 400])
        
        main_layout.addWidget(splitter)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #3C3C3C;
                color: #FFFFFF;
                border-bottom: 1px solid #555555;
            }
            QMenuBar::item {
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #0078D4;
            }
        """)
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Project", self)
        open_action.setShortcut("Ctrl+O") 
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("Export to HTML", self)
        export_action.triggered.connect(self.export_html)
        file_menu.addAction(export_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        view_menu.addAction(zoom_out_action)
        
        fit_action = QAction("Fit to Window", self)
        fit_action.setShortcut("Ctrl+0")
        view_menu.addAction(fit_action)
        
    def create_toolbar(self):
        """Create the toolbar."""
        toolbar = self.addToolBar("Main")
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #404040;
                border: none;
                spacing: 3px;
            }
            QToolButton {
                background-color: #505050;
                color: #FFFFFF;
                border: 1px solid #606060;
                padding: 5px;
                border-radius: 3px;
                min-width: 60px;
            }
            QToolButton:hover {
                background-color: #606060;
            }
            QToolButton:pressed {
                background-color: #0078D4;
            }
        """)
        
        # Add actions to toolbar
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        preview_action = QAction("Preview", self)
        preview_action.triggered.connect(self.preview_game)
        toolbar.addAction(preview_action)
        
        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_html)
        toolbar.addAction(export_action)
        
    def setup_connections(self):
        """Setup signal connections."""
        self.canvas_widget.node_clicked.connect(self.on_node_selected)
        
    def on_node_selected(self, node_id: str):
        """Handle node selection."""
        self.properties_panel.node_id_label.setText(f"Selected: {node_id}")
        self.status_bar.showMessage(f"Selected node: {node_id}")
        
    def new_project(self):
        """Create a new project."""
        if hasattr(self.original_app, 'project_handler'):
            self.original_app.project_handler.new_project()
        self.status_bar.showMessage("New project created")
        
    def open_project(self):
        """Open a project."""
        if hasattr(self.original_app, 'project_handler'):
            self.original_app.project_handler.load_project()
        self.status_bar.showMessage("Project opened")
        
    def save_project(self):
        """Save the current project."""
        if hasattr(self.original_app, 'project_handler'):
            self.original_app.project_handler.save_project()
        self.status_bar.showMessage("Project saved")
        
    def export_html(self):
        """Export to HTML."""
        if hasattr(self.original_app, 'html_exporter'):
            self.original_app.html_exporter.export_to_html()
        self.status_bar.showMessage("Exported to HTML")
        
    def preview_game(self):
        """Preview the game."""
        self.status_bar.showMessage("Opening game preview...")
        # This would trigger the original preview system
        
    def sync_with_original_app(self):
        """Sync the PySide UI with the original CustomTkinter app."""
        # Clear canvas
        self.canvas_widget.nodes.clear()
        
        # Add nodes from original app
        if hasattr(self.original_app, 'nodes'):
            for node_id, node in self.original_app.nodes.items():
                self.canvas_widget.add_node(
                    node_id,
                    getattr(node, 'x', 100),
                    getattr(node, 'y', 100),
                    {
                        'title': getattr(node, 'title', ''),
                        'content': getattr(node, 'content', ''),
                        'type': type(node).__name__
                    }
                )
                
        # Update project info
        if hasattr(self.original_app, 'project_name'):
            self.properties_panel.project_name_label.setText(f"Project Name: {self.original_app.project_name}")
            
        if hasattr(self.original_app, 'project_file_path'):
            path = self.original_app.project_file_path or "Not saved"
            self.properties_panel.project_path_label.setText(f"Path: {path}")
            
        # Update statistics
        node_count = len(getattr(self.original_app, 'nodes', {}))
        self.properties_panel.node_count_label.setText(f"Nodes: {node_count}")
        
        self.canvas_widget.update()


class PySideWrapper:
    """Wrapper class to integrate PySide6 UI with existing DVGE engine."""
    
    def __init__(self, original_app):
        self.original_app = original_app
        self.pyside_app = None
        self.main_window = None
        
    def create_modern_ui(self):
        """Create and show the modern PySide6 UI."""
        if not QApplication.instance():
            self.pyside_app = QApplication(sys.argv)
        else:
            self.pyside_app = QApplication.instance()
            
        # Apply dark theme
        self.pyside_app.setStyle('Fusion')
        
        # Create main window
        self.main_window = ModernDVGEMainWindow(self.original_app)
        
        # Sync with original app
        self.main_window.sync_with_original_app()
        
        # Show window
        self.main_window.show()
        
        return self.main_window
        
    def run(self):
        """Run the PySide application."""
        if self.pyside_app and self.main_window:
            return self.pyside_app.exec()
        return 0