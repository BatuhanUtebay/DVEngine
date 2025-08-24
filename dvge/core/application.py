# dvge/core/application.py

"""Main application class for DVGE."""

import os
import customtkinter as ctk
from ..constants import *
from ..models import DialogueNode, Quest, GameTimer, Enemy
from .state_manager import StateManager
from .variable_system import VariableSystem


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
        
        # Initialize variable system
        self.variable_system = VariableSystem()
        self.variable_system.set_variables_ref(self.variables)
        self.variable_system.set_flags_ref(self.story_flags)
        
        # Initialize feature systems
        self._initialize_feature_systems()
        
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
        
        # Initialize plugin system
        self._initialize_plugin_system()
        
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
        
        # Feature system data
        self.reputation_data = {}  # {faction_id: value}
        self.loot_tables = {}  # {table_id: table_data}
        self.active_puzzles = {}  # {puzzle_id: puzzle_state}
        self.minigame_results = {}  # {minigame_id: results}
        self.skill_modifiers = {}  # {skill_type: modifier}
        
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
        self.bind_all("<Control-p>", lambda e: self._open_live_preview())

    def _open_search_dialog(self):
        """Opens the search dialog."""
        from ..ui.dialogs.search_dialog import SearchDialog
        SearchDialog(self)

    def _open_live_preview(self):
        """Opens live preview via keyboard shortcut."""
        if hasattr(self, 'preview_toolbar'):
            self.preview_toolbar.preview_controls._open_preview()

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
        
        # Update preview toolbar if it exists
        if hasattr(self, 'preview_toolbar'):
            self.preview_toolbar.update_node_info(self.active_node_id)

    def new_project_handler(self):
        """Create a new project."""
        try:
            print("DEBUG: Starting new_project_handler")
            from ..core.utils import ask_yes_no
            if ask_yes_no("New Project", "Create a new project? Unsaved changes will be lost."):
                print("DEBUG: User confirmed new project")
                # Show template selection dialog
                from ..ui.dialogs.template_selection_dialog import TemplateSelectionDialog
                print("DEBUG: Imported template dialog")
                template_dialog = TemplateSelectionDialog(self)
                print("DEBUG: Created template dialog")
                result = template_dialog.show()
                print(f"DEBUG: Dialog result: {result}")
                
                if result is None:
                    print("DEBUG: User cancelled")
                    return  # User cancelled
                    
                if result["action"] == "create_blank":
                    print("DEBUG: Creating blank project")
                    self._initialize_project_state()
                elif result["action"] == "create_from_template":
                    template = result["template"]
                    print(f"DEBUG: Applying template: {template.name}")
                    self._apply_template(template)
                
                # Re-initialize variable system with new references
                self.variable_system.set_variables_ref(self.variables)
                self.variable_system.set_flags_ref(self.story_flags)
                
                self.state_manager.clear_history()
                self.canvas_manager.redraw_all_nodes()
                self.properties_panel.update_all_panels()
                self.state_manager.save_state("New Project")
                print("DEBUG: New project handler completed successfully")
            else:
                print("DEBUG: User declined new project")
        except Exception as e:
            print(f"DEBUG ERROR in new_project_handler: {e}")
            import traceback
            traceback.print_exc()

    def save_project_handler(self): 
        """Save the current project."""
        return self.project_handler.save_project()
        
    def load_project_handler(self): 
        """Load a project from file."""
        success = self.project_handler.load_project()
        if success:
            # Re-initialize variable system after loading
            self.variable_system.set_variables_ref(self.variables)
            self.variable_system.set_flags_ref(self.story_flags)
        return success
        
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

    def _initialize_feature_systems(self):
        """Initialize the advanced feature systems."""
        try:
            from ..features.skill_checks import SkillCheckSystem
            from ..features.reputation import ReputationSystem
            from ..features.loot_system import LootTable
            from ..features.media_system import MediaLibrary
            
            self.skill_check_system = SkillCheckSystem()
            self.reputation_system = ReputationSystem()
            self.loot_tables = {}  # Will store loot tables by ID
            self.media_library = MediaLibrary()
            
        except ImportError as e:
            print(f"Warning: Some feature systems not available: {e}")
            # Create minimal fallback systems
            self.skill_check_system = None
            self.reputation_system = None
            self.loot_tables = {}
            self.media_library = None
        
        # Initialize AI service and enhanced systems
        self._initialize_ai_systems()
    
    def _initialize_ai_systems(self):
        """Initialize AI service and enhanced AI features."""
        try:
            from ..ai.ai_service import AIService
            
            # Initialize AI service
            self.ai_service = AIService(self)
            print("AI Service initialized successfully")
            
            # Initialize AI UI integration
            if self.ai_service.is_enhanced_ai_available():
                from ..ui.ai_integration import AIIntegrationManager
                self.ai_integration = AIIntegrationManager(self)
                print("AI Integration Manager initialized successfully")
            else:
                self.ai_integration = None
                print("Enhanced AI features not available")
            
        except ImportError as e:
            print(f"Warning: AI systems not available: {e}")
            self.ai_service = None
            self.ai_integration = None
        except Exception as e:
            print(f"Error initializing AI systems: {e}")
            self.ai_service = None
            self.ai_integration = None
        
    

    def _save_state_for_undo(self, action_name=""):
        """Wrapper for state manager save_state method."""
        self.state_manager.save_state(action_name)
        
    def _apply_template(self, template):
        """Apply a project template to create a new project."""
        from .template_manager import TemplateManager
        
        template_manager = TemplateManager()
        template_manager.apply_template(template, self)
    
    def _initialize_plugin_system(self):
        """Initialize the plugin system."""
        try:
            from .plugin_system import PluginManager
            self.plugin_manager = PluginManager(self)
            
            # Load all plugins
            self.plugin_manager.load_all_plugins()
            
            # Load plugin states if they exist
            plugin_states_file = os.path.expanduser('~/.dvge/plugin_states.json')
            if os.path.exists(plugin_states_file):
                self.plugin_manager.load_plugin_states(plugin_states_file)
                
        except Exception as e:
            print(f"Failed to initialize plugin system: {e}")
            self.plugin_manager = None
    
    def register_exporter(self, exporter_plugin):
        """Register a custom exporter plugin."""
        if not hasattr(self, 'custom_exporters'):
            self.custom_exporters = {}
        
        format_name = exporter_plugin.get_export_format_name()
        self.custom_exporters[format_name] = exporter_plugin
        
        print(f"Registered custom exporter: {format_name}")
    
    def get_available_exporters(self):
        """Get all available export formats."""
        exporters = {
            "HTML Game": self.export_game_handler,
            "Enhanced Mobile HTML": self._export_enhanced_mobile
        }
        
        # Add custom exporters from plugins
        if hasattr(self, 'custom_exporters'):
            for name, exporter in self.custom_exporters.items():
                exporters[name] = lambda path=None, exp=exporter: self._export_with_plugin(exp, path)
        
        return exporters
    
    def _export_with_plugin(self, exporter_plugin, file_path=None):
        """Export using a plugin exporter."""
        from tkinter import filedialog
        
        if not file_path:
            file_path = filedialog.asksaveasfilename(
                title=f"Export as {exporter_plugin.get_export_format_name()}",
                defaultextension=exporter_plugin.get_file_extension(),
                filetypes=[(
                    exporter_plugin.get_export_format_name(),
                    f"*{exporter_plugin.get_file_extension()}"
                )]
            )
        
        if file_path:
            return exporter_plugin.export(self, file_path)
        return False
    
    def add_menu_item(self, menu_item):
        """Add a menu item from a plugin."""
        # This would integrate with the menu system
        print(f"Plugin wants to add menu item: {menu_item}")
    
    def register_ui_panel(self, panel_class):
        """Register a UI panel from a plugin."""
        # This would integrate with the UI system
        print(f"Plugin wants to register UI panel: {panel_class}")
    
    def cleanup_plugins(self):
        """Clean up the plugin system."""
        if hasattr(self, 'plugin_manager') and self.plugin_manager:
            # Save plugin states
            plugin_states_file = os.path.expanduser('~/.dvge/plugin_states.json')
            os.makedirs(os.path.dirname(plugin_states_file), exist_ok=True)
            self.plugin_manager.save_plugin_states(plugin_states_file)
            
            # Cleanup plugins
            self.plugin_manager.cleanup()
    
    def destroy(self):
        """Override destroy to cleanup plugins."""
        self.cleanup_plugins()
        super().destroy()