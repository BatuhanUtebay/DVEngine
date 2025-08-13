# dvge/ui/widgets/condition_effect_widgets.py

"""Widgets for creating and editing conditions and effects on dialogue choices."""

import customtkinter as ctk
from ...constants import *
from .enhanced_condition_effect_widgets import EnhancedConditionEffectWidgets


class ConditionEffectWidgets:
    """Handles creation of condition and effect UI widgets for dialogue choices."""
    
    def __init__(self, app):
        self.app = app
        self.enhanced_widgets = EnhancedConditionEffectWidgets(app)

    def create_condition_row(self, parent, opt_idx, cond_idx, cond_data, update_callback):
        """Creates a complete row for editing a single condition."""
        row_frame = ctk.CTkFrame(parent, fg_color=COLOR_SECONDARY_FRAME)
        row_frame.pack(fill="x", pady=2, ipady=4)
        
        cond_type = cond_data.get("type", "stat")
        
        def on_type_change(choice):
            cond_data["type"] = choice.lower()
            update_callback()
        
        # Type selector dropdown
        type_combo = ctk.CTkComboBox(
            row_frame, 
            values=["Stat", "Item", "Flag", "Quest", "Variable"], 
            width=75, 
            command=on_type_change, 
            font=FONT_PROPERTIES_ENTRY
        )
        type_combo.set(cond_type.capitalize())
        type_combo.pack(side="left", padx=(5,2))

        # Create type-specific widgets based on condition type
        if cond_type == "stat":
            self._create_stat_condition_widgets(row_frame, opt_idx, cond_idx, cond_data)
        elif cond_type == "item":
            self._create_item_condition_widgets(row_frame, opt_idx, cond_idx, cond_data)
        elif cond_type == "flag":
            self._create_flag_condition_widgets(row_frame, opt_idx, cond_idx, cond_data)
        elif cond_type == "quest":
            self._create_quest_condition_widgets(row_frame, opt_idx, cond_idx, cond_data)
        elif cond_type == "variable":
            self.enhanced_widgets.create_variable_condition_widgets(row_frame, opt_idx, cond_idx, cond_data)

        # Remove button for this condition
        remove_btn = ctk.CTkButton(
            row_frame, 
            text="✕", 
            width=28, 
            height=28, 
            fg_color="transparent", 
            hover_color=COLOR_ERROR,
            command=lambda: self._remove_condition(opt_idx, cond_idx, update_callback)
        )
        remove_btn.pack(side="right", padx=(2,5))

    def create_effect_row(self, parent, opt_idx, effect_idx, effect_data, update_callback):
        """Creates a complete row for editing a single effect."""
        row_frame = ctk.CTkFrame(parent, fg_color=COLOR_SECONDARY_FRAME)
        row_frame.pack(fill="x", pady=2, ipady=4)
        
        effect_type = effect_data.get("type", "stat")
        
        def on_type_change(choice):
            effect_data["type"] = choice.lower()
            update_callback()
        
        # Type selector dropdown
        type_combo = ctk.CTkComboBox(
            row_frame, 
            values=["Stat", "Item", "Flag", "Quest", "Variable"], 
            width=75, 
            command=on_type_change, 
            font=FONT_PROPERTIES_ENTRY
        )
        type_combo.set(effect_type.capitalize())
        type_combo.pack(side="left", padx=(5,2))

        # Create type-specific widgets based on effect type
        if effect_type == "stat":
            self._create_stat_effect_widgets(row_frame, opt_idx, effect_idx, effect_data)
        elif effect_type == "item":
            self._create_item_effect_widgets(row_frame, opt_idx, effect_idx, effect_data)
        elif effect_type == "flag":
            self._create_flag_effect_widgets(row_frame, opt_idx, effect_idx, effect_data)
        elif effect_type == "quest":
            self._create_quest_effect_widgets(row_frame, opt_idx, effect_idx, effect_data)
        elif effect_type == "variable":
            self.enhanced_widgets.create_variable_effect_widgets(row_frame, opt_idx, effect_idx, effect_data)

        # Remove button for this effect
        remove_btn = ctk.CTkButton(
            row_frame, 
            text="✕", 
            width=28, 
            height=28, 
            fg_color="transparent", 
            hover_color=COLOR_ERROR,
            command=lambda: self._remove_effect(opt_idx, effect_idx, update_callback)
        )
        remove_btn.pack(side="right", padx=(2,5))

    def _create_stat_condition_widgets(self, parent, opt_idx, cond_idx, cond_data):
        """Creates widgets for stat-based conditions (e.g., strength >= 10)."""
        # Stat name selector
        available_stats = list(self.app.player_stats.keys()) if self.app.player_stats else ["health", "strength"]
        stat_combo = ctk.CTkComboBox(
            parent, 
            values=available_stats, 
            width=80,
            command=lambda c: self._on_condition_prop_change(opt_idx, cond_idx, 'subject', c)
        )
        stat_combo.set(cond_data.get("subject", ""))
        stat_combo.pack(side="left", padx=2)
        
        # Comparison operator selector
        op_combo = ctk.CTkComboBox(
            parent, 
            values=["==", "!=", ">", "<", ">=", "<="], 
            width=50,
            command=lambda c: self._on_condition_prop_change(opt_idx, cond_idx, 'operator', c)
        )
        op_combo.set(cond_data.get("operator", ">="))
        op_combo.pack(side="left", padx=2)
        
        # Value input
        val_entry = ctk.CTkEntry(parent, width=60)
        val_entry.insert(0, str(cond_data.get("value", "10")))
        val_entry.bind(
            "<KeyRelease>", 
            lambda e, w=val_entry: self._on_condition_prop_change(opt_idx, cond_idx, 'value', w.get())
        )
        val_entry.pack(side="left", padx=2, expand=True, fill="x")

    def _create_item_condition_widgets(self, parent, opt_idx, cond_idx, cond_data):
        """Creates widgets for item-based conditions (e.g., has 'Magic Key')."""
        # Item name input
        item_entry = ctk.CTkEntry(parent, placeholder_text="Item name", width=120)
        item_entry.insert(0, cond_data.get("subject", ""))
        item_entry.bind(
            "<KeyRelease>", 
            lambda e, w=item_entry: self._on_condition_prop_change(opt_idx, cond_idx, 'subject', w.get())
        )
        item_entry.pack(side="left", padx=2, expand=True, fill="x")
        
        # Has/Doesn't have selector
        has_combo = ctk.CTkComboBox(parent, values=["has", "doesn't have"], width=100)
        has_combo.set(cond_data.get("operator", "has"))
        has_combo.configure(
            command=lambda c: self._on_condition_prop_change(opt_idx, cond_idx, 'operator', c)
        )
        has_combo.pack(side="left", padx=2)

    def _create_flag_condition_widgets(self, parent, opt_idx, cond_idx, cond_data):
        """Creates widgets for flag-based conditions (e.g., visited_castle is true)."""
        # Flag name selector
        available_flags = list(self.app.story_flags.keys()) if self.app.story_flags else ["flag1", "flag2"]
        flag_combo = ctk.CTkComboBox(
            parent, 
            values=available_flags, 
            width=100,
            command=lambda c: self._on_condition_prop_change(opt_idx, cond_idx, 'subject', c)
        )
        flag_combo.set(cond_data.get("subject", ""))
        flag_combo.pack(side="left", padx=2)
        
        # Is/Is not selector
        is_combo = ctk.CTkComboBox(parent, values=["is", "is not"], width=60)
        is_combo.set(cond_data.get("operator", "is"))
        is_combo.configure(
            command=lambda c: self._on_condition_prop_change(opt_idx, cond_idx, 'operator', c)
        )
        is_combo.pack(side="left", padx=2)
        
        # True/False value selector
        value_combo = ctk.CTkComboBox(parent, values=["true", "false"], width=60)
        value_combo.set(str(cond_data.get("value", "true")).lower())
        value_combo.configure(
            command=lambda c: self._on_condition_prop_change(opt_idx, cond_idx, 'value', c == "true")
        )
        value_combo.pack(side="left", padx=2)

    def _create_quest_condition_widgets(self, parent, opt_idx, cond_idx, cond_data):
        """Creates widgets for quest-based conditions (e.g., main_quest is completed)."""
        # Quest name selector
        available_quests = list(self.app.quests.keys()) if self.app.quests else ["quest1", "quest2"]
        quest_combo = ctk.CTkComboBox(
            parent, 
            values=available_quests, 
            width=100,
            command=lambda c: self._on_condition_prop_change(opt_idx, cond_idx, 'subject', c)
        )
        quest_combo.set(cond_data.get("subject", ""))
        quest_combo.pack(side="left", padx=2)
        
        # Is/Is not selector
        is_combo = ctk.CTkComboBox(parent, values=["is", "is not"], width=60)
        is_combo.set(cond_data.get("operator", "is"))
        is_combo.configure(
            command=lambda c: self._on_condition_prop_change(opt_idx, cond_idx, 'operator', c)
        )
        is_combo.pack(side="left", padx=2)
        
        # Quest state selector
        state_combo = ctk.CTkComboBox(parent, values=["active", "completed", "failed"], width=80)
        state_combo.set(cond_data.get("value", "completed"))
        state_combo.configure(
            command=lambda c: self._on_condition_prop_change(opt_idx, cond_idx, 'value', c)
        )
        state_combo.pack(side="left", padx=2)

    def _create_stat_effect_widgets(self, parent, opt_idx, effect_idx, effect_data):
        """Creates widgets for stat-based effects (e.g., strength += 5)."""
        # Stat name selector
        available_stats = list(self.app.player_stats.keys()) if self.app.player_stats else ["health", "strength"]
        stat_combo = ctk.CTkComboBox(
            parent, 
            values=available_stats, 
            width=80,
            command=lambda c: self._on_effect_prop_change(opt_idx, effect_idx, 'subject', c)
        )
        stat_combo.set(effect_data.get("subject", ""))
        stat_combo.pack(side="left", padx=2)
        
        # Operation selector (set, add, subtract)
        op_combo = ctk.CTkComboBox(
            parent, 
            values=["=", "+=", "-="], 
            width=50,
            command=lambda c: self._on_effect_prop_change(opt_idx, effect_idx, 'operator', c)
        )
        op_combo.set(effect_data.get("operator", "+="))
        op_combo.pack(side="left", padx=2)
        
        # Value input
        val_entry = ctk.CTkEntry(parent, width=60)
        val_entry.insert(0, str(effect_data.get("value", "1")))
        val_entry.bind(
            "<KeyRelease>", 
            lambda e, w=val_entry: self._on_effect_prop_change(opt_idx, effect_idx, 'value', w.get())
        )
        val_entry.pack(side="left", padx=2, expand=True, fill="x")

    def _create_item_effect_widgets(self, parent, opt_idx, effect_idx, effect_data):
        """Creates widgets for item-based effects (e.g., add 'Magic Sword')."""
        # Add/Remove action selector
        action_combo = ctk.CTkComboBox(parent, values=["add", "remove"], width=70)
        action_combo.set(effect_data.get("operator", "add"))
        action_combo.configure(
            command=lambda c: self._on_effect_prop_change(opt_idx, effect_idx, 'operator', c)
        )
        action_combo.pack(side="left", padx=2)
        
        # Item name input
        item_entry = ctk.CTkEntry(parent, placeholder_text="Item name", width=120)
        item_entry.insert(0, effect_data.get("subject", ""))
        item_entry.bind(
            "<KeyRelease>", 
            lambda e, w=item_entry: self._on_effect_prop_change(opt_idx, effect_idx, 'subject', w.get())
        )
        item_entry.pack(side="left", padx=2, expand=True, fill="x")

    def _create_flag_effect_widgets(self, parent, opt_idx, effect_idx, effect_data):
        """Creates widgets for flag-based effects (e.g., set visited_castle to true)."""
        # "Set" label
        set_label = ctk.CTkLabel(parent, text="Set", width=30)
        set_label.pack(side="left", padx=2)
        
        # Flag name selector
        available_flags = list(self.app.story_flags.keys()) if self.app.story_flags else ["flag1", "flag2"]
        flag_combo = ctk.CTkComboBox(
            parent, 
            values=available_flags, 
            width=100,
            command=lambda c: self._on_effect_prop_change(opt_idx, effect_idx, 'subject', c)
        )
        flag_combo.set(effect_data.get("subject", ""))
        flag_combo.pack(side="left", padx=2)
        
        # "to" label
        to_label = ctk.CTkLabel(parent, text="to", width=20)
        to_label.pack(side="left", padx=2)
        
        # True/False value selector
        value_combo = ctk.CTkComboBox(parent, values=["true", "false"], width=60)
        value_combo.set(str(effect_data.get("value", "true")).lower())
        value_combo.configure(
            command=lambda c: self._on_effect_prop_change(opt_idx, effect_idx, 'value', c == "true")
        )
        value_combo.pack(side="left", padx=2)

    def _create_quest_effect_widgets(self, parent, opt_idx, effect_idx, effect_data):
        """Creates widgets for quest-based effects (e.g., set main_quest to completed)."""
        # "Set" label
        set_label = ctk.CTkLabel(parent, text="Set", width=30)
        set_label.pack(side="left", padx=2)
        
        # Quest name selector
        available_quests = list(self.app.quests.keys()) if self.app.quests else ["quest1", "quest2"]
        quest_combo = ctk.CTkComboBox(
            parent, 
            values=available_quests, 
            width=100,
            command=lambda c: self._on_effect_prop_change(opt_idx, effect_idx, 'subject', c)
        )
        quest_combo.set(effect_data.get("subject", ""))
        quest_combo.pack(side="left", padx=2)
        
        # "to" label
        to_label = ctk.CTkLabel(parent, text="to", width=20)
        to_label.pack(side="left", padx=2)
        
        # Quest state selector
        state_combo = ctk.CTkComboBox(parent, values=["active", "completed", "failed"], width=80)
        state_combo.set(effect_data.get("value", "active"))
        state_combo.configure(
            command=lambda c: self._on_effect_prop_change(opt_idx, effect_idx, 'value', c)
        )
        state_combo.pack(side="left", padx=2)

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

    def _remove_condition(self, opt_idx, cond_idx, update_callback):
        """Removes a condition from an option."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if (opt_idx < len(node.options) and 
            cond_idx < len(node.options[opt_idx].get("conditions", []))):
            
            self.app._save_state_for_undo("Remove Condition")
            del node.options[opt_idx]["conditions"][cond_idx]
            update_callback()
            self.app.canvas_manager.redraw_node(self.app.active_node_id)

    def _remove_effect(self, opt_idx, effect_idx, update_callback):
        """Removes an effect from an option."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if (opt_idx < len(node.options) and 
            effect_idx < len(node.options[opt_idx].get("effects", []))):
            
            self.app._save_state_for_undo("Remove Effect")
            del node.options[opt_idx]["effects"][effect_idx]
            update_callback()
            self.app.canvas_manager.redraw_node(self.app.active_node_id)