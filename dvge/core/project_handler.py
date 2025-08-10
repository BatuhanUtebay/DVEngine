# dvge/core/project_handler.py
import json
import os
from tkinter import filedialog, messagebox
from ..data_models import DialogueNode, Quest, GameTimer
from ..game_mechanics import Enemy

class ProjectHandler:
    """Handles loading and saving of project files."""
    
    def __init__(self, app):
        self.app = app
    
    def save_project(self):
        """Saves the current project state to a .dvgproj file."""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".dvgproj", 
                filetypes=[("DVG Project Files", "*.dvgproj")]
            )
            if not filepath: 
                return False
                
            project_data = self._create_project_data()
            
            with open(filepath, 'w', encoding='utf-8') as f: 
                json.dump(project_data, f, indent=4)
                
            messagebox.showinfo("Save Successful", f"Project saved to {os.path.basename(filepath)}")
            return True
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save project: {e}")
            return False
    
    def load_project(self):
        """Loads a project from a .dvgproj file."""
        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("DVG Project Files", "*.dvgproj")]
            )
            if not filepath: 
                return False

            with open(filepath, 'r', encoding='utf-8') as f: 
                project_data = json.load(f)

            self._load_project_data(project_data)
            
            messagebox.showinfo("Load Successful", "Project loaded successfully.")
            return True
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load project: {e}")
            return False
    
    def _create_project_data(self):
        """Create the project data dictionary for saving."""
        return {
            "version": "1.0.0",
            "nodes": {node_id: node.to_dict() for node_id, node in self.app.nodes.items()},
            "player_stats": self.app.player_stats,
            "player_inventory": self.app.player_inventory,
            "story_flags": self.app.story_flags,
            "quests": {quest_id: quest.to_dict() for quest_id, quest in self.app.quests.items()},
            "variables": getattr(self.app, 'variables', {}),
            "enemies": {eid: e.to_dict() for eid, e in getattr(self.app, 'enemies', {}).items()},
            "timers": {tid: t.to_dict() for tid, t in getattr(self.app, 'timers', {}).items()},
            "node_id_counter": self.app.node_id_counter,
            "project_settings": self.app.project_settings
        }
    
    def _load_project_data(self, project_data):
        """Load project data into the application."""
        # Clear current state
        self.app.canvas.delete("all")
        self.app.nodes.clear()
        self.app.set_selection([])
        self.app.canvas_manager.draw_grid()

        # Reset to defaults first
        self.app._initialize_project_state()
        
        # Load data
        self.app.node_id_counter = project_data.get("node_id_counter", 0)
        self.app.player_stats = project_data.get("player_stats", {})
        self.app.player_inventory = project_data.get("player_inventory", [])
        self.app.story_flags = project_data.get("story_flags", {})
        self.app.variables = project_data.get("variables", {})
        self.app.project_settings = project_data.get("project_settings", {
            "font": "Merriweather", 
            "title_font": "Special Elite", 
            "background": ""
        })
        
        # Load quests
        self.app.quests.clear()
        for quest_id, quest_data in project_data.get("quests", {}).items():
            self.app.quests[quest_id] = Quest.from_dict(quest_data)

        # Load enemies
        self.app.enemies.clear()
        for enemy_id, enemy_data in project_data.get("enemies", {}).items():
            self.app.enemies[enemy_id] = Enemy.from_dict(enemy_data)

        # Load timers
        self.app.timers.clear()
        for timer_id, timer_data in project_data.get("timers", {}).items():
            self.app.timers[timer_id] = GameTimer.from_dict(timer_data)

        # Load nodes
        for node_id, node_data in project_data.get("nodes", {}).items():
            self.app.nodes[node_data['editor_data']['id']] = DialogueNode.from_dict(node_data)
        
        # Reset undo/redo
        self.app.undo_stack.clear()
        self.app.redo_stack.clear()
        self.app._save_state_for_undo("Load Project")

        # Update UI
        self.app.canvas_manager.redraw_all_nodes()
        self.app.properties_panel.update_all_panels()