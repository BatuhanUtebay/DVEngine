# dvge/models/music_system.py

"""Dynamic music system for adaptive storytelling soundtracks."""

import os
import json
import math
from typing import Dict, List, Optional, Union
from enum import Enum


class MusicMood(Enum):
    """Predefined music moods for automatic selection."""
    PEACEFUL = "peaceful"
    TENSE = "tense"
    DRAMATIC = "dramatic"
    ROMANTIC = "romantic"
    MYSTERIOUS = "mysterious"
    EPIC = "epic"
    SAD = "sad"
    HAPPY = "happy"
    COMBAT = "combat"
    EXPLORATION = "exploration"
    SUSPENSE = "suspense"
    TRIUMPHANT = "triumphant"


class MusicIntensity(Enum):
    """Music intensity levels for dynamic layering."""
    AMBIENT = 1      # Subtle background
    LOW = 2          # Gentle presence
    MEDIUM = 3       # Standard intensity
    HIGH = 4         # Strong emotional impact
    INTENSE = 5      # Maximum dramatic effect


class TransitionType(Enum):
    """Types of music transitions."""
    CROSSFADE = "crossfade"      # Fade out old, fade in new
    INSTANT = "instant"          # Immediate switch
    OVERLAP = "overlap"          # Layer both tracks briefly
    PAUSE_RESUME = "pause_resume" # Pause current, resume later
    LAYER = "layer"              # Add as additional layer


