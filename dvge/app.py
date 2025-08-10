import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import copy
import os
import sys

from .constants import *
from .data_models import DialogueNode, Quest, GameTimer
from .game_mechanics import Enemy
from .ui.main_menu import create_menu
from .ui.properties_panel import PropertiesPanel
from .ui.canvas_manager import CanvasManager
from .ui.search_dialog import SearchDialog

class DVGApp(ctk.CTk):
    """
    The main application class.
    """
    def __init__(self):
        super().__init__()
        self.title("Dialogue Venture Game Engine")
        self.geometry("1800x1000")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLOR_BACKGROUND)

        # --- State Management ---
        self.nodes = {}
        self.player_stats = {}
        self.player_inventory = []
        self.story_flags = {}
        self.quests = {}
        self.variables = {}
        self.enemies = {}
        self.timers = {}
        
        self.selected_node_ids = []
        self.active_node_id = None
        self.node_id_counter = 0
        self.project_settings = {}
        self.undo_stack = []
        self.redo_stack = []
        
        # Initialize handlers (import here to avoid circular imports)
        from .core.project_handler import ProjectHandler
        from .core.html_exporter import HTMLExporter  
        from .core.validation import ProjectValidator
        
        self.project_handler = ProjectHandler(self)
        self.html_exporter = HTMLExporter(self)
        self.validator = ProjectValidator(self)
        
        self._initialize_project_state()
        self._setup_ui()
        self._bind_events()
        
        # Create property widgets container
        self.prop_widgets = {}
        
        # Initial state
        self.after(100, self._save_state_for_undo, "Initial State")

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
        # --- UI Structure ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        create_menu(self)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10,0))
        header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header_frame, text="Dialogue Venture", font=FONT_TITLE).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            header_frame, 
            text="Export Game", 
            command=self.export_game_handler, 
            fg_color=COLOR_SUCCESS, 
            hover_color="#27AE60"
        ).grid(row=0, column=1, sticky="e")
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=3)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Canvas
        self.canvas = tk.Canvas(
            self.main_frame, 
            bg=COLOR_CANVAS_BACKGROUND, 
            highlightthickness=0, 
            borderwidth=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=(10,5))
        self.canvas_manager = CanvasManager(self)

        # Properties panel
        self.properties_panel = PropertiesPanel(self.main_frame, self)
        self.properties_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10))

        # Initial draw
        self.canvas_manager.draw_grid()
        self.canvas_manager.draw_placeholder_if_empty()
        self.properties_panel.update_all_panels()

    def _bind_events(self):
        """Bind keyboard shortcuts and events."""
        self.bind_all("<Control-z>", self.undo)
        self.bind_all("<Control-y>", self.redo)
        self.bind_all("<Control-f>", lambda e: SearchDialog(self))
        self.bind_all("<Delete>", self.canvas_manager.delete_selected_nodes)
        self.bind_all("<Control-s>", lambda event: self.save_project_handler())
        self.bind_all("<Control-o>", lambda event: self.load_project_handler())
        self.bind_all("<Control-n>", lambda event: self.new_project_handler())

    def _save_state_for_undo(self, action_name=""):
        """Saves a snapshot of the current project state for the undo stack."""
        try:
            state = {
                'nodes': {nid: n.to_dict() for nid, n in self.nodes.items()},
                'player_stats': copy.deepcopy(self.player_stats),
                'player_inventory': copy.deepcopy(self.player_inventory),
                'story_flags': copy.deepcopy(self.story_flags),
                'quests': {qid: q.to_dict() for qid, q in self.quests.items()},
                'variables': copy.deepcopy(self.variables),
                'enemies': {eid: e.to_dict() for eid, e in self.enemies.items()},
                'timers': {tid: t.to_dict() for tid, t in self.timers.items()},
                'node_id_counter': self.node_id_counter,
                'project_settings': copy.deepcopy(self.project_settings),
                'active_node_id': self.active_node_id,
                'selected_node_ids': copy.deepcopy(self.selected_node_ids)
            }
            self.undo_stack.append(state)
            self.redo_stack.clear()
            if len(self.undo_stack) > 50: 
                self.undo_stack.pop(0)
        except Exception as e:
            print(f"Error saving state for undo: {e}")

    def _restore_state(self, state):
        """Restores the project to a given state from the undo/redo stack."""
        try:
            # Clear current state
            self.nodes.clear()
            self.quests.clear()
            self.enemies.clear()
            self.timers.clear()
            
            # Restore nodes
            for node_id, node_data in state['nodes'].items():
                self.nodes[node_id] = DialogueNode.from_dict(node_data)
            
            # Restore other data
            for qid, qdata in state.get('quests', {}).items(): 
                self.quests[qid] = Quest.from_dict(qdata)
            for eid, edata in state.get('enemies', {}).items(): 
                self.enemies[eid] = Enemy.from_dict(edata)
            for tid, tdata in state.get('timers', {}).items(): 
                self.timers[tid] = GameTimer.from_dict(tdata)

            self.player_stats = state['player_stats']
            self.player_inventory = state['player_inventory']
            self.story_flags = state['story_flags']
            self.variables = state.get('variables', {})
            self.node_id_counter = state['node_id_counter']
            self.project_settings = state['project_settings']
            self.active_node_id = state.get('active_node_id')
            self.selected_node_ids = state.get('selected_node_ids', [])
            
            # Update UI
            self.canvas_manager.redraw_all_nodes()
            self.properties_panel.update_all_panels()
            
        except Exception as e:
            print(f"Error restoring state: {e}")
            messagebox.showerror("Error", f"Failed to restore state: {e}")

    def undo(self, event=None):
        """Undo the last action."""
        if len(self.undo_stack) > 1:
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)
            previous_state = self.undo_stack[-1]
            self._restore_state(copy.deepcopy(previous_state))
            
    def redo(self, event=None):
        """Redo the last undone action."""
        if self.redo_stack:
            state_to_restore = self.redo_stack.pop()
            self.undo_stack.append(state_to_restore)
            self._restore_state(copy.deepcopy(state_to_restore))

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
        if messagebox.askyesno("New Project", "Create a new project? Unsaved changes will be lost."):
            self._initialize_project_state()
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.canvas_manager.redraw_all_nodes()
            self.properties_panel.update_all_panels()
            self._save_state_for_undo("New Project")

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