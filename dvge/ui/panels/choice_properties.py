# dvge/ui/panels/choice_properties.py

"""Choice properties tab for editing dialogue options and special nodes."""

import customtkinter as ctk
from ...constants import *
from ...models import DiceRollNode
from ..widgets.condition_effect_widgets import ConditionEffectWidgets


class ChoicePropertiesTab:
    """Handles the Choices tab in the properties panel."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.condition_effect_widgets = ConditionEffectWidgets(app)
        
        self._setup_layout()
        self._create_widgets()

    def _setup_layout(self):
        """Sets up the tab layout."""
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

    def _create_widgets(self):
        """Creates all widgets for the choices tab."""
        # Scrollable frame for options
        self.options_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.options_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.options_frame.grid_columnconfigure(0, weight=1)

        # Add choice button
        self.add_choice_button = ctk.CTkButton(
            self.parent, text="+ Add Choice", command=self._add_choice_from_panel
        )
        self.add_choice_button.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))

    def update_panel(self):
        """Updates the panel with current node data."""
        # Clear existing options
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        is_node_active = self.app.active_node_id and self.app.active_node_id in self.app.nodes
        
        # Enable/disable add button
        self.add_choice_button.configure(state="normal" if is_node_active else "disabled")

        if is_node_active:
            node = self.app.nodes[self.app.active_node_id]
            
            if isinstance(node, DiceRollNode):
                self._create_dice_roll_widgets(node)
            else:
                self._create_dialogue_options(node)

    def _create_dice_roll_widgets(self, node):
        """Creates widgets for dice roll node configuration."""
        dice_frame = ctk.CTkFrame(self.options_frame, fg_color=COLOR_PRIMARY_FRAME)
        dice_frame.pack(fill="x", pady=5, padx=5)
        dice_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            dice_frame, text="Dice Roll Settings", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_ACCENT
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        
        # Number of dice
        ctk.CTkLabel(
            dice_frame, text="Number of Dice:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        num_dice_entry = ctk.CTkEntry(dice_frame, font=FONT_PROPERTIES_ENTRY)
        num_dice_entry.insert(0, str(node.num_dice))
        num_dice_entry.grid(row=1, column=1, sticky="ew", padx=10)
        num_dice_entry.bind(
            "<KeyRelease>", 
            lambda e, w=num_dice_entry: self._on_dice_prop_change('num_dice', w.get())
        )

        # Number of sides
        ctk.CTkLabel(
            dice_frame, text="Number of Sides:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        num_sides_entry = ctk.CTkEntry(dice_frame, font=FONT_PROPERTIES_ENTRY)
        num_sides_entry.insert(0, str(node.num_sides))
        num_sides_entry.grid(row=2, column=1, sticky="ew", padx=10)
        num_sides_entry.bind(
            "<KeyRelease>", 
            lambda e, w=num_sides_entry: self._on_dice_prop_change('num_sides', w.get())
        )

        # Success threshold
        ctk.CTkLabel(
            dice_frame, text="Success Threshold:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        success_threshold_entry = ctk.CTkEntry(dice_frame, font=FONT_PROPERTIES_ENTRY)
        success_threshold_entry.insert(0, str(node.success_threshold))
        success_threshold_entry.grid(row=3, column=1, sticky="ew", padx=10)
        success_threshold_entry.bind(
            "<KeyRelease>", 
            lambda e, w=success_threshold_entry: self._on_dice_prop_change('success_threshold', w.get())
        )

        # Node selection combos
        node_ids = ["", "[End Game]"] + sorted(list(self.app.nodes.keys()))
        
        # Success node
        ctk.CTkLabel(
            dice_frame, text="Success Node:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        success_node_combo = ctk.CTkComboBox(
            dice_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY
        )
        success_node_combo.set(node.success_node)
        success_node_combo.configure(
            command=lambda choice: self._on_dice_prop_change('success_node', choice)
        )
        success_node_combo.grid(row=4, column=1, sticky="ew", padx=10)

        # Failure node
        ctk.CTkLabel(
            dice_frame, text="Failure Node:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=5, column=0, padx=10, pady=5, sticky="w")
        
        failure_node_combo = ctk.CTkComboBox(
            dice_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY
        )
        failure_node_combo.set(node.failure_node)
        failure_node_combo.configure(
            command=lambda choice: self._on_dice_prop_change('failure_node', choice)
        )
        failure_node_combo.grid(row=5, column=1, sticky="ew", padx=10)

    def _create_dialogue_options(self, node):
        """Creates widgets for dialogue options."""
        for i, option in enumerate(node.options):
            self._create_option_widget(i, option)

    def _create_option_widget(self, index, option_data):
        """Creates a widget for a single dialogue option."""
        option_frame = ctk.CTkFrame(self.options_frame, fg_color=COLOR_PRIMARY_FRAME)
        option_frame.pack(fill="x", pady=5, padx=5)
        option_frame.grid_columnconfigure(1, weight=1)

        # Header
        ctk.CTkLabel(
            option_frame, text=f"Choice #{index+1}", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_ACCENT
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10,5), sticky="w")
        
        # Option text
        ctk.CTkLabel(
            option_frame, text="Text:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        text_entry = ctk.CTkEntry(option_frame, font=FONT_PROPERTIES_ENTRY)
        text_entry.insert(0, option_data.get("text", ""))
        text_entry.grid(row=1, column=1, columnspan=3, sticky="ew", padx=10)
        text_entry.bind(
            "<KeyRelease>", 
            lambda e, i=index, w=text_entry: self._on_option_prop_change(i, 'text', w.get())
        )

        # Next node selection
        node_ids = ["", "[End Game]"] + sorted(list(self.app.nodes.keys()))
        
        ctk.CTkLabel(
            option_frame, text="Next Node:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        combobox = ctk.CTkComboBox(option_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY)
        combobox.set(option_data.get("nextNode", ""))
        combobox.configure(
            command=lambda choice, i=index: self._on_option_prop_change(i, 'nextNode', choice)
        )
        combobox.grid(row=2, column=1, columnspan=3, sticky="ew", padx=10)

        # Conditions and Effects
        self._create_conditions_effects_section(option_frame, index, option_data)
        
        # Remove button
        ctk.CTkButton(
            option_frame, text="Remove Choice", 
            fg_color=COLOR_ERROR, hover_color="#C0392B", height=28,
            command=lambda i=index: self._remove_option_from_node(i)
        ).grid(row=4, column=0, columnspan=4, pady=10, padx=10, sticky="ew")

    def _create_conditions_effects_section(self, parent, option_index, option_data):
        """Creates the conditions and effects section for an option."""
        cond_eff_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cond_eff_frame.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5)
        cond_eff_frame.grid_columnconfigure((0,1), weight=1)

        # Ensure conditions and effects exist
        if "conditions" not in option_data:
            option_data["conditions"] = []
        if "effects" not in option_data:
            option_data["effects"] = []

        # Conditions section
        conditions_frame = ctk.CTkFrame(cond_eff_frame, fg_color="transparent")
        conditions_frame.grid(row=0, column=0, sticky="nsew", padx=5)
        
        ctk.CTkLabel(
            conditions_frame, text="Conditions", font=(FONT_FAMILY, 10, "bold")
        ).pack(anchor="w")
        
        for cond_idx, cond in enumerate(option_data["conditions"]):
            self.condition_effect_widgets.create_condition_row(
                conditions_frame, option_index, cond_idx, cond, self.update_panel
            )
        
        ctk.CTkButton(
            conditions_frame, text="+ Condition", height=24,
            command=lambda oi=option_index: self._add_condition(oi)
        ).pack(fill="x", pady=5)

        # Effects section
        effects_frame = ctk.CTkFrame(cond_eff_frame, fg_color="transparent")
        effects_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        
        ctk.CTkLabel(
            effects_frame, text="Effects", font=(FONT_FAMILY, 10, "bold")
        ).pack(anchor="w")
        
        for effect_idx, effect in enumerate(option_data["effects"]):
            self.condition_effect_widgets.create_effect_row(
                effects_frame, option_index, effect_idx, effect, self.update_panel
            )
        
        ctk.CTkButton(
            effects_frame, text="+ Effect", height=24,
            command=lambda oi=option_index: self._add_effect(oi)
        ).pack(fill="x", pady=5)

    def _on_dice_prop_change(self, key, value):
        """Handles dice roll property changes."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if isinstance(node, DiceRollNode):
            self.app._save_state_for_undo("Change Dice Property")
            setattr(node, key, value)
            self.app.canvas_manager.redraw_node(self.app.active_node_id)

    def _on_option_prop_change(self, index, key, value):
        """Handles option property changes."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if index < len(node.options):
            self.app._save_state_for_undo("Change Option Property")
            node.options[index][key] = value
            
            if key == 'text':
                self.app.canvas_manager.redraw_node(self.app.active_node_id)
            elif 'Node' in key:
                self.app.canvas_manager.draw_connections()

    def _add_condition(self, opt_idx):
        """Adds a new condition to an option."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if opt_idx < len(node.options):
            self.app._save_state_for_undo("Add Condition")
            node.options[opt_idx]["conditions"].append({
                'type': 'stat', 'subject': '', 'operator': '>=', 'value': 10
            })
            self.update_panel()
            self.app.canvas_manager.redraw_node(self.app.active_node_id)

    def _add_effect(self, opt_idx):
        """Adds a new effect to an option."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if opt_idx < len(node.options):
            self.app._save_state_for_undo("Add Effect")
            node.options[opt_idx]["effects"].append({
                'type': 'stat', 'subject': '', 'operator': '+=', 'value': 1
            })
            self.update_panel()
            self.app.canvas_manager.redraw_node(self.app.active_node_id)

    def add_option_to_node(self, node_id):
        """Adds a new option to the specified node."""
        if node_id and node_id in self.app.nodes:
            self.app._save_state_for_undo("Add Choice")
            self.app.nodes[node_id].options.append({
                "text": "New Option", "nextNode": "", "conditions": [], "effects": []
            })
            return True
        return False

    def _add_choice_from_panel(self):
        """Adds a choice from the panel button."""
        if not self.app.active_node_id:
            return
        
        if self.add_option_to_node(self.app.active_node_id):
            self.app.canvas_manager.redraw_node(self.app.active_node_id)
            self.update_panel()

    def _remove_option_from_node(self, index):
        """Removes an option from the current node."""
        if not self.app.active_node_id:
            return
        
        self.app._save_state_for_undo("Remove Choice")
        del self.app.nodes[self.app.active_node_id].options[index]
        self.app.canvas_manager.redraw_node(self.app.active_node_id)
        self.update_panel()