# dvge/ui/panels/simple_media_panel.py

"""Simple, reliable media panel for DVGE."""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ...core.application import DVGApp


class SimpleMediaPanel(ctk.CTkFrame):
    """Simple, reliable media panel that definitely works."""

    def __init__(self, parent, app_ref=None, on_change_callback=None):
        super().__init__(parent)
        self.app_ref = app_ref
        self.on_change_callback = on_change_callback
        self.current_node = None
        
        # Always create UI - no complex checking
        self.create_ui()

    def create_ui(self):
        """Create the UI - guaranteed to work."""
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Media & Assets",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Status info
        status_label = ctk.CTkLabel(
            self,
            text="Configure media assets for this node",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        status_label.pack(pady=(0, 20))

        # Background Image Section
        bg_frame = ctk.CTkFrame(self)
        bg_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            bg_frame,
            text="Background Image",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.bg_var = ctk.StringVar()
        self.bg_entry = ctk.CTkEntry(
            bg_frame,
            textvariable=self.bg_var,
            placeholder_text="Select background image file..."
        )
        self.bg_entry.pack(fill="x", padx=10, pady=5)
        
        bg_button_frame = ctk.CTkFrame(bg_frame)
        bg_button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            bg_button_frame,
            text="Browse Image",
            command=self._browse_background,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            bg_button_frame,
            text="Clear",
            command=self._clear_background,
            width=80,
            fg_color="gray"
        ).pack(side="left", padx=5)

        # Audio Section
        audio_frame = ctk.CTkFrame(self)
        audio_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            audio_frame,
            text="Audio/Sound Effect",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.audio_var = ctk.StringVar()
        self.audio_entry = ctk.CTkEntry(
            audio_frame,
            textvariable=self.audio_var,
            placeholder_text="Select audio file..."
        )
        self.audio_entry.pack(fill="x", padx=10, pady=5)
        
        audio_button_frame = ctk.CTkFrame(audio_frame)
        audio_button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            audio_button_frame,
            text="Browse Audio",
            command=self._browse_audio,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            audio_button_frame,
            text="Clear",
            command=self._clear_audio,
            width=80,
            fg_color="gray"
        ).pack(side="left", padx=5)

        # Background Music Section
        music_frame = ctk.CTkFrame(self)
        music_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            music_frame,
            text="Background Music",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.music_var = ctk.StringVar()
        self.music_entry = ctk.CTkEntry(
            music_frame,
            textvariable=self.music_var,
            placeholder_text="Select background music file..."
        )
        self.music_entry.pack(fill="x", padx=10, pady=5)
        
        music_button_frame = ctk.CTkFrame(music_frame)
        music_button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            music_button_frame,
            text="Browse Music",
            command=self._browse_music,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            music_button_frame,
            text="Clear",
            command=self._clear_music,
            width=80,
            fg_color="gray"
        ).pack(side="left", padx=5)

        # Preview section
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            preview_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        action_buttons = ctk.CTkFrame(preview_frame)
        action_buttons.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            action_buttons,
            text="Test in Preview",
            command=self._test_preview,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_buttons,
            text="Advanced Media",
            command=self._open_advanced_media,
            width=120,
            fg_color="#1f538d"
        ).pack(side="right", padx=5)

        # Current node info
        self.node_info_label = ctk.CTkLabel(
            self,
            text="Select a node to configure its media",
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        )
        self.node_info_label.pack(pady=20)

    def _browse_background(self):
        """Browse for background image."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=filetypes
        )
        
        if filepath:
            self.bg_var.set(filepath)
            self._update_node_property('backgroundImage', filepath)

    def _browse_audio(self):
        """Browse for audio file."""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.ogg *.m4a *.aac"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=filetypes
        )
        
        if filepath:
            self.audio_var.set(filepath)
            self._update_node_property('audio', filepath)

    def _browse_music(self):
        """Browse for music file."""
        filetypes = [
            ("Music files", "*.mp3 *.wav *.ogg *.m4a *.aac"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select Background Music",
            filetypes=filetypes
        )
        
        if filepath:
            self.music_var.set(filepath)
            self._update_node_property('music', filepath)

    def _clear_background(self):
        """Clear background image."""
        self.bg_var.set("")
        self._update_node_property('backgroundImage', "")

    def _clear_audio(self):
        """Clear audio."""
        self.audio_var.set("")
        self._update_node_property('audio', "")

    def _clear_music(self):
        """Clear music."""
        self.music_var.set("")
        self._update_node_property('music', "")

    def _update_node_property(self, property_name: str, value: str):
        """Update node property and trigger callback."""
        if self.current_node:
            setattr(self.current_node, property_name, value)
            if self.on_change_callback:
                self.on_change_callback()

    def _test_preview(self):
        """Test media in preview."""
        if not self.current_node:
            messagebox.showinfo("No Node", "Please select a node first")
            return
        
        # Check if preview is available
        if hasattr(self.app_ref, 'preview_toolbar'):
            try:
                self.app_ref.preview_toolbar.preview_controls._open_preview()
                messagebox.showinfo("Preview", "Opening preview window to test media...")
            except:
                messagebox.showinfo("Preview", "Preview window not available")
        else:
            messagebox.showinfo("Preview", "Preview functionality not available")

    def _open_advanced_media(self):
        """Open advanced media editor (future feature)."""
        messagebox.showinfo(
            "Advanced Media", 
            "Advanced media features coming soon!\n\n" +
            "This will include:\n" +
            "- Video support\n" +
            "- Animation & effects\n" +
            "- Timeline editor\n" +
            "- Multi-layer media\n\n" +
            "For now, use the basic image/audio controls above."
        )

    def load_node(self, node):
        """Load node data into the panel."""
        self.current_node = node
        
        if node:
            # Load current values
            self.bg_var.set(getattr(node, 'backgroundImage', ''))
            self.audio_var.set(getattr(node, 'audio', ''))
            self.music_var.set(getattr(node, 'music', ''))
            
            # Update info label
            self.node_info_label.configure(
                text=f"Configuring media for: {node.id}"
            )
        else:
            # Clear values
            self.bg_var.set('')
            self.audio_var.set('')
            self.music_var.set('')
            self.node_info_label.configure(
                text="Select a node to configure its media"
            )

    def clear(self):
        """Clear the panel."""
        self.load_node(None)

    def set_media_library(self, media_library):
        """Set media library (for compatibility)."""
        pass  # Not needed for simple version