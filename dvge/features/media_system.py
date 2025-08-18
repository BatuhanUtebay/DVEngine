# dvge/features/media_system.py

"""Advanced Media System for DVGE - Supports videos, animations, keyframes, and effects."""

import os
import json
import base64
import mimetypes
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class MediaType(Enum):
    """Types of media assets supported."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MUSIC = "music"


class AnimationType(Enum):
    """Types of animations supported."""
    FADE = "fade"
    SLIDE = "slide"
    SCALE = "scale"
    ROTATE = "rotate"
    POSITION = "position"
    COLOR = "color"
    BLUR = "blur"
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    CUSTOM = "custom"


class EasingType(Enum):
    """Animation easing functions."""
    LINEAR = "linear"
    EASE_IN = "ease-in"
    EASE_OUT = "ease-out"
    EASE_IN_OUT = "ease-in-out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"
    CUBIC_BEZIER = "cubic-bezier"


@dataclass
class Keyframe:
    """A single keyframe in an animation timeline."""
    time: float  # Time in seconds
    properties: Dict[str, Any]  # CSS properties and values
    easing: EasingType = EasingType.EASE_IN_OUT

    def to_dict(self) -> Dict[str, Any]:
        return {
            'time': self.time,
            'properties': self.properties,
            'easing': self.easing.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Keyframe':
        return cls(
            time=data['time'],
            properties=data['properties'],
            easing=EasingType(data.get('easing', 'ease-in-out'))
        )


@dataclass
class MediaEffect:
    """A visual effect applied to media."""
    effect_type: str  # blur, brightness, contrast, hue-rotate, etc.
    value: Any  # Effect strength/value
    animated: bool = False  # Whether this effect is animated
    keyframes: List[Keyframe] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'effect_type': self.effect_type,
            'value': self.value,
            'animated': self.animated,
            'keyframes': [kf.to_dict() for kf in self.keyframes]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MediaEffect':
        return cls(
            effect_type=data['effect_type'],
            value=data['value'],
            animated=data.get('animated', False),
            keyframes=[Keyframe.from_dict(kf)
                       for kf in data.get('keyframes', [])]
        )


@dataclass
class MediaAsset:
    """A media asset with all its properties and animations."""
    asset_id: str  # Unique identifier
    name: str  # Display name
    file_path: str  # Path to the file
    media_type: MediaType

    # Transform properties
    x: float = 0  # Position X (percentage)
    y: float = 0  # Position Y (percentage)
    width: float = 100  # Width (percentage)
    height: float = 100  # Height (percentage)
    rotation: float = 0  # Rotation in degrees
    opacity: float = 1.0  # Opacity (0-1)
    z_index: int = 0  # Layer order

    # Animation properties
    animations: List[Dict[str, Any]] = field(default_factory=list)
    effects: List[MediaEffect] = field(default_factory=list)

    # Playback properties (for video/audio)
    autoplay: bool = False
    loop: bool = False
    muted: bool = False
    volume: float = 1.0
    start_time: float = 0  # When to start playing (seconds into node)

    # Timing
    fade_in_duration: float = 0
    fade_out_duration: float = 0
    duration_override: Optional[float] = None  # Override natural duration

    def to_dict(self) -> Dict[str, Any]:
        return {
            'asset_id': self.asset_id,
            'name': self.name,
            'file_path': self.file_path,
            'media_type': self.media_type.value,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'rotation': self.rotation,
            'opacity': self.opacity,
            'z_index': self.z_index,
            'animations': self.animations,
            'effects': [effect.to_dict() for effect in self.effects],
            'autoplay': self.autoplay,
            'loop': self.loop,
            'muted': self.muted,
            'volume': self.volume,
            'start_time': self.start_time,
            'fade_in_duration': self.fade_in_duration,
            'fade_out_duration': self.fade_out_duration,
            'duration_override': self.duration_override
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MediaAsset':
        return cls(
            asset_id=data['asset_id'],
            name=data['name'],
            file_path=data['file_path'],
            media_type=MediaType(data['media_type']),
            x=data.get('x', 0),
            y=data.get('y', 0),
            width=data.get('width', 100),
            height=data.get('height', 100),
            rotation=data.get('rotation', 0),
            opacity=data.get('opacity', 1.0),
            z_index=data.get('z_index', 0),
            animations=data.get('animations', []),
            effects=[MediaEffect.from_dict(e)
                     for e in data.get('effects', [])],
            autoplay=data.get('autoplay', False),
            loop=data.get('loop', False),
            muted=data.get('muted', False),
            volume=data.get('volume', 1.0),
            start_time=data.get('start_time', 0),
            fade_in_duration=data.get('fade_in_duration', 0),
            fade_out_duration=data.get('fade_out_duration', 0),
            duration_override=data.get('duration_override')
        )


class MediaLibrary:
    """Manages all media assets for the project."""

    def __init__(self, project_path: str = ""):
        self.project_path = project_path
        self.assets: Dict[str, MediaAsset] = {}
        self.asset_counter = 0
        self._supported_formats = {
            MediaType.IMAGE: ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'],
            MediaType.VIDEO: ['.mp4', '.webm', '.ogg', '.avi', '.mov'],
            MediaType.AUDIO: ['.mp3', '.wav', '.ogg', '.m4a'],
            MediaType.MUSIC: ['.mp3', '.wav', '.ogg', '.m4a']
        }

    def add_asset(self, file_path: str, name: str = "") -> Optional[MediaAsset]:
        """Add a new media asset to the library."""
        if not os.path.exists(file_path):
            return None

        # Determine media type from file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        media_type = None
        for mtype, extensions in self._supported_formats.items():
            if ext in extensions:
                media_type = mtype
                break

        if not media_type:
            return None  # Unsupported format

        # Generate unique ID
        self.asset_counter += 1
        asset_id = f"asset_{self.asset_counter}"

        # Use filename as default name
        if not name:
            name = os.path.splitext(os.path.basename(file_path))[0]

        asset = MediaAsset(
            asset_id=asset_id,
            name=name,
            file_path=file_path,
            media_type=media_type
        )

        self.assets[asset_id] = asset
        return asset

    def remove_asset(self, asset_id: str) -> bool:
        """Remove an asset from the library."""
        if asset_id in self.assets:
            del self.assets[asset_id]
            return True
        return False

    def get_asset(self, asset_id: str) -> Optional[MediaAsset]:
        """Get an asset by ID."""
        return self.assets.get(asset_id)

    def get_assets_by_type(self, media_type: MediaType) -> List[MediaAsset]:
        """Get all assets of a specific type."""
        return [asset for asset in self.assets.values() if asset.media_type == media_type]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize library to dictionary."""
        return {
            'assets': {aid: asset.to_dict() for aid, asset in self.assets.items()},
            'asset_counter': self.asset_counter
        }

    def from_dict(self, data: Dict[str, Any]):
        """Load library from dictionary."""
        self.assets = {
            aid: MediaAsset.from_dict(asset_data)
            for aid, asset_data in data.get('assets', {}).items()
        }
        self.asset_counter = data.get('asset_counter', 0)

    def encode_asset_for_export(self, asset: MediaAsset) -> Optional[str]:
        """Encode asset as base64 for HTML export."""
        try:
            if not os.path.exists(asset.file_path):
                return None

            with open(asset.file_path, 'rb') as f:
                content = f.read()
                encoded = base64.b64encode(content).decode('utf-8')

                # Get MIME type
                mime_type, _ = mimetypes.guess_type(asset.file_path)
                if not mime_type:
                    # Fallback MIME types
                    ext = os.path.splitext(asset.file_path)[1].lower()
                    mime_map = {
                        '.mp4': 'video/mp4',
                        '.webm': 'video/webm',
                        '.ogg': 'video/ogg',
                        '.png': 'image/png',
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.gif': 'image/gif',
                        '.mp3': 'audio/mpeg',
                        '.wav': 'audio/wav'
                    }
                    mime_type = mime_map.get(ext, 'application/octet-stream')

                return f"data:{mime_type};base64,{encoded}"
        except Exception as e:
            print(f"Error encoding asset {asset.asset_id}: {e}")
            return None


