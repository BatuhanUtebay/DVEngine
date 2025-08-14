# dvge/ui/panels/properties_panel.py

"""Main properties panel with tabbed interface - FIXED VERSION."""

import customtkinter as ctk
from ...constants import *
from .node_properties import NodePropertiesTab
from .choice_properties import ChoicePropertiesTab
from .player_panel import PlayerPanel
from .variables_panel import VariablesPanel
from .flags_panel import FlagsPanel
from .quests_panel import QuestsPanel
from .project_panel import ProjectPanel


class AdvancedNodePropertiesTab:
    """Import the fixed advanced node properties."""
    pass


# Import the fixed implementation
exec(open('dvge/ui/panels/advanced_node_properties.py').read())


class PropertiesPanel(ctk.CTkFrame):
    """Main properties panel containing all tabs."""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_PRIMARY_FRAME)
        self.app = app
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_header()
        self._create_tab_view()
        self._initialize_tabs()

    def _create_header(self):
        """Creates the panel header."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15,10))
        ctk.CTkLabel(header, text="Inspector", font=FONT_TITLE).pack(side="left")

    def _create_tab_view(self):
        """Creates the main tab view."""
        self.tab_view = ctk.CTkTabview(
            self, 
            fg_color=COLOR_SECONDARY_FRAME,
            segmented_button_fg_color=COLOR_PRIMARY_FRAME,
            segmented_button_selected_color=COLOR_ACCENT,
            segmented_button_selected_hover_color=COLOR_ACCENT_HOVER,
            segmented_button_unselected_hover_color=COLOR_SECONDARY_FRAME
        )
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))

    def _initialize_tabs(self):
        tab_names = ["Node", "Advanced", "Choices", "Player", "Variables", "Flags", "Quests", "Project"]
        for tab_name in tab_names:
            self.tab_view.add(tab_name)
    
        # Initialize tab content
        self.node_tab = NodePropertiesTab(self.tab_view.tab("Node"), self.app)
        self.choices_tab = ChoicePropertiesTab(self.tab_view.tab("Choices"), self.app)
        self.player_tab = PlayerPanel(self.tab_view.tab("Player"), self.app)
        self.variables_tab = VariablesPanel(self.tab_view.tab("Variables"), self.app)
        self.flags_tab = FlagsPanel(self.tab_view.tab("Flags"), self.app)
        self.quests_tab = QuestsPanel(self.tab_view.tab("Quests"), self.app)
        self.project_tab = ProjectPanel(self.tab_view.tab("Project"), self.app)
        self.advanced_tab = AdvancedNodePropertiesTab(self.tab_view.tab("Advanced"), self.app)

    def update_all_panels(self):
        """Updates all tabs with current data."""
        self.update_properties_panel()
        self.player_tab.update_panel()
        self.variables_tab.update_panel()
        self.flags_tab.update_panel()
        self.quests_tab.update_panel()
        self.project_tab.update_panel()

    def update_properties_panel(self):
        """Updates the node and choices tabs."""
        self.node_tab.update_panel()
        self.advanced_tab.update_panel()
        self.choices_tab.update_panel()

    def add_option_to_node(self, node_id):
        """Adds a new option to the specified node."""
        return self.choices_tab.add_option_to_node(node_id)