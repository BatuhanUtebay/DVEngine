# dvge/models/transitions.py

"""Visual Novel Mode - Transition effects and animations."""

import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum


class TransitionType(Enum):
    """Available transition types."""
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    DISSOLVE = "dissolve"
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    ROTATE = "rotate"
    FLIP_HORIZONTAL = "flip_horizontal"
    FLIP_VERTICAL = "flip_vertical"
    BLUR = "blur"
    IRIS_IN = "iris_in"
    IRIS_OUT = "iris_out"
    CUT = "cut"
    CROSSFADE = "crossfade"


class EasingType(Enum):
    """Easing functions for smooth animations."""
    LINEAR = "linear"
    EASE_IN = "ease-in"
    EASE_OUT = "ease-out" 
    EASE_IN_OUT = "ease-in-out"
    EASE_IN_QUAD = "ease-in-quad"
    EASE_OUT_QUAD = "ease-out-quad"
    EASE_IN_OUT_QUAD = "ease-in-out-quad"
    EASE_IN_CUBIC = "ease-in-cubic"
    EASE_OUT_CUBIC = "ease-out-cubic"
    EASE_IN_OUT_CUBIC = "ease-in-out-cubic"
    EASE_IN_QUART = "ease-in-quart"
    EASE_OUT_QUART = "ease-out-quart"
    EASE_IN_OUT_QUART = "ease-in-out-quart"
    EASE_IN_BOUNCE = "ease-in-bounce"
    EASE_OUT_BOUNCE = "ease-out-bounce"
    EASE_IN_OUT_BOUNCE = "ease-in-out-bounce"


@dataclass
class TransitionConfig:
    """Configuration for a transition effect."""
    type: str = TransitionType.FADE.value
    duration: float = 0.5  # seconds
    easing: str = EasingType.EASE_IN_OUT.value
    delay: float = 0.0     # seconds
    direction: str = "in"  # "in", "out", "in-out"
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransitionConfig':
        return cls(**data)


@dataclass 
class KeyFrame:
    """Represents a keyframe in an animation sequence."""
    time: float              # Time in seconds (0.0 to 1.0)
    properties: Dict[str, Any]  # CSS properties at this keyframe
    easing: str = EasingType.LINEAR.value
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeyFrame':
        return cls(**data)