class AnimationEngine:
    """Handles creation and management of animations."""

    @staticmethod
    def create_fade_animation(duration: float, from_opacity: float = 0, to_opacity: float = 1) -> Dict[str, Any]:
        """Create a fade animation."""
        return {
            'type': 'fade',
            'duration': duration,
            'keyframes': [
                {'time': 0, 'opacity': from_opacity},
                {'time': duration, 'opacity': to_opacity}
            ]
        }

    @staticmethod
    def create_slide_animation(duration: float, from_pos: Tuple[float, float], to_pos: Tuple[float, float]) -> Dict[str, Any]:
        """Create a slide animation."""
        return {
            'type': 'slide',
            'duration': duration,
            'keyframes': [
                {'time': 0, 'x': from_pos[0], 'y': from_pos[1]},
                {'time': duration, 'x': to_pos[0], 'y': to_pos[1]}
            ]
        }

    @staticmethod
    def create_scale_animation(duration: float, from_scale: float = 0, to_scale: float = 1) -> Dict[str, Any]:
        """Create a scale animation."""
        return {
            'type': 'scale',
            'duration': duration,
            'keyframes': [
                {'time': 0, 'transform': f'scale({from_scale})'},
                {'time': duration, 'transform': f'scale({to_scale})'}
            ]
        }

    @staticmethod
    def create_rotation_animation(duration: float, from_angle: float = 0, to_angle: float = 360) -> Dict[str, Any]:
        """Create a rotation animation."""
        return {
            'type': 'rotation',
            'duration': duration,
            'keyframes': [
                {'time': 0, 'transform': f'rotate({from_angle}deg)'},
                {'time': duration, 'transform': f'rotate({to_angle}deg)'}
            ]
        }

    @staticmethod
    def create_custom_animation(duration: float, keyframes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a custom animation with user-defined keyframes."""
        return {
            'type': 'custom',
            'duration': duration,
            'keyframes': keyframes
        }


class EffectsEngine:
    """Handles visual effects creation and application."""

    @staticmethod
    def create_blur_effect(strength: float = 5.0) -> MediaEffect:
        """Create a blur effect."""
        return MediaEffect(
            effect_type='blur',
            value=f'{strength}px'
        )

    @staticmethod
    def create_brightness_effect(level: float = 1.0) -> MediaEffect:
        """Create a brightness effect (1.0 = normal, 0 = black, 2.0 = very bright)."""
        return MediaEffect(
            effect_type='brightness',
            value=level
        )

    @staticmethod
    def create_contrast_effect(level: float = 1.0) -> MediaEffect:
        """Create a contrast effect (1.0 = normal, 0 = gray, 2.0 = high contrast)."""
        return MediaEffect(
            effect_type='contrast',
            value=level
        )

    @staticmethod
    def create_hue_rotate_effect(degrees: float = 0) -> MediaEffect:
        """Create a hue rotation effect."""
        return MediaEffect(
            effect_type='hue-rotate',
            value=f'{degrees}deg'
        )

    @staticmethod
    def create_saturate_effect(level: float = 1.0) -> MediaEffect:
        """Create a saturation effect (1.0 = normal, 0 = grayscale, 2.0 = very saturated)."""
        return MediaEffect(
            effect_type='saturate',
            value=level
        )

    @staticmethod
    def create_sepia_effect(level: float = 1.0) -> MediaEffect:
        """Create a sepia effect (0 = normal, 1.0 = full sepia)."""
        return MediaEffect(
            effect_type='sepia',
            value=level
        )

    @staticmethod
    def create_drop_shadow_effect(x: float = 2, y: float = 2, blur: float = 4, color: str = 'rgba(0,0,0,0.5)') -> MediaEffect:
        """Create a drop shadow effect."""
        return MediaEffect(
            effect_type='drop-shadow',
            value=f'{x}px {y}px {blur}px {color}'
        )


# Preset animation collections
class MediaPresets:
    """Common media and animation presets."""

    @staticmethod
    def telltale_style_fade_in() -> Dict[str, Any]:
        """Telltale Games style fade-in effect."""
        return AnimationEngine.create_fade_animation(1.5, 0, 1)

    @staticmethod
    def dramatic_slide_in() -> Dict[str, Any]:
        """Dramatic slide-in from left."""
        return AnimationEngine.create_slide_animation(1.2, (-100, 0), (0, 0))

    @staticmethod
    def zoom_reveal() -> Dict[str, Any]:
        """Zoom-in reveal effect."""
        return AnimationEngine.create_scale_animation(1.0, 0.1, 1.0)

    @staticmethod
    def mystery_blur_in() -> List[MediaEffect]:
        """Mystery-style blur-in effect."""
        blur_effect = EffectsEngine.create_blur_effect(10.0)
        blur_effect.animated = True
        blur_effect.keyframes = [
            Keyframe(0, {'filter': 'blur(10px)'}, EasingType.EASE_OUT),
            Keyframe(2.0, {'filter': 'blur(0px)'}, EasingType.EASE_OUT)
        ]
        return [blur_effect]

    @staticmethod
    def sepia_memory_effect() -> List[MediaEffect]:
        """Sepia effect for flashback/memory scenes."""
        return [
            EffectsEngine.create_sepia_effect(0.7),
            EffectsEngine.create_brightness_effect(1.1),
            EffectsEngine.create_contrast_effect(0.9)
        ]

    @staticmethod
    def action_scene_effects() -> List[MediaEffect]:
        """High contrast, saturated effects for action scenes."""
        return [
            EffectsEngine.create_contrast_effect(1.3),
            EffectsEngine.create_saturate_effect(1.4),
            EffectsEngine.create_brightness_effect(1.1)
        ]
