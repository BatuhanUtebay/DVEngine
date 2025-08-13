# dvge/core/application.py

"""Main application class for DVGE."""

import customtkinter as ctk
from ..constants import *
from ..models import DialogueNode, Quest, GameTimer, Enemy
from .state_manager import StateManager


class DVGApp(ctk.CTk):
    """The main application class."""
    
    def __init__(self):
        super().__init__()
        self.title("Dialogue Venture Game Engine")
        self.geometry("1800x1000")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLOR_BACKGROUND)

        # Initialize state
        self._initialize_project_state()
        
        # Initialize managers and handlers
        self.state_manager = StateManager(self)
        
        # Import handlers here to avoid circular imports
        from .project_handler import ProjectHandler
        from .html_exporter import HTMLExporter  
        from .validation import ProjectValidator
        
        self.project_handler = ProjectHandler(self)
        self.html_exporter = HTMLExporter(self)
        self.validator = ProjectValidator(self)
        
        # Setup UI
        self._setup_ui()
        self._bind_events()
        
        # Create property widgets container
        self.prop_widgets = {}
        
        # Initial state
        self.after(100, self.state_manager.save_state, "Initial State")

    def _initialize_project_state(self):
        """Sets default values for a new project."""
        self.nodes = {}
        self.player_stats = {"health": 100, "strength": 10, "defense": 5}
        self.player_inventory = [{"name": "Health Potion", "description": "Restores 20 health."}]
        self.story_flags = {}
        self.quests = {}
        self.variables = {"gold": 50}
        self.enemies = {"goblin": Enemy("goblin", "Goblin", 20, 5, 2)}
        self.timers = {"bomb_timer": GameTimer("bomb_timer", 30)}
        
        self.project_settings = {
            "font": "Merriweather", 
            "title_font": "Special Elite", 
            "background": ""
        }
        self.node_id_counter = 0
        self.active_node_id = None
        self.selected_node_ids = []

    def _setup_ui(self):
        """Initialize the user interface."""
        from ..ui.main_window import setup_main_window
        setup_main_window(self)

    def _bind_events(self):
        """Bind keyboard shortcuts and events."""
        self.bind_all("<Control-z>", self.undo)
        self.bind_all("<Control-y>", self.redo)
        self.bind_all("<Control-f>", lambda e: self._open_search_dialog())
        self.bind_all("<Delete>", self.canvas_manager.delete_selected_nodes)
        self.bind_all("<Control-s>", lambda event: self.save_project_handler())
        self.bind_all("<Control-o>", lambda event: self.load_project_handler())
        self.bind_all("<Control-n>", lambda event: self.new_project_handler())

    def _open_search_dialog(self):
        """Opens the search dialog."""
        from ..ui.dialogs.search_dialog import SearchDialog
        SearchDialog(self)

    def undo(self, event=None):
        """Undo the last action."""
        self.state_manager.undo()
            
    def redo(self, event=None):
        """Redo the last undone action."""
        self.state_manager.redo()

    def set_selection(self, new_selection_ids, active_node_id=None):
        """Update the current selection."""
        self.selected_node_ids = new_selection_ids if new_selection_ids else []
        
        if active_node_id:
            self.active_node_id = active_node_id
        elif self.selected_node_ids:
            self.active_node_id = self.selected_node_ids[-1]
        else:
            self.active_node_id = None
        
        # Update UI
        self.canvas_manager.update_selection_visuals()
        self.properties_panel.update_properties_panel()

    def new_project_handler(self):
        """Create a new project."""
        from ..core.utils import ask_yes_no
        if ask_yes_no("New Project", "Create a new project? Unsaved changes will be lost."):
            self._initialize_project_state()
            self.state_manager.clear_history()
            self.canvas_manager.redraw_all_nodes()
            self.properties_panel.update_all_panels()
            self.state_manager.save_state("New Project")

    def save_project_handler(self): 
        """Save the current project."""
        return self.project_handler.save_project()
        
    def load_project_handler(self): 
        """Load a project from file."""
        return self.project_handler.load_project()
        
    def export_game_handler(self): 
        """Export the game to HTML."""
        return self.html_exporter.export_game()

    def validate_project(self):
        """Validate the current project."""
        return self.validator.validate_project()

    def get_node_by_id(self, node_id):
        """Get a node by its ID."""
        return self.nodes.get(node_id)

    def get_all_node_ids(self):
        """Get all node IDs."""
        return list(self.nodes.keys())

    def add_node(self, node):
        """Add a node to the project."""
        if node.id in self.nodes:
            raise ValueError(f"Node with ID '{node.id}' already exists")
        self.nodes[node.id] = node

    def remove_node(self, node_id):
        """Remove a node from the project."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            # Clean up references
            for node in self.nodes.values():
                for option in getattr(node, 'options', []):
                    if option.get('nextNode') == node_id:
                        option['nextNode'] = ""

    def _save_state_for_undo(self, action_name=""):
        """Wrapper for state manager save_state method."""
        self.state_manager.save_state(action_name)