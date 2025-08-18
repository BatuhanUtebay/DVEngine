# dvge/ui/windows/media_window.py

"""Standalone Media Manager Window for DVGE."""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ...core.application import DVGApp


class MediaWindow(ctk.CTkToplevel):
    """Standalone media manager window."""

    def __init__(self, parent, app_ref=None):
        super().__init__(parent)
        
        self.app_ref = app_ref
        self.current_node = None
        
        # Window setup
        self.title("Media Manager - DVGE")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()  # Make it modal
        
        # Load current node
        if app_ref and hasattr(app_ref, 'active_node_id') and app_ref.active_node_id:
            self.current_node = app_ref.nodes.get(app_ref.active_node_id)
        
        self.create_ui()
        
        # Load data if we have a current node
        if self.current_node:
            self.load_node_data()

    def create_ui(self):
        """Create the media window UI."""
        
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Media Manager",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # Close button
        close_button = ctk.CTkButton(
            header_frame,
            text="Close",
            command=self.destroy,
            width=100,
            fg_color="gray"
        )
        close_button.pack(side="right", padx=20, pady=15)
        
        # Node info
        self.node_info_frame = ctk.CTkFrame(self)
        self.node_info_frame.pack(fill="x", padx=20, pady=10)
        
        self.node_info_label = ctk.CTkLabel(
            self.node_info_frame,
            text="No node selected",
            font=ctk.CTkFont(size=14)
        )
        self.node_info_label.pack(pady=15)
        
        # Main content
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create two columns
        left_column = ctk.CTkFrame(content_frame)
        left_column.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        right_column = ctk.CTkFrame(content_frame)
        right_column.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        # Left column - Background Image
        self.create_background_section(left_column)
        
        # Left column - Audio
        self.create_audio_section(left_column)
        
        # Right column - Music
        self.create_music_section(right_column)
        
        # Right column - Preview and Actions
        self.create_actions_section(right_column)
        
        # Bottom buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        ctk.CTkButton(
            button_frame,
            text="Apply Changes",
            command=self.apply_changes,
            width=150,
            fg_color="#2E8B57",
            hover_color="#228B22"
        ).pack(side="left", padx=20, pady=15)
        
        ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            command=self.reset_to_defaults,
            width=150,
            fg_color="#CD853F",
            hover_color="#D2691E"
        ).pack(side="right", padx=20, pady=15)

    def create_background_section(self, parent):
        """Create background image section."""
        bg_frame = ctk.CTkFrame(parent)
        bg_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            bg_frame,
            text="Background Image",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        self.bg_var = ctk.StringVar()
        self.bg_entry = ctk.CTkEntry(
            bg_frame,
            textvariable=self.bg_var,
            placeholder_text="No background image selected",
            width=300
        )
        self.bg_entry.pack(pady=5, padx=15)
        
        bg_buttons = ctk.CTkFrame(bg_frame)
        bg_buttons.pack(pady=15, padx=15)
        
        ctk.CTkButton(
            bg_buttons,
            text="Browse Image",
            command=self.browse_background,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            bg_buttons,
            text="Clear",
            command=self.clear_background,
            width=80,
            fg_color="gray"
        ).pack(side="left", padx=5)
        
        # Preview area for background
        self.bg_preview_frame = ctk.CTkFrame(bg_frame)
        self.bg_preview_frame.pack(fill="x", pady=10, padx=15)
        
        self.bg_preview_label = ctk.CTkLabel(
            self.bg_preview_frame,
            text="Background preview will appear here",
            height=80,
            text_color="#666666"
        )
        self.bg_preview_label.pack(pady=20)

    def create_audio_section(self, parent):
        """Create audio section."""
        audio_frame = ctk.CTkFrame(parent)
        audio_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            audio_frame,
            text="Sound Effect",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        self.audio_var = ctk.StringVar()
        self.audio_entry = ctk.CTkEntry(
            audio_frame,
            textvariable=self.audio_var,
            placeholder_text="No audio file selected",
            width=300
        )
        self.audio_entry.pack(pady=5, padx=15)
        
        audio_buttons = ctk.CTkFrame(audio_frame)
        audio_buttons.pack(pady=15, padx=15)
        
        ctk.CTkButton(
            audio_buttons,
            text="Browse Audio",
            command=self.browse_audio,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            audio_buttons,
            text="Clear",
            command=self.clear_audio,
            width=80,
            fg_color="gray"
        ).pack(side="left", padx=5)

    def create_music_section(self, parent):
        """Create music section."""
        music_frame = ctk.CTkFrame(parent)
        music_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            music_frame,
            text="Background Music",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        self.music_var = ctk.StringVar()
        self.music_entry = ctk.CTkEntry(
            music_frame,
            textvariable=self.music_var,
            placeholder_text="No music file selected",
            width=300
        )
        self.music_entry.pack(pady=5, padx=15)
        
        music_buttons = ctk.CTkFrame(music_frame)
        music_buttons.pack(pady=15, padx=15)
        
        ctk.CTkButton(
            music_buttons,
            text="Browse Music",
            command=self.browse_music,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            music_buttons,
            text="Clear",
            command=self.clear_music,
            width=80,
            fg_color="gray"
        ).pack(side="left", padx=5)

    def create_actions_section(self, parent):
        """Create actions and preview section."""
        actions_frame = ctk.CTkFrame(parent)
        actions_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        ctk.CTkButton(
            actions_frame,
            text="Test in Preview",
            command=self.test_in_preview,
            width=200
        ).pack(pady=10)
        
        ctk.CTkButton(
            actions_frame,
            text="Open File Location",
            command=self.open_file_location,
            width=200
        ).pack(pady=5)
        
        # Info section
        info_frame = ctk.CTkFrame(actions_frame)
        info_frame.pack(fill="x", pady=15, padx=10)
        
        ctk.CTkLabel(
            info_frame,
            text="Supported Formats:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            info_frame,
            text="Images: PNG, JPG, GIF, WebP\nAudio: MP3, WAV, OGG, M4A",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        ).pack(pady=(0, 10))

    def browse_background(self):
        """Browse for background image."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=filetypes,
            parent=self
        )
        
        if filepath:
            self.bg_var.set(filepath)
            self.update_preview()

    def browse_audio(self):
        """Browse for audio file."""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.ogg *.m4a *.aac"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=filetypes,
            parent=self
        )
        
        if filepath:
            self.audio_var.set(filepath)

    def browse_music(self):
        """Browse for music file."""
        filetypes = [
            ("Music files", "*.mp3 *.wav *.ogg *.m4a *.aac"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select Background Music",
            filetypes=filetypes,
            parent=self
        )
        
        if filepath:
            self.music_var.set(filepath)

    def clear_background(self):
        """Clear background image."""
        self.bg_var.set("")
        self.update_preview()

    def clear_audio(self):
        """Clear audio."""
        self.audio_var.set("")

    def clear_music(self):
        """Clear music."""
        self.music_var.set("")

    def update_preview(self):
        """Update the background preview."""
        bg_path = self.bg_var.get()
        
        if bg_path and os.path.exists(bg_path):
            filename = os.path.basename(bg_path)
            self.bg_preview_label.configure(
                text=f"Background: {filename}",
                text_color="#4CAF50"
            )
        else:
            self.bg_preview_label.configure(
                text="Background preview will appear here",
                text_color="#666666"
            )

    def load_node_data(self):
        """Load data from current node."""
        if self.current_node:
            self.node_info_label.configure(
                text=f"Editing media for node: {self.current_node.id}"
            )
            
            # Load existing values
            self.bg_var.set(getattr(self.current_node, 'backgroundImage', ''))
            self.audio_var.set(getattr(self.current_node, 'audio', ''))
            self.music_var.set(getattr(self.current_node, 'music', ''))
            
            self.update_preview()
        else:
            self.node_info_label.configure(text="No node selected")

    def apply_changes(self):
        """Apply changes to the current node."""
        if not self.current_node:
            messagebox.showerror("No Node", "No node selected to apply changes to.")
            return
        
        # Apply changes
        self.current_node.backgroundImage = self.bg_var.get()
        self.current_node.audio = self.audio_var.get()
        self.current_node.music = self.music_var.get()
        
        # Trigger app update
        if self.app_ref and hasattr(self.app_ref, 'state_manager'):
            self.app_ref.state_manager.save_state("Media updated")
        
        if self.app_ref and hasattr(self.app_ref, 'canvas_manager'):
            self.app_ref.canvas_manager.redraw_all_nodes()
        
        messagebox.showinfo("Success", "Media changes applied successfully!")

    def reset_to_defaults(self):
        """Reset all media to defaults."""
        if messagebox.askyesno("Confirm Reset", "Clear all media settings for this node?"):
            self.bg_var.set("")
            self.audio_var.set("")
            self.music_var.set("")
            self.update_preview()

    def test_in_preview(self):
        """Test media in preview."""
        if not self.current_node:
            messagebox.showinfo("No Node", "Please select a node first")
            return
        
        # Apply current changes first
        self.apply_changes()
        
        # Open preview if available
        if self.app_ref and hasattr(self.app_ref, 'preview_toolbar'):
            try:
                self.app_ref.preview_toolbar.preview_controls._open_preview()
                messagebox.showinfo("Preview", "Opening preview window to test media...")
            except:
                messagebox.showinfo("Preview", "Preview window not available")
        else:
            messagebox.showinfo("Preview", "Preview functionality not available")

    def open_file_location(self):
        """Open file location of selected media."""
        paths = [self.bg_var.get(), self.audio_var.get(), self.music_var.get()]
        valid_paths = [p for p in paths if p and os.path.exists(p)]
        
        if valid_paths:
            # Open the directory of the first valid file
            directory = os.path.dirname(valid_paths[0])
            try:
                os.startfile(directory)  # Windows
            except:
                messagebox.showinfo("Info", f"Files located in: {directory}")
        else:
            messagebox.showinfo("No Files", "No media files selected or files not found")