@dataclass
class CustomAnimation:
    """Represents a custom animation sequence."""
    id: str
    name: str
    keyframes: List[KeyFrame]
    duration: float = 1.0
    loop: bool = False
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "keyframes": [kf.to_dict() for kf in self.keyframes]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomAnimation':
        keyframes = [KeyFrame.from_dict(kf_data) for kf_data in data.get("keyframes", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            keyframes=keyframes,
            duration=data.get("duration", 1.0),
            loop=data.get("loop", False),
            description=data.get("description", "")
        )


class TransitionEngine:
    """Engine for managing transitions and animations in Visual Novel Mode."""
    
    def __init__(self):
        self.transition_presets: Dict[str, TransitionConfig] = {}
        self.custom_animations: Dict[str, CustomAnimation] = {}
        
        self._initialize_presets()
    
    def _initialize_presets(self):
        """Initialize built-in transition presets."""
        presets = {
            # Basic transitions
            "fade_in": TransitionConfig(
                type=TransitionType.FADE.value,
                duration=0.5,
                direction="in",
                properties={"from_opacity": 0, "to_opacity": 1}
            ),
            "fade_out": TransitionConfig(
                type=TransitionType.FADE.value,
                duration=0.5,
                direction="out", 
                properties={"from_opacity": 1, "to_opacity": 0}
            ),
            "crossfade": TransitionConfig(
                type=TransitionType.CROSSFADE.value,
                duration=1.0,
                properties={"overlap": 0.5}
            ),
            
            # Slide transitions
            "slide_in_left": TransitionConfig(
                type=TransitionType.SLIDE_LEFT.value,
                duration=0.7,
                direction="in",
                easing=EasingType.EASE_OUT_CUBIC.value,
                properties={"from_x": -100, "to_x": 0, "unit": "%"}
            ),
            "slide_in_right": TransitionConfig(
                type=TransitionType.SLIDE_RIGHT.value,
                duration=0.7,
                direction="in",
                easing=EasingType.EASE_OUT_CUBIC.value,
                properties={"from_x": 100, "to_x": 0, "unit": "%"}
            ),
            "slide_out_left": TransitionConfig(
                type=TransitionType.SLIDE_LEFT.value,
                duration=0.5,
                direction="out",
                easing=EasingType.EASE_IN_CUBIC.value,
                properties={"from_x": 0, "to_x": -100, "unit": "%"}
            ),
            "slide_out_right": TransitionConfig(
                type=TransitionType.SLIDE_RIGHT.value,
                duration=0.5,
                direction="out",
                easing=EasingType.EASE_IN_CUBIC.value,
                properties={"from_x": 0, "to_x": 100, "unit": "%"}
            ),
            
            # Zoom transitions
            "zoom_in": TransitionConfig(
                type=TransitionType.ZOOM_IN.value,
                duration=0.8,
                direction="in",
                easing=EasingType.EASE_OUT_QUAD.value,
                properties={
                    "from_scale": 0.3,
                    "to_scale": 1.0,
                    "from_opacity": 0,
                    "to_opacity": 1
                }
            ),
            "zoom_out": TransitionConfig(
                type=TransitionType.ZOOM_OUT.value,
                duration=0.6,
                direction="out",
                easing=EasingType.EASE_IN_QUAD.value,
                properties={
                    "from_scale": 1.0,
                    "to_scale": 0.3,
                    "from_opacity": 1,
                    "to_opacity": 0
                }
            ),
            
            # Wipe transitions
            "wipe_left": TransitionConfig(
                type=TransitionType.WIPE_LEFT.value,
                duration=0.8,
                properties={"direction": "left"}
            ),
            "wipe_right": TransitionConfig(
                type=TransitionType.WIPE_RIGHT.value,
                duration=0.8,
                properties={"direction": "right"}
            ),
            
            # Dissolve effect
            "dissolve": TransitionConfig(
                type=TransitionType.DISSOLVE.value,
                duration=1.2,
                properties={"noise_scale": 0.5, "threshold": 0.3}
            ),
            
            # Rotation effects
            "rotate_in": TransitionConfig(
                type=TransitionType.ROTATE.value,
                duration=0.8,
                direction="in",
                easing=EasingType.EASE_OUT_BOUNCE.value,
                properties={
                    "from_rotation": -180,
                    "to_rotation": 0,
                    "from_scale": 0.5,
                    "to_scale": 1.0,
                    "from_opacity": 0,
                    "to_opacity": 1
                }
            ),
            
            # Flip effects
            "flip_in": TransitionConfig(
                type=TransitionType.FLIP_HORIZONTAL.value,
                duration=0.6,
                direction="in",
                properties={
                    "from_rotation_y": -90,
                    "to_rotation_y": 0,
                    "perspective": 1000
                }
            ),
            
            # Blur effects
            "blur_in": TransitionConfig(
                type=TransitionType.BLUR.value,
                duration=0.7,
                direction="in",
                properties={
                    "from_blur": 10,
                    "to_blur": 0,
                    "from_opacity": 0.5,
                    "to_opacity": 1.0
                }
            ),
            
            # Iris effects
            "iris_in": TransitionConfig(
                type=TransitionType.IRIS_IN.value,
                duration=1.0,
                properties={"center": [0.5, 0.5]}  # Center of screen
            ),
            "iris_out": TransitionConfig(
                type=TransitionType.IRIS_OUT.value,
                duration=0.8,
                properties={"center": [0.5, 0.5]}
            ),
            
            # Instant cut
            "cut": TransitionConfig(
                type=TransitionType.CUT.value,
                duration=0.0
            )
        }
        
        self.transition_presets = presets
    
    def get_preset(self, preset_name: str) -> Optional[TransitionConfig]:
        """Get a transition preset by name."""
        return self.transition_presets.get(preset_name)
    
    def add_custom_preset(self, name: str, config: TransitionConfig):
        """Add a custom transition preset."""
        self.transition_presets[name] = config
    
    def get_all_presets(self) -> Dict[str, TransitionConfig]:
        """Get all available transition presets."""
        return self.transition_presets.copy()
    
    def get_presets_by_type(self, transition_type: str) -> Dict[str, TransitionConfig]:
        """Get all presets of a specific type."""
        return {
            name: config for name, config in self.transition_presets.items()
            if config.type == transition_type
        }
    
    def create_custom_animation(self, animation: CustomAnimation) -> bool:
        """Create a custom animation sequence."""
        if animation.id in self.custom_animations:
            return False
        
        self.custom_animations[animation.id] = animation
        return True
    
    def get_custom_animation(self, animation_id: str) -> Optional[CustomAnimation]:
        """Get a custom animation by ID."""
        return self.custom_animations.get(animation_id)
    
    def generate_css_animation(self, config: TransitionConfig, 
                             target_selector: str = ".vn-element") -> str:
        """Generate CSS animation code for a transition config."""
        animation_name = f"transition_{config.type}_{id(config)}"
        
        css = f"""
/* {config.type.title()} Transition */
@keyframes {animation_name} {{"""
        
        if config.type == TransitionType.FADE.value:
            if config.direction == "in":
                css += f"""
    0% {{ opacity: {config.properties.get('from_opacity', 0)}; }}
    100% {{ opacity: {config.properties.get('to_opacity', 1)}; }}"""
            else:
                css += f"""
    0% {{ opacity: {config.properties.get('from_opacity', 1)}; }}
    100% {{ opacity: {config.properties.get('to_opacity', 0)}; }}"""
        
        elif config.type in [TransitionType.SLIDE_LEFT.value, TransitionType.SLIDE_RIGHT.value]:
            from_x = config.properties.get('from_x', 0)
            to_x = config.properties.get('to_x', 0)
            unit = config.properties.get('unit', 'px')
            css += f"""
    0% {{ transform: translateX({from_x}{unit}); }}
    100% {{ transform: translateX({to_x}{unit}); }}"""
        
        elif config.type in [TransitionType.SLIDE_UP.value, TransitionType.SLIDE_DOWN.value]:
            from_y = config.properties.get('from_y', 0)
            to_y = config.properties.get('to_y', 0)
            unit = config.properties.get('unit', 'px')
            css += f"""
    0% {{ transform: translateY({from_y}{unit}); }}
    100% {{ transform: translateY({to_y}{unit}); }}"""
        
        elif config.type in [TransitionType.ZOOM_IN.value, TransitionType.ZOOM_OUT.value]:
            from_scale = config.properties.get('from_scale', 1.0)
            to_scale = config.properties.get('to_scale', 1.0)
            from_opacity = config.properties.get('from_opacity', 1.0)
            to_opacity = config.properties.get('to_opacity', 1.0)
            css += f"""
    0% {{ 
        transform: scale({from_scale}); 
        opacity: {from_opacity}; 
    }}
    100% {{ 
        transform: scale({to_scale}); 
        opacity: {to_opacity}; 
    }}"""
        
        elif config.type == TransitionType.ROTATE.value:
            from_rot = config.properties.get('from_rotation', 0)
            to_rot = config.properties.get('to_rotation', 0)
            from_scale = config.properties.get('from_scale', 1.0)
            to_scale = config.properties.get('to_scale', 1.0)
            from_opacity = config.properties.get('from_opacity', 1.0)
            to_opacity = config.properties.get('to_opacity', 1.0)
            css += f"""
    0% {{ 
        transform: rotate({from_rot}deg) scale({from_scale}); 
        opacity: {from_opacity}; 
    }}
    100% {{ 
        transform: rotate({to_rot}deg) scale({to_scale}); 
        opacity: {to_opacity}; 
    }}"""
        
        elif config.type == TransitionType.BLUR.value:
            from_blur = config.properties.get('from_blur', 0)
            to_blur = config.properties.get('to_blur', 0)
            from_opacity = config.properties.get('from_opacity', 1.0)
            to_opacity = config.properties.get('to_opacity', 1.0)
            css += f"""
    0% {{ 
        filter: blur({from_blur}px); 
        opacity: {from_opacity}; 
    }}
    100% {{ 
        filter: blur({to_blur}px); 
        opacity: {to_opacity}; 
    }}"""
        
        elif config.type == TransitionType.FLIP_HORIZONTAL.value:
            from_rot_y = config.properties.get('from_rotation_y', 0)
            to_rot_y = config.properties.get('to_rotation_y', 0)
            perspective = config.properties.get('perspective', 1000)
            css += f"""
    0% {{ transform: perspective({perspective}px) rotateY({from_rot_y}deg); }}
    100% {{ transform: perspective({perspective}px) rotateY({to_rot_y}deg); }}"""
        
        elif config.type == TransitionType.FLIP_VERTICAL.value:
            from_rot_x = config.properties.get('from_rotation_x', 0)
            to_rot_x = config.properties.get('to_rotation_x', 0)
            perspective = config.properties.get('perspective', 1000)
            css += f"""
    0% {{ transform: perspective({perspective}px) rotateX({from_rot_x}deg); }}
    100% {{ transform: perspective({perspective}px) rotateX({to_rot_x}deg); }}"""
        
        css += f"""
}}

{target_selector}.{config.type}-transition {{
    animation: {animation_name} {config.duration}s {config.easing} {config.delay}s both;
}}
"""
        
        return css
    
    def generate_javascript_trigger(self, config: TransitionConfig, element_id: str) -> str:
        """Generate JavaScript code to trigger a transition."""
        js = f"""
// Trigger {config.type} transition on element {element_id}
function trigger{config.type.title().replace('_', '')}Transition(elementId) {{
    const element = document.getElementById(elementId || '{element_id}');
    if (!element) return;
    
    // Remove any existing transition classes
    element.className = element.className.replace(/\\b\\w*-transition\\b/g, '');
    
    // Add the new transition class
    element.classList.add('{config.type}-transition');
    
    // Auto-remove transition class after animation completes
    setTimeout(() => {{
        element.classList.remove('{config.type}-transition');
    }}, {int((config.duration + config.delay) * 1000)});
}}
"""
        return js
    
    def export_for_html(self) -> Dict[str, Any]:
        """Export transition data for HTML game export."""
        return {
            "presets": {
                name: config.to_dict()
                for name, config in self.transition_presets.items()
            },
            "custom_animations": {
                anim_id: animation.to_dict()
                for anim_id, animation in self.custom_animations.items()
            }
        }
    
    def generate_complete_css(self) -> str:
        """Generate complete CSS for all transition presets."""
        css_parts = []
        
        # Add base transition styles
        css_parts.append("""
/* Visual Novel Transition Base Styles */
.vn-element {
    transition-property: opacity, transform, filter;
    transition-duration: 0.3s;
    transition-timing-function: ease-in-out;
}

.vn-element.transitioning {
    pointer-events: none;
}
""")
        
        # Generate CSS for each preset
        for name, config in self.transition_presets.items():
            css_parts.append(self.generate_css_animation(config))
        
        return "\n".join(css_parts)
    
    def get_transition_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Suggest appropriate transitions based on context."""
        scene_type = context.get("scene_type", "dialogue")
        mood = context.get("mood", "neutral")
        pacing = context.get("pacing", "normal")  # slow, normal, fast
        
        suggestions = []
        
        if scene_type == "dialogue":
            if pacing == "slow":
                suggestions.extend(["fade_in", "dissolve", "blur_in"])
            elif pacing == "fast":
                suggestions.extend(["cut", "slide_in_left", "slide_in_right"])
            else:
                suggestions.extend(["fade_in", "crossfade", "slide_in_left"])
        
        elif scene_type == "action":
            suggestions.extend(["zoom_in", "slide_in_right", "wipe_left", "cut"])
        
        elif scene_type == "dramatic":
            suggestions.extend(["iris_in", "zoom_in", "rotate_in", "dissolve"])
        
        elif scene_type == "comedy":
            suggestions.extend(["flip_in", "rotate_in", "zoom_in"])
        
        if mood == "mysterious":
            suggestions.extend(["iris_in", "dissolve", "blur_in"])
        elif mood == "cheerful":
            suggestions.extend(["zoom_in", "flip_in", "rotate_in"])
        elif mood == "dramatic":
            suggestions.extend(["iris_in", "wipe_left", "dissolve"])
        elif mood == "tense":
            suggestions.extend(["cut", "zoom_in", "slide_in_right"])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:6]  # Return top 6 suggestions