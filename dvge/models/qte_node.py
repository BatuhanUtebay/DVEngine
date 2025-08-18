# dvge/models/qte_node.py

"""Quick Time Event (QTE) node implementation for action sequences."""

from .base_node import BaseNode
from ..constants import *
import json


class QTENode(BaseNode):
    """Represents a Quick Time Event node for interactive action sequences."""

    NODE_TYPE = "QTE"

    def __init__(self, x, y, node_id, npc="System", text="", **kwargs):
        super().__init__(x, y, node_id, npc, text, **kwargs)

        # QTE sequence configuration
        self.qte_type = "sequence"  # sequence, mash, hold, rhythm
        self.button_sequence = ["SPACE"]  # List of keys/buttons to press
        self.time_limit = 3.0  # Time limit in seconds
        self.difficulty = "normal"  # easy, normal, hard

        # Visual settings
        self.show_button_prompts = True
        self.show_progress_bar = True
        self.show_countdown = True
        self.prompt_style = "modern"  # modern, classic, minimal

        # Sequence-specific settings
        self.sequence_timing = 1.0  # Time between button prompts
        self.allow_early_press = False  # Can press before prompt appears
        self.require_exact_timing = False  # Must press at exact moment

        # Button mashing settings (for mash type)
        self.mash_target_count = 10  # Number of presses needed
        self.mash_button = "SPACE"

        # Hold button settings (for hold type)
        self.hold_duration = 2.0  # How long to hold
        self.hold_button = "SPACE"

        # Rhythm settings (for rhythm type)
        self.rhythm_pattern = [1.0, 0.5, 0.5, 1.0]  # Beat timings
        self.rhythm_tolerance = 0.2  # Timing tolerance

        # Outcomes
        self.success_node = ""  # Node ID for success
        self.failure_node = ""  # Node ID for failure
        self.partial_success_node = ""  # Node ID for partial success

        # Performance thresholds
        self.perfect_threshold = 0.95  # 95% accuracy for perfect
        self.success_threshold = 0.7   # 70% accuracy for success

        # Effects and feedback
        self.success_message = "Success!"
        self.failure_message = "Failed!"
        self.perfect_message = "Perfect!"
        self.vibration_enabled = True
        self.screen_shake_enabled = True

        # Accessibility options
        self.auto_complete_mode = False  # For accessibility
        self.simplified_controls = False
        self.visual_indicators_only = False

    def add_button_to_sequence(self, button):
        """Add a button to the QTE sequence."""
        if button not in self.button_sequence:
            self.button_sequence.append(button)

    def remove_button_from_sequence(self, button):
        """Remove a button from the QTE sequence."""
        if button in self.button_sequence:
            self.button_sequence.remove(button)

    def set_difficulty(self, difficulty):
        """Set QTE difficulty and adjust parameters accordingly."""
        self.difficulty = difficulty

        # Adjust parameters based on difficulty
        if difficulty == "easy":
            self.time_limit *= 1.5
            self.success_threshold = 0.5
            self.rhythm_tolerance = 0.3
        elif difficulty == "hard":
            self.time_limit *= 0.7
            self.success_threshold = 0.8
            self.rhythm_tolerance = 0.1
            self.require_exact_timing = True
        else:  # normal
            pass  # Keep default values

    def get_expected_duration(self):
        """Calculate expected duration of QTE in seconds."""
        if self.qte_type == "sequence":
            return len(self.button_sequence) * self.sequence_timing + 1.0
        elif self.qte_type == "mash":
            return self.time_limit
        elif self.qte_type == "hold":
            return self.hold_duration + 1.0
        elif self.qte_type == "rhythm":
            return sum(self.rhythm_pattern) + 1.0
        return self.time_limit

    def validate_configuration(self):
        """Validate QTE configuration for common issues."""
        issues = []

        if not self.button_sequence and self.qte_type == "sequence":
            issues.append("Sequence QTE needs at least one button")

        if self.time_limit <= 0:
            issues.append("Time limit must be positive")

        if not self.success_node and not self.failure_node:
            issues.append("QTE needs at least one outcome node")

        if self.qte_type == "rhythm" and not self.rhythm_pattern:
            issues.append("Rhythm QTE needs a pattern")

        return issues

    def to_dict(self):
        """Serializes the QTE node's data."""
        data = super().to_dict()
        data["game_data"].update({
            "qte_type": self.qte_type,
            "button_sequence": self.button_sequence,
            "time_limit": self.time_limit,
            "difficulty": self.difficulty,
            "show_button_prompts": self.show_button_prompts,
            "show_progress_bar": self.show_progress_bar,
            "show_countdown": self.show_countdown,
            "prompt_style": self.prompt_style,
            "sequence_timing": self.sequence_timing,
            "allow_early_press": self.allow_early_press,
            "require_exact_timing": self.require_exact_timing,
            "mash_target_count": self.mash_target_count,
            "mash_button": self.mash_button,
            "hold_duration": self.hold_duration,
            "hold_button": self.hold_button,
            "rhythm_pattern": self.rhythm_pattern,
            "rhythm_tolerance": self.rhythm_tolerance,
            "success_node": self.success_node,
            "failure_node": self.failure_node,
            "partial_success_node": self.partial_success_node,
            "perfect_threshold": self.perfect_threshold,
            "success_threshold": self.success_threshold,
            "success_message": self.success_message,
            "failure_message": self.failure_message,
            "perfect_message": self.perfect_message,
            "vibration_enabled": self.vibration_enabled,
            "screen_shake_enabled": self.screen_shake_enabled,
            "auto_complete_mode": self.auto_complete_mode,
            "simplified_controls": self.simplified_controls,
            "visual_indicators_only": self.visual_indicators_only
        })
        return data

    def get_height(self):
        """Calculates the total height including QTE info and connection handles."""
        base_height = super().get_height()

        # Add space for QTE type info and timing
        qte_info_height = 40

        # Add space for type-specific details
        if self.button_sequence or self.qte_type in ['mash', 'hold', 'rhythm']:
            detail_height = 20
        else:
            detail_height = 0

        # Add space for outcome connections (always show at least success/failure)
        outcome_count = 2  # success and failure
        if self.partial_success_node:  # Add partial success if configured
            outcome_count += 1

        outcome_height = outcome_count * 15  # 15px per outcome line

        # Add space for accessibility indicator if enabled
        accessibility_height = 15 if self.auto_complete_mode else 0

        return base_height + qte_info_height + detail_height + outcome_height + accessibility_height

    @classmethod
    def from_dict(cls, data):
        """Creates a QTENode instance from a dictionary."""
        game_data = data['game_data']
        editor_data = data['editor_data']

        node = cls(
            x=editor_data['x'],
            y=editor_data['y'],
            node_id=editor_data['id'],
            npc=game_data.get('npc', 'System'),
            text=game_data.get('text', ''),
            theme=game_data.get('backgroundTheme', ''),
            chapter=game_data.get('chapter', ''),
            color=editor_data.get('color', NODE_DEFAULT_COLOR),
            backgroundImage=game_data.get('backgroundImage', ''),
            audio=game_data.get('audio', ''),
            music=game_data.get('music', '')
        )

        # Load QTE-specific properties
        node.qte_type = game_data.get('qte_type', 'sequence')
        node.button_sequence = game_data.get('button_sequence', ['SPACE'])
        node.time_limit = game_data.get('time_limit', 3.0)
        node.difficulty = game_data.get('difficulty', 'normal')
        node.show_button_prompts = game_data.get('show_button_prompts', True)
        node.show_progress_bar = game_data.get('show_progress_bar', True)
        node.show_countdown = game_data.get('show_countdown', True)
        node.prompt_style = game_data.get('prompt_style', 'modern')
        node.sequence_timing = game_data.get('sequence_timing', 1.0)
        node.allow_early_press = game_data.get('allow_early_press', False)
        node.require_exact_timing = game_data.get(
            'require_exact_timing', False)
        node.mash_target_count = game_data.get('mash_target_count', 10)
        node.mash_button = game_data.get('mash_button', 'SPACE')
        node.hold_duration = game_data.get('hold_duration', 2.0)
        node.hold_button = game_data.get('hold_button', 'SPACE')
        node.rhythm_pattern = game_data.get(
            'rhythm_pattern', [1.0, 0.5, 0.5, 1.0])
        node.rhythm_tolerance = game_data.get('rhythm_tolerance', 0.2)
        node.success_node = game_data.get('success_node', '')
        node.failure_node = game_data.get('failure_node', '')
        node.partial_success_node = game_data.get('partial_success_node', '')
        node.perfect_threshold = game_data.get('perfect_threshold', 0.95)
        node.success_threshold = game_data.get('success_threshold', 0.7)
        node.success_message = game_data.get('success_message', 'Success!')
        node.failure_message = game_data.get('failure_message', 'Failed!')
        node.perfect_message = game_data.get('perfect_message', 'Perfect!')
        node.vibration_enabled = game_data.get('vibration_enabled', True)
        node.screen_shake_enabled = game_data.get('screen_shake_enabled', True)
        node.auto_complete_mode = game_data.get('auto_complete_mode', False)
        node.simplified_controls = game_data.get('simplified_controls', False)
        node.visual_indicators_only = game_data.get(
            'visual_indicators_only', False)

        return node


class QTEEvent:
    """Represents a single QTE input event."""

    def __init__(self, button, timing, success=False):
        self.button = button
        self.timing = timing  # Time when button was pressed
        self.expected_timing = 0  # When button should have been pressed
        self.success = success
        self.accuracy = 0.0  # How accurate the timing was (0.0 - 1.0)


class QTEResult:
    """Represents the result of a completed QTE sequence."""

    def __init__(self):
        self.overall_success = False
        self.perfect_execution = False
        self.accuracy_percentage = 0.0
        self.events = []  # List of QTEEvent objects
        self.completion_time = 0.0
        self.outcome = "failure"  # success, failure, partial, perfect
        self.next_node_id = ""

    def calculate_score(self):
        """Calculate overall performance score."""
        if not self.events:
            return 0.0

        total_accuracy = sum(event.accuracy for event in self.events)
        return total_accuracy / len(self.events)

    def get_performance_grade(self):
        """Get letter grade for performance."""
        score = self.calculate_score()
        if score >= 0.95:
            return "S"  # Perfect
        elif score >= 0.85:
            return "A"
        elif score >= 0.75:
            return "B"
        elif score >= 0.65:
            return "C"
        elif score >= 0.50:
            return "D"
        else:
            return "F"
