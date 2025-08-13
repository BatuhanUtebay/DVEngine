# dvge/models/game_timer.py

"""Game timer model for timed events and countdowns."""


class GameTimer:
    """Represents a timer for timed events."""
    
    def __init__(self, timer_id, duration=60):
        self.id = timer_id
        self.duration = duration  # in seconds
        self._remaining_time = duration
        self._is_running = False
    
    def to_dict(self):
        """Serializes the timer data into a dictionary."""
        return {
            "id": self.id,
            "duration": self.duration
        }
    
    @staticmethod
    def from_dict(data):
        """Creates a GameTimer instance from a dictionary."""
        return GameTimer(
            timer_id=data.get('id', ''),
            duration=data.get('duration', 60)
        )
    
    def start(self):
        """Starts the timer."""
        self._is_running = True
        self._remaining_time = self.duration
    
    def stop(self):
        """Stops the timer."""
        self._is_running = False
    
    def pause(self):
        """Pauses the timer."""
        self._is_running = False
    
    def resume(self):
        """Resumes the timer."""
        self._is_running = True
    
    def reset(self):
        """Resets the timer to its original duration."""
        self._remaining_time = self.duration
        self._is_running = False
    
    def tick(self, delta_time=1):
        """Updates the timer by the specified amount."""
        if self._is_running and self._remaining_time > 0:
            self._remaining_time = max(0, self._remaining_time - delta_time)
    
    def is_expired(self):
        """Returns True if the timer has reached zero."""
        return self._remaining_time <= 0
    
    def is_running(self):
        """Returns True if the timer is currently running."""
        return self._is_running
    
    def get_remaining_time(self):
        """Returns the remaining time in seconds."""
        return self._remaining_time
    
    def get_progress(self):
        """Returns the timer progress as a value between 0 and 1."""
        if self.duration <= 0:
            return 1.0
        return 1.0 - (self._remaining_time / self.duration)