# dvge/app.py
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import copy

from .constants import *
from .data_models import DialogueNode, Quest, GameTimer
from .game_mechanics import Enemy
from .ui.main_menu import create_menu
from .ui.properties_panel import PropertiesPanel
from .ui.canvas_manager import CanvasManager
from .ui.search_dialog import SearchDialog
from .core.project_handler import save_project, load_project
from .core.html_exporter import export_game

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
        # New state for advanced mechanics
        self.variables = {}
        self.enemies = {}
        self.timers = {}
        
        self.selected_node_ids = []
        self.active_node_id = None
        self.node_id_counter = 0
        self.project_settings = {}
        self.undo_stack = []
        self.redo_stack = []
        self._initialize_project_state()

        # --- UI Structure ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        create_menu(self)

        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10,0))
        header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header_frame, text="Dialogue Venture", font=FONT_TITLE).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(header_frame, text="Export Game", command=self.export_game_handler, 
                      fg_color=COLOR_SUCCESS, hover_color="#27AE60").grid(row=0, column=1, sticky="e")
        
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=3)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.main_frame, bg=COLOR_CANVAS_BACKGROUND, highlightthickness=0, borderwidth=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=(10,5))
        self.canvas_manager = CanvasManager(self)

        self.properties_panel = PropertiesPanel(self.main_frame, self)
        self.properties_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10))

        self.bind_events()
        self.properties_panel.update_all_panels()
        self.canvas_manager.draw_grid()
        self.canvas_manager.draw_placeholder_if_empty()
        
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
        
        self.project_settings = {"font": "Merriweather", "title_font": "Special Elite", "background": ""}
        self.node_id_counter = 0
        self.active_node_id = None
        self.selected_node_ids = []

    def bind_events(self):
        self.bind_all("<Control-z>", self.undo)
        self.bind_all("<Control-y>", self.redo)
        self.bind_all("<Control-f>", lambda e: SearchDialog(self))
        self.bind_all("<Delete>", self.canvas_manager.delete_selected_nodes)
        self.bind_all("<Control-s>", lambda event: self.save_project_handler())
        self.bind_all("<Control-o>", lambda event: self.load_project_handler())

    def _save_state_for_undo(self, action_name=""):
        """Saves a snapshot of the current project state for the undo stack."""
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
        if len(self.undo_stack) > 50: self.undo_stack.pop(0)

    def _restore_state(self, state):
        """Restores the project to a given state from the undo/redo stack."""
        self.nodes.clear()
        for node_id, node_data in state['nodes'].items():
            self.nodes[node_id] = DialogueNode.from_dict(node_data)
        
        self.quests.clear()
        for qid, qdata in state.get('quests', {}).items(): self.quests[qid] = Quest.from_dict(qdata)
        self.enemies.clear()
        for eid, edata in state.get('enemies', {}).items(): self.enemies[eid] = Enemy.from_dict(edata)
        self.timers.clear()
        for tid, tdata in state.get('timers', {}).items(): self.timers[tid] = GameTimer.from_dict(tdata)

        self.player_stats = state['player_stats']
        self.player_inventory = state['player_inventory']
        self.story_flags = state['story_flags']
        self.variables = state.get('variables', {})
        self.node_id_counter = state['node_id_counter']
        self.project_settings = state['project_settings']
        self.active_node_id = state.get('active_node_id')
        self.selected_node_ids = state.get('selected_node_ids', [])
        
        self.canvas_manager.redraw_all_nodes()
        self.properties_panel.update_all_panels()

    def undo(self, event=None):
        if len(self.undo_stack) > 1:
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)
            previous_state = self.undo_stack[-1]
            self._restore_state(copy.deepcopy(previous_state))
            
    def redo(self, event=None):
        if self.redo_stack:
            state_to_restore = self.redo_stack.pop()
            self.undo_stack.append(state_to_restore)
            self._restore_state(copy.deepcopy(state_to_restore))

    def set_selection(self, new_selection_ids, active_node_id=None):
        self.selected_node_ids = new_selection_ids
        if active_node_id:
            self.active_node_id = active_node_id
        elif self.selected_node_ids:
            self.active_node_id = self.selected_node_ids[-1]
        else:
            self.active_node_id = None
        
        self.canvas_manager.update_selection_visuals()
        self.properties_panel.update_properties_panel()

    def save_project_handler(self): save_project(self)
    def load_project_handler(self): load_project(self)
    def export_game_handler(self): export_game(self)
