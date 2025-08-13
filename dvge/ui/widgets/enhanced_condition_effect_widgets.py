# dvge/ui/widgets/enhanced_condition_effect_widgets.py

"""Enhanced condition/effect widgets with variable system support."""

import customtkinter as ctk
from ...constants import *


class EnhancedConditionEffectWidgets:
    """Enhanced widgets supporting the new variable system."""
    
    def __init__(self, app):
        self.app = app

    def create_variable_condition_widgets(self, parent, opt_idx, cond_idx, cond_data):
        """Creates widgets for variable-based conditions (e.g., gold >= 100)."""
        # Variable name selector
        available_vars = list(getattr(self.app, 'variables', {}).keys()) or ["gold", "score"]
        var_combo = ctk.CTkComboBox(
            parent, 
            values=available_vars, 
            width=80,
            command=lambda c: self._on_condition_prop_change(opt_idx, cond_idx, 'subject', c)
        )
        var_combo.set(cond_data.get("subject", ""))
        var_combo.pack(side="left", padx=2)
        
        # Comparison operator selector
        op_combo = ctk.CTkComboBox(
            parent, 
            values=["==", "!=", ">", "<", ">=", "<="], 
            width=50,
            command=lambda c: self._on_condition_prop_change(opt_idx, cond_idx, 'operator', c)
        )
        op_combo.set(cond_data.get("operator", ">="))
        op_combo.pack(side="left", padx=2)
        
        # Value input (supports expressions)
        val_entry = ctk.CTkEntry(parent, width=80, placeholder_text="Value or {var}")
        val_entry.insert(0, str(cond_data.get("value", "10")))
        val_entry.bind(
            "<KeyRelease>", 
            lambda e, w=val_entry: self._on_condition_prop_change(opt_idx, cond_idx, 'value', w.get())
        )
        val_entry.pack(side="left", padx=2, expand=True, fill="x")

    def create_variable_effect_widgets(self, parent, opt_idx, effect_idx, effect_data):
        """Creates widgets for variable-based effects with mathematical operations."""
        # Variable name selector
        available_vars = list(getattr(self.app, 'variables', {}).keys()) or ["gold", "score"]
        var_combo = ctk.CTkComboBox(
            parent, 
            values=available_vars, 
            width=80,
            command=lambda c: self._on_effect_prop_change(opt_idx, effect_idx, 'subject', c)
        )
        var_combo.set(effect_data.get("subject", ""))
        var_combo.pack(side="left", padx=2)
        
        # Enhanced operation selector
        op_combo = ctk.CTkComboBox(
            parent, 
            values=["=", "+=", "-=", "*=", "/=", "%=", "min", "max"], 
            width=50,
            command=lambda c: self._on_effect_prop_change(opt_idx, effect_idx, 'operator', c)
        )
        op_combo.set(effect_data.get("operator", "+="))
        op_combo.pack(side="left", padx=2)
        
        # Value input (supports expressions and variables)
        val_entry = ctk.CTkEntry(parent, width=100, placeholder_text="Value, {var}, or expression")
        val_entry.insert(0, str(effect_data.get("value", "1")))
        val_entry.bind(
            "<KeyRelease>", 
            lambda e, w=val_entry: self._on_effect_prop_change(opt_idx, effect_idx, 'value', w.get())
        )
        val_entry.pack(side="left", padx=2, expand=True, fill="x")

    def _on_condition_prop_change(self, opt_idx, cond_idx, key, value):
        """Handles changes to condition properties."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if (opt_idx < len(node.options) and 
            cond_idx < len(node.options[opt_idx].get("conditions", []))):
            
            self.app._save_state_for_undo("Change Condition")
            node.options[opt_idx]["conditions"][cond_idx][key] = value
            self.app.canvas_manager.redraw_node(self.app.active_node_id)

    def _on_effect_prop_change(self, opt_idx, effect_idx, key, value):
        """Handles changes to effect properties."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if (opt_idx < len(node.options) and 
            effect_idx < len(node.options[opt_idx].get("effects", []))):
            
            self.app._save_state_for_undo("Change Effect")
            node.options[opt_idx]["effects"][effect_idx][key] = value
            self.app.canvas_manager.redraw_node(self.app.active_node_id)