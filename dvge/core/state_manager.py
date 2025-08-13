# dvge/core/state_manager.py

"""State management for undo/redo functionality."""

import copy
from tkinter import messagebox


class StateManager:
    """Handles undo/redo functionality and state snapshots."""
    
    def __init__(self, app):
        self.app = app
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_states = 50
    
    def save_state(self, action_name=""):
        """Saves a snapshot of the current project state for the undo stack."""
        try:
            state = self._create_state_snapshot()
            self.undo_stack.append(state)
            self.redo_stack.clear()
            
            # Limit undo stack size
            if len(self.undo_stack) > self.max_undo_states:
                self.undo_stack.pop(0)
                
        except Exception as e:
            print(f"Error saving state for undo: {e}")
    
    def undo(self):
        """Undo the last action."""
        if len(self.undo_stack) > 1:
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)
            previous_state = self.undo_stack[-1]
            self._restore_state(copy.deepcopy(previous_state))
            return True
        return False
    
    def redo(self):
        """Redo the last undone action."""
        if self.redo_stack:
            state_to_restore = self.redo_stack.pop()
            self.undo_stack.append(state_to_restore)
            self._restore_state(copy.deepcopy(state_to_restore))
            return True
        return False
    
    def clear_history(self):
        """Clears the undo/redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def _create_state_snapshot(self):
        """Creates a complete snapshot of the current application state."""
        return {
            'nodes': {nid: n.to_dict() for nid, n in self.app.nodes.items()},
            'player_stats': copy.deepcopy(self.app.player_stats),
            'player_inventory': copy.deepcopy(self.app.player_inventory),
            'story_flags': copy.deepcopy(self.app.story_flags),
            'quests': {qid: q.to_dict() for qid, q in self.app.quests.items()},
            'variables': copy.deepcopy(getattr(self.app, 'variables', {})),
            'enemies': {eid: e.to_dict() for eid, e in getattr(self.app, 'enemies', {}).items()},
            'timers': {tid: t.to_dict() for tid, t in getattr(self.app, 'timers', {}).items()},
            'node_id_counter': self.app.node_id_counter,
            'project_settings': copy.deepcopy(self.app.project_settings),
            'active_node_id': self.app.active_node_id,
            'selected_node_ids': copy.deepcopy(self.app.selected_node_ids)
        }
    
    def _restore_state(self, state):
        """Restores the project to a given state from the undo/redo stack."""
        try:
            from ..models import create_node_from_dict, Quest, GameTimer, Enemy
            
            # Clear current state
            self.app.nodes.clear()
            self.app.quests.clear()
            self.app.enemies.clear()
            self.app.timers.clear()
            
            # Restore nodes
            for node_id, node_data in state['nodes'].items():
                self.app.nodes[node_id] = create_node_from_dict(node_data)
            
            # Restore other data
            for qid, qdata in state.get('quests', {}).items():
                self.app.quests[qid] = Quest.from_dict(qdata)
            for eid, edata in state.get('enemies', {}).items():
                self.app.enemies[eid] = Enemy.from_dict(edata)
            for tid, tdata in state.get('timers', {}).items():
                self.app.timers[tid] = GameTimer.from_dict(tdata)

            self.app.player_stats = state['player_stats']
            self.app.player_inventory = state['player_inventory']
            self.app.story_flags = state['story_flags']
            self.app.variables = state.get('variables', {})
            self.app.node_id_counter = state['node_id_counter']
            self.app.project_settings = state['project_settings']
            self.app.active_node_id = state.get('active_node_id')
            self.app.selected_node_ids = state.get('selected_node_ids', [])
            
            # Update UI
            self.app.canvas_manager.redraw_all_nodes()
            self.app.properties_panel.update_all_panels()
            
        except Exception as e:
            print(f"Error restoring state: {e}")
            messagebox.showerror("Error", f"Failed to restore state: {e}")