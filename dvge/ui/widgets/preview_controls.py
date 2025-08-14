# dvge/ui/widgets/preview_controls.py

"""Preview control widgets for the main interface."""

import customtkinter as ctk
from ...constants import *


class PreviewControlWidget(ctk.CTkFrame):
    """Widget containing preview controls for the main interface."""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.preview_window = None
        
        self._setup_controls()
        
    def _setup_controls(self):
        """Sets up the preview control buttons."""
        # Preview button
        self.preview_btn = ctk.CTkButton(
            self, text="▶️ Live Preview", 
            command=self._open_preview,
            fg_color=COLOR_SUCCESS,
            hover_color="#27AE60",
            font=FONT_PROPERTIES_LABEL
        )
        self.preview_btn.pack(side="left", padx=(0,10))
        
        # Quick test button
        self.quick_test_btn = ctk.CTkButton(
            self, text="🚀 Quick Test", 
            command=self._quick_test,
            font=FONT_PROPERTIES_ENTRY
        )
        self.quick_test_btn.pack(side="left", padx=(0,5))
        
        # Validation button
        self.validate_btn = ctk.CTkButton(
            self, text="✓ Validate", 
            command=self._validate_project,
            font=FONT_PROPERTIES_ENTRY,
            width=80
        )
        self.validate_btn.pack(side="left")
        
    def _open_preview(self):
        """Opens the live preview window."""
        # Check if project has intro node
        if "intro" not in self.app.nodes:
            from ...core.utils import show_warning
            show_warning("Preview Error", "No 'intro' node found! Please create an intro node first.")
            return
            
        # Close existing preview window if open
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
            
        # Create new preview window
        try:
            # Try to use enhanced preview window first
            from ..windows.preview_window import EnhancedPreviewWindow
            self.preview_window = EnhancedPreviewWindow(self.app)
        except ImportError:
            # Fallback to regular preview window
            from ..windows.preview_window import PreviewWindow
            self.preview_window = PreviewWindow(self.app)
        
    def _quick_test(self):
        """Performs a quick test from the current selected node."""
        if not self.app.active_node_id:
            from ...core.utils import show_warning
            show_warning("Quick Test", "Please select a node to test from.")
            return
            
        # Close existing preview window if open
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
            
        # Create preview window starting from selected node
        try:
            # Try to use enhanced preview window first
            from ..windows.preview_window import EnhancedPreviewWindow
            self.preview_window = EnhancedPreviewWindow(self.app)
            self.preview_window.preview_engine.start_game(self.app.active_node_id)
        except ImportError:
            # Fallback to regular preview window
            from ..windows.preview_window import PreviewWindow
            self.preview_window = PreviewWindow(self.app)
            self.preview_window.preview_engine.start_game(self.app.active_node_id)
        
    def _validate_project(self):
        """Validates the current project."""
        errors, warnings = self.app.validate_project()
        
        if not errors and not warnings:
            from ...core.utils import show_info
            show_info("Validation", "✅ Project validation passed! No issues found.")
        else:
            message = "Project validation results:\n\n"
            if errors:
                message += "❌ ERRORS:\n" + "\n".join(f"• {error}" for error in errors) + "\n\n"
            if warnings:
                message += "⚠️ WARNINGS:\n" + "\n".join(f"• {warning}" for warning in warnings)
            
            from ...core.utils import show_warning
            show_warning("Validation Results", message)


class PreviewToolbar(ctk.CTkFrame):
    """Toolbar containing preview and testing tools."""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_PRIMARY_FRAME, height=60)
        self.app = app
        
        self.grid_columnconfigure(1, weight=1)
        
        self._setup_toolbar()
        
    def _setup_toolbar(self):
        """Sets up the preview toolbar."""
        # Left side - Preview controls
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        
        self.preview_controls = PreviewControlWidget(left_frame, self.app)
        self.preview_controls.pack(side="left")
        
        # Center - Project status
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=0, column=1, padx=15, pady=10)
        
        self.status_label = ctk.CTkLabel(
            status_frame, text="Ready to preview", 
            font=FONT_PROPERTIES_ENTRY,
            text_color=COLOR_TEXT_MUTED
        )
        self.status_label.pack()
        
        # Right side - Node info
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=0, column=2, sticky="e", padx=15, pady=10)
        
        self.node_info_label = ctk.CTkLabel(
            right_frame, text="No node selected", 
            font=FONT_PROPERTIES_ENTRY
        )
        self.node_info_label.pack()
        
    def update_status(self, message, color=None):
        """Updates the status message."""
        self.status_label.configure(text=message)
        if color:
            self.status_label.configure(text_color=color)
            
    def update_node_info(self, node_id=None):
        """Updates the node information display."""
        if node_id and node_id in self.app.nodes:
            node = self.app.nodes[node_id]
            node_type = type(node).__name__.replace("Node", "")
            info_text = f"Selected: {node_id} ({node_type})"
            self.node_info_label.configure(text=info_text)
        else:
            self.node_info_label.configure(text="No node selected")