import customtkinter as ctk
from ...constants import *
from .feature_panels import (
    SkillCheckPanel,
    LootPanel,
    ReputationPanel,
    PuzzlePanel,
    MinigamePanel
)


class AdvancedFeaturesTab(ctk.CTkFrame):
    """Enhanced Advanced tab with all feature panels."""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.current_node = None
        
        self._setup_layout()
        self._create_widgets()
        
    def _setup_layout(self):
        """Sets up the tab layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
    def _create_widgets(self):
        """Creates the feature selection and panels."""
        # Feature selector
        selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        selector_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        selector_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            selector_frame, text="Feature Type:",
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_TEXT_MUTED
        ).grid(row=0, column=0, padx=5, sticky="w")
        
        self.feature_selector = ctk.CTkComboBox(
            selector_frame,
            values=[
                "Node Settings",
                "Skill Checks",
                "Loot Tables",
                "Reputation",
                "Puzzles",
                "Minigames"
            ],
            font=FONT_PROPERTIES_ENTRY,
            command=self._on_feature_change
        )
        self.feature_selector.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Content area
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        
        # Initialize panels (hidden initially)
        self.panels = {
            "Node Settings": self._create_node_settings_panel(),
            "Skill Checks": SkillCheckPanel(self.content_container, self.app),
            "Loot Tables": LootPanel(self.content_container, self.app),
            "Reputation": ReputationPanel(self.content_container, self.app),
            "Puzzles": PuzzlePanel(self.content_container, self.app),
            "Minigames": MinigamePanel(self.content_container, self.app)
        }
        
        # Hide all panels initially
        for panel in self.panels.values():
            panel.grid_remove()
            
        # Show default panel
        self.feature_selector.set("Node Settings")
        self._show_panel("Node Settings")
        
    def _create_node_settings_panel(self):
        """Creates the default node settings panel."""
        panel = ctk.CTkFrame(self.content_container, fg_color="transparent")
        panel.grid(row=0, column=0, sticky="nsew")
        
        # This would contain the existing advanced node properties
        # (Shop items, Timer settings, etc.)
        info_label = ctk.CTkLabel(
            panel,
            text="Select a feature from the dropdown above\nto configure advanced node properties.",
            font=FONT_PROPERTIES_ENTRY,
            text_color=COLOR_TEXT_MUTED,
            justify="center"
        )
        info_label.pack(expand=True)
        
        return panel
        
    def _on_feature_change(self, choice):
        """Handles feature selection change."""
        self._show_panel(choice)
        
    def _show_panel(self, panel_name):
        """Shows the selected panel and hides others."""
        for name, panel in self.panels.items():
            if name == panel_name:
                panel.grid(row=0, column=0, sticky="nsew")
            else:
                panel.grid_remove()
                
    def update_panel(self, node=None):
        """Updates all panels with current node data."""
        self.current_node = node
        
        # Update each panel if it has an update method
        for panel in self.panels.values():
            if hasattr(panel, 'update_panel'):
                panel.update_panel(node)
                
        # Enable/disable features based on node type
        if node:
            node_type = type(node).__name__
            
            # Enable relevant features for each node type
            if "DiceRoll" in node_type:
                self.feature_selector.configure(values=[
                    "Node Settings",
                    "Skill Checks",
                    "Puzzles"
                ])
            elif "Shop" in node_type:
                self.feature_selector.configure(values=[
                    "Node Settings",
                    "Loot Tables",
                    "Reputation"
                ])
            elif "Combat" in node_type:
                self.feature_selector.configure(values=[
                    "Node Settings",
                    "Skill Checks",
                    "Loot Tables"
                ])
            elif "Timer" in node_type:
                self.feature_selector.configure(values=[
                    "Node Settings",
                    "Minigames",
                    "Puzzles"
                ])
            else:
                # Show all features for standard nodes
                self.feature_selector.configure(values=[
                    "Node Settings",
                    "Skill Checks",
                    "Loot Tables",
                    "Reputation",
                    "Puzzles",
                    "Minigames"
                ])