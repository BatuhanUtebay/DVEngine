# dvge/models/enemy.py

"""Enemy model for combat encounters."""


class Enemy:
    """Represents an enemy with stats for the combat system."""
    
    def __init__(self, enemy_id, name="New Enemy", hp=10, attack=3, defense=1):
        self.id = enemy_id
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self._current_hp = hp
    
    def to_dict(self):
        """Serializes the enemy data into a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense
        }
    
    @staticmethod
    def from_dict(data):
        """Creates an Enemy instance from a dictionary."""
        return Enemy(
            enemy_id=data.get('id', ''),
            name=data.get('name', 'New Enemy'),
            hp=data.get('hp', 10),
            attack=data.get('attack', 3),
            defense=data.get('defense', 1)
        )
    
    def take_damage(self, damage):
        """Applies damage to the enemy."""
        actual_damage = max(0, damage - self.defense)
        self._current_hp = max(0, self._current_hp - actual_damage)
        return actual_damage
    
    def heal(self, amount):
        """Heals the enemy by the specified amount."""
        self._current_hp = min(self.max_hp, self._current_hp + amount)
    
    def is_alive(self):
        """Returns True if the enemy is still alive."""
        return self._current_hp > 0
    
    def is_dead(self):
        """Returns True if the enemy is dead."""
        return self._current_hp <= 0