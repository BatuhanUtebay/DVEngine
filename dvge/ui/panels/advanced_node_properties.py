# dvge/ui/panels/advanced_node_properties.py

"""Advanced node properties for specialized node types."""

import customtkinter as ctk
from tkinter import messagebox
from ...constants import *
from ...models import ShopNode, RandomEventNode, TimerNode, InventoryNode


class AdvancedNodePropertiesTab:
    """Handles advanced node type properties in a separate tab."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.current_node_type = None
        
        self._setup_layout()
        self._create_widgets()

    def _setup_layout(self):
        """Sets up the tab layout."""
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)

    def _create_widgets(self):
        """Creates all widgets for the advanced properties tab."""
        # Node type selector
        type_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        type_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        type_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            type_frame, text="Node Type:", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_TEXT_MUTED
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.type_combo = ctk.CTkComboBox(
            type_frame, 
            values=["Dialogue", "Shop", "RandomEvent", "Timer", "Inventory", "DiceRoll", "Combat"],
            command=self._on_type_change,
            font=FONT_PROPERTIES_ENTRY
        )
        self.type_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Scrollable content area for type-specific properties
        self.content_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        self.content_frame.grid_columnconfigure(0, weight=1)

    def update_panel(self):
        """Updates the panel with current node data."""
        is_node_active = self.app.active_node_id and self.app.active_node_id in self.app.nodes
        
        # Enable/disable type selector
        state = "normal" if is_node_active else "disabled"
        self.type_combo.configure(state=state)
        
        if is_node_active:
            node = self.app.nodes[self.app.active_node_id]
            node_type = type(node).__name__
            self.type_combo.set(node_type)
            self.current_node_type = node_type
            self._update_content_for_type(node_type, node)
        else:
            self.type_combo.set("Dialogue")
            self._clear_content()

    def _on_type_change(self, new_type):
        """Handles node type changes."""
        if not self.app.active_node_id:
            return
            
        current_node = self.app.nodes[self.app.active_node_id]
        current_type = type(current_node).__name__
        
        if new_type == current_type:
            return
            
        # Confirm type change
        if not messagebox.askyesno(
            "Change Node Type", 
            f"Change node type from {current_type} to {new_type}?\n"
            "This will reset node-specific properties."
        ):
            self.type_combo.set(current_type)
            return
        
        # Convert node type
        self._convert_node_type(current_node, new_type)

    def _convert_node_type(self, current_node, new_type):
        """Converts a node to a different type."""
        self.app._save_state_for_undo("Change Node Type")
        
        # Preserve common properties
        common_props = {
            'x': current_node.x,
            'y': current_node.y,
            'node_id': current_node.id,
            'npc': current_node.npc,
            'text': current_node.text,
            'theme': current_node.backgroundTheme,
            'chapter': current_node.chapter,
            'color': current_node.color,
            'backgroundImage': current_node.backgroundImage,
            'audio': current_node.audio,
            'music': current_node.music
        }
        
        # Create new node based on type
        if new_type == "Shop":
            new_node = ShopNode(**common_props)
        elif new_type == "RandomEvent":
            new_node = RandomEventNode(**common_props)
        elif new_type == "Timer":
            new_node = TimerNode(**common_props)
        elif new_type == "Inventory":
            new_node = InventoryNode(**common_props)
        else:
            # Import other node types
            from ...models import DialogueNode, DiceRollNode, CombatNode
            if new_type == "DiceRoll":
                new_node = DiceRollNode(**common_props)
            elif new_type == "Combat":
                new_node = CombatNode(**common_props)
            else:  # Default to Dialogue
                new_node = DialogueNode(**common_props)
                # Preserve options for dialogue nodes
                if hasattr(current_node, 'options'):
                    new_node.options = current_node.options
        
        # Replace in app
        self.app.nodes[current_node.id] = new_node
        
        # Update visuals
        self.app.canvas_manager.redraw_node(current_node.id)
        self.update_panel()

    def _update_content_for_type(self, node_type, node):
        """Updates content area based on node type."""
        self._clear_content()
        
        if node_type == "Shop":
            self._create_shop_properties(node)
        elif node_type == "RandomEvent":
            self._create_random_event_properties(node)
        elif node_type == "Timer":
            self._create_timer_properties(node)
        elif node_type == "Inventory":
            self._create_inventory_properties(node)
        else:
            self._create_standard_properties_info()

    def _clear_content(self):
        """Clears the content area."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _create_shop_properties(self, node):
        """Creates shop-specific property widgets."""
        # Currency variable
        currency_frame = self._create_property_frame("Currency Variable")
        currency_entry = ctk.CTkEntry(currency_frame, font=FONT_PROPERTIES_ENTRY)
        currency_entry.insert(0, node.currency_variable)
        currency_entry.pack(fill="x", pady=5)
        currency_entry.bind("<KeyRelease>", lambda e: self._update_shop_property(node, 'currency_variable', currency_entry.get()))
        
        # Continue node
        continue_frame = self._create_property_frame("Continue to Node")
        node_ids = ["", "[End Game]"] + sorted(list(self.app.nodes.keys()))
        continue_combo = ctk.CTkComboBox(continue_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY)
        continue_combo.set(node.continue_node)
        continue_combo.configure(command=lambda choice: self._update_shop_property(node, 'continue_node', choice))
        continue_combo.pack(fill="x", pady=5)
        
        # Items for sale
        sale_frame = self._create_property_frame("Items for Sale")
        self._create_shop_items_list(sale_frame, node.items_for_sale, "sale", node)
        
        # Items to buy
        buy_frame = self._create_property_frame("Items Shop Buys")
        self._create_shop_items_list(buy_frame, node.items_to_buy, "buy", node)

    def _create_random_event_properties(self, node):
        """Creates random event-specific property widgets."""
        # Auto trigger
        auto_frame = self._create_property_frame("Auto Trigger")
        auto_var = ctk.BooleanVar(value=node.auto_trigger)
        auto_check = ctk.CTkCheckBox(
            auto_frame, text="Trigger automatically", 
            variable=auto_var,
            command=lambda: self._update_random_property(node, 'auto_trigger', auto_var.get())
        )
        auto_check.pack(pady=5)
        
        # Random outcomes
        outcomes_frame = self._create_property_frame("Random Outcomes")
        self._create_outcomes_list(outcomes_frame, node.random_outcomes, node)

    def _create_timer_properties(self, node):
        """Creates timer-specific property widgets."""
        # Wait time
        time_frame = self._create_property_frame("Wait Time")
        time_subframe = ctk.CTkFrame(time_frame, fg_color="transparent")
        time_subframe.pack(fill="x", pady=5)
        time_subframe.grid_columnconfigure(0, weight=1)
        
        time_entry = ctk.CTkEntry(time_subframe, font=FONT_PROPERTIES_ENTRY, width=100)
        time_entry.insert(0, str(node.wait_time))
        time_entry.grid(row=0, column=0, padx=(0,5), sticky="ew")
        time_entry.bind("<KeyRelease>", lambda e: self._update_timer_property(node, 'wait_time', time_entry.get()))
        
        unit_combo = ctk.CTkComboBox(
            time_subframe, values=["seconds", "minutes", "hours", "days"], 
            width=100, font=FONT_PROPERTIES_ENTRY
        )
        unit_combo.set(node.time_unit)
        unit_combo.configure(command=lambda choice: self._update_timer_property(node, 'time_unit', choice))
        unit_combo.grid(row=0, column=1)
        
        # Next node
        next_frame = self._create_property_frame("Next Node")
        node_ids = ["", "[End Game]"] + sorted(list(self.app.nodes.keys()))
        next_combo = ctk.CTkComboBox(next_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY)
        next_combo.set(node.next_node)
        next_combo.configure(command=lambda choice: self._update_timer_property(node, 'next_node', choice))
        next_combo.pack(fill="x", pady=5)
        
        # Options
        options_frame = self._create_property_frame("Timer Options")
        
        countdown_var = ctk.BooleanVar(value=node.show_countdown)
        ctk.CTkCheckBox(
            options_frame, text="Show countdown", 
            variable=countdown_var,
            command=lambda: self._update_timer_property(node, 'show_countdown', countdown_var.get())
        ).pack(anchor="w", pady=2)
        
        skip_var = ctk.BooleanVar(value=node.allow_skip)
        ctk.CTkCheckBox(
            options_frame, text="Allow skip", 
            variable=skip_var,
            command=lambda: self._update_timer_property(node, 'allow_skip', skip_var.get())
        ).pack(anchor="w", pady=2)

    def _create_inventory_properties(self, node):
        """Creates inventory-specific property widgets."""
        # Continue node
        continue_frame = self._create_property_frame("Continue to Node")
        node_ids = ["", "[End Game]"] + sorted(list(self.app.nodes.keys()))
        continue_combo = ctk.CTkComboBox(continue_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY)
        continue_combo.set(node.continue_node)
        continue_combo.configure(command=lambda choice: self._update_inventory_property(node, 'continue_node', choice))
        continue_combo.pack(fill="x", pady=5)
        
        # Auto open
        auto_frame = self._create_property_frame("Auto Open")
        auto_var = ctk.BooleanVar(value=node.auto_open)
        auto_check = ctk.CTkCheckBox(
            auto_frame, text="Open inventory automatically", 
            variable=auto_var,
            command=lambda: self._update_inventory_property(node, 'auto_open', auto_var.get())
        )
        auto_check.pack(pady=5)
        
        # Crafting recipes
        recipes_frame = self._create_property_frame("Crafting Recipes")
        self._create_recipes_list(recipes_frame, node.crafting_recipes, node)
        
        # Item actions
        actions_frame = self._create_property_frame("Item Actions")
        self._create_actions_list(actions_frame, node.item_actions, node)

    def _create_standard_properties_info(self):
        """Shows info for standard node types."""
        info_frame = ctk.CTkFrame(self.content_frame, fg_color=COLOR_PRIMARY_FRAME)
        info_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            info_frame, 
            text="This node type uses standard properties.\n"
            "Configure options in the 'Choices' tab.",
            font=FONT_PROPERTIES_ENTRY,
            justify="center"
        ).pack(pady=20)

    def _create_property_frame(self, title):
        """Creates a labeled frame for a property section."""
        frame = ctk.CTkFrame(self.content_frame, fg_color=COLOR_PRIMARY_FRAME)
        frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(
            frame, text=title, 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_ACCENT
        ).pack(anchor="w", padx=10, pady=(10,5))
        
        return frame

    def _create_shop_items_list(self, parent, items, item_type, node):
        """Creates a list of shop items with add/remove functionality."""
        # Items list
        for i, item in enumerate(items):
            item_frame = ctk.CTkFrame(parent, fg_color=COLOR_SECONDARY_FRAME)
            item_frame.pack(fill="x", pady=2, padx=10)
            item_frame.grid_columnconfigure(0, weight=1)
            
            # Item name
            name_entry = ctk.CTkEntry(item_frame, placeholder_text="Item name")
            name_entry.insert(0, item.get('name', ''))
            name_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            name_entry.bind("<KeyRelease>", lambda e, idx=i, w=name_entry: self._update_shop_item(node, item_type, idx, 'name', w.get()))
            
            # Price
            price_entry = ctk.CTkEntry(item_frame, placeholder_text="Price", width=80)
            price_entry.insert(0, str(item.get('price', 0)))
            price_entry.grid(row=0, column=1, padx=5, pady=5)
            price_entry.bind("<KeyRelease>", lambda e, idx=i, w=price_entry: self._update_shop_item(node, item_type, idx, 'price', w.get()))
            
            # Remove button
            ctk.CTkButton(
                item_frame, text="✕", width=30, height=30,
                fg_color="transparent", hover_color=COLOR_ERROR,
                command=lambda idx=i: self._remove_shop_item(node, item_type, idx)
            ).grid(row=0, column=2, padx=5, pady=5)
        
        # Add button
        ctk.CTkButton(
            parent, text=f"+ Add Item", 
            command=lambda: self._add_shop_item(node, item_type)
        ).pack(pady=5, padx=10)

    def _create_outcomes_list(self, parent, outcomes, node):
        """Creates a list of random outcomes."""
        for i, outcome in enumerate(outcomes):
            outcome_frame = ctk.CTkFrame(parent, fg_color=COLOR_SECONDARY_FRAME)
            outcome_frame.pack(fill="x", pady=2, padx=10)
            outcome_frame.grid_columnconfigure(1, weight=1)
            
            # Weight
            weight_entry = ctk.CTkEntry(outcome_frame, placeholder_text="Weight", width=60)
            weight_entry.insert(0, str(outcome.get('weight', 1)))
            weight_entry.grid(row=0, column=0, padx=5, pady=5)
            weight_entry.bind("<KeyRelease>", lambda e, idx=i, w=weight_entry: self._update_outcome(node, idx, 'weight', w.get()))
            
            # Next node
            node_ids = ["", "[End Game]"] + sorted(list(self.app.nodes.keys()))
            node_combo = ctk.CTkComboBox(outcome_frame, values=node_ids, width=150)
            node_combo.set(outcome.get('next_node', ''))
            node_combo.configure(command=lambda choice, idx=i: self._update_outcome(node, idx, 'next_node', choice))
            node_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            
            # Description
            desc_entry = ctk.CTkEntry(outcome_frame, placeholder_text="Description")
            desc_entry.insert(0, outcome.get('description', ''))
            desc_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,5), sticky="ew")
            desc_entry.bind("<KeyRelease>", lambda e, idx=i, w=desc_entry: self._update_outcome(node, idx, 'description', w.get()))
            
            # Remove button
            ctk.CTkButton(
                outcome_frame, text="✕", width=30, height=30,
                fg_color="transparent", hover_color=COLOR_ERROR,
                command=lambda idx=i: self._remove_outcome(node, idx)
            ).grid(row=0, column=2, padx=5, pady=5)
        
        # Add button
        ctk.CTkButton(
            parent, text="+ Add Outcome", 
            command=lambda: self._add_outcome(node)
        ).pack(pady=5, padx=10)

    def _create_recipes_list(self, parent, recipes, node):
        """Creates a list of crafting recipes."""
        for i, recipe in enumerate(recipes):
            recipe_frame = ctk.CTkFrame(parent, fg_color=COLOR_SECONDARY_FRAME)
            recipe_frame.pack(fill="x", pady=2, padx=10)
            recipe_frame.grid_columnconfigure(1, weight=1)
            
            # Recipe name
            name_entry = ctk.CTkEntry(recipe_frame, placeholder_text="Recipe name")
            name_entry.insert(0, recipe.get('name', ''))
            name_entry.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
            name_entry.bind("<KeyRelease>", lambda e, idx=i, w=name_entry: self._update_recipe(node, idx, 'name', w.get()))
            
            # Ingredients
            ing_entry = ctk.CTkEntry(recipe_frame, placeholder_text="Ingredients (comma separated)")
            ingredients = ', '.join(recipe.get('ingredients', []))
            ing_entry.insert(0, ingredients)
            ing_entry.grid(row=1, column=0, padx=5, pady=(0,5), sticky="ew")
            ing_entry.bind("<KeyRelease>", lambda e, idx=i, w=ing_entry: self._update_recipe_ingredients(node, idx, w.get()))
            
            # Result
            result_entry = ctk.CTkEntry(recipe_frame, placeholder_text="Result item", width=150)
            result_entry.insert(0, recipe.get('result', ''))
            result_entry.grid(row=1, column=1, padx=5, pady=(0,5), sticky="ew")
            result_entry.bind("<KeyRelease>", lambda e, idx=i, w=result_entry: self._update_recipe(node, idx, 'result', w.get()))
            
            # Remove button
            ctk.CTkButton(
                recipe_frame, text="✕", width=30, height=30,
                fg_color="transparent", hover_color=COLOR_ERROR,
                command=lambda idx=i: self._remove_recipe(node, idx)
            ).grid(row=0, column=2, rowspan=2, padx=5, pady=5)
        
        # Add button
        ctk.CTkButton(
            parent, text="+ Add Recipe", 
            command=lambda: self._add_recipe(node)
        ).pack(pady=5, padx=10)

    def _create_actions_list(self, parent, actions, node):
        """Creates a list of item actions."""
        for i, action in enumerate(actions):
            action_frame = ctk.CTkFrame(parent, fg_color=COLOR_SECONDARY_FRAME)
            action_frame.pack(fill="x", pady=2, padx=10)
            action_frame.grid_columnconfigure(1, weight=1)
            
            # Action name
            name_entry = ctk.CTkEntry(action_frame, placeholder_text="Action name (Use, Examine, etc.)")
            name_entry.insert(0, action.get('name', ''))
            name_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            name_entry.bind("<KeyRelease>", lambda e, idx=i, w=name_entry: self._update_action(node, idx, 'name', w.get()))
            
            # Target items
            items_entry = ctk.CTkEntry(action_frame, placeholder_text="Target items (comma separated)")
            items = ', '.join(action.get('target_items', []))
            items_entry.insert(0, items)
            items_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            items_entry.bind("<KeyRelease>", lambda e, idx=i, w=items_entry: self._update_action_items(node, idx, w.get()))
            
            # Remove button
            ctk.CTkButton(
                action_frame, text="✕", width=30, height=30,
                fg_color="transparent", hover_color=COLOR_ERROR,
                command=lambda idx=i: self._remove_action(node, idx)
            ).grid(row=0, column=2, padx=5, pady=5)
        
        # Add button
        ctk.CTkButton(
            parent, text="+ Add Action", 
            command=lambda: self._add_action(node)
        ).pack(pady=5, padx=10)

    # Update methods for shop nodes
    def _update_shop_property(self, node, prop, value):
        """Updates a shop node property."""
        self.app._save_state_for_undo("Update Shop Property")
        setattr(node, prop, value)
        self.app.canvas_manager.redraw_node(node.id)

    def _update_shop_item(self, node, item_type, index, prop, value):
        """Updates a shop item property."""
        self.app._save_state_for_undo("Update Shop Item")
        items = node.items_for_sale if item_type == "sale" else node.items_to_buy
        if index < len(items):
            if prop == 'price':
                try:
                    items[index][prop] = float(value)
                except ValueError:
                    items[index][prop] = 0
            else:
                items[index][prop] = value

    def _add_shop_item(self, node, item_type):
        """Adds a new shop item."""
        self.app._save_state_for_undo("Add Shop Item")
        new_item = {'name': 'New Item', 'price': 10}
        items = node.items_for_sale if item_type == "sale" else node.items_to_buy
        items.append(new_item)
        self.update_panel()

    def _remove_shop_item(self, node, item_type, index):
        """Removes a shop item."""
        self.app._save_state_for_undo("Remove Shop Item")
        items = node.items_for_sale if item_type == "sale" else node.items_to_buy
        if index < len(items):
            del items[index]
        self.update_panel()

    # Update methods for random event nodes
    def _update_random_property(self, node, prop, value):
        """Updates a random event property."""
        self.app._save_state_for_undo("Update Random Event Property")
        setattr(node, prop, value)

    def _update_outcome(self, node, index, prop, value):
        """Updates a random outcome."""
        self.app._save_state_for_undo("Update Random Outcome")
        if index < len(node.random_outcomes):
            if prop == 'weight':
                try:
                    node.random_outcomes[index][prop] = float(value)
                except ValueError:
                    node.random_outcomes[index][prop] = 1
            else:
                node.random_outcomes[index][prop] = value

    def _add_outcome(self, node):
        """Adds a new random outcome."""
        self.app._save_state_for_undo("Add Random Outcome")
        new_outcome = {'weight': 1, 'next_node': '', 'description': 'New outcome'}
        node.random_outcomes.append(new_outcome)
        self.update_panel()

    def _remove_outcome(self, node, index):
        """Removes a random outcome."""
        self.app._save_state_for_undo("Remove Random Outcome")
        if index < len(node.random_outcomes):
            del node.random_outcomes[index]
        self.update_panel()

    # Update methods for timer nodes
    def _update_timer_property(self, node, prop, value):
        """Updates a timer property."""
        self.app._save_state_for_undo("Update Timer Property")
        if prop == 'wait_time':
            try:
                setattr(node, prop, float(value))
            except ValueError:
                setattr(node, prop, 5)
        else:
            setattr(node, prop, value)

    # Update methods for inventory nodes
    def _update_inventory_property(self, node, prop, value):
        """Updates an inventory property."""
        self.app._save_state_for_undo("Update Inventory Property")
        setattr(node, prop, value)

    def _update_recipe(self, node, index, prop, value):
        """Updates a recipe property."""
        self.app._save_state_for_undo("Update Recipe")
        if index < len(node.crafting_recipes):
            node.crafting_recipes[index][prop] = value

    def _update_recipe_ingredients(self, node, index, value):
        """Updates recipe ingredients."""
        self.app._save_state_for_undo("Update Recipe Ingredients")
        if index < len(node.crafting_recipes):
            ingredients = [item.strip() for item in value.split(',') if item.strip()]
            node.crafting_recipes[index]['ingredients'] = ingredients

    def _add_recipe(self, node):
        """Adds a new recipe."""
        self.app._save_state_for_undo("Add Recipe")
        new_recipe = {'name': 'New Recipe', 'ingredients': [], 'result': 'New Item'}
        node.crafting_recipes.append(new_recipe)
        self.update_panel()

    def _remove_recipe(self, node, index):
        """Removes a recipe."""
        self.app._save_state_for_undo("Remove Recipe")
        if index < len(node.crafting_recipes):
            del node.crafting_recipes[index]
        self.update_panel()

    def _update_action(self, node, index, prop, value):
        """Updates an action property."""
        self.app._save_state_for_undo("Update Action")
        if index < len(node.item_actions):
            node.item_actions[index][prop] = value

    def _update_action_items(self, node, index, value):
        """Updates action target items."""
        self.app._save_state_for_undo("Update Action Items")
        if index < len(node.item_actions):
            items = [item.strip() for item in value.split(',') if item.strip()]
            node.item_actions[index]['target_items'] = items

    def _add_action(self, node):
        """Adds a new action."""
        self.app._save_state_for_undo("Add Action")
        new_action = {'name': 'Use', 'target_items': []}
        node.item_actions.append(new_action)
        self.update_panel()

    def _remove_action(self, node, index):
        """Removes an action."""
        self.app._save_state_for_undo("Remove Action")
        if index < len(node.item_actions):
            del node.item_actions[index]
        self.update_panel()