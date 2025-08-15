import random
from typing import Dict, List, Tuple, Optional


class SkillCheckSystem:
    """Manages skill checks with modifiers, advantages, and special abilities."""
    
    def __init__(self):
        self.active_modifiers = {}
        self.advantage_sources = []
        self.disadvantage_sources = []
        
    def perform_skill_check(
        self, 
        skill_value: int, 
        difficulty: int, 
        skill_type: str = "general",
        use_modifiers: bool = True,
        critical_enabled: bool = True
    ) -> Tuple[bool, Dict]:
        """
        Performs an enhanced skill check with various modifiers.
        
        Returns: (success, details_dict)
        """
        # Base roll (d20 system inspired)
        roll = random.randint(1, 20)
        
        # Check for advantage/disadvantage
        if self.advantage_sources and not self.disadvantage_sources:
            second_roll = random.randint(1, 20)
            roll = max(roll, second_roll)
            advantage_used = True
        elif self.disadvantage_sources and not self.advantage_sources:
            second_roll = random.randint(1, 20)
            roll = min(roll, second_roll)
            advantage_used = False
        else:
            advantage_used = None
            
        # Critical success/failure
        is_critical_success = roll == 20 and critical_enabled
        is_critical_failure = roll == 1 and critical_enabled
        
        # Apply modifiers
        total_modifier = skill_value
        if use_modifiers:
            for mod_type, mod_value in self.active_modifiers.items():
                if mod_type == skill_type or mod_type == "all":
                    total_modifier += mod_value
                    
        # Calculate final result
        final_value = roll + total_modifier
        
        # Determine success
        if is_critical_success:
            success = True
            margin = 20  # Maximum margin
        elif is_critical_failure:
            success = False
            margin = -20
        else:
            success = final_value >= difficulty
            margin = final_value - difficulty
            
        return success, {
            'roll': roll,
            'skill_value': skill_value,
            'modifiers': total_modifier - skill_value,
            'final_value': final_value,
            'difficulty': difficulty,
            'margin': margin,
            'critical_success': is_critical_success,
            'critical_failure': is_critical_failure,
            'advantage': advantage_used,
            'skill_type': skill_type
        }
        
    def add_temporary_modifier(self, mod_type: str, value: int, duration: int = 1):
        """Adds a temporary modifier that affects skill checks."""
        self.active_modifiers[mod_type] = value
        
    def remove_modifier(self, mod_type: str):
        """Removes a temporary modifier."""
        self.active_modifiers.pop(mod_type, None)
        
    def add_advantage(self, source: str):
        """Adds a source of advantage for skill checks."""
        if source not in self.advantage_sources:
            self.advantage_sources.append(source)
            
    def add_disadvantage(self, source: str):
        """Adds a source of disadvantage for skill checks."""
        if source not in self.disadvantage_sources:
            self.disadvantage_sources.append(source)
            
    def clear_advantages(self):
        """Clears all advantage/disadvantage sources."""
        self.advantage_sources.clear()
        self.disadvantage_sources.clear()


class SkillCheckNode:
    """Enhanced DiceRollNode with skill check mechanics."""
    
    def __init__(self, node_id: str, skill_type: str = "general", 
                 base_difficulty: int = 15, **kwargs):
        self.id = node_id
        self.skill_type = skill_type
        self.base_difficulty = base_difficulty
        self.allow_retries = kwargs.get('allow_retries', False)
        self.retry_penalty = kwargs.get('retry_penalty', 5)
        self.critical_success_node = kwargs.get('critical_success_node', '')
        self.critical_failure_node = kwargs.get('critical_failure_node', '')
        self.partial_success_threshold = kwargs.get('partial_success_threshold', -5)
        self.partial_success_node = kwargs.get('partial_success_node', '')
        
        # Modifiers based on items or conditions
        self.item_modifiers = kwargs.get('item_modifiers', {})  # {item_name: modifier}
        self.condition_modifiers = kwargs.get('condition_modifiers', {})  # {flag: modifier}
        
    def calculate_modifiers(self, inventory: List, flags: Dict) -> int:
        """Calculates total modifiers from items and conditions."""
        total = 0
        
        # Item bonuses
        for item in inventory:
            if item.get('name') in self.item_modifiers:
                total += self.item_modifiers[item.get('name')]
                
        # Condition bonuses
        for flag, modifier in self.condition_modifiers.items():
            if flags.get(flag, False):
                total += modifier
                
        return total