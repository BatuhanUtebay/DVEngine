# dvge/app.py
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import copy

from .constants import *
from .data_models import DialogueNode
from .ui.main_menu import create_menu
from .ui.properties_panel import PropertiesPanel
from .ui.canvas_manager import CanvasManager
from .ui.search_dialog import SearchDialog
from .core.project_handler import save_project, load_project
from .core.html_exporter import export_game

class DVGApp(ctk.CTk):
    """
    The main application class. It inherits from CustomTkinter's CTk class and
    manages the entire application, including the UI, canvas, and all interactions.
    """
    def __init__(self):
        super().__init__()
        self.title("Dialogue Venture Game Engine")
        self.geometry("1800x1000")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- State Management ---
        self.nodes = {}
        self.player_stats = {}
        self.player_inventory = []
        self.story_flags = {}
        self.selected_node_ids = []
        self.active_node_id = None
        self.node_id_counter = 0
        self.project_settings = {}
        self.undo_stack = []
        self.redo_stack = []
        self._initialize_project_state()

        # --- UI Structure ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        create_menu(self)
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=3) # Canvas column
        self.main_frame.grid_columnconfigure(1, weight=1) # Properties Panel column
        self.main_frame.grid_rowconfigure(1, weight=1) # Make the content row expand

        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(header_frame, text="Export to HTML Game", command=self.export_game_handler, fg_color="#1a9c47", hover_color="#147836").grid(row=0, column=1, sticky="e", padx=10)

        # --- Canvas ---
        self.canvas = tk.Canvas(self.main_frame, bg="#2B2B2B", highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.canvas_manager = CanvasManager(self)

        # --- Properties Panel ---
        self.properties_panel = PropertiesPanel(self.main_frame, self)
        self.properties_panel.grid(row=1, column=1, sticky="ns", padx=(5, 0))

        self.bind_events()
        self.properties_panel.update_all_panels()
        self.canvas_manager.draw_grid()
        self.canvas_manager.draw_placeholder_if_empty()
        
        # Save initial state for undo
        self.after(100, self._save_state_for_undo, "Initial State")

    def _initialize_project_state(self):
        """Sets default values for a new project."""
        self.nodes = {}
        self.player_stats = {"strength": 10, "charisma": 10, "sanity": 70}
        self.player_inventory = ["Old Map"]
        self.story_flags = {"game_started": True, "met_the_king": False}
        self.project_settings = {"font": "Merriweather", "title_font": "Special Elite", "background": ""}
        self.node_id_counter = 0
        self.active_node_id = None
        self.selected_node_ids = []

    def bind_events(self):
        """Binds all keyboard and mouse events."""
        self.bind_all("<Control-z>", self.undo)
        self.bind_all("<Control-y>", self.redo)
        self.bind_all("<Control-f>", lambda e: SearchDialog(self))
        self.bind_all("<Delete>", self.canvas_manager.delete_selected_nodes)
        self.bind_all("<Control-s>", lambda event: self.save_project_handler())
        self.bind_all("<Control-o>", lambda event: self.load_project_handler())

    def _save_state_for_undo(self, action_name=""):
        """Saves a snapshot of the current project state for the undo stack."""
        state = {
            'nodes': copy.deepcopy({nid: n.to_dict() for nid, n in self.nodes.items()}),
            'player_stats': copy.deepcopy(self.player_stats),
            'player_inventory': copy.deepcopy(self.player_inventory),
            'story_flags': copy.deepcopy(self.story_flags),
            'node_id_counter': self.node_id_counter,
            'project_settings': copy.deepcopy(self.project_settings),
            'active_node_id': self.active_node_id,
            'selected_node_ids': copy.deepcopy(self.selected_node_ids)
        }
        self.undo_stack.append(state)
        self.redo_stack.clear()
        if len(self.undo_stack) > 50: self.undo_stack.pop(0)

    def _restore_state(self, state):
        """Restores the project to a given state from the undo/redo stack."""
        self.nodes.clear()
        for node_id, node_data in state['nodes'].items():
            self.nodes[node_id] = DialogueNode.from_dict(node_data)
        
        self.player_stats = state['player_stats']
        self.player_inventory = state['player_inventory']
        self.story_flags = state['story_flags']
        self.node_id_counter = state['node_id_counter']
        self.project_settings = state['project_settings']
        self.active_node_id = state.get('active_node_id')
        self.selected_node_ids = state.get('selected_node_ids', [])
        
        self.canvas_manager.redraw_all_nodes()
        self.properties_panel.update_all_panels()

    def undo(self, event=None):
        """Reverts to the previous state in the undo stack."""
        if len(self.undo_stack) > 1:
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)
            previous_state = self.undo_stack[-1]
            self._restore_state(copy.deepcopy(previous_state))
            
    def redo(self, event=None):
        """Re-applies a state from the redo stack."""
        if self.redo_stack:
            state_to_restore = self.redo_stack.pop()
            self.undo_stack.append(state_to_restore)
            self._restore_state(copy.deepcopy(state_to_restore))

    def set_selection(self, new_selection_ids, active_node_id=None):
        """Sets the current selection and updates the UI accordingly."""
        self.selected_node_ids = new_selection_ids
        if active_node_id:
            self.active_node_id = active_node_id
        elif self.selected_node_ids:
            self.active_node_id = self.selected_node_ids[-1]
        else:
            self.active_node_id = None
        
        self.canvas_manager.update_selection_visuals()
        self.properties_panel.update_properties_panel()

    # --- Handler Methods for Core Logic ---
    def save_project_handler(self):
        save_project(self)

    def load_project_handler(self):
        load_project(self)

    def export_game_handler(self):
        export_game(self)
