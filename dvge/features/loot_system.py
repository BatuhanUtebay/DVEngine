import random
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Rarity(Enum):
    """Loot rarity tiers."""
    COMMON = ("Common", 0.6, "#888888")
    UNCOMMON = ("Uncommon", 0.25, "#2ECC71")
    RARE = ("Rare", 0.10, "#3498DB")
    EPIC = ("Epic", 0.04, "#9B59B6")
    LEGENDARY = ("Legendary", 0.01, "#F39C12")
    
    def __init__(self, display_name: str, weight: float, color: str):
        self.display_name = display_name
        self.weight = weight
        self.color = color


class LootTable:
    """Manages loot drops with weighted random selection."""
    
    def __init__(self, table_name: str):
        self.name = table_name
        self.items = []  # List of (item, rarity, weight_modifier)
        self.guaranteed_items = []
        self.gold_range = (0, 0)
        self.experience_range = (0, 0)
        
    def add_item(self, item_name: str, description: str, 
                 rarity: Rarity, weight_modifier: float = 1.0,
                 properties: Optional[Dict] = None):
        """Adds an item to the loot table."""
        self.items.append({
            'name': item_name,
            'description': description,
            'rarity': rarity,
            'weight': rarity.weight * weight_modifier,
            'properties': properties or {}
        })
        
    def add_guaranteed(self, item_name: str, description: str):
        """Adds a guaranteed drop."""
        self.guaranteed_items.append({
            'name': item_name,
            'description': description
        })
        
    def set_currency_range(self, min_gold: int, max_gold: int):
        """Sets the gold drop range."""
        self.gold_range = (min_gold, max_gold)
        
    def roll_loot(self, luck_modifier: float = 1.0, 
                  num_rolls: int = 1) -> Dict:
        """Rolls for loot drops."""
        drops = {
            'items': [],
            'gold': 0,
            'experience': 0
        }
        
        # Add guaranteed items
        drops['items'].extend(self.guaranteed_items)
        
        # Roll for random items
        for _ in range(num_rolls):
            if self.items and random.random() < 0.7:  # 70% chance for item
                item = self._select_weighted_item(luck_modifier)
                if item:
                    drops['items'].append(item)
                    
        # Roll for gold
        if self.gold_range[1] > 0:
            base_gold = random.randint(*self.gold_range)
            drops['gold'] = int(base_gold * luck_modifier)
            
        # Roll for experience
        if self.experience_range[1] > 0:
            drops['experience'] = random.randint(*self.experience_range)
            
        return drops
        
    def _select_weighted_item(self, luck_modifier: float) -> Optional[Dict]:
        """Selects an item based on weighted random."""
        if not self.items:
            return None
            
        # Apply luck to weights
        weighted_items = []
        for item in self.items:
            modified_weight = item['weight']
            if item['rarity'] in [Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY]:
                modified_weight *= luck_modifier
            weighted_items.append((item, modified_weight))
            
        # Weighted random selection
        total_weight = sum(w for _, w in weighted_items)
        if total_weight <= 0:
            return None
            
        rand = random.uniform(0, total_weight)
        current = 0
        
        for item, weight in weighted_items:
            current += weight
            if rand <= current:
                return item.copy()
                
        return None


class TreasureChestNode:
    """Special node for treasure chests with loot tables."""
    
    def __init__(self, node_id: str, loot_table: LootTable, **kwargs):
        self.id = node_id
        self.loot_table = loot_table
        self.is_locked = kwargs.get('is_locked', False)
        self.lock_difficulty = kwargs.get('lock_difficulty', 15)
        self.required_key = kwargs.get('required_key', None)
        self.is_trapped = kwargs.get('is_trapped', False)
        self.trap_damage = kwargs.get('trap_damage', 10)
        self.already_looted = False
        self.respawns = kwargs.get('respawns', False)
        self.respawn_time = kwargs.get('respawn_time', 100)  # In game steps
        
    def attempt_open(self, has_key: bool = False, 
                     lockpick_skill: int = 0) -> Tuple[bool, str]:
        """Attempts to open the chest."""
        if self.already_looted and not self.respawns:
            return False, "The chest is empty."
            
        if self.is_locked:
            if self.required_key and not has_key:
                return False, f"Requires {self.required_key}"
            elif not self.required_key:
                # Lockpicking attempt
                roll = random.randint(1, 20) + lockpick_skill
                if roll < self.lock_difficulty:
                    return False, "Failed to pick the lock"
                    
        return True, "Success"