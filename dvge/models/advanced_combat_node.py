# dvge/models/advanced_combat_node.py

"""Advanced turn-based combat node with detailed mechanics."""

from .base_node import BaseNode
from typing import Dict, List, Any, Optional
import json


class AdvancedCombatNode(BaseNode):
    """Advanced turn-based combat node with skills, equipment, and strategy."""
    
    def __init__(self, x=0, y=0, node_id=""):
        super().__init__(x, y, node_id)
        
        # Set default properties for display
        self.npc = "Combat Encounter"
        self.text = "A fierce battle awaits! Prepare for advanced turn-based combat with strategic depth, skills, and environmental effects."
        
        # Combat configuration
        self.combat_type = "advanced"  # advanced, boss, arena, survival
        self.environment = "default"  # affects certain abilities
        self.weather = "clear"  # rain, storm, sunny, etc.
        self.terrain_effects = []  # modifiers based on battlefield
        
        # Victory/defeat conditions
        self.victory_conditions = ["defeat_all_enemies"]  # defeat_all, survive_turns, protect_ally
        self.defeat_conditions = ["party_defeated"]  # party_defeated, ally_dies, time_limit
        self.turn_limit = 0  # 0 = no limit
        
        # Rewards
        self.experience_reward = 100
        self.gold_reward = 50
        self.item_rewards = []
        self.skill_points_reward = 1
        
        # Combat participants
        self.enemies = []  # List of enemy configurations
        self.allies = []   # List of ally configurations
        self.environmental_hazards = []  # Traps, obstacles, etc.
        
        # Add a default enemy to ensure the node is functional
        self.add_enemy({
            "name": "Test Enemy",
            "level": 1,
            "health": 60,
            "max_health": 60,
            "mana": 30,
            "max_mana": 30,
            "stats": {
                "strength": 10,
                "agility": 10,
                "intelligence": 8,
                "vitality": 10,
                "luck": 8
            },
            "skills": ["basic_attack"],
            "ai_type": "aggressive",
            "position": "front"
        })
        
        # Node connections
        self.victory_node = ""
        self.defeat_node = ""
        self.escape_node = ""  # If escape is allowed
        
        # Combat settings
        self.allow_escape = True
        self.escape_difficulty = 10  # DC for escape attempts
        self.formation_matters = True  # Front/back row positioning
        self.initiative_system = "agility"  # agility, random, fixed
        
        # Special mechanics
        self.special_rules = []  # Custom combat rules for this encounter
        self.environmental_effects = []  # Ongoing battlefield effects
        self.dialogue_triggers = {}  # Dialogue that triggers during combat
        
    def to_dict(self):
        """Convert node to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            "node_type": "AdvancedCombat",
            "game_data": {
                "npc": getattr(self, 'npc', 'Combat'),
                "text": getattr(self, 'text', 'A fierce battle begins!'),
                
                # Combat configuration
                "combat_type": self.combat_type,
                "environment": self.environment,
                "weather": self.weather,
                "terrain_effects": self.terrain_effects,
                
                # Victory/defeat conditions
                "victory_conditions": self.victory_conditions,
                "defeat_conditions": self.defeat_conditions,
                "turn_limit": self.turn_limit,
                
                # Rewards
                "experience_reward": self.experience_reward,
                "gold_reward": self.gold_reward,
                "item_rewards": self.item_rewards,
                "skill_points_reward": self.skill_points_reward,
                
                # Combat participants
                "enemies": self.enemies,
                "allies": self.allies,
                "environmental_hazards": self.environmental_hazards,
                
                # Node connections
                "victory_node": self.victory_node,
                "defeat_node": self.defeat_node,
                "escape_node": self.escape_node,
                
                # Combat settings
                "allow_escape": self.allow_escape,
                "escape_difficulty": self.escape_difficulty,
                "formation_matters": self.formation_matters,
                "initiative_system": self.initiative_system,
                
                # Special mechanics
                "special_rules": self.special_rules,
                "environmental_effects": self.environmental_effects,
                "dialogue_triggers": self.dialogue_triggers
            }
        })
        return base_dict
    
    def update_from_dict(self, data):
        """Update node from dictionary data."""
        super().update_from_dict(data)
        
        if 'game_data' in data:
            game_data = data['game_data']
            
            # Combat configuration
            self.combat_type = game_data.get('combat_type', 'advanced')
            self.environment = game_data.get('environment', 'default')
            self.weather = game_data.get('weather', 'clear')
            self.terrain_effects = game_data.get('terrain_effects', [])
            
            # Victory/defeat conditions
            self.victory_conditions = game_data.get('victory_conditions', ['defeat_all_enemies'])
            self.defeat_conditions = game_data.get('defeat_conditions', ['party_defeated'])
            self.turn_limit = game_data.get('turn_limit', 0)
            
            # Rewards
            self.experience_reward = game_data.get('experience_reward', 100)
            self.gold_reward = game_data.get('gold_reward', 50)
            self.item_rewards = game_data.get('item_rewards', [])
            self.skill_points_reward = game_data.get('skill_points_reward', 1)
            
            # Combat participants
            self.enemies = game_data.get('enemies', [])
            self.allies = game_data.get('allies', [])
            self.environmental_hazards = game_data.get('environmental_hazards', [])
            
            # Node connections
            self.victory_node = game_data.get('victory_node', '')
            self.defeat_node = game_data.get('defeat_node', '')
            self.escape_node = game_data.get('escape_node', '')
            
            # Combat settings
            self.allow_escape = game_data.get('allow_escape', True)
            self.escape_difficulty = game_data.get('escape_difficulty', 10)
            self.formation_matters = game_data.get('formation_matters', True)
            self.initiative_system = game_data.get('initiative_system', 'agility')
            
            # Special mechanics
            self.special_rules = game_data.get('special_rules', [])
            self.environmental_effects = game_data.get('environmental_effects', [])
            self.dialogue_triggers = game_data.get('dialogue_triggers', {})
    
    @classmethod
    def from_dict(cls, data):
        """Create node from dictionary data."""
        editor_data = data.get('editor_data', {})
        node = cls(
            x=editor_data.get('x', 0),
            y=editor_data.get('y', 0),
            node_id=editor_data.get('id', '')
        )
        node.update_from_dict(data)
        return node
    
    def get_height(self):
        """Calculate node height based on content."""
        base_height = 120
        content_lines = len(self.enemies) + len(self.allies) + len(self.environmental_hazards)
        return base_height + (content_lines * 15)
    
    def add_enemy(self, enemy_config):
        """Add an enemy to the combat encounter."""
        default_enemy = {
            "id": f"enemy_{len(self.enemies) + 1}",
            "name": "Unknown Enemy",
            "level": 1,
            "health": 100,
            "max_health": 100,
            "mana": 50,
            "max_mana": 50,
            "stats": {
                "strength": 10,
                "agility": 10,
                "intelligence": 10,
                "vitality": 10,
                "luck": 10
            },
            "skills": ["basic_attack"],
            "equipment": {},
            "ai_type": "aggressive",
            "position": "front",
            "status_effects": [],
            "loot_table": "basic_enemy",
            "experience_value": 25,
            "special_abilities": [],
            "resistances": {},
            "weaknesses": {},
            "behavioral_triggers": {}
        }
        
        enemy = {**default_enemy, **enemy_config}
        self.enemies.append(enemy)
        return enemy
    
    def add_ally(self, ally_config):
        """Add an ally to the combat encounter."""
        default_ally = {
            "id": f"ally_{len(self.allies) + 1}",
            "name": "Ally",
            "level": 1,
            "health": 80,
            "max_health": 80,
            "mana": 40,
            "max_mana": 40,
            "stats": {
                "strength": 8,
                "agility": 12,
                "intelligence": 10,
                "vitality": 8,
                "luck": 12
            },
            "skills": ["basic_attack", "heal"],
            "equipment": {},
            "ai_type": "support",
            "position": "back",
            "status_effects": []
        }
        
        ally = {**default_ally, **ally_config}
        self.allies.append(ally)
        return ally
    
    def add_environmental_hazard(self, hazard_config):
        """Add an environmental hazard to the battlefield."""
        default_hazard = {
            "id": f"hazard_{len(self.environmental_hazards) + 1}",
            "name": "Hazard",
            "type": "damage",  # damage, debuff, terrain, interactive
            "effect": {
                "damage": 10,
                "element": "physical"
            },
            "trigger": "turn_end",  # turn_start, turn_end, on_move, manual
            "target": "all",  # all, random, front_row, back_row
            "duration": -1,  # -1 = permanent, 0 = one-time, >0 = countdown
            "description": "A dangerous environmental effect"
        }
        
        hazard = {**default_hazard, **hazard_config}
        self.environmental_hazards.append(hazard)
        return hazard


class CombatSkill:
    """Represents a skill/ability that can be used in combat."""
    
    def __init__(self, skill_id: str, config: Dict[str, Any]):
        self.id = skill_id
        self.name = config.get('name', 'Unnamed Skill')
        self.description = config.get('description', '')
        
        # Costs and requirements
        self.mana_cost = config.get('mana_cost', 0)
        self.stamina_cost = config.get('stamina_cost', 0)
        self.health_cost = config.get('health_cost', 0)
        self.item_cost = config.get('item_cost', {})  # {"item_name": quantity}
        self.cooldown = config.get('cooldown', 0)
        
        # Targeting
        self.target_type = config.get('target_type', 'single_enemy')
        # Options: single_enemy, all_enemies, single_ally, all_allies, self, 
        # front_row, back_row, random, area_effect
        self.range = config.get('range', 'melee')  # melee, ranged, magic
        self.requires_line_of_sight = config.get('requires_line_of_sight', False)
        
        # Effects
        self.damage = config.get('damage', 0)
        self.damage_type = config.get('damage_type', 'physical')
        self.healing = config.get('healing', 0)
        self.accuracy = config.get('accuracy', 95)
        self.critical_chance = config.get('critical_chance', 5)
        self.critical_multiplier = config.get('critical_multiplier', 2.0)
        
        # Status effects applied
        self.status_effects = config.get('status_effects', [])
        self.buff_effects = config.get('buff_effects', [])
        self.debuff_effects = config.get('debuff_effects', [])
        
        # Special properties
        self.element = config.get('element', 'neutral')
        self.damage_formula = config.get('damage_formula', 'strength')
        self.special_effects = config.get('special_effects', [])
        self.animation = config.get('animation', 'default')
        
        # AI considerations
        self.ai_priority = config.get('ai_priority', 'medium')
        self.ai_conditions = config.get('ai_conditions', [])


class StatusEffect:
    """Represents a temporary effect on a combat participant."""
    
    def __init__(self, effect_id: str, config: Dict[str, Any]):
        self.id = effect_id
        self.name = config.get('name', 'Unknown Effect')
        self.description = config.get('description', '')
        self.type = config.get('type', 'neutral')  # buff, debuff, neutral
        
        # Duration
        self.duration = config.get('duration', 3)  # turns remaining
        self.permanent = config.get('permanent', False)
        
        # Effects
        self.stat_modifiers = config.get('stat_modifiers', {})
        self.damage_over_time = config.get('damage_over_time', 0)
        self.healing_over_time = config.get('healing_over_time', 0)
        self.damage_resistance = config.get('damage_resistance', {})
        self.damage_vulnerability = config.get('damage_vulnerability', {})
        
        # Special properties
        self.stackable = config.get('stackable', False)
        self.stacks = config.get('stacks', 1)
        self.dispellable = config.get('dispellable', True)
        self.trigger_effects = config.get('trigger_effects', {})
        
        # Visual
        self.icon = config.get('icon', '⚡')
        self.color = config.get('color', '#888888')


class CombatAI:
    """AI behavior system for combat participants."""
    
    def __init__(self, ai_type: str = "balanced"):
        self.type = ai_type
        self.behaviors = {
            "aggressive": {
                "attack_priority": 0.8,
                "defense_priority": 0.1,
                "support_priority": 0.1,
                "target_preference": "lowest_health",
                "risk_tolerance": "high"
            },
            "defensive": {
                "attack_priority": 0.3,
                "defense_priority": 0.5,
                "support_priority": 0.2,
                "target_preference": "strongest",
                "risk_tolerance": "low"
            },
            "support": {
                "attack_priority": 0.2,
                "defense_priority": 0.2,
                "support_priority": 0.6,
                "target_preference": "ally_lowest_health",
                "risk_tolerance": "medium"
            },
            "tactical": {
                "attack_priority": 0.4,
                "defense_priority": 0.3,
                "support_priority": 0.3,
                "target_preference": "strategic",
                "risk_tolerance": "medium"
            },
            "berserker": {
                "attack_priority": 0.9,
                "defense_priority": 0.05,
                "support_priority": 0.05,
                "target_preference": "random",
                "risk_tolerance": "extreme"
            }
        }
        
        self.current_behavior = self.behaviors.get(ai_type, self.behaviors["balanced"])
        self.memory = {}  # Remember what happened in combat
        self.adaptive = False  # Whether AI learns and adapts
    
    def choose_action(self, actor, allies, enemies, battlefield_state):
        """Choose the best action for an AI-controlled character."""
        available_actions = self._get_available_actions(actor)
        
        if not available_actions:
            return {"type": "wait", "target": None}
        
        # Evaluate each action
        action_scores = {}
        for action in available_actions:
            score = self._evaluate_action(action, actor, allies, enemies, battlefield_state)
            action_scores[action] = score
        
        # Choose highest scoring action
        best_action = max(action_scores.items(), key=lambda x: x[1])
        return self._format_action(best_action[0], actor, allies, enemies)
    
    def _get_available_actions(self, actor):
        """Get all actions this actor can currently perform."""
        actions = ["basic_attack"]  # Always available
        
        # Add skills if actor has mana/stamina
        for skill_id in actor.get('skills', []):
            if self._can_use_skill(actor, skill_id):
                actions.append(skill_id)
        
        # Add items if actor has any
        for item in actor.get('items', []):
            if self._can_use_item(actor, item):
                actions.append(f"use_{item}")
        
        return actions
    
    def _evaluate_action(self, action, actor, allies, enemies, battlefield_state):
        """Evaluate how good an action would be."""
        behavior = self.current_behavior
        score = 0
        
        # Basic action type scoring
        if action == "basic_attack":
            score += behavior["attack_priority"] * 50
        elif action.startswith("heal") or action.startswith("support"):
            score += behavior["support_priority"] * 60
        elif action.startswith("defend") or action.startswith("block"):
            score += behavior["defense_priority"] * 40
        
        # Situational modifiers
        actor_health_ratio = actor.get('health', 100) / actor.get('max_health', 100)
        if actor_health_ratio < 0.3:
            if action.startswith("heal"):
                score += 40
            elif action == "basic_attack" and behavior["risk_tolerance"] == "low":
                score -= 30
        
        # Target availability
        if enemies and action in ["basic_attack"] + [s for s in actor.get('skills', []) if 'damage' in s]:
            score += 20
        
        return score + (hash(action) % 10)  # Add small random factor
    
    def _format_action(self, action, actor, allies, enemies):
        """Format the chosen action with appropriate target."""
        if action == "basic_attack":
            target = self._choose_target(enemies, self.current_behavior["target_preference"])
            return {"type": "attack", "skill": "basic_attack", "target": target}
        
        # Handle other action types
        return {"type": "wait", "target": None}
    
    def _choose_target(self, targets, preference):
        """Choose target based on AI preference."""
        if not targets:
            return None
        
        if preference == "lowest_health":
            return min(targets, key=lambda t: t.get('health', 100))
        elif preference == "highest_health":
            return max(targets, key=lambda t: t.get('health', 100))
        elif preference == "random":
            import random
            return random.choice(targets)
        else:
            return targets[0]  # Default to first target
    
    def _can_use_skill(self, actor, skill_id):
        """Check if actor can use a specific skill."""
        # This would check mana, cooldowns, etc.
        return True  # Simplified for now
    
    def _can_use_item(self, actor, item):
        """Check if actor can use a specific item."""
        # This would check inventory, etc.
        return True  # Simplified for now