# dvge/ui/panels/flags_panel.py

"""Flags panel for managing story flags."""

from tkinter import messagebox
import customtkinter as ctk
from ...constants import *
from ..widgets.custom_widgets import ScrollableListFrame


class FlagsPanel:
    """Handles the Flags tab in the properties panel."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self._setup_layout()
        self._create_widgets()

    def _setup_layout(self):
        """Sets up the tab layout."""
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

    def _create_widgets(self):
        """Creates all widgets for the flags panel."""
        # Main container
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Scrollable flags frame
        self.flags_frame = ScrollableListFrame(
            main_frame, 
            label_text="Story Flags", 
            label_font=FONT_PROPERTIES_LABEL
        )
        self.flags_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add flag button
        ctk.CTkButton(
            main_frame, text="+ Add Flag", command=self._add_story_flag
        ).grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    def update_panel(self):
        """Updates the panel with current data."""
        self.flags_frame.clear_all()
        
        for flag, value in self.app.story_flags.items():
            item_frame = self.flags_frame.add_item_frame()
            item_frame.grid_columnconfigure(0, weight=1)
            
            # Flag name entry
            name_entry = ctk.CTkEntry(item_frame)
            name_entry.insert(0, flag)
            name_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            name_entry.bind(
                "<KeyRelease>", 
                lambda e, old_name=flag, w=name_entry: self._rename_story_flag(old_name, w.get())
            )
            
            # Value combobox
            val_combo = ctk.CTkComboBox(item_frame, values=["true", "false"], width=90)
            val_combo.set("true" if value else "false")
            val_combo.configure(command=lambda c, f=flag: self._change_flag_default(f, c))
            val_combo.grid(row=0, column=1, padx=5, pady=5)
            
            # Delete button
            ctk.CTkButton(
                item_frame, text="✕", width=28, height=28, 
                fg_color="transparent", hover_color=COLOR_ERROR,
                command=lambda f=flag: self._delete_story_flag(f)
            ).grid(row=0, column=2, padx=5, pady=5)

    def _add_story_flag(self):
        """Adds a new story flag."""
        self.app._save_state_for_undo("Add Flag")
        flag_name = f"new_flag_{len(self.app.story_flags)}"
        self.app.story_flags[flag_name] = False
        self.update_panel()
        
    def _rename_story_flag(self, old_name, new_name):
        """Renames a story flag."""
        if not new_name or (new_name in self.app.story_flags and new_name != old_name):
            return
        
        self.app._save_state_for_undo("Rename Flag")
        self.app.story_flags[new_name] = self.app.story_flags.pop(old_name)
        
    def _change_flag_default(self, flag_name, value_str):
        """Changes the default value of a flag."""
        self.app._save_state_for_undo("Change Flag Default")
        self.app.story_flags[flag_name] = (value_str == "true")
        
    def _delete_story_flag(self, flag_name):
        """Deletes a story flag."""
        if messagebox.askyesno("Delete Flag", f"Delete '{flag_name}'?"):
            self.app._save_state_for_undo("Delete Flag")
            self.app.story_flags.pop(flag_name, None)
            self.update_panel()