# dvge/ui/panels/project_panel.py

"""Project panel for managing project-wide settings."""

from tkinter import messagebox
import customtkinter as ctk
from ...constants import *


class ProjectPanel:
    """Handles the Project tab in the properties panel."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.prop_widgets = {}
        
        self._setup_layout()
        self._create_widgets()

    def _setup_layout(self):
        """Sets up the tab layout."""
        self.parent.grid_columnconfigure(0, weight=1)

    def _create_widgets(self):
        """Creates all widgets for the project panel."""
        # Visual settings frame
        visuals_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        visuals_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        visuals_frame.grid_columnconfigure(1, weight=1)
        
        # Main Font
        ctk.CTkLabel(
            visuals_frame, text="Main Font:", font=FONT_PROPERTIES_LABEL
        ).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        
        self.prop_widgets["font_combo"] = ctk.CTkComboBox(
            visuals_frame, 
            values=["Merriweather", "Lato", "Roboto", "Playfair Display", "Source Code Pro"], 
            font=FONT_PROPERTIES_ENTRY
        )
        self.prop_widgets["font_combo"].grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        # Title Font
        ctk.CTkLabel(
            visuals_frame, text="Title Font:", font=FONT_PROPERTIES_LABEL
        ).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        
        self.prop_widgets["title_font_combo"] = ctk.CTkComboBox(
            visuals_frame, 
            values=["Special Elite", "Cinzel", "Orbitron", "Press Start 2P"], 
            font=FONT_PROPERTIES_ENTRY
        )
        self.prop_widgets["title_font_combo"].grid(row=1, column=1, padx=5, pady=8, sticky="ew")

        # Background
        ctk.CTkLabel(
            visuals_frame, text="Background:", font=FONT_PROPERTIES_LABEL
        ).grid(row=2, column=0, padx=5, pady=8, sticky="w")
        
        self.prop_widgets["background_entry"] = ctk.CTkEntry(
            visuals_frame, 
            font=FONT_PROPERTIES_ENTRY, 
            placeholder_text="#263238 or url(...)"
        )
        self.prop_widgets["background_entry"].grid(row=2, column=1, padx=5, pady=8, sticky="ew")
        
        # Save button
        ctk.CTkButton(
            self.parent, text="Save Project Settings", 
            command=self._save_project_settings
        ).grid(row=1, column=0, pady=10, padx=10, sticky="ew")

    def update_panel(self):
        """Updates the panel with current data."""
        settings = self.app.project_settings
        
        self.prop_widgets["font_combo"].set(settings.get("font", "Merriweather"))
        self.prop_widgets["title_font_combo"].set(settings.get("title_font", "Special Elite"))
        
        background_entry = self.prop_widgets["background_entry"]
        background_entry.delete(0, 'end')
        background_entry.insert(0, settings.get("background", ""))

    def _save_project_settings(self):
        """Saves the project settings."""
        self.app._save_state_for_undo("Save Project Settings")
        
        self.app.project_settings["font"] = self.prop_widgets["font_combo"].get()
        self.app.project_settings["title_font"] = self.prop_widgets["title_font_combo"].get()
        self.app.project_settings["background"] = self.prop_widgets["background_entry"].get()
        
        messagebox.showinfo("Saved", "Project settings have been saved.")