class MusicTrack:
    """Represents a single music track with metadata."""
    
    def __init__(self, track_id: str, name: str = "", file_path: str = ""):
        self.track_id = track_id
        self.name = name or track_id.replace('_', ' ').title()
        self.file_path = file_path
        
        # Categorization
        self.mood = MusicMood.PEACEFUL
        self.intensity = MusicIntensity.MEDIUM
        self.tags = []  # Additional tags like ["orchestral", "piano", "strings"]
        
        # Technical properties
        self.duration = 0.0  # Track length in seconds
        self.loop_start = 0.0  # Loop point start
        self.loop_end = 0.0   # Loop point end (0 = end of track)
        self.is_loopable = True
        self.bpm = 120        # Beats per minute for syncing
        
        # Usage context
        self.situations = []  # When to use: ["dialogue", "combat", "exploration"]
        self.characters = []  # Associated characters
        self.chapters = []    # Specific story chapters
        self.emotions = []    # Emotional contexts ["joy", "fear", "love"]
        
        # Audio properties
        self.volume = 1.0     # Default volume (0.0 - 1.0)
        self.fade_in_time = 2.0   # Default fade in duration
        self.fade_out_time = 2.0  # Default fade out duration
        
        # Advanced features
        self.layers = {}      # Additional instrumental layers
        self.variations = {}  # Different versions (intensity, instrumentation)
        self.stem_tracks = {} # Individual instrument stems for mixing
        
        # Conditions for automatic selection
        self.play_conditions = []     # When to auto-play this track
        self.stop_conditions = []     # When to stop this track
        self.priority = 5             # Selection priority (1-10, higher = more priority)
    
    def matches_context(self, context: Dict) -> float:
        """Calculate how well this track matches the given context."""
        score = 0.0
        
        # Mood matching (high weight)
        if context.get('mood') == self.mood.value:
            score += 10.0
        
        # Intensity matching
        context_intensity = context.get('intensity', 3)
        intensity_diff = abs(self.intensity.value - context_intensity)
        score += max(0, 5 - intensity_diff)
        
        # Situation matching
        situation = context.get('situation', '')
        if situation in self.situations:
            score += 8.0
        
        # Character matching
        character = context.get('character', '')
        if character in self.characters:
            score += 6.0
        
        # Emotion matching
        emotions = context.get('emotions', [])
        emotion_matches = len(set(emotions) & set(self.emotions))
        score += emotion_matches * 3.0
        
        # Tag matching
        tags = context.get('tags', [])
        tag_matches = len(set(tags) & set(self.tags))
        score += tag_matches * 2.0
        
        # Chapter matching
        chapter = context.get('chapter', '')
        if chapter in self.chapters:
            score += 4.0
        
        # Priority boost
        score += self.priority
        
        return score
    
    def to_dict(self) -> Dict:
        """Serialize track to dictionary."""
        return {
            "track_id": self.track_id,
            "name": self.name,
            "file_path": self.file_path,
            "mood": self.mood.value,
            "intensity": self.intensity.value,
            "tags": self.tags,
            "duration": self.duration,
            "loop_start": self.loop_start,
            "loop_end": self.loop_end,
            "is_loopable": self.is_loopable,
            "bpm": self.bpm,
            "situations": self.situations,
            "characters": self.characters,
            "chapters": self.chapters,
            "emotions": self.emotions,
            "volume": self.volume,
            "fade_in_time": self.fade_in_time,
            "fade_out_time": self.fade_out_time,
            "layers": self.layers,
            "variations": self.variations,
            "stem_tracks": self.stem_tracks,
            "play_conditions": self.play_conditions,
            "stop_conditions": self.stop_conditions,
            "priority": self.priority
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create track from dictionary."""
        track = cls(data["track_id"], data.get("name", ""), data.get("file_path", ""))
        
        track.mood = MusicMood(data.get("mood", "peaceful"))
        track.intensity = MusicIntensity(data.get("intensity", 3))
        track.tags = data.get("tags", [])
        track.duration = data.get("duration", 0.0)
        track.loop_start = data.get("loop_start", 0.0)
        track.loop_end = data.get("loop_end", 0.0)
        track.is_loopable = data.get("is_loopable", True)
        track.bpm = data.get("bpm", 120)
        track.situations = data.get("situations", [])
        track.characters = data.get("characters", [])
        track.chapters = data.get("chapters", [])
        track.emotions = data.get("emotions", [])
        track.volume = data.get("volume", 1.0)
        track.fade_in_time = data.get("fade_in_time", 2.0)
        track.fade_out_time = data.get("fade_out_time", 2.0)
        track.layers = data.get("layers", {})
        track.variations = data.get("variations", {})
        track.stem_tracks = data.get("stem_tracks", {})
        track.play_conditions = data.get("play_conditions", [])
        track.stop_conditions = data.get("stop_conditions", [])
        track.priority = data.get("priority", 5)
        
        return track


class MusicPlaylist:
    """A collection of tracks that work well together."""
    
    def __init__(self, playlist_id: str, name: str = ""):
        self.playlist_id = playlist_id
        self.name = name or playlist_id.replace('_', ' ').title()
        self.tracks = []  # List of track IDs
        self.description = ""
        
        # Playlist behavior
        self.shuffle = False
        self.auto_advance = True
        self.cross_fade = True
        self.loop_playlist = True
        
        # Context matching
        self.contexts = []  # When to use this playlist
        self.weight = 1.0   # Playlist selection weight
    
    def to_dict(self) -> Dict:
        """Serialize playlist to dictionary."""
        return {
            "playlist_id": self.playlist_id,
            "name": self.name,
            "tracks": self.tracks,
            "description": self.description,
            "shuffle": self.shuffle,
            "auto_advance": self.auto_advance,
            "cross_fade": self.cross_fade,
            "loop_playlist": self.loop_playlist,
            "contexts": self.contexts,
            "weight": self.weight
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create playlist from dictionary."""
        playlist = cls(data["playlist_id"], data.get("name", ""))
        playlist.tracks = data.get("tracks", [])
        playlist.description = data.get("description", "")
        playlist.shuffle = data.get("shuffle", False)
        playlist.auto_advance = data.get("auto_advance", True)
        playlist.cross_fade = data.get("cross_fade", True)
        playlist.loop_playlist = data.get("loop_playlist", True)
        playlist.contexts = data.get("contexts", [])
        playlist.weight = data.get("weight", 1.0)
        return playlist


class MusicContext:
    """Represents the current story/emotional context for music selection."""
    
    def __init__(self):
        self.mood = MusicMood.PEACEFUL
        self.intensity = MusicIntensity.MEDIUM
        self.situation = ""           # "dialogue", "combat", "exploration"
        self.character = ""           # Current speaking character
        self.chapter = ""            # Current story chapter
        self.emotions = []           # Current emotional tags
        self.tags = []               # Additional context tags
        self.node_type = ""          # Type of current node
        self.choice_weight = 0.0     # How dramatic/important recent choices were
        self.tension_level = 0.0     # Current story tension (0.0-1.0)
        
        # Advanced context
        self.relationship_context = {}  # Character relationships
        self.story_flags = {}           # Current story state
        self.time_of_day = ""          # "morning", "evening", etc.
        self.location = ""             # Current story location
        
        # Dynamic factors
        self.recent_events = []        # Recent story events that affect music
        self.emotional_momentum = 0.0  # Building emotional intensity
        self.pacing = "normal"         # "slow", "normal", "fast"
    
    def calculate_intensity(self) -> float:
        """Calculate dynamic intensity based on context factors."""
        base_intensity = self.intensity.value
        
        # Adjust based on tension
        intensity = base_intensity + (self.tension_level * 2)
        
        # Adjust based on emotional momentum
        intensity += self.emotional_momentum
        
        # Adjust based on choice weight
        intensity += self.choice_weight * 0.5
        
        # Situation modifiers
        if self.situation == "combat":
            intensity += 2
        elif self.situation == "romance":
            intensity += 1
        elif self.situation == "exploration":
            intensity -= 0.5
        
        return max(1, min(5, intensity))
    
    def to_dict(self) -> Dict:
        """Convert context to dictionary for music matching."""
        return {
            "mood": self.mood.value,
            "intensity": self.calculate_intensity(),
            "situation": self.situation,
            "character": self.character,
            "chapter": self.chapter,
            "emotions": self.emotions,
            "tags": self.tags,
            "node_type": self.node_type,
            "choice_weight": self.choice_weight,
            "tension_level": self.tension_level,
            "relationship_context": self.relationship_context,
            "story_flags": self.story_flags,
            "time_of_day": self.time_of_day,
            "location": self.location,
            "recent_events": self.recent_events,
            "emotional_momentum": self.emotional_momentum,
            "pacing": self.pacing
        }


class DynamicMusicEngine:
    """Core engine for dynamic music selection and management."""
    
    def __init__(self):
        self.tracks = {}      # track_id -> MusicTrack
        self.playlists = {}   # playlist_id -> MusicPlaylist
        self.context = MusicContext()
        
        # Current state
        self.current_track = None
        self.current_playlist = None
        self.is_playing = False
        self.current_volume = 1.0
        
        # Transition settings
        self.default_transition = TransitionType.CROSSFADE
        self.transition_duration = 3.0
        self.enable_auto_selection = True
        
        # Advanced features
        self.mood_history = []        # Track mood changes over time
        self.intensity_curve = []     # Track intensity changes
        self.adaptation_learning = {} # Learn from user preferences
        
        # Audio layers
        self.active_layers = {}       # Currently playing audio layers
        self.stem_mixing = False      # Enable individual instrument control
    
    def add_track(self, track: MusicTrack):
        """Add a track to the music library."""
        self.tracks[track.track_id] = track
    
    def remove_track(self, track_id: str):
        """Remove a track from the library."""
        if track_id in self.tracks:
            del self.tracks[track_id]
    
    def get_track(self, track_id: str) -> Optional[MusicTrack]:
        """Get a track by ID."""
        return self.tracks.get(track_id)
    
    def find_best_track(self, context: Dict = None) -> Optional[MusicTrack]:
        """Find the best track for the current or given context."""
        if context is None:
            context = self.context.to_dict()
        
        if not self.tracks:
            return None
        
        # Calculate scores for all tracks
        scored_tracks = []
        for track in self.tracks.values():
            score = track.matches_context(context)
            scored_tracks.append((score, track))
        
        # Sort by score (highest first)
        scored_tracks.sort(key=lambda x: x[0], reverse=True)
        
        # Return the best match
        return scored_tracks[0][1] if scored_tracks else None
    
    def update_context(self, **kwargs):
        """Update the current music context."""
        for key, value in kwargs.items():
            if hasattr(self.context, key):
                setattr(self.context, key, value)
        
        # Auto-select new music if enabled
        if self.enable_auto_selection:
            self.auto_select_music()
    
    def auto_select_music(self):
        """Automatically select and transition to appropriate music."""
        best_track = self.find_best_track()
        
        if best_track and best_track != self.current_track:
            self.transition_to_track(best_track.track_id)
    
    def transition_to_track(self, track_id: str, transition_type: TransitionType = None):
        """Transition to a new track with the specified transition."""
        new_track = self.get_track(track_id)
        if not new_track:
            return False
        
        if transition_type is None:
            transition_type = self.default_transition
        
        # Store previous track info
        previous_track = self.current_track
        
        # Update current track
        self.current_track = new_track
        
        # This would trigger the actual audio transition in the HTML export
        # For now, we just update the state
        
        return True
    
    def analyze_story_context(self, node_data: Dict) -> Dict:
        """Analyze a story node to extract musical context."""
        context = {
            "mood": MusicMood.PEACEFUL.value,
            "intensity": 3,
            "situation": "dialogue",
            "emotions": [],
            "tags": []
        }
        
        # Analyze text content for emotional indicators
        text = node_data.get("text", "").lower()
        
        # Mood detection from text
        if any(word in text for word in ["fight", "battle", "attack", "danger"]):
            context["mood"] = MusicMood.COMBAT.value
            context["intensity"] = 5
        elif any(word in text for word in ["love", "kiss", "heart", "romantic"]):
            context["mood"] = MusicMood.ROMANTIC.value
            context["intensity"] = 3
        elif any(word in text for word in ["mystery", "strange", "unknown", "secret"]):
            context["mood"] = MusicMood.MYSTERIOUS.value
            context["intensity"] = 4
        elif any(word in text for word in ["sad", "cry", "death", "loss", "grief"]):
            context["mood"] = MusicMood.SAD.value
            context["intensity"] = 2
        elif any(word in text for word in ["happy", "joy", "celebrate", "victory"]):
            context["mood"] = MusicMood.HAPPY.value
            context["intensity"] = 3
        
        # Node type analysis
        node_type = node_data.get("node_type", "")
        if node_type == "Combat" or node_type == "AdvancedCombat":
            context["mood"] = MusicMood.COMBAT.value
            context["situation"] = "combat"
            context["intensity"] = 5
        elif node_type == "Shop":
            context["mood"] = MusicMood.PEACEFUL.value
            context["situation"] = "shop"
            context["intensity"] = 2
        
        # Character context
        character = node_data.get("character_id", "") or node_data.get("npc", "")
        if character:
            context["character"] = character
        
        # Chapter context
        chapter = node_data.get("chapter", "")
        if chapter:
            context["chapter"] = chapter
        
        return context
    
    def export_for_web(self) -> Dict:
        """Export music system data for web export."""
        return {
            "tracks": {tid: track.to_dict() for tid, track in self.tracks.items()},
            "playlists": {pid: playlist.to_dict() for pid, playlist in self.playlists.items()},
            "settings": {
                "default_transition": self.default_transition.value,
                "transition_duration": self.transition_duration,
                "enable_auto_selection": self.enable_auto_selection
            }
        }
    
    def import_from_web(self, data: Dict):
        """Import music system data from web export."""
        # Import tracks
        for track_data in data.get("tracks", {}).values():
            track = MusicTrack.from_dict(track_data)
            self.tracks[track.track_id] = track
        
        # Import playlists
        for playlist_data in data.get("playlists", {}).values():
            playlist = MusicPlaylist.from_dict(playlist_data)
            self.playlists[playlist.playlist_id] = playlist
        
        # Import settings
        settings = data.get("settings", {})
        self.default_transition = TransitionType(settings.get("default_transition", "crossfade"))
        self.transition_duration = settings.get("transition_duration", 3.0)
        self.enable_auto_selection = settings.get("enable_auto_selection", True)
    
    def to_dict(self) -> Dict:
        """Serialize entire music system."""
        return {
            "tracks": {tid: track.to_dict() for tid, track in self.tracks.items()},
            "playlists": {pid: playlist.to_dict() for pid, playlist in self.playlists.items()},
            "settings": {
                "default_transition": self.default_transition.value,
                "transition_duration": self.transition_duration,
                "enable_auto_selection": self.enable_auto_selection
            },
            "current_state": {
                "current_track": self.current_track.track_id if self.current_track else None,
                "current_playlist": self.current_playlist.playlist_id if self.current_playlist else None,
                "current_volume": self.current_volume
            }
        }
    
    def from_dict(self, data: Dict):
        """Load music system from dictionary."""
        self.tracks = {}
        self.playlists = {}
        
        # Load tracks
        for track_data in data.get("tracks", {}).values():
            track = MusicTrack.from_dict(track_data)
            self.tracks[track.track_id] = track
        
        # Load playlists
        for playlist_data in data.get("playlists", {}).values():
            playlist = MusicPlaylist.from_dict(playlist_data)
            self.playlists[playlist.playlist_id] = playlist
        
        # Load settings
        settings = data.get("settings", {})
        if "default_transition" in settings:
            self.default_transition = TransitionType(settings["default_transition"])
        self.transition_duration = settings.get("transition_duration", 3.0)
        self.enable_auto_selection = settings.get("enable_auto_selection", True)
        
        # Load current state
        state = data.get("current_state", {})
        current_track_id = state.get("current_track")
        if current_track_id and current_track_id in self.tracks:
            self.current_track = self.tracks[current_track_id]
        
        self.current_volume = state.get("current_volume", 1.0)