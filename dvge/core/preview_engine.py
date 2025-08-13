# dvge/core/preview_engine.py

"""Live preview game engine for testing games within the editor."""

import copy
import random
from typing import Dict, Any, List, Optional, Callable
from ..models import DiceRollNode, CombatNode


class PreviewGameEngine:
    """Handles game logic for live preview mode."""
    
    def __init__(self, app):
        self.app = app
        self.reset_game_state()
        
        # Callbacks for UI updates
        self.on_node_change: Optional[Callable] = None
        self.on_state_change: Optional[Callable] = None
        self.on_message: Optional[Callable] = None
        
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
            
        # Process node data
        node_data = self._process_node_for_preview(node)
        
        # Notify UI
        if self.on_node_change:
            self.on_node_change(node_data)
        if self.on_state_change:
            self.on_state_change(self.get_debug_state())
            
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
                    'effects': option.get('effects', [])
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
        
    def choose_option(self, option_index: int):
        """Player chooses a dialogue option."""
        node = self.app.nodes.get(self.current_node_id)
        if not node or option_index >= len(getattr(node, 'options', [])):
            return
            
        option = node.options[option_index]
        
        # Apply effects
        self._apply_effects(option.get('effects', []))
        
        # Navigate to next node
        next_node = option.get('nextNode', '')
        if next_node:
            self.current_node_id = next_node
            self.render_current_node()
            
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