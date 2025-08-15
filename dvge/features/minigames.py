
import random
from typing import Dict, List, Tuple, Optional
from enum import Enum


class MinigameType(Enum):
    """Types of minigames available."""
    CARD_GAME = "card_game"
    DICE_GAME = "dice_game"
    REACTION = "reaction"
    RHYTHM = "rhythm"
    BETTING = "betting"


class CardGame:
    """Simple card game mechanics (like Higher/Lower)."""
    
    def __init__(self, game_type: str = "higher_lower"):
        self.game_type = game_type
        self.deck = self._create_deck()
        self.current_card = None
        self.score = 0
        self.streak = 0
        
    def _create_deck(self) -> List[int]:
        """Creates a standard deck (just values for simplicity)."""
        return list(range(1, 14)) * 4  # 1-13, four suits
        
    def draw_card(self) -> int:
        """Draws a random card."""
        if not self.deck:
            self.deck = self._create_deck()
        card = random.choice(self.deck)
        self.deck.remove(card)
        return card
        
    def play_higher_lower(self, guess: str) -> Tuple[bool, int, int]:
        """Plays a round of higher/lower."""
        if self.current_card is None:
            self.current_card = self.draw_card()
            
        next_card = self.draw_card()
        
        if guess == "higher":
            success = next_card > self.current_card
        elif guess == "lower":
            success = next_card < self.current_card
        else:  # equal
            success = next_card == self.current_card
            
        old_card = self.current_card
        self.current_card = next_card
        
        if success:
            self.streak += 1
            self.score += self.streak * 10
        else:
            self.streak = 0
            
        return success, old_card, next_card


class ReactionGame:
    """Quick-time event style reaction game."""
    
    def __init__(self):
        self.target_time = random.uniform(1.5, 4.0)  # seconds
        self.tolerance = 0.5  # seconds
        self.perfect_tolerance = 0.1
        
    def check_reaction(self, reaction_time: float) -> str:
        """Checks reaction timing."""
        diff = abs(reaction_time - self.target_time)
        
        if diff <= self.perfect_tolerance:
            return "perfect"
        elif diff <= self.tolerance:
            return "good"
        else:
            return "miss"


class BettingGame:
    """Simple betting/gambling mechanics."""
    
    def __init__(self, game_type: str = "dice"):
        self.game_type = game_type
        self.house_edge = 0.02  # 2% house edge
        
    def play_dice_bet(self, bet_amount: int, 
                     guess: int, num_dice: int = 2) -> Tuple[bool, int, List[int]]:
        """Simple dice betting game."""
        dice = [random.randint(1, 6) for _ in range(num_dice)]
        total = sum(dice)
        
        if guess == total:
            # Exact guess pays 10:1
            winnings = bet_amount * 10
            return True, winnings, dice
        elif abs(guess - total) <= 1:
            # Close guess pays 2:1
            winnings = bet_amount * 2
            return True, winnings, dice
        else:
            return False, -bet_amount, dice
            
    def play_coin_flip(self, bet_amount: int, 
                       choice: str) -> Tuple[bool, int, str]:
        """Simple coin flip."""
        result = random.choice(["heads", "tails"])
        
        if choice == result:
            # Account for house edge
            winnings = int(bet_amount * (2 - self.house_edge))
            return True, winnings, result
        else:
            return False, -bet_amount, result


class MinigameNode:
    """Node that contains a minigame challenge."""
    
    def __init__(self, node_id: str, minigame_type: MinigameType, **kwargs):
        self.id = node_id
        self.minigame_type = minigame_type
        self.entry_fee = kwargs.get('entry_fee', 0)
        self.max_plays = kwargs.get('max_plays', 3)
        self.current_plays = 0
        
        # Navigation
        self.win_node = kwargs.get('win_node', '')
        self.lose_node = kwargs.get('lose_node', '')
        self.skip_node = kwargs.get('skip_node', '')
        
        # Rewards
        self.base_reward = kwargs.get('base_reward', 50)
        self.streak_multiplier = kwargs.get('streak_multiplier', 1.5)
        
        # Initialize appropriate game
        if minigame_type == MinigameType.CARD_GAME:
            self.game = CardGame()
        elif minigame_type == MinigameType.REACTION:
            self.game = ReactionGame()
        elif minigame_type == MinigameType.BETTING:
            self.game = BettingGame()
        else:
            self.game = None