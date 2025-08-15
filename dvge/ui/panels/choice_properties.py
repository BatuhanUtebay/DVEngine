import customtkinter as ctk
from ...constants import *
from ...models import DiceRollNode, CombatNode, ShopNode, RandomEventNode, TimerNode, InventoryNode
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
        
        if is_node_active:
            node = self.app.nodes[self.app.active_node_id]
            
            # Check if this node type supports standard choices
            supports_choices = hasattr(node, 'options')
            
            # Enable/disable add button based on node type
            self.add_choice_button.configure(
                state="normal" if supports_choices else "disabled"
            )
            
            if isinstance(node, DiceRollNode):
                self._create_dice_roll_widgets(node)
            elif isinstance(node, CombatNode):
                self._create_combat_widgets(node)
            elif isinstance(node, ShopNode):
                self._create_shop_widgets(node)
            elif isinstance(node, RandomEventNode):
                self._create_random_event_widgets(node)
            elif isinstance(node, TimerNode):
                self._create_timer_widgets(node)
            elif isinstance(node, InventoryNode):
                self._create_inventory_widgets(node)
            elif supports_choices:
                self._create_dialogue_options(node)
            else:
                self._show_no_choices_message()
        else:
            self.add_choice_button.configure(state="disabled")

    def _show_no_choices_message(self):
        """Shows a message when node type doesn't support choices."""
        info_frame = ctk.CTkFrame(self.options_frame, fg_color=COLOR_PRIMARY_FRAME)
        info_frame.pack(fill="x", pady=20, padx=10)
        
        ctk.CTkLabel(
            info_frame,
            text="This node type uses specialized navigation.\nConfigure in the 'Advanced' tab.",
            font=FONT_PROPERTIES_ENTRY,
            text_color=COLOR_TEXT_MUTED,
            justify="center"
        ).pack(pady=20)

    def _create_dice_roll_widgets(self, node):
        """Creates widgets for dice roll node configuration."""
        dice_frame = ctk.CTkFrame(self.options_frame, fg_color=COLOR_PRIMARY_FRAME)
        dice_frame.pack(fill="x", pady=5, padx=5)
        dice_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            dice_frame, text="Dice Roll Navigation", 
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
        node_ids = ["", "[End Game]"] + sorted([nid for nid in self.app.nodes.keys() if nid != node.id])
        
        # Success node
        ctk.CTkLabel(
            dice_frame, text="Success → Go to:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        success_node_combo = ctk.CTkComboBox(
            dice_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY
        )
        success_node_combo.set(node.success_node)
        success_node_combo.configure(
            command=lambda choice: self._on_dice_prop_change('success_node', choice)
        )
        success_node_combo.grid(row=4, column=1, sticky="ew", padx=10, pady=5)

        # Failure node
        ctk.CTkLabel(
            dice_frame, text="Failure → Go to:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=5, column=0, padx=10, pady=5, sticky="w")
        
        failure_node_combo = ctk.CTkComboBox(
            dice_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY
        )
        failure_node_combo.set(node.failure_node)
        failure_node_combo.configure(
            command=lambda choice: self._on_dice_prop_change('failure_node', choice)
        )
        failure_node_combo.grid(row=5, column=1, sticky="ew", padx=10, pady=(5,10))

    def _create_combat_widgets(self, node):
        """Creates widgets for combat node configuration."""
        combat_frame = ctk.CTkFrame(self.options_frame, fg_color=COLOR_PRIMARY_FRAME)
        combat_frame.pack(fill="x", pady=5, padx=5)
        combat_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            combat_frame, text="Combat Navigation", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_ACCENT
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")

        node_ids = ["", "[End Game]"] + sorted([nid for nid in self.app.nodes.keys() if nid != node.id])
        
        # Success node
        ctk.CTkLabel(
            combat_frame, text="Victory → Go to:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        success_node_combo = ctk.CTkComboBox(
            combat_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY
        )
        success_node_combo.set(node.successNode)
        success_node_combo.configure(
            command=lambda choice: self._on_combat_prop_change('successNode', choice)
        )
        success_node_combo.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        # Failure node
        ctk.CTkLabel(
            combat_frame, text="Defeat → Go to:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        failure_node_combo = ctk.CTkComboBox(
            combat_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY
        )
        failure_node_combo.set(node.failNode)
        failure_node_combo.configure(
            command=lambda choice: self._on_combat_prop_change('failNode', choice)
        )
        failure_node_combo.grid(row=2, column=1, sticky="ew", padx=10, pady=(5,10))

        # Add info about enemies
        ctk.CTkLabel(
            combat_frame, 
            text="Configure enemies in the 'Advanced' tab",
            font=FONT_PROPERTIES_ENTRY, text_color=COLOR_TEXT_MUTED
        ).grid(row=3, column=0, columnspan=2, padx=10, pady=(0,10))

    def _create_shop_widgets(self, node):
        """Creates widgets for shop node with exit choices."""
        shop_frame = ctk.CTkFrame(self.options_frame, fg_color=COLOR_PRIMARY_FRAME)
        shop_frame.pack(fill="x", pady=5, padx=5)
        shop_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            shop_frame, text="Shop Navigation", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_ACCENT
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")

        # Continue node (where to go when leaving shop)
        ctk.CTkLabel(
            shop_frame, text="Exit Shop → Go to:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        node_ids = ["", "[End Game]"] + sorted([nid for nid in self.app.nodes.keys() if nid != node.id])
        continue_combo = ctk.CTkComboBox(
            shop_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY
        )
        continue_combo.set(node.continue_node)
        continue_combo.configure(
            command=lambda choice: self._on_shop_prop_change('continue_node', choice)
        )
        continue_combo.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        # Add note about shop configuration
        ctk.CTkLabel(
            shop_frame, 
            text="Configure shop items and prices in the 'Advanced' tab",
            font=FONT_PROPERTIES_ENTRY, text_color=COLOR_TEXT_MUTED
        ).grid(row=2, column=0, columnspan=2, padx=10, pady=(0,10))

    def _create_random_event_widgets(self, node):
        """Creates widgets for random event node outcomes."""
        event_frame = ctk.CTkFrame(self.options_frame, fg_color=COLOR_PRIMARY_FRAME)
        event_frame.pack(fill="x", pady=5, padx=5)
        event_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            event_frame, text="Random Event Outcomes", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_ACCENT
        ).grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")

        # Auto trigger setting
        auto_var = ctk.BooleanVar(value=node.auto_trigger)
        auto_check = ctk.CTkCheckBox(
            event_frame, text="Trigger automatically on entry", 
            variable=auto_var,
            command=lambda: self._on_random_prop_change('auto_trigger', auto_var.get())
        )
        auto_check.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Outcomes list
        outcomes_label = ctk.CTkLabel(
            event_frame, text="Possible Outcomes (each leads to a different node):", 
            font=FONT_PROPERTIES_ENTRY
        )
        outcomes_label.grid(row=2, column=0, padx=10, pady=(10,5), sticky="w")
        
        for i, outcome in enumerate(node.random_outcomes):
            outcome_frame = ctk.CTkFrame(event_frame, fg_color=COLOR_SECONDARY_FRAME)
            outcome_frame.grid(row=3+i, column=0, sticky="ew", padx=10, pady=2)
            outcome_frame.grid_columnconfigure(2, weight=1)

            # Weight
            weight_entry = ctk.CTkEntry(outcome_frame, width=60, placeholder_text="Weight")
            weight_entry.insert(0, str(outcome.get('weight', 1)))
            weight_entry.grid(row=0, column=0, padx=5, pady=5)
            weight_entry.bind("<KeyRelease>", lambda e, idx=i, w=weight_entry: self._update_outcome(idx, 'weight', w.get()))

            # Description
            desc_entry = ctk.CTkEntry(outcome_frame, placeholder_text="Outcome description")
            desc_entry.insert(0, outcome.get('description', ''))
            desc_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            desc_entry.bind("<KeyRelease>", lambda e, idx=i, w=desc_entry: self._update_outcome(idx, 'description', w.get()))

            # Next node
            node_ids = ["", "[End Game]"] + sorted([nid for nid in self.app.nodes.keys() if nid != node.id])
            node_combo = ctk.CTkComboBox(outcome_frame, values=node_ids, width=150)
            node_combo.set(outcome.get('next_node', ''))
            node_combo.configure(command=lambda choice, idx=i: self._update_outcome(idx, 'next_node', choice))
            node_combo.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

            # Remove button
            ctk.CTkButton(
                outcome_frame, text="✕", width=30, height=30,
                fg_color="transparent", hover_color=COLOR_ERROR,
                command=lambda idx=i: self._remove_outcome(idx)
            ).grid(row=0, column=3, padx=5, pady=5)

        # Add outcome button
        ctk.CTkButton(
            event_frame, text="+ Add Outcome", 
            command=self._add_outcome
        ).grid(row=3+len(node.random_outcomes), column=0, pady=10, padx=10, sticky="ew")

    def _create_timer_widgets(self, node):
        """Creates widgets for timer node configuration."""
        timer_frame = ctk.CTkFrame(self.options_frame, fg_color=COLOR_PRIMARY_FRAME)
        timer_frame.pack(fill="x", pady=5, padx=5)
        timer_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            timer_frame, text="Timer Navigation", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_ACCENT
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")

        # Next node (where to go after timer expires)
        ctk.CTkLabel(
            timer_frame, text="After Timer → Go to:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        node_ids = ["", "[End Game]"] + sorted([nid for nid in self.app.nodes.keys() if nid != node.id])
        next_combo = ctk.CTkComboBox(
            timer_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY
        )
        next_combo.set(node.next_node)
        next_combo.configure(
            command=lambda choice: self._on_timer_prop_change('next_node', choice)
        )
        next_combo.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        # Add note about timer configuration
        ctk.CTkLabel(
            timer_frame, 
            text="Configure timer duration and options in the 'Advanced' tab",
            font=FONT_PROPERTIES_ENTRY, text_color=COLOR_TEXT_MUTED
        ).grid(row=2, column=0, columnspan=2, padx=10, pady=(0,10))

    def _create_inventory_widgets(self, node):
        """Creates widgets for inventory node configuration."""
        inv_frame = ctk.CTkFrame(self.options_frame, fg_color=COLOR_PRIMARY_FRAME)
        inv_frame.pack(fill="x", pady=5, padx=5)
        inv_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            inv_frame, text="Inventory Navigation", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_ACCENT
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")

        # Continue node (where to go when closing inventory)
        ctk.CTkLabel(
            inv_frame, text="Close Inventory → Go to:", font=FONT_PROPERTIES_ENTRY
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        node_ids = ["", "[End Game]"] + sorted([nid for nid in self.app.nodes.keys() if nid != node.id])
        continue_combo = ctk.CTkComboBox(
            inv_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY
        )
        continue_combo.set(node.continue_node)
        continue_combo.configure(
            command=lambda choice: self._on_inventory_prop_change('continue_node', choice)
        )
        continue_combo.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        # Add note about inventory configuration
        ctk.CTkLabel(
            inv_frame, 
            text="Configure crafting recipes and item actions in the 'Advanced' tab",
            font=FONT_PROPERTIES_ENTRY, text_color=COLOR_TEXT_MUTED
        ).grid(row=2, column=0, columnspan=2, padx=10, pady=(0,10))

    def _create_dialogue_options(self, node):
        """Creates widgets for dialogue options."""
        if not hasattr(node, 'options'):
            self._show_no_choices_message()
            return
            
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
        node_ids = ["", "[End Game]"] + sorted([nid for nid in self.app.nodes.keys() if nid != self.app.active_node_id])
        
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

    # Event handlers for dice roll nodes
    def _on_dice_prop_change(self, key, value):
        """Handles dice roll property changes."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if isinstance(node, DiceRollNode):
            self.app._save_state_for_undo("Change Dice Property")
            try:
                if key in ['num_dice', 'num_sides', 'success_threshold']:
                    setattr(node, key, int(value))
                else:
                    setattr(node, key, value)
            except ValueError:
                pass
            self.app.canvas_manager.redraw_node(self.app.active_node_id)
            self.app.canvas_manager.draw_connections()

    # Event handlers for combat nodes
    def _on_combat_prop_change(self, key, value):
        """Handles combat property changes."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if isinstance(node, CombatNode):
            self.app._save_state_for_undo("Change Combat Property")
            setattr(node, key, value)
            self.app.canvas_manager.redraw_node(self.app.active_node_id)
            self.app.canvas_manager.draw_connections()

    # Event handlers for shop nodes
    def _on_shop_prop_change(self, key, value):
        """Handles shop property changes."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if isinstance(node, ShopNode):
            self.app._save_state_for_undo("Change Shop Property")
            setattr(node, key, value)
            self.app.canvas_manager.redraw_node(self.app.active_node_id)
            self.app.canvas_manager.draw_connections()

    # Event handlers for random event nodes
    def _on_random_prop_change(self, key, value):
        """Handles random event property changes."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if isinstance(node, RandomEventNode):
            self.app._save_state_for_undo("Change Random Event Property")
            setattr(node, key, value)

    def _update_outcome(self, index, key, value):
        """Updates a random outcome."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if isinstance(node, RandomEventNode) and index < len(node.random_outcomes):
            self.app._save_state_for_undo("Update Outcome")
            if key == 'weight':
                try:
                    node.random_outcomes[index][key] = float(value)
                except ValueError:
                    node.random_outcomes[index][key] = 1
            else:
                node.random_outcomes[index][key] = value
            
            # Redraw connections if next_node changed
            if key == 'next_node':
                self.app.canvas_manager.draw_connections()

    def _add_outcome(self):
        """Adds a new random outcome."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if isinstance(node, RandomEventNode):
            self.app._save_state_for_undo("Add Outcome")
            node.random_outcomes.append({
                'weight': 1,
                'description': 'New outcome',
                'next_node': ''
            })
            self.update_panel()

    def _remove_outcome(self, index):
        """Removes a random outcome."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if isinstance(node, RandomEventNode) and index < len(node.random_outcomes):
            self.app._save_state_for_undo("Remove Outcome")
            del node.random_outcomes[index]
            self.update_panel()
            self.app.canvas_manager.draw_connections()

    # Event handlers for timer nodes
    def _on_timer_prop_change(self, key, value):
        """Handles timer property changes."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if isinstance(node, TimerNode):
            self.app._save_state_for_undo("Change Timer Property")
            setattr(node, key, value)
            self.app.canvas_manager.draw_connections()

    # Event handlers for inventory nodes
    def _on_inventory_prop_change(self, key, value):
        """Handles inventory property changes."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if isinstance(node, InventoryNode):
            self.app._save_state_for_undo("Change Inventory Property")
            setattr(node, key, value)
            self.app.canvas_manager.draw_connections()

    # Standard dialogue option handlers
    def _on_option_prop_change(self, index, key, value):
        """Handles option property changes."""
        if not self.app.active_node_id:
            return
        
        node = self.app.nodes[self.app.active_node_id]
        if hasattr(node, 'options') and index < len(node.options):
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
        if hasattr(node, 'options') and opt_idx < len(node.options):
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
        if hasattr(node, 'options') and opt_idx < len(node.options):
            self.app._save_state_for_undo("Add Effect")
            node.options[opt_idx]["effects"].append({
                'type': 'stat', 'subject': '', 'operator': '+=', 'value': 1
            })
            self.update_panel()
            self.app.canvas_manager.redraw_node(self.app.active_node_id)

    def add_option_to_node(self, node_id):
        """Adds a new option to the specified node."""
        if node_id and node_id in self.app.nodes:
            node = self.app.nodes[node_id]
            # Only add options to nodes that support them
            if hasattr(node, 'options'):
                self.app._save_state_for_undo("Add Choice")
                node.options.append({
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
        
        node = self.app.nodes[self.app.active_node_id]
        if hasattr(node, 'options') and index < len(node.options):
            self.app._save_state_for_undo("Remove Choice")
            del node.options[index]
            self.app.canvas_manager.redraw_node(self.app.active_node_id)
            self.update_panel()