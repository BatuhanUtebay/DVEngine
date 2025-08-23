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
from .advanced_node_properties import AdvancedNodePropertiesTab

# Import AI Assistant Panel (with fallback if not available)
try:
    from .ai_assistant_panel import AIAssistantPanel
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("AI Assistant Panel not available - AI features disabled")

# Import Voice Panel (with fallback if not available)
try:
    from .voice_panel import VoicePanel
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("Voice Panel not available - Voice features disabled")

# Import Marketplace Panel (with fallback if not available)
try:
    from .marketplace_panel import MarketplacePanel
    MARKETPLACE_AVAILABLE = True
except ImportError:
    MARKETPLACE_AVAILABLE = False
    print("Marketplace Panel not available - Marketplace features disabled")



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
        # Base tab names
        tab_names = ["Node", "Advanced", "Choices", "Player", "Variables", "Flags", "Quests", "Project"]
        
        # Add Voice tab if available
        if VOICE_AVAILABLE:
            tab_names.append("Voice")
        
        # Add Marketplace tab if available
        if MARKETPLACE_AVAILABLE:
            tab_names.append("Marketplace")
        
        # Add AI Assistant tab if available
        if AI_AVAILABLE:
            tab_names.append("AI Assistant")
        
        # Create tabs
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
        
        # Initialize Voice tab if available
        if VOICE_AVAILABLE:
            try:
                voice_tab_frame = self.tab_view.tab("Voice")
                voice_tab_frame.grid_columnconfigure(0, weight=1)
                voice_tab_frame.grid_rowconfigure(0, weight=1)
                
                self.voice_tab = VoicePanel(voice_tab_frame, self.app)
                self.voice_tab.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            except Exception as e:
                print(f"Failed to initialize Voice panel: {e}")
                self.voice_tab = None
        else:
            self.voice_tab = None
        
        # Initialize Marketplace tab if available
        if MARKETPLACE_AVAILABLE:
            try:
                marketplace_tab_frame = self.tab_view.tab("Marketplace")
                marketplace_tab_frame.grid_columnconfigure(0, weight=1)
                marketplace_tab_frame.grid_rowconfigure(0, weight=1)
                
                self.marketplace_tab = MarketplacePanel(marketplace_tab_frame, self.app)
                self.marketplace_tab.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            except Exception as e:
                print(f"Failed to initialize Marketplace panel: {e}")
                self.marketplace_tab = None
        else:
            self.marketplace_tab = None
        
        # Initialize AI Assistant tab if available
        if AI_AVAILABLE:
            try:
                ai_assistant_tab_frame = self.tab_view.tab("AI Assistant")
                ai_assistant_tab_frame.grid_columnconfigure(0, weight=1)
                ai_assistant_tab_frame.grid_rowconfigure(0, weight=1)
                
                self.ai_assistant_tab = AIAssistantPanel(ai_assistant_tab_frame, self.app)
                self.ai_assistant_tab.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            except Exception as e:
                print(f"Failed to initialize AI Assistant panel: {e}")
                self.ai_assistant_tab = None
        else:
            self.ai_assistant_tab = None

    def update_all_panels(self):
        """Updates all tabs with current data."""
        self.update_properties_panel()
        self.player_tab.update_panel()
        self.variables_tab.update_panel()
        self.flags_tab.update_panel()
        self.quests_tab.update_panel()
        self.project_tab.update_panel()
        
        # Update Voice panel if available
        if hasattr(self, 'voice_tab') and self.voice_tab:
            try:
                self.voice_tab._refresh_all()
            except Exception as e:
                print(f"Error updating Voice panel: {e}")
        
        # Update Visual Scripting panel if available and a node is selected
        if hasattr(self, 'visual_scripting_tab') and self.visual_scripting_tab and hasattr(self.app, 'selected_node_ids') and self.app.selected_node_ids:
            try:
                self.visual_scripting_tab.on_node_selected(self.app.selected_node_ids[0])
            except Exception as e:
                print(f"Error updating Visual Scripting panel: {e}")
        
        # Update AI assistant if available and a node is selected
        if hasattr(self, 'ai_assistant_tab') and self.ai_assistant_tab and hasattr(self.app, 'selected_node_ids') and self.app.selected_node_ids:
            try:
                self.ai_assistant_tab.on_node_selected(self.app.selected_node_ids[0])
            except Exception as e:
                print(f"Error updating AI assistant panel: {e}")

    def update_properties_panel(self):
        """Updates the node and choices tabs."""
        self.node_tab.update_panel()
        self.advanced_tab.update_panel()
        self.choices_tab.update_panel()

    def add_option_to_node(self, node_id):
        """Adds a new option to the specified node."""
        return self.choices_tab.add_option_to_node(node_id)
