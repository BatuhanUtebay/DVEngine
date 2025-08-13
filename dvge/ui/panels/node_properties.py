# dvge/ui/panels/node_properties.py

"""Node properties tab for editing individual node settings."""

import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import customtkinter as ctk
from ...constants import *


class NodePropertiesTab:
    """Handles the Node tab in the properties panel."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.prop_widgets = {}
        
        self._setup_layout()
        self._create_widgets()

    def _setup_layout(self):
        """Sets up the tab layout."""
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(3, weight=1)

    def _create_widgets(self):
        """Creates all widgets for the node properties tab."""
        self._create_info_section()
        self._create_media_section()
        self._create_auto_advance_section()
        self._create_dialogue_section()
        self._create_save_button()

    def _create_info_section(self):
        """Creates the basic info section."""
        info_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Node ID
        ctk.CTkLabel(
            info_frame, text="Node ID:", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_TEXT_MUTED
        ).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        
        self.prop_widgets["id_var"] = tk.StringVar()
        self.prop_widgets["id_entry"] = ctk.CTkEntry(
            info_frame, textvariable=self.prop_widgets["id_var"], 
            font=FONT_PROPERTIES_ENTRY
        )
        self.prop_widgets["id_entry"].grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        # NPC/Narrator
        ctk.CTkLabel(
            info_frame, text="NPC/Narrator:", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_TEXT_MUTED
        ).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        
        self.prop_widgets["npc_entry"] = ctk.CTkEntry(
            info_frame, font=FONT_PROPERTIES_ENTRY
        )
        self.prop_widgets["npc_entry"].grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        
        # Theme
        ctk.CTkLabel(
            info_frame, text="Theme:", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_TEXT_MUTED
        ).grid(row=2, column=0, padx=5, pady=8, sticky="w")
        
        self.prop_widgets["theme_combo"] = ctk.CTkComboBox(
            info_frame, 
            values=["theme-default", "theme-dream", "theme-ritual"], 
            font=FONT_PROPERTIES_ENTRY
        )
        self.prop_widgets["theme_combo"].grid(row=2, column=1, padx=5, pady=8, sticky="ew")
        
        # Chapter
        ctk.CTkLabel(
            info_frame, text="Chapter Title:", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_TEXT_MUTED
        ).grid(row=3, column=0, padx=5, pady=8, sticky="w")
        
        self.prop_widgets["chapter_entry"] = ctk.CTkEntry(
            info_frame, font=FONT_PROPERTIES_ENTRY
        )
        self.prop_widgets["chapter_entry"].grid(row=3, column=1, padx=5, pady=8, sticky="ew")
        
        # Color button
        ctk.CTkButton(
            info_frame, text="Set Node Color", command=self._set_node_color
        ).grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=8)

    def _create_media_section(self):
        """Creates the media files section."""
        media_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        media_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        media_frame.grid_columnconfigure(0, weight=1)
        
        # Background Image
        ctk.CTkLabel(
            media_frame, text="Background Image:", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_TEXT_MUTED
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5)
        
        self.prop_widgets["bg_image_entry"] = ctk.CTkEntry(
            media_frame, font=FONT_PROPERTIES_ENTRY, 
            placeholder_text="No image selected..."
        )
        self.prop_widgets["bg_image_entry"].grid(row=1, column=0, sticky="ew", padx=(5,0))
        
        ctk.CTkButton(
            media_frame, text="...", width=40, 
            command=self._select_background_image
        ).grid(row=1, column=1, padx=(5,5))
        
        # Audio
        ctk.CTkLabel(
            media_frame, text="Audio (MP3):", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_TEXT_MUTED
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=(10,0))
        
        self.prop_widgets["audio_entry"] = ctk.CTkEntry(
            media_frame, font=FONT_PROPERTIES_ENTRY, 
            placeholder_text="No audio selected..."
        )
        self.prop_widgets["audio_entry"].grid(row=3, column=0, sticky="ew", padx=(5,0))
        
        ctk.CTkButton(
            media_frame, text="...", width=40, 
            command=self._select_audio_file
        ).grid(row=3, column=1, padx=(5,5))

        # Music
        ctk.CTkLabel(
            media_frame, text="Music (MP3):", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_TEXT_MUTED
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=(10,0))
        
        self.prop_widgets["music_entry"] = ctk.CTkEntry(
            media_frame, font=FONT_PROPERTIES_ENTRY, 
            placeholder_text="No music selected..."
        )
        self.prop_widgets["music_entry"].grid(row=5, column=0, sticky="ew", padx=(5,0))
        
        ctk.CTkButton(
            media_frame, text="...", width=40, 
            command=self._select_music_file
        ).grid(row=5, column=1, padx=(5,5))

    def _create_auto_advance_section(self):
        """Creates the auto-advance section."""
        auto_advance_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        auto_advance_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        auto_advance_frame.grid_columnconfigure(1, weight=1)

        self.prop_widgets["auto_advance_var"] = tk.BooleanVar()
        self.prop_widgets["auto_advance_checkbox"] = ctk.CTkCheckBox(
            auto_advance_frame, text="Auto-advance to next node", 
            variable=self.prop_widgets["auto_advance_var"], 
            command=self._on_auto_advance_change
        )
        self.prop_widgets["auto_advance_checkbox"].grid(
            row=0, column=0, columnspan=2, sticky="w", padx=5
        )

        ctk.CTkLabel(
            auto_advance_frame, text="Delay (seconds):", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_TEXT_MUTED
        ).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        
        self.prop_widgets["auto_advance_delay_entry"] = ctk.CTkEntry(
            auto_advance_frame, font=FONT_PROPERTIES_ENTRY
        )
        self.prop_widgets["auto_advance_delay_entry"].grid(
            row=1, column=1, padx=5, pady=8, sticky="ew"
        )

    def _create_dialogue_section(self):
        """Creates the dialogue text section."""
        dialogue_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        dialogue_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(10, 10))
        dialogue_frame.grid_columnconfigure(0, weight=1)
        dialogue_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            dialogue_frame, text="Dialogue/Text:", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_TEXT_MUTED
        ).grid(row=0, column=0, sticky="w", padx=5)
        
        self.prop_widgets["text_box"] = ctk.CTkTextbox(
            dialogue_frame, wrap="word", font=FONT_PROPERTIES_ENTRY, border_spacing=5
        )
        self.prop_widgets["text_box"].grid(row=1, column=0, sticky="nsew", padx=5, pady=(5,0))

    def _create_save_button(self):
        """Creates the save button."""
        ctk.CTkButton(
            self.parent, text="Save Node Changes", 
            command=self._save_properties_to_node, 
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER
        ).grid(row=4, column=0, pady=10, padx=10, sticky="ew")

    def update_panel(self):
        """Updates the panel with current node data."""
        is_node_active = self.app.active_node_id and self.app.active_node_id in self.app.nodes
        
        # Enable/disable widgets - BUT don't disable the ID entry unless it's intro
        state = "normal" if is_node_active else "disabled"
        for name, widget in self.prop_widgets.items():
            if hasattr(widget, 'configure') and name != "id_entry":  # Don't disable ID entry here
                widget.configure(state=state)

        if is_node_active:
            self._populate_node_data()
        else:
            self._clear_node_data()

    def _populate_node_data(self):
        """Populates the form with current node data."""
        node = self.app.nodes[self.app.active_node_id]
        
        # Handle ID entry - only make readonly for intro node
        self.prop_widgets["id_var"].set(node.id)
        if node.id == "intro":
            self.prop_widgets["id_entry"].configure(state="readonly")
        else:
            self.prop_widgets["id_entry"].configure(state="normal")  # Make sure it's editable
        
        self._set_entry_value("npc_entry", node.npc)
        self.prop_widgets["theme_combo"].set(node.backgroundTheme or "theme-default")
        self._set_entry_value("chapter_entry", node.chapter)
        self._set_textbox_value("text_box", node.text)
        self._set_entry_value("bg_image_entry", node.backgroundImage)
        self._set_entry_value("audio_entry", node.audio)
        self._set_entry_value("music_entry", node.music)
        
        self.prop_widgets["auto_advance_var"].set(node.auto_advance)
        self._set_entry_value("auto_advance_delay_entry", str(node.auto_advance_delay))

    def _clear_node_data(self):
        """Clears all form data when no node is selected."""
        self.prop_widgets["id_var"].set("No node selected")
        self.prop_widgets["id_entry"].configure(state="readonly")
        
        for widget_name in ["npc_entry", "chapter_entry", "bg_image_entry", 
                           "audio_entry", "music_entry", "auto_advance_delay_entry"]:
            self._set_entry_value(widget_name, "")
        
        self.prop_widgets["theme_combo"].set('')
        self.prop_widgets["text_box"].delete("1.0", "end")
        self.prop_widgets["text_box"].configure(state="disabled")

    def _set_entry_value(self, widget_name, value):
        """Helper to set entry widget value."""
        widget = self.prop_widgets[widget_name]
        widget.delete(0, 'end')
        widget.insert(0, value)

    def _set_textbox_value(self, widget_name, value):
        """Helper to set textbox widget value."""
        widget = self.prop_widgets[widget_name]
        widget.delete("1.0", "end")
        widget.insert("1.0", value)

    def _select_background_image(self):
        """Opens file dialog for background image selection."""
        if not self.app.active_node_id:
            return
        
        filepath = filedialog.askopenfilename(
            title="Select Background Image", 
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if filepath:
            self._set_entry_value("bg_image_entry", filepath)

    def _select_audio_file(self):
        """Opens file dialog for audio file selection."""
        if not self.app.active_node_id:
            return
        
        filepath = filedialog.askopenfilename(
            title="Select Audio File", 
            filetypes=[("MP3 Files", "*.mp3")]
        )
        if filepath:
            self._set_entry_value("audio_entry", filepath)
            
    def _select_music_file(self):
        """Opens file dialog for music file selection."""
        if not self.app.active_node_id:
            return
        
        filepath = filedialog.askopenfilename(
            title="Select Music File", 
            filetypes=[("MP3 Files", "*.mp3")]
        )
        if filepath:
            self._set_entry_value("music_entry", filepath)

    def _on_auto_advance_change(self):
        """Handles auto-advance checkbox changes."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        node.auto_advance = self.prop_widgets["auto_advance_var"].get()

    def _set_node_color(self):
        """Opens color picker for node color selection."""
        if not self.app.active_node_id:
            return
        
        color_code = colorchooser.askcolor(title="Choose node color")
        if color_code and color_code[1]:
            self.app._save_state_for_undo("Set Node Color")
            self.app.nodes[self.app.active_node_id].color = color_code[1]
            self.app.canvas_manager.redraw_node(self.app.active_node_id)

    def _save_properties_to_node(self):
        """Saves all property changes to the current node."""
        if not self.app.active_node_id:
            return
        
        self.app._save_state_for_undo("Save Node Properties")
        node = self.app.nodes[self.app.active_node_id]
        
        # Handle node ID change
        new_id = self.prop_widgets["id_var"].get().strip()
        if new_id != node.id and new_id and node.id != "intro":
            if new_id in self.app.nodes:
                messagebox.showerror("Error", f"Node ID '{new_id}' already exists.")
                self.prop_widgets["id_var"].set(node.id)
                return
            if not new_id:
                messagebox.showerror("Error", "Node ID cannot be empty.")
                self.prop_widgets["id_var"].set(node.id)
                return
            
            # Update node ID and references
            old_id = node.id
            self.app.nodes[new_id] = self.app.nodes.pop(old_id)
            node.id = new_id
            
            # Update references in other nodes
            for n in self.app.nodes.values():
                for opt in getattr(n, 'options', []):
                    if opt.get('nextNode') == old_id:
                        opt['nextNode'] = new_id
                        
                # Also update special node types
                if hasattr(n, 'success_node') and n.success_node == old_id:
                    n.success_node = new_id
                if hasattr(n, 'failure_node') and n.failure_node == old_id:
                    n.failure_node = new_id
            
            self.app.active_node_id = new_id
            self.app.selected_node_ids = [
                nid if nid != old_id else new_id 
                for nid in self.app.selected_node_ids
            ]
        
        # Update other properties
        node.npc = self.prop_widgets["npc_entry"].get()
        node.text = self.prop_widgets["text_box"].get("1.0", "end-1c")
        node.backgroundTheme = self.prop_widgets["theme_combo"].get()
        node.chapter = self.prop_widgets["chapter_entry"].get()
        node.backgroundImage = self.prop_widgets["bg_image_entry"].get()
        node.audio = self.prop_widgets["audio_entry"].get()
        node.music = self.prop_widgets["music_entry"].get()
        node.auto_advance = self.prop_widgets["auto_advance_var"].get()
        
        try:
            node.auto_advance_delay = float(self.prop_widgets["auto_advance_delay_entry"].get())
        except ValueError:
            node.auto_advance_delay = 0
        
        # Update UI
        self.app.canvas_manager.redraw_all_nodes()
        self.update_panel()
        messagebox.showinfo("Saved", f"Changes for {self.app.active_node_id} have been saved.")