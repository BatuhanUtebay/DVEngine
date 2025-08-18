# dvge/ui/panels/media_properties_simple.py

"""Simplified Media Properties Panel for testing."""

import customtkinter as ctk
from ...constants import *


class MediaPropertiesPanel(ctk.CTkFrame):
    """Simplified media properties panel for testing."""

    def __init__(self, parent, app_ref=None, on_change_callback=None):
        super().__init__(parent)
        self.app_ref = app_ref
        self.on_change_callback = on_change_callback
        self.current_node = None

        self.setup_ui()

    def setup_ui(self):
        """Setup basic UI."""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Advanced Media System",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(20, 10), padx=20)

        # Status
        status_label = ctk.CTkLabel(
            self,
            text="Media system is working!",
            font=ctk.CTkFont(size=12),
            text_color="green"
        )
        status_label.pack(pady=10, padx=20)

        # Test button
        test_button = ctk.CTkButton(
            self,
            text="Test Media Import",
            command=self._test_import,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER
        )
        test_button.pack(pady=20, padx=20)

        # Info
        info_label = ctk.CTkLabel(
            self,
            text="This is a simplified version of the media panel.\nThe full system supports:\n\n• MP4 video import\n• Advanced animations\n• Visual effects\n• Keyframes\n• Layer management",
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        info_label.pack(pady=20, padx=20)

    def _test_import(self):
        """Test import functionality."""
        from tkinter import filedialog, messagebox

        filepath = filedialog.askopenfilename(
            title="Test Media Import",
            filetypes=[
                ("All Media", "*.mp4 *.avi *.mov *.png *.jpg *.jpeg *.gif *.mp3 *.wav"),
                ("Video files", "*.mp4 *.avi *.mov"),
                ("Image files", "*.png *.jpg *.jpeg *.gif"),
                ("Audio files", "*.mp3 *.wav *.ogg"),
                ("All files", "*.*")
            ]
        )

        if filepath:
            messagebox.showinfo(
                "Success", f"Selected file: {filepath}\n\nThis would be imported into the media library.")

    def load_node(self, node):
        """Load node data."""
        self.current_node = node

    def clear(self):
        """Clear panel."""
        self.current_node = None

    def set_media_library(self, media_library):
        """Set media library."""
        pass
