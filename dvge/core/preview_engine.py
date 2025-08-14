# dvge/core/enhanced_preview_engine.py

"""Enhanced preview game engine with full support for special node types."""

import copy
import random
import time
from typing import Dict, Any, List, Optional, Callable
from ..models import DiceRollNode, CombatNode, ShopNode, RandomEventNode, TimerNode, InventoryNode


class EnhancedPreviewGameEngine:
    """Enhanced game engine with full support for special node types."""
    
    def __init__(self, app):
        self.app = app
        self.reset_game_state()
        
        # Callbacks for UI updates
        self.on_node_change: Optional[Callable] = None
        self.on_state_change: Optional[Callable] = None
        self.on_message: Optional[Callable] = None
        self.on_shop_open: Optional[Callable] = None
        self.on_inventory_open: Optional[Callable] = None
        self.on_timer_start: Optional[Callable] = None
        
        # Timer tracking
        self.active_timers = {}
        
    def reset_game_state(self):
        """Resets the game to initial state."""
        # Copy initial states from app
        self.player_stats = copy.deepcopy(self.app.player_stats)
        self.player_inventory = copy.deepcopy(self.app.player_inventory)
        self.story_flags = copy.deepcopy(self.app.story_flags)
        self.variables = copy.deepcopy(getattr(self.app, 'variables', {}))
        self.quests = copy.deepcopy({qid: q.to_dict() for qid, q in self.app.quests.items()})
        
        # Game state
        self.current_node_id = "intro"
        self.node_history = []
        self.is_game_over = False
        self.pending_navigation = None
        
        # Clear timers
        self.active_timers.clear()
        
        # Initialize variable system for text substitution
        from .variable_system import VariableSystem
        self.var_system = VariableSystem()
        self.var_system.set_variables_ref(self.variables)
        self.var_system.set_flags_ref(self.story_flags)
        
    def start_game(self, start_node_id: str = "intro"):
        """Starts the game from specified node."""
        self.reset_game_state()
        self.current_node_id = start_node_id
        self.render_current_node()
        
    def render_current_node(self):
        """Renders the current node and processes its content."""
        if self.current_node_id == "[End Game]":
            self.is_game_over = True
            if self.on_node_change:
                self.on_node_change({
                    'id': '[End Game]',
                    'npc': 'Game Over',
                    'text': 'The story ends here.',
                    'options': [],
                    'node_type': 'EndGame'
                })
            return
            
        node = self.app.nodes.get(self.current_node_id)
        if not node:
            if self.on_message:
                self.on_message(f"Node '{self.current_node_id}' not found!", "error")
            return
            
        # Add to history
        if not self.node_history or self.node_history[-1] != self.current_node_id:
            self.node_history.append(self.current_node_id)
            
        # Process node based on type
        if isinstance(node, ShopNode):
            self._handle_shop_node(node)
        elif isinstance(node, RandomEventNode):
            self._handle_random_event_node(node)
        elif isinstance(node, TimerNode):
            self._handle_timer_node(node)
        elif isinstance(node, InventoryNode):
            self._handle_inventory_node(node)
        else:
            # Process as regular node
            node_data = self._process_node_for_preview(node)
            if self.on_node_change:
                self.on_node_change(node_data)
                
        # Notify UI of state change
        if self.on_state_change:
            self.on_state_change(self.get_debug_state())
            
    def _handle_shop_node(self, node: ShopNode):
        """Handles shop node processing."""
        # Process basic node data
        node_data = self._process_node_for_preview(node)
        
        # Add shop-specific data
        node_data.update({
            'node_type': 'ShopNode',
            'shop_data': {
                'items_for_sale': copy.deepcopy(node.items_for_sale),
                'items_to_buy': copy.deepcopy(node.items_to_buy),
                'currency_variable': node.currency_variable,
                'continue_node': node.continue_node
            }
        })
        
        # Update options to include shop interaction
        shop_options = []
        
        # Add shop interaction option
        shop_options.append({
            'index': 0,
            'text': '🏪 Browse Shop',
            'action': 'open_shop',
            'nextNode': '',
            'effects': []
        })
        
        # Add continue option if specified
        if node.continue_node:
            shop_options.append({
                'index': 1,
                'text': 'Continue on your way',
                'action': 'navigate',
                'nextNode': node.continue_node,
                'effects': []
            })
        
        node_data['options'] = shop_options
        
        if self.on_node_change:
            self.on_node_change(node_data)
            
    def _handle_random_event_node(self, node: RandomEventNode):
        """Handles random event node processing."""
        node_data = self._process_node_for_preview(node)
        node_data['node_type'] = 'RandomEventNode'
        
        if node.auto_trigger:
            # Automatically trigger the random event
            self._trigger_random_event(node)
        else:
            # Show trigger option
            node_data['options'] = [{
                'index': 0,
                'text': '🎲 Trigger Random Event',
                'action': 'random_event',
                'nextNode': '',
                'effects': []
            }]
            
            if self.on_node_change:
                self.on_node_change(node_data)
                
    def _handle_timer_node(self, node: TimerNode):
        """Handles timer node processing."""
        node_data = self._process_node_for_preview(node)
        node_data.update({
            'node_type': 'TimerNode',
            'timer_data': {
                'wait_time': node.wait_time,
                'time_unit': node.time_unit,
                'total_seconds': node.get_seconds(),
                'next_node': node.next_node,
                'show_countdown': node.show_countdown,
                'allow_skip': node.allow_skip
            }
        })
        
        # Prepare timer options
        timer_options = []
        if node.allow_skip:
            timer_options.append({
                'index': 0,
                'text': '⏭️ Skip Wait',
                'action': 'skip_timer',
                'nextNode': node.next_node,
                'effects': []
            })
        
        node_data['options'] = timer_options
        
        if self.on_node_change:
            self.on_node_change(node_data)
            
        # Start the timer
        if self.on_timer_start:
            self.on_timer_start(node.get_seconds(), node.next_node, node.show_countdown)
            
    def _handle_inventory_node(self, node: InventoryNode):
        """Handles inventory node processing."""
        node_data = self._process_node_for_preview(node)
        node_data.update({
            'node_type': 'InventoryNode',
            'inventory_data': {
                'crafting_recipes': copy.deepcopy(node.crafting_recipes),
                'item_actions': copy.deepcopy(node.item_actions),
                'continue_node': node.continue_node,
                'auto_open': node.auto_open
            }
        })
        
        # Prepare inventory options
        inventory_options = []
        
        if not node.auto_open:
            inventory_options.append({
                'index': 0,
                'text': '🎒 Open Inventory',
                'action': 'open_inventory',
                'nextNode': '',
                'effects': []
            })
        
        if node.continue_node:
            inventory_options.append({
                'index': len(inventory_options),
                'text': 'Continue',
                'action': 'navigate', 
                'nextNode': node.continue_node,
                'effects': []
            })
        
        node_data['options'] = inventory_options
        
        if self.on_node_change:
            self.on_node_change(node_data)
            
        # Auto-open inventory if specified
        if node.auto_open and self.on_inventory_open:
            self.on_inventory_open(node_data['inventory_data'])
    
    def _process_node_for_preview(self, node) -> Dict[str, Any]:
        """Processes a node for preview display."""
        # Apply variable substitution to text
        processed_text = self.var_system.substitute_text(node.text)
        
        # Get available options based on conditions
        available_options = []
        for i, option in enumerate(getattr(node, 'options', [])):
            if self._check_conditions(option.get('conditions', [])):
                processed_option_text = self.var_system.substitute_text(option.get('text', ''))
                available_options.append({
                    'index': i,
                    'text': processed_option_text,
                    'nextNode': option.get('nextNode', ''),
                    'effects': option.get('effects', []),
                    'action': 'navigate'
                })
        
        return {
            'id': node.id,
            'npc': node.npc,
            'text': processed_text,
            'options': available_options,
            'node_type': type(node).__name__,
            'chapter': getattr(node, 'chapter', ''),
            'backgroundTheme': getattr(node, 'backgroundTheme', ''),
            'auto_advance': getattr(node, 'auto_advance', False),
            'auto_advance_delay': getattr(node, 'auto_advance_delay', 0),
            # Special node data
            'dice_data': self._get_dice_data(node) if isinstance(node, DiceRollNode) else None,
            'combat_data': self._get_combat_data(node) if isinstance(node, CombatNode) else None
        }
        
    def choose_option(self, option_index: int):
        """Player chooses a dialogue option."""
        node = self.app.nodes.get(self.current_node_id)
        if not node:
            return
            
        # Handle special node types
        if isinstance(node, ShopNode):
            self._handle_shop_option(node, option_index)
        elif isinstance(node, RandomEventNode):
            self._trigger_random_event(node)
        elif isinstance(node, TimerNode):
            self._handle_timer_option(node, option_index)
        elif isinstance(node, InventoryNode):
            self._handle_inventory_option(node, option_index)
        else:
            # Handle regular dialogue options
            if option_index >= len(getattr(node, 'options', [])):
                return
                
            option = node.options[option_index]
            
            # Apply effects
            self._apply_effects(option.get('effects', []))
            
            # Navigate to next node
            next_node = option.get('nextNode', '')
            if next_node:
                self.current_node_id = next_node
                self.render_current_node()
                
    def _handle_shop_option(self, node: ShopNode, option_index: int):
        """Handles shop option selection."""
        if option_index == 0:  # Browse shop
            if self.on_shop_open:
                shop_data = {
                    'items_for_sale': copy.deepcopy(node.items_for_sale),
                    'items_to_buy': copy.deepcopy(node.items_to_buy),
                    'currency_variable': node.currency_variable,
                    'continue_node': node.continue_node
                }
                self.on_shop_open(shop_data)
        elif option_index == 1 and node.continue_node:  # Continue
            self.current_node_id = node.continue_node
            self.render_current_node()
            
    def _handle_timer_option(self, node: TimerNode, option_index: int):
        """Handles timer option selection."""
        if option_index == 0 and node.allow_skip:  # Skip timer
            if node.next_node:
                self.current_node_id = node.next_node
                self.render_current_node()
                
    def _handle_inventory_option(self, node: InventoryNode, option_index: int):
        """Handles inventory option selection."""
        if option_index == 0:  # Open inventory
            if self.on_inventory_open:
                inventory_data = {
                    'crafting_recipes': copy.deepcopy(node.crafting_recipes),
                    'item_actions': copy.deepcopy(node.item_actions),
                    'continue_node': node.continue_node
                }
                self.on_inventory_open(inventory_data)
        elif node.continue_node:  # Continue
            self.current_node_id = node.continue_node
            self.render_current_node()
            
    def _trigger_random_event(self, node: RandomEventNode):
        """Triggers a random event."""
        if not node.random_outcomes:
            return
            
        # Calculate weighted random selection
        total_weight = sum(outcome.get('weight', 1) for outcome in node.random_outcomes)
        random_value = random.random() * total_weight
        
        current_weight = 0
        selected_outcome = None
        
        for outcome in node.random_outcomes:
            current_weight += outcome.get('weight', 1)
            if random_value <= current_weight:
                selected_outcome = outcome
                break
                
        if selected_outcome:
            if self.on_message:
                self.on_message(f"Random Event: {selected_outcome.get('description', 'Something happened!')}", "info")
                
            # Navigate to outcome node after delay
            next_node = selected_outcome.get('next_node')
            if next_node:
                self.pending_navigation = next_node
                # Use a shorter delay for preview
                if self.on_node_change:
                    # Show outcome briefly
                    outcome_data = {
                        'id': f"{node.id}_outcome",
                        'npc': 'Random Event',
                        'text': selected_outcome.get('description', 'Something unexpected happened!'),
                        'options': [],
                        'node_type': 'RandomOutcome'
                    }
                    self.on_node_change(outcome_data)
                    
    def complete_pending_navigation(self):
        """Completes a pending navigation (used for random events and timers)."""
        if self.pending_navigation:
            self.current_node_id = self.pending_navigation
            self.pending_navigation = None
            self.render_current_node()
            
    def timer_expired(self, next_node: str):
        """Called when a timer expires."""
        if next_node:
            self.current_node_id = next_node
            self.render_current_node()
            
    def buy_item(self, item_name: str, price: int, currency_var: str):
        """Handles buying an item from a shop."""
        current_currency = self.variables.get(currency_var, 0)
        
        if current_currency >= price:
            # Deduct currency
            self.variables[currency_var] = current_currency - price
            
            # Add item to inventory
            self.player_inventory.append({
                'name': item_name,
                'description': f'Purchased from shop for {price} {currency_var}'
            })
            
            if self.on_message:
                self.on_message(f"Bought {item_name} for {price} {currency_var}!", "success")
                
            return True
        else:
            if self.on_message:
                self.on_message(f"Not enough {currency_var}! Need {price}, have {current_currency}", "warning")
            return False
            
    def sell_item(self, item_name: str, price: int, currency_var: str):
        """Handles selling an item to a shop."""
        # Find item in inventory
        item_index = next((i for i, item in enumerate(self.player_inventory) 
                          if item.get('name') == item_name), -1)
        
        if item_index >= 0:
            # Remove item from inventory
            del self.player_inventory[item_index]
            
            # Add currency
            self.variables[currency_var] = self.variables.get(currency_var, 0) + price
            
            if self.on_message:
                self.on_message(f"Sold {item_name} for {price} {currency_var}!", "success")
                
            return True
        else:
            if self.on_message:
                self.on_message(f"You don't have {item_name} to sell!", "warning")
            return False
            
    def craft_item(self, recipe_name: str, ingredients: List[str], result: str):
        """Handles crafting an item."""
        # Check if all ingredients are available
        inventory_items = [item.get('name') for item in self.player_inventory]
        
        missing_ingredients = []
        for ingredient in ingredients:
            if ingredient not in inventory_items:
                missing_ingredients.append(ingredient)
                
        if missing_ingredients:
            if self.on_message:
                self.on_message(f"Missing ingredients: {', '.join(missing_ingredients)}", "warning")
            return False
            
        # Remove ingredients from inventory
        for ingredient in ingredients:
            item_index = next((i for i, item in enumerate(self.player_inventory) 
                              if item.get('name') == ingredient), -1)
            if item_index >= 0:
                del self.player_inventory[item_index]
                
        # Add result to inventory
        self.player_inventory.append({
            'name': result,
            'description': f'Crafted using {recipe_name}'
        })
        
        if self.on_message:
            self.on_message(f"Successfully crafted {result}!", "success")
            
        return True
        
    def close_shop(self, continue_node: str = None):
        """Handles closing the shop."""
        if continue_node:
            self.current_node_id = continue_node
            self.render_current_node()
            
    def close_inventory(self, continue_node: str = None):
        """Handles closing the inventory."""
        if continue_node:
            self.current_node_id = continue_node
            self.render_current_node()
    
    # ... (rest of the methods remain the same as in the original preview_engine.py)
    
    def _get_dice_data(self, node: DiceRollNode) -> Dict[str, Any]:
        """Gets dice roll specific data."""
        return {
            'num_dice': node.num_dice,
            'num_sides': node.num_sides,
            'success_threshold': node.success_threshold,
            'success_node': node.success_node,
            'failure_node': node.failure_node
        }
        
    def _get_combat_data(self, node: CombatNode) -> Dict[str, Any]:
        """Gets combat specific data."""
        return {
            'enemies': node.enemies,
            'successNode': node.successNode,
            'failNode': node.failNode
        }
        
    def perform_dice_roll(self):
        """Performs a dice roll for DiceRollNode."""
        node = self.app.nodes.get(self.current_node_id)
        if not isinstance(node, DiceRollNode):
            return
            
        # Roll dice
        total = 0
        rolls = []
        for _ in range(node.num_dice):
            roll = random.randint(1, node.num_sides)
            rolls.append(roll)
            total += roll
            
        success = total >= node.success_threshold
        
        # Show result
        result_text = f"Rolled: {total}"
        if len(rolls) > 1:
            result_text += f" ({' + '.join(map(str, rolls))})"
        result_text += f" - {'Success!' if success else 'Failed!'}"
        
        if self.on_message:
            self.on_message(result_text, "success" if success else "warning")
            
        # Navigate based on result
        next_node = node.success_node if success else node.failure_node
        if next_node:
            self.current_node_id = next_node
            self.render_current_node()
            
    def perform_combat(self):
        """Performs combat for CombatNode."""
        node = self.app.nodes.get(self.current_node_id)
        if not isinstance(node, CombatNode):
            return
            
        # Simple combat calculation
        player_power = (
            self.player_stats.get('strength', 10) + 
            self.player_stats.get('defense', 5) + 
            (self.player_stats.get('health', 100) / 10)
        )
        
        # Add some randomness
        random_factor = random.uniform(0.8, 1.2)
        final_power = player_power * random_factor
        
        # Determine victory (adjust threshold as needed)
        victory = final_power > 50
        
        result_text = f"Combat Power: {final_power:.1f} - {'Victory!' if victory else 'Defeat!'}"
        if self.on_message:
            self.on_message(result_text, "success" if victory else "error")
            
        # Navigate based on result
        next_node = node.successNode if victory else node.failNode
        if next_node:
            self.current_node_id = next_node
            self.render_current_node()
            
    def jump_to_node(self, node_id: str):
        """Jumps directly to a specific node (for testing)."""
        if node_id in self.app.nodes or node_id == "[End Game]":
            self.current_node_id = node_id
            self.render_current_node()
        else:
            if self.on_message:
                self.on_message(f"Node '{node_id}' not found!", "error")
                
    def _check_conditions(self, conditions: List[Dict[str, Any]]) -> bool:
        """Checks if all conditions are met."""
        if not conditions:
            return True
            
        for condition in conditions:
            if not self._check_single_condition(condition):
                return False
        return True
        
    def _check_single_condition(self, condition: Dict[str, Any]) -> bool:
        """Checks a single condition."""
        cond_type = condition.get('type', 'stat')
        subject = condition.get('subject', '')
        operator = condition.get('operator', '>=')
        value = condition.get('value', 0)
        
        if cond_type == 'stat':
            player_stat = self.player_stats.get(subject, 0)
            return self._compare_values(player_stat, operator, value)
            
        elif cond_type == 'item':
            has_item = any(item.get('name') == subject for item in self.player_inventory)
            return (operator == 'has') == has_item
            
        elif cond_type == 'flag':
            flag_value = self.story_flags.get(subject, False)
            comparison_value = (str(value).lower() == 'true')
            return (operator == 'is') == (flag_value == comparison_value)
            
        elif cond_type == 'quest':
            quest = self.quests.get(subject, {})
            quest_state = quest.get('state', 'inactive')
            return (operator == 'is') == (quest_state == value)
            
        elif cond_type == 'variable':
            var_value = self.variables.get(subject, 0)
            try:
                # Handle variable references in value
                if isinstance(value, str) and '{' in str(value):
                    value = self.var_system.evaluate_math_expression(str(value))
                else:
                    value = float(value)
            except:
                value = 0
            return self._compare_values(var_value, operator, value)
            
        return True
        
    def _compare_values(self, left, operator: str, right) -> bool:
        """Compares two values using the given operator."""
        try:
            left = float(left)
            right = float(right)
            
            if operator == '==': return left == right
            elif operator == '!=': return left != right
            elif operator == '>': return left > right
            elif operator == '<': return left < right
            elif operator == '>=': return left >= right
            elif operator == '<=': return left <= right
            
        except (ValueError, TypeError):
            return str(left) == str(right)
            
        return False
        
    def _apply_effects(self, effects: List[Dict[str, Any]]):
        """Applies a list of effects."""
        for effect in effects:
            self._apply_single_effect(effect)
            
        # Update variable system references
        self.var_system.set_variables_ref(self.variables)
        self.var_system.set_flags_ref(self.story_flags)
        
    def _apply_single_effect(self, effect: Dict[str, Any]):
        """Applies a single effect."""
        effect_type = effect.get('type', 'stat')
        subject = effect.get('subject', '')
        operator = effect.get('operator', '+=')
        value = effect.get('value', 0)
        
        if effect_type == 'stat':
            try:
                value = float(value)
            except:
                value = 0
                
            if subject not in self.player_stats:
                self.player_stats[subject] = 0
                
            current = self.player_stats[subject]
            if operator == '=':
                self.player_stats[subject] = value
            elif operator == '+=':
                self.player_stats[subject] = current + value
            elif operator == '-=':
                self.player_stats[subject] = current - value
                
        elif effect_type == 'item':
            if operator == 'add':
                if not any(item.get('name') == subject for item in self.player_inventory):
                    self.player_inventory.append({'name': subject, 'description': ''})
            elif operator == 'remove':
                self.player_inventory = [
                    item for item in self.player_inventory 
                    if item.get('name') != subject
                ]
                
        elif effect_type == 'flag':
            bool_value = (str(value).lower() == 'true')
            self.story_flags[subject] = bool_value
            
        elif effect_type == 'quest':
            if subject in self.quests:
                self.quests[subject]['state'] = value
                
        elif effect_type == 'variable':
            try:
                # Handle expressions in value
                if isinstance(value, str) and ('{' in str(value) or any(op in str(value) for op in ['+', '-', '*', '/'])):
                    value = self.var_system.evaluate_math_expression(str(value))
                else:
                    value = float(value)
            except:
                value = 0
                
            if subject not in self.variables:
                self.variables[subject] = 0
                
            self.var_system.apply_variable_effect(subject, operator, value)
            
    def get_debug_state(self) -> Dict[str, Any]:
        """Returns current game state for debugging."""
        return {
            'current_node': self.current_node_id,
            'history': self.node_history.copy(),
            'player_stats': self.player_stats.copy(),
            'variables': self.variables.copy(),
            'story_flags': self.story_flags.copy(),
            'inventory': [item.copy() for item in self.player_inventory],
            'quests': self.quests.copy()
        }