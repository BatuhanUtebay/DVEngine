import customtkinter as ctk
from ....constants import *


class SkillCheckPanel(ctk.CTkFrame):
    """Panel for configuring enhanced skill checks."""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.current_node = None
        
        self._setup_layout()
        self._create_widgets()
        
    def _setup_layout(self):
        """Sets up the panel layout."""
        self.grid_columnconfigure(0, weight=1)
        
    def _create_widgets(self):
        """Creates all widgets for skill check configuration."""
        # Title
        title_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        title_frame.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(
            title_frame, text="⚡ Skill Check Configuration",
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_ACCENT
        ).pack(padx=10, pady=10)
        
        # Skill Type Selection
        type_frame = ctk.CTkFrame(self, fg_color="transparent")
        type_frame.pack(fill="x", pady=5, padx=10)
        type_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            type_frame, text="Skill Type:",
            font=FONT_PROPERTIES_ENTRY
        ).grid(row=0, column=0, padx=5, sticky="w")
        
        self.skill_type_combo = ctk.CTkComboBox(
            type_frame,
            values=["Strength", "Dexterity", "Intelligence", "Charisma", "Perception", "Luck"],
            font=FONT_PROPERTIES_ENTRY
        )
        self.skill_type_combo.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Difficulty Settings
        diff_frame = ctk.CTkFrame(self, fg_color=COLOR_SECONDARY_FRAME)
        diff_frame.pack(fill="x", pady=5, padx=10)
        diff_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            diff_frame, text="Base Difficulty:",
            font=FONT_PROPERTIES_ENTRY
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.difficulty_slider = ctk.CTkSlider(
            diff_frame, from_=5, to=30, number_of_steps=25
        )
        self.difficulty_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        self.difficulty_label = ctk.CTkLabel(
            diff_frame, text="15",
            font=FONT_PROPERTIES_ENTRY
        )
        self.difficulty_label.grid(row=0, column=2, padx=10, pady=5)
        
        self.difficulty_slider.configure(
            command=lambda v: self.difficulty_label.configure(text=str(int(v)))
        )
        
        # Critical Options
        crit_frame = ctk.CTkFrame(self, fg_color="transparent")
        crit_frame.pack(fill="x", pady=5, padx=10)
        
        self.allow_criticals = ctk.CTkCheckBox(
            crit_frame, text="Allow Critical Success/Failure",
            font=FONT_PROPERTIES_ENTRY
        )
        self.allow_criticals.pack(side="left", padx=5)
        
        self.allow_retries = ctk.CTkCheckBox(
            crit_frame, text="Allow Retries",
            font=FONT_PROPERTIES_ENTRY
        )
        self.allow_retries.pack(side="left", padx=20)
        
        # Item Modifiers
        mod_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        mod_frame.pack(fill="both", expand=True, pady=5, padx=10)
        
        ctk.CTkLabel(
            mod_frame, text="Item Modifiers:",
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_SUCCESS
        ).pack(padx=10, pady=5, anchor="w")
        
        self.modifiers_frame = ctk.CTkScrollableFrame(mod_frame, height=150)
        self.modifiers_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Add Modifier Button
        ctk.CTkButton(
            mod_frame, text="+ Add Item Modifier",
            command=self._add_modifier_row, height=28
        ).pack(pady=5)
        
    def _add_modifier_row(self):
        """Adds a new item modifier row."""
        row_frame = ctk.CTkFrame(self.modifiers_frame, fg_color=COLOR_SECONDARY_FRAME)
        row_frame.pack(fill="x", pady=2)
        row_frame.grid_columnconfigure(0, weight=1)
        
        item_entry = ctk.CTkEntry(row_frame, placeholder_text="Item name")
        item_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        modifier_entry = ctk.CTkEntry(row_frame, placeholder_text="+/-", width=60)
        modifier_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkButton(
            row_frame, text="✕", width=30, height=30,
            fg_color="transparent", hover_color=COLOR_ERROR,
            command=row_frame.destroy
        ).grid(row=0, column=2, padx=5, pady=5)
        
    def update_panel(self, node):
        """Updates panel with node data."""
        self.current_node = node