# dvge/game_mechanics.py
# NEW FILE: This file will hold classes related to advanced game mechanics like Enemies.

class Enemy:
    """
    Represents an enemy with stats for the combat system.
    """
    def __init__(self, enemy_id, name="New Enemy", hp=10, attack=3, defense=1):
        self.id = enemy_id
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense

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
