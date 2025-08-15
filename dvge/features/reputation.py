from typing import Dict, List, Optional
from enum import Enum


class ReputationLevel(Enum):
    """Reputation levels with NPCs or factions."""
    HOSTILE = ("Hostile", -100, -51, "#E74C3C")
    UNFRIENDLY = ("Unfriendly", -50, -11, "#E67E22")
    NEUTRAL = ("Neutral", -10, 10, "#95A5A6")
    FRIENDLY = ("Friendly", 11, 50, "#3498DB")
    ALLIED = ("Allied", 51, 100, "#2ECC71")
    
    def __init__(self, name: str, min_val: int, max_val: int, color: str):
        self.display_name = name
        self.min_value = min_val
        self.max_value = max_val
        self.color = color
        
    @classmethod
    def get_level(cls, value: int):
        """Gets reputation level from numeric value."""
        for level in cls:
            if level.min_value <= value <= level.max_value:
                return level
        return cls.NEUTRAL


class ReputationSystem:
    """Manages reputation with various factions and NPCs."""
    
    def __init__(self):
        self.reputations = {}  # faction_id: value
        self.faction_relationships = {}  # faction_id: {other_faction: modifier}
        self.reputation_perks = {}  # faction_id: [(threshold, perk_id)]
        
    def modify_reputation(self, faction_id: str, amount: int, 
                         propagate: bool = True) -> Dict[str, int]:
        """Modifies reputation with a faction."""
        if faction_id not in self.reputations:
            self.reputations[faction_id] = 0
            
        old_value = self.reputations[faction_id]
        self.reputations[faction_id] = max(-100, min(100, old_value + amount))
        
        changes = {faction_id: amount}
        
        # Propagate to related factions
        if propagate and faction_id in self.faction_relationships:
            for other_faction, modifier in self.faction_relationships[faction_id].items():
                related_change = int(amount * modifier)
                if related_change != 0:
                    sub_changes = self.modify_reputation(
                        other_faction, related_change, propagate=False
                    )
                    changes.update(sub_changes)
                    
        return changes
        
    def get_reputation_level(self, faction_id: str) -> ReputationLevel:
        """Gets the reputation level with a faction."""
        value = self.reputations.get(faction_id, 0)
        return ReputationLevel.get_level(value)
        
    def check_reputation_requirement(self, faction_id: str, 
                                   required_level: ReputationLevel) -> bool:
        """Checks if reputation meets requirement."""
        current = self.reputations.get(faction_id, 0)
        return current >= required_level.min_value
        
    def get_unlocked_perks(self, faction_id: str) -> List[str]:
        """Gets list of unlocked perks for a faction."""
        if faction_id not in self.reputation_perks:
            return []
            
        current = self.reputations.get(faction_id, 0)
        unlocked = []
        
        for threshold, perk_id in self.reputation_perks[faction_id]:
            if current >= threshold:
                unlocked.append(perk_id)
                
        return unlocked


class ReputationGatedNode:
    """Node that requires certain reputation to access."""
    
    def __init__(self, node_id: str, **kwargs):
        self.id = node_id
        self.reputation_requirements = kwargs.get('reputation_requirements', {})
        # Format: {faction_id: minimum_value}
        self.reputation_changes = kwargs.get('reputation_changes', {})
        # Format: {faction_id: change_amount}
        
    def check_access(self, reputation_system: ReputationSystem) -> bool:
        """Checks if player can access this node."""
        for faction, min_value in self.reputation_requirements.items():
            if reputation_system.reputations.get(faction, 0) < min_value:
                return False
        return True