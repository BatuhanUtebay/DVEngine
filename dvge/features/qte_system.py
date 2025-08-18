# dvge/features/qte_system.py

"""Core Quick Time Event system for handling interactive sequences."""

import time
import random
from typing import List, Dict, Callable, Optional
from ..models.qte_node import QTENode, QTEEvent, QTEResult


class QTEEngine:
    """Core engine for processing Quick Time Events."""

    def __init__(self):
        self.current_qte = None
        self.qte_active = False
        self.start_time = 0
        self.events = []
        self.callbacks = {}
        self.performance_stats = {}

    def start_qte(self, qte_node: QTENode, callbacks: Dict[str, Callable] = None):
        """Start a QTE sequence."""
        self.current_qte = qte_node
        self.qte_active = True
        self.start_time = time.time()
        self.events = []
        self.callbacks = callbacks or {}

        # Validate QTE configuration
        issues = qte_node.validate_configuration()
        if issues:
            self._end_qte_with_error(
                f"QTE configuration error: {'; '.join(issues)}")
            return False

        # Auto-complete for accessibility
        if qte_node.auto_complete_mode:
            self._auto_complete_qte()
            return True

        # Start the appropriate QTE type
        if qte_node.qte_type == "sequence":
            return self._start_sequence_qte()
        elif qte_node.qte_type == "mash":
            return self._start_mash_qte()
        elif qte_node.qte_type == "hold":
            return self._start_hold_qte()
        elif qte_node.qte_type == "rhythm":
            return self._start_rhythm_qte()
        else:
            self._end_qte_with_error(f"Unknown QTE type: {qte_node.qte_type}")
            return False

    def process_input(self, key: str, press_time: float = None) -> bool:
        """Process player input during QTE."""
        if not self.qte_active or not self.current_qte:
            return False

        if press_time is None:
            press_time = time.time()

        # Handle different QTE types
        if self.current_qte.qte_type == "sequence":
            return self._process_sequence_input(key, press_time)
        elif self.current_qte.qte_type == "mash":
            return self._process_mash_input(key, press_time)
        elif self.current_qte.qte_type == "hold":
            return self._process_hold_input(key, press_time)
        elif self.current_qte.qte_type == "rhythm":
            return self._process_rhythm_input(key, press_time)

        return False

    def update(self) -> bool:
        """Update QTE state - call this regularly during QTE."""
        if not self.qte_active:
            return False

        current_time = time.time()
        elapsed = current_time - self.start_time

        # Check for timeout
        if elapsed > self.current_qte.time_limit:
            self._end_qte_timeout()
            return False

        # Update QTE-specific logic
        if self.current_qte.qte_type == "hold":
            return self._update_hold_qte(elapsed)
        elif self.current_qte.qte_type == "rhythm":
            return self._update_rhythm_qte(elapsed)

        return True

    def get_current_state(self) -> Dict:
        """Get current QTE state for UI updates."""
        if not self.qte_active or not self.current_qte:
            return {"active": False}

        current_time = time.time()
        elapsed = current_time - self.start_time
        remaining = max(0, self.current_qte.time_limit - elapsed)
        progress = elapsed / self.current_qte.time_limit if self.current_qte.time_limit > 0 else 0

        state = {
            "active": True,
            "qte_type": self.current_qte.qte_type,
            "elapsed_time": elapsed,
            "remaining_time": remaining,
            "progress": progress,
            "events_count": len(self.events),
            "show_prompts": self.current_qte.show_button_prompts,
            "show_progress": self.current_qte.show_progress_bar,
            "show_countdown": self.current_qte.show_countdown
        }

        # Add type-specific state
        if self.current_qte.qte_type == "sequence":
            state["button_sequence"] = self.current_qte.button_sequence
            state["current_button_index"] = len(self.events)
            state["next_button"] = self._get_next_expected_button()
        elif self.current_qte.qte_type == "mash":
            state["mash_count"] = len(self.events)
            state["mash_target"] = self.current_qte.mash_target_count
            state["mash_button"] = self.current_qte.mash_button
        elif self.current_qte.qte_type == "hold":
            state["hold_button"] = self.current_qte.hold_button
            state["hold_duration"] = self.current_qte.hold_duration
            state["is_holding"] = getattr(self, '_holding', False)
        elif self.current_qte.qte_type == "rhythm":
            state["rhythm_pattern"] = self.current_qte.rhythm_pattern
            state["current_beat"] = getattr(self, '_current_beat', 0)

        return state

    def _start_sequence_qte(self) -> bool:
        """Start a button sequence QTE."""
        self._current_sequence_index = 0
        self._call_callback('qte_started', {
            'type': 'sequence',
            'buttons': self.current_qte.button_sequence,
            'time_limit': self.current_qte.time_limit
        })
        return True

    def _start_mash_qte(self) -> bool:
        """Start a button mashing QTE."""
        self._mash_count = 0
        self._call_callback('qte_started', {
            'type': 'mash',
            'button': self.current_qte.mash_button,
            'target': self.current_qte.mash_target_count,
            'time_limit': self.current_qte.time_limit
        })
        return True

    def _start_hold_qte(self) -> bool:
        """Start a button hold QTE."""
        self._holding = False
        self._hold_start_time = 0
        self._call_callback('qte_started', {
            'type': 'hold',
            'button': self.current_qte.hold_button,
            'duration': self.current_qte.hold_duration
        })
        return True

    def _start_rhythm_qte(self) -> bool:
        """Start a rhythm-based QTE."""
        self._current_beat = 0
        self._rhythm_start_time = time.time()
        self._next_beat_time = self._rhythm_start_time + \
            self.current_qte.rhythm_pattern[0]
        self._call_callback('qte_started', {
            'type': 'rhythm',
            'pattern': self.current_qte.rhythm_pattern,
            'tolerance': self.current_qte.rhythm_tolerance
        })
        return True

    def _process_sequence_input(self, key: str, press_time: float) -> bool:
        """Process input for sequence QTE."""
        expected_button = self._get_next_expected_button()

        if not expected_button:
            return False  # Sequence complete

        # Check if correct button
        success = (key.upper() == expected_button.upper())

        # Calculate timing accuracy
        expected_time = self.start_time + \
            (len(self.events) * self.current_qte.sequence_timing)
        timing_difference = abs(press_time - expected_time)
        max_difference = self.current_qte.sequence_timing / 2
        accuracy = max(0, 1.0 - (timing_difference / max_difference))

        # Create event
        event = QTEEvent(key, press_time - self.start_time, success)
        event.expected_timing = expected_time - self.start_time
        event.accuracy = accuracy if success else 0.0
        self.events.append(event)

        self._call_callback('qte_input', {
            'key': key,
            'success': success,
            'accuracy': accuracy,
            'sequence_progress': len(self.events) / len(self.current_qte.button_sequence)
        })

        # Check if sequence complete
        if len(self.events) >= len(self.current_qte.button_sequence):
            self._end_qte_success()

        return success

    def _process_mash_input(self, key: str, press_time: float) -> bool:
        """Process input for button mashing QTE."""
        if key.upper() != self.current_qte.mash_button.upper():
            return False

        # Add mash event
        event = QTEEvent(key, press_time - self.start_time, True)
        event.accuracy = 1.0  # Mashing doesn't have timing accuracy
        self.events.append(event)

        progress = len(self.events) / self.current_qte.mash_target_count

        self._call_callback('qte_input', {
            'key': key,
            'success': True,
            'mash_count': len(self.events),
            'progress': progress
        })

        # Check if target reached
        if len(self.events) >= self.current_qte.mash_target_count:
            self._end_qte_success()

        return True

    def _process_hold_input(self, key: str, press_time: float) -> bool:
        """Process input for button hold QTE."""
        if key.upper() != self.current_qte.hold_button.upper():
            return False

        if not self._holding:
            self._holding = True
            self._hold_start_time = press_time

            self._call_callback('qte_input', {
                'key': key,
                'action': 'hold_start',
                'success': True
            })

        return True

    def _process_rhythm_input(self, key: str, press_time: float) -> bool:
        """Process input for rhythm QTE."""
        if self._current_beat >= len(self.current_qte.rhythm_pattern):
            return False

        # Check timing accuracy
        timing_difference = abs(press_time - self._next_beat_time)
        success = timing_difference <= self.current_qte.rhythm_tolerance
        accuracy = max(0, 1.0 - (timing_difference /
                       self.current_qte.rhythm_tolerance))

        # Create event
        event = QTEEvent(key, press_time - self.start_time, success)
        event.expected_timing = self._next_beat_time - self.start_time
        event.accuracy = accuracy if success else 0.0
        self.events.append(event)

        self._call_callback('qte_input', {
            'key': key,
            'success': success,
            'accuracy': accuracy,
            'beat': self._current_beat,
            'timing_difference': timing_difference
        })

        # Advance to next beat
        self._current_beat += 1
        if self._current_beat < len(self.current_qte.rhythm_pattern):
            self._next_beat_time += self.current_qte.rhythm_pattern[self._current_beat]
        else:
            # Rhythm complete
            self._end_qte_success()

        return success

    def _update_hold_qte(self, elapsed: float) -> bool:
        """Update hold QTE state."""
        if self._holding:
            hold_duration = elapsed - (self._hold_start_time - self.start_time)
            if hold_duration >= self.current_qte.hold_duration:
                # Hold complete
                event = QTEEvent(self.current_qte.hold_button,
                                 hold_duration, True)
                event.accuracy = 1.0
                self.events.append(event)
                self._end_qte_success()
                return False

        return True

    def _update_rhythm_qte(self, elapsed: float) -> bool:
        """Update rhythm QTE state."""
        # Check if we've missed a beat
        current_time = time.time()
        if (hasattr(self, '_next_beat_time') and
                current_time > self._next_beat_time + self.current_qte.rhythm_tolerance):

            # Missed beat
            event = QTEEvent("", elapsed, False)
            event.accuracy = 0.0
            self.events.append(event)

            self._call_callback('qte_input', {
                'key': '',
                'success': False,
                'accuracy': 0.0,
                'beat': self._current_beat,
                'missed': True
            })

            # Move to next beat or end
            self._current_beat += 1
            if self._current_beat < len(self.current_qte.rhythm_pattern):
                self._next_beat_time += self.current_qte.rhythm_pattern[self._current_beat]
            else:
                self._end_qte_failure()
                return False

        return True

    def _get_next_expected_button(self) -> str:
        """Get the next expected button in sequence."""
        if (hasattr(self, '_current_sequence_index') and
                self._current_sequence_index < len(self.current_qte.button_sequence)):
            return self.current_qte.button_sequence[self._current_sequence_index]
        elif len(self.events) < len(self.current_qte.button_sequence):
            return self.current_qte.button_sequence[len(self.events)]
        return ""

    def _auto_complete_qte(self):
        """Auto-complete QTE for accessibility."""
        # Create perfect events for the QTE
        if self.current_qte.qte_type == "sequence":
            for i, button in enumerate(self.current_qte.button_sequence):
                event = QTEEvent(button, i * 0.5, True)
                event.accuracy = 1.0
                self.events.append(event)
        else:
            # For other types, create a single perfect event
            event = QTEEvent("AUTO", 0, True)
            event.accuracy = 1.0
            self.events.append(event)

        self._end_qte_success()

    def _end_qte_success(self):
        """End QTE with success."""
        result = self._create_result("success")
        self._call_callback('qte_completed', result)
        self._reset_state()

    def _end_qte_failure(self):
        """End QTE with failure."""
        result = self._create_result("failure")
        self._call_callback('qte_completed', result)
        self._reset_state()

    def _end_qte_timeout(self):
        """End QTE due to timeout."""
        result = self._create_result("timeout")
        self._call_callback('qte_completed', result)
        self._reset_state()

    def _end_qte_with_error(self, error: str):
        """End QTE with error."""
        self._call_callback('qte_error', {'error': error})
        self._reset_state()

    def _create_result(self, outcome: str) -> QTEResult:
        """Create QTE result object."""
        result = QTEResult()
        result.events = self.events.copy()
        result.completion_time = time.time() - self.start_time
        result.outcome = outcome

        # Calculate performance metrics
        if self.events:
            total_accuracy = sum(event.accuracy for event in self.events)
            result.accuracy_percentage = total_accuracy / len(self.events)

            # Determine result type
            if result.accuracy_percentage >= self.current_qte.perfect_threshold:
                result.perfect_execution = True
                result.overall_success = True
                result.outcome = "perfect"
                result.next_node_id = self.current_qte.success_node
            elif result.accuracy_percentage >= self.current_qte.success_threshold:
                result.overall_success = True
                result.outcome = "success"
                result.next_node_id = self.current_qte.success_node
            else:
                result.overall_success = False
                if self.current_qte.partial_success_node and result.accuracy_percentage > 0.3:
                    result.outcome = "partial"
                    result.next_node_id = self.current_qte.partial_success_node
                else:
                    result.outcome = "failure"
                    result.next_node_id = self.current_qte.failure_node
        else:
            result.accuracy_percentage = 0.0
            result.overall_success = False
            result.next_node_id = self.current_qte.failure_node

        return result

    def _call_callback(self, event_type: str, data: Dict):
        """Call registered callback for event."""
        if event_type in self.callbacks:
            self.callbacks[event_type](data)

    def _reset_state(self):
        """Reset QTE engine state."""
        self.current_qte = None
        self.qte_active = False
        self.start_time = 0
        self.events = []

        # Clear type-specific state
        if hasattr(self, '_current_sequence_index'):
            delattr(self, '_current_sequence_index')
        if hasattr(self, '_mash_count'):
            delattr(self, '_mash_count')
        if hasattr(self, '_holding'):
            delattr(self, '_holding')
        if hasattr(self, '_hold_start_time'):
            delattr(self, '_hold_start_time')
        if hasattr(self, '_current_beat'):
            delattr(self, '_current_beat')
        if hasattr(self, '_rhythm_start_time'):
            delattr(self, '_rhythm_start_time')
        if hasattr(self, '_next_beat_time'):
            delattr(self, '_next_beat_time')


class QTEPresets:
    """Predefined QTE configurations for common scenarios."""

    @staticmethod
    def create_dodge_sequence():
        """Create a dodge/evasion QTE."""
        return {
            'qte_type': 'sequence',
            'button_sequence': ['A', 'D'],
            'time_limit': 2.0,
            'difficulty': 'normal',
            'success_message': 'Dodged successfully!',
            'failure_message': 'Hit! Take damage.'
        }

    @staticmethod
    def create_button_mash():
        """Create a button mashing QTE."""
        return {
            'qte_type': 'mash',
            'mash_button': 'SPACE',
            'mash_target_count': 15,
            'time_limit': 5.0,
            'success_message': 'Broke free!',
            'failure_message': 'Failed to escape!'
        }

    @staticmethod
    def create_precision_hold():
        """Create a precision hold QTE."""
        return {
            'qte_type': 'hold',
            'hold_button': 'E',
            'hold_duration': 3.0,
            'time_limit': 4.0,
            'success_message': 'Steady hands!',
            'failure_message': 'Hand slipped!'
        }

    @staticmethod
    def create_conversation_rhythm():
        """Create a conversation rhythm QTE."""
        return {
            'qte_type': 'rhythm',
            'rhythm_pattern': [1.5, 1.0, 0.8, 1.2],
            'rhythm_tolerance': 0.3,
            'time_limit': 6.0,
            'success_message': 'Perfect timing!',
            'failure_message': 'Awkward silence...'
        }
