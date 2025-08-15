import customtkinter as ctk
from ....constants import *
from ....features.reputation import ReputationLevel


class ReputationPanel(ctk.CTkFrame):
    """Panel for configuring reputation and faction relationships."""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.current_node = None
        
        self._setup_layout()
        self._create_widgets()
        
    def _setup_layout(self):
        """Sets up the panel layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
    def _create_widgets(self):
        """Creates reputation configuration widgets."""
        # Title
        title_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        title_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(
            title_frame, text="🏛️ Reputation System",
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_ACCENT
        ).pack(padx=10, pady=10)
        
        # Faction Management
        faction_frame = ctk.CTkFrame(self, fg_color="transparent")
        faction_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        faction_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            faction_frame, text="Manage Factions:",
            font=FONT_PROPERTIES_LABEL
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        ctk.CTkButton(
            faction_frame, text="+ Add Faction",
            command=self._add_faction_dialog, height=28
        ).grid(row=0, column=1, padx=5, pady=5, sticky="e")
        
        # Factions List
        self.factions_container = ctk.CTkScrollableFrame(
            self, fg_color=COLOR_SECONDARY_FRAME, height=200
        )
        self.factions_container.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        # Initialize with default factions
        self._add_default_factions()
        
        # Node-specific Requirements
        req_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        req_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        req_frame.grid_columnconfigure(0, weight=1)
        req_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            req_frame, text="Node Reputation Requirements:",
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_WARNING
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.requirements_frame = ctk.CTkScrollableFrame(req_frame)
        self.requirements_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        ctk.CTkButton(
            req_frame, text="+ Add Requirement",
            command=self._add_requirement_row, height=28
        ).grid(row=2, column=0, pady=5)
        
        # Reputation Changes
        changes_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        changes_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(
            changes_frame, text="Reputation Changes (on node entry):",
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_SUCCESS
        ).pack(padx=10, pady=10, anchor="w")
        
        self.changes_frame = ctk.CTkScrollableFrame(changes_frame, height=150)
        self.changes_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkButton(
            changes_frame, text="+ Add Change",
            command=self._add_change_row, height=28
        ).pack(pady=5)
        
    def _add_default_factions(self):
        """Adds default faction entries."""
        default_factions = [
            ("Guards", 0, "#3498DB"),
            ("Thieves Guild", 0, "#8E44AD"),
            ("Merchants", 0, "#F39C12"),
            ("Nobles", 0, "#E74C3C"),
            ("Common Folk", 0, "#2ECC71")
        ]
        
        for faction_name, default_rep, color in default_factions:
            self._create_faction_entry(faction_name, default_rep, color)
            
    def _create_faction_entry(self, name, reputation, color):
        """Creates a faction entry in the list."""
        faction_frame = ctk.CTkFrame(self.factions_container)
        faction_frame.pack(fill="x", pady=2, padx=5)
        faction_frame.grid_columnconfigure(1, weight=1)
        
        # Color indicator
        indicator = ctk.CTkLabel(
            faction_frame, text="●", font=("Arial", 16),
            text_color=color, width=30
        )
        indicator.grid(row=0, column=0, padx=5)
        
        # Faction name
        name_label = ctk.CTkLabel(
            faction_frame, text=name,
            font=FONT_PROPERTIES_LABEL
        )
        name_label.grid(row=0, column=1, padx=5, sticky="w")
        
        # Reputation slider
        rep_slider = ctk.CTkSlider(
            faction_frame, from_=-100, to=100,
            number_of_steps=200, width=200
        )
        rep_slider.set(reputation)
        rep_slider.grid(row=0, column=2, padx=10, sticky="ew")
        
        # Reputation value label
        value_label = ctk.CTkLabel(
            faction_frame, text=str(reputation),
            font=FONT_PROPERTIES_ENTRY, width=50
        )
        value_label.grid(row=0, column=3, padx=5)
        
        # Level label
        level = ReputationLevel.get_level(reputation)
        level_label = ctk.CTkLabel(
            faction_frame, text=level.display_name,
            font=FONT_PROPERTIES_ENTRY,
            text_color=level.color
        )
        level_label.grid(row=0, column=4, padx=5)
        
        # Update labels when slider moves
        def update_labels(value):
            val = int(value)
            value_label.configure(text=str(val))
            level = ReputationLevel.get_level(val)
            level_label.configure(
                text=level.display_name,
                text_color=level.color
            )
            
        rep_slider.configure(command=update_labels)
        
        # Delete button
        ctk.CTkButton(
            faction_frame, text="✕", width=30, height=30,
            fg_color="transparent", hover_color=COLOR_ERROR,
            command=faction_frame.destroy
        ).grid(row=0, column=5, padx=5)
        
    def _add_faction_dialog(self):
        """Shows dialog to add a new faction."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Faction")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Faction name
        ctk.CTkLabel(
            dialog, text="Faction Name:",
            font=FONT_PROPERTIES_LABEL
        ).pack(pady=(20,5))
        
        name_entry = ctk.CTkEntry(dialog, placeholder_text="Enter faction name")
        name_entry.pack(pady=5, padx=20, fill="x")
        
        # Color selection
        color_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        color_frame.pack(pady=10)
        
        colors = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6", "#1ABC9C"]
        selected_color = ctk.StringVar(value=colors[0])
        
        for color in colors:
            btn = ctk.CTkRadioButton(
                color_frame, text="", fg_color=color,
                variable=selected_color, value=color,
                width=30, height=30
            )
            btn.pack(side="left", padx=5)
            
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        def add_faction():
            name = name_entry.get()
            if name:
                self._create_faction_entry(name, 0, selected_color.get())
                dialog.destroy()
                
        ctk.CTkButton(
            button_frame, text="Add",
            command=add_faction
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame, text="Cancel",
            command=dialog.destroy,
            fg_color=COLOR_ERROR
        ).pack(side="left", padx=5)
        
    def _add_requirement_row(self):
        """Adds a reputation requirement row."""
        row_frame = ctk.CTkFrame(self.requirements_frame, fg_color=COLOR_SECONDARY_FRAME)
        row_frame.pack(fill="x", pady=2)
        row_frame.grid_columnconfigure(0, weight=1)
        
        # Faction selector
        faction_combo = ctk.CTkComboBox(
            row_frame,
            values=["Guards", "Thieves Guild", "Merchants", "Nobles", "Common Folk"],
            width=150
        )
        faction_combo.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Comparison operator
        op_combo = ctk.CTkComboBox(
            row_frame,
            values=["At least", "At most", "Exactly"],
            width=100
        )
        op_combo.set("At least")
        op_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Level selector
        level_combo = ctk.CTkComboBox(
            row_frame,
            values=["Hostile", "Unfriendly", "Neutral", "Friendly", "Allied"],
            width=100
        )
        level_combo.set("Friendly")
        level_combo.grid(row=0, column=2, padx=5, pady=5)
        
        # Remove button
        ctk.CTkButton(
            row_frame, text="✕", width=30, height=30,
            fg_color="transparent", hover_color=COLOR_ERROR,
            command=row_frame.destroy
        ).grid(row=0, column=3, padx=5, pady=5)
        
    def _add_change_row(self):
        """Adds a reputation change row."""
        row_frame = ctk.CTkFrame(self.changes_frame, fg_color=COLOR_SECONDARY_FRAME)
        row_frame.pack(fill="x", pady=2)
        row_frame.grid_columnconfigure(0, weight=1)
        
        # Faction selector
        faction_combo = ctk.CTkComboBox(
            row_frame,
            values=["Guards", "Thieves Guild", "Merchants", "Nobles", "Common Folk"],
            width=150
        )
        faction_combo.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Change amount
        change_entry = ctk.CTkEntry(row_frame, placeholder_text="+/- amount", width=100)
        change_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Propagate checkbox
        propagate_var = ctk.BooleanVar(value=True)
        propagate_check = ctk.CTkCheckBox(
            row_frame, text="Propagate",
            variable=propagate_var, width=100
        )
        propagate_check.grid(row=0, column=2, padx=5, pady=5)
        
        # Remove button
        ctk.CTkButton(
            row_frame, text="✕", width=30, height=30,
            fg_color="transparent", hover_color=COLOR_ERROR,
            command=row_frame.destroy
        ).grid(row=0, column=3, padx=5, pady=5)