import random
from typing import List, Dict, Optional, Tuple
from enum import Enum


class PuzzleType(Enum):
    """Types of puzzles available."""
    RIDDLE = "riddle"
    SEQUENCE = "sequence"
    CIPHER = "cipher"
    MEMORY = "memory"
    LOGIC = "logic"
    PATTERN = "pattern"


class Puzzle:
    """Base puzzle class."""
    
    def __init__(self, puzzle_id: str, puzzle_type: PuzzleType):
        self.id = puzzle_id
        self.type = puzzle_type
        self.attempts_allowed = 3
        self.current_attempts = 0
        self.hints = []
        self.solution = None
        self.is_solved = False
        
    def check_solution(self, answer) -> bool:
        """Checks if the provided answer is correct."""
        self.current_attempts += 1
        if answer == self.solution:
            self.is_solved = True
            return True
        return False
        
    def get_hint(self) -> Optional[str]:
        """Returns a hint if available."""
        hints_given = max(0, self.current_attempts - 1)
        if hints_given < len(self.hints):
            return self.hints[hints_given]
        return None


class SequencePuzzle(Puzzle):
    """Number or pattern sequence puzzle."""
    
    def __init__(self, puzzle_id: str, sequence: List, 
                 missing_positions: List[int]):
        super().__init__(puzzle_id, PuzzleType.SEQUENCE)
        self.full_sequence = sequence
        self.missing_positions = missing_positions
        self.display_sequence = sequence.copy()
        
        # Hide missing elements
        for pos in missing_positions:
            self.display_sequence[pos] = "?"
            
        self.solution = [sequence[pos] for pos in missing_positions]
        
        
class CipherPuzzle(Puzzle):
    """Substitution cipher puzzle."""
    
    def __init__(self, puzzle_id: str, encrypted_text: str, 
                 cipher_type: str = "caesar"):
        super().__init__(puzzle_id, PuzzleType.CIPHER)
        self.encrypted_text = encrypted_text
        self.cipher_type = cipher_type
        
        if cipher_type == "caesar":
            self.shift = random.randint(1, 25)
            self.solution = self._decrypt_caesar(encrypted_text, self.shift)
        elif cipher_type == "reverse":
            self.solution = encrypted_text[::-1]
            
    def _decrypt_caesar(self, text: str, shift: int) -> str:
        """Decrypts Caesar cipher."""
        result = ""
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                result += chr((ord(char) - ascii_offset - shift) % 26 + ascii_offset)
            else:
                result += char
        return result


class MemoryPuzzle(Puzzle):
    """Memory-based puzzle (Simon Says style)."""
    
    def __init__(self, puzzle_id: str, sequence_length: int = 5):
        super().__init__(puzzle_id, PuzzleType.MEMORY)
        self.sequence_length = sequence_length
        colors = ["Red", "Blue", "Green", "Yellow", "Purple"]
        self.solution = [random.choice(colors) for _ in range(sequence_length)]
        self.display_time = 3000  # milliseconds to show sequence
        

class PuzzleNode:
    """Node that presents a puzzle challenge."""
    
    def __init__(self, node_id: str, puzzle: Puzzle, **kwargs):
        self.id = node_id
        self.puzzle = puzzle
        self.success_node = kwargs.get('success_node', '')
        self.failure_node = kwargs.get('failure_node', '')
        self.partial_success_node = kwargs.get('partial_success_node', '')
        self.hint_cost = kwargs.get('hint_cost', 10)  # Cost in gold/resource
        self.skip_cost = kwargs.get('skip_cost', 50)
        self.intelligence_bypass = kwargs.get('intelligence_bypass', 20)
        
        # Rewards
        self.success_rewards = kwargs.get('success_rewards', {})
        self.failure_penalties = kwargs.get('failure_penalties', {})