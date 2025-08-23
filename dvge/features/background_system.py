# dvge/features/background_system.py

"""Visual Novel Mode - Background and scene management system."""

import os
import json
import uuid
import base64
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class BackgroundAsset:
    """Represents a background image asset."""
    id: str
    name: str
    file_path: str
    category: str = "general"  # general, indoor, outdoor, fantasy, sci-fi, etc.
    time_of_day: str = "any"   # any, dawn, day, dusk, night
    mood: str = "neutral"      # neutral, cheerful, dark, mysterious, romantic, etc.
    width: int = 0
    height: int = 0
    description: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackgroundAsset':
        return cls(**data)


@dataclass
class BackgroundLayer:
    """Represents a background layer for parallax effects."""
    id: str
    asset_id: str
    depth: float = 1.0         # Parallax depth (1.0 = no parallax)
    opacity: float = 1.0
    blend_mode: str = "normal" # normal, multiply, screen, overlay
    offset_x: int = 0
    offset_y: int = 0
    scale: float = 1.0
    visible: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackgroundLayer':
        return cls(**data)


@dataclass
class SceneBackground:
    """Represents a complete background composition."""
    id: str
    name: str
    primary_asset_id: str      # Main background
    layers: List[BackgroundLayer] = None
    ambient_color: str = "#000000"  # Overlay color for mood
    ambient_opacity: float = 0.0
    parallax_enabled: bool = False
    transition_type: str = "fade"   # fade, slide, dissolve, cut
    transition_duration: float = 1.0
    description: str = ""
    
    def __post_init__(self):
        if self.layers is None:
            self.layers = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "layers": [layer.to_dict() for layer in self.layers]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SceneBackground':
        layers = [BackgroundLayer.from_dict(layer_data) for layer_data in data.get("layers", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            primary_asset_id=data["primary_asset_id"],
            layers=layers,
            ambient_color=data.get("ambient_color", "#000000"),
            ambient_opacity=data.get("ambient_opacity", 0.0),
            parallax_enabled=data.get("parallax_enabled", False),
            transition_type=data.get("transition_type", "fade"),
            transition_duration=data.get("transition_duration", 1.0),
            description=data.get("description", "")
        )


@dataclass
class EnvironmentalEffect:
    """Represents environmental effects like weather, particles, etc."""
    id: str
    name: str
    effect_type: str = "particles"  # particles, weather, lighting, animation
    config: Dict[str, Any] = None
    intensity: float = 1.0
    enabled: bool = True
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnvironmentalEffect':
        return cls(**data)


class BackgroundManager:
    """Central background management system for Visual Novel Mode."""
    
    def __init__(self, app=None):
        self.app = app
        self.background_assets: Dict[str, BackgroundAsset] = {}
        self.scene_backgrounds: Dict[str, SceneBackground] = {}
        self.environmental_effects: Dict[str, EnvironmentalEffect] = {}
        
        # Storage paths
        self.bg_data_dir = Path.home() / ".dvge" / "background_data"
        self.bg_assets_dir = self.bg_data_dir / "assets"
        self.bg_assets_file = self.bg_data_dir / "background_assets.json"
        self.scene_backgrounds_file = self.bg_data_dir / "scene_backgrounds.json"
        self.effects_file = self.bg_data_dir / "environmental_effects.json"
        
        self._ensure_directories()
        self._load_data()
        self._create_default_backgrounds()
    
    def _ensure_directories(self):
        """Create necessary directories for background data storage."""
        self.bg_data_dir.mkdir(parents=True, exist_ok=True)
        self.bg_assets_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_data(self):
        """Load background data from disk."""
        try:
            # Load background assets
            if self.bg_assets_file.exists():
                with open(self.bg_assets_file, 'r', encoding='utf-8') as f:
                    assets_data = json.load(f)
                    self.background_assets = {
                        aid: BackgroundAsset.from_dict(data)
                        for aid, data in assets_data.items()
                    }
            
            # Load scene backgrounds
            if self.scene_backgrounds_file.exists():
                with open(self.scene_backgrounds_file, 'r', encoding='utf-8') as f:
                    backgrounds_data = json.load(f)
                    self.scene_backgrounds = {
                        bid: SceneBackground.from_dict(data)
                        for bid, data in backgrounds_data.items()
                    }
            
            # Load environmental effects
            if self.effects_file.exists():
                with open(self.effects_file, 'r', encoding='utf-8') as f:
                    effects_data = json.load(f)
                    self.environmental_effects = {
                        eid: EnvironmentalEffect.from_dict(data)
                        for eid, data in effects_data.items()
                    }
                    
        except Exception as e:
            print(f"Error loading background data: {e}")
    
    def _save_data(self):
        """Save background data to disk."""
        try:
            # Save background assets
            with open(self.bg_assets_file, 'w', encoding='utf-8') as f:
                json.dump({
                    aid: asset.to_dict()
                    for aid, asset in self.background_assets.items()
                }, f, indent=2)
            
            # Save scene backgrounds
            with open(self.scene_backgrounds_file, 'w', encoding='utf-8') as f:
                json.dump({
                    bid: background.to_dict()
                    for bid, background in self.scene_backgrounds.items()
                }, f, indent=2)
            
            # Save environmental effects
            with open(self.effects_file, 'w', encoding='utf-8') as f:
                json.dump({
                    eid: effect.to_dict()
                    for eid, effect in self.environmental_effects.items()
                }, f, indent=2)
                
        except Exception as e:
            print(f"Error saving background data: {e}")
    
    def _create_default_backgrounds(self):
        """Create default background assets for common scenarios."""
        if self.background_assets:
            return  # Already have backgrounds
        
        defaults = [
            {
                "name": "Solid Color - Black",
                "category": "solid",
                "description": "Simple black background",
                "color": "#000000"
            },
            {
                "name": "Solid Color - White", 
                "category": "solid",
                "description": "Simple white background",
                "color": "#ffffff"
            },
            {
                "name": "Gradient - Dark",
                "category": "gradient",
                "description": "Dark gradient background",
                "gradient": "linear-gradient(45deg, #232526, #414345)"
            },
            {
                "name": "Gradient - Blue",
                "category": "gradient", 
                "description": "Blue gradient background",
                "gradient": "linear-gradient(45deg, #1e3c72, #2a5298)"
            }
        ]
        
        for default in defaults:
            asset_id = str(uuid.uuid4())
            asset = BackgroundAsset(
                id=asset_id,
                name=default["name"],
                file_path="",  # Procedural background
                category=default["category"],
                description=default["description"]
            )
            
            # Add extra properties for procedural backgrounds
            if "color" in default:
                asset.tags.append(f"color:{default['color']}")
            if "gradient" in default:
                asset.tags.append(f"gradient:{default['gradient']}")
            
            self.background_assets[asset_id] = asset
        
        self._save_data()
    
    def import_background_from_file(self, name: str, file_path: str, 
                                  category: str = "general", 
                                  time_of_day: str = "any",
                                  mood: str = "neutral") -> Optional[str]:
        """Import a background from an image file."""
        if not os.path.exists(file_path):
            return None
        
        try:
            # Copy file to background assets directory
            file_ext = os.path.splitext(file_path)[1]
            new_filename = f"bg_{uuid.uuid4()}{file_ext}"
            new_path = self.bg_assets_dir / new_filename
            
            import shutil
            shutil.copy2(file_path, new_path)
            
            # Get image dimensions
            width, height = self._get_image_dimensions(str(new_path))
            
            # Create background asset
            asset_id = str(uuid.uuid4())
            asset = BackgroundAsset(
                id=asset_id,
                name=name,
                file_path=str(new_path),
                category=category,
                time_of_day=time_of_day,
                mood=mood,
                width=width,
                height=height,
                description=f"Imported from {os.path.basename(file_path)}"
            )
            
            self.background_assets[asset_id] = asset
            self._save_data()
            return asset_id
            
        except Exception as e:
            print(f"Error importing background: {e}")
            return None
    
    def _get_image_dimensions(self, file_path: str) -> Tuple[int, int]:
        """Get image dimensions without loading the full image."""
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                return img.size
        except ImportError:
            # Fallback if PIL not available
            return (1920, 1080)  # Common default
        except Exception:
            return (1920, 1080)  # Default on error
    
    def create_background_asset(self, asset_data: BackgroundAsset) -> bool:
        """Create a new background asset."""
        if asset_data.id in self.background_assets:
            return False
        
        self.background_assets[asset_data.id] = asset_data
        self._save_data()
        return True
    
    def get_background_asset(self, asset_id: str) -> Optional[BackgroundAsset]:
        """Get a background asset by ID."""
        return self.background_assets.get(asset_id)
    
    def update_background_asset(self, asset_data: BackgroundAsset) -> bool:
        """Update an existing background asset."""
        if asset_data.id not in self.background_assets:
            return False
        
        self.background_assets[asset_data.id] = asset_data
        self._save_data()
        return True
    
    def delete_background_asset(self, asset_id: str) -> bool:
        """Delete a background asset."""
        if asset_id not in self.background_assets:
            return False
        
        asset = self.background_assets[asset_id]
        
        # Delete the image file if it exists
        if asset.file_path and os.path.exists(asset.file_path):
            try:
                os.remove(asset.file_path)
            except Exception as e:
                print(f"Error deleting background file {asset.file_path}: {e}")
        
        # Remove from scene backgrounds that use this asset
        for scene in self.scene_backgrounds.values():
            if scene.primary_asset_id == asset_id:
                scene.primary_asset_id = ""
            scene.layers = [
                layer for layer in scene.layers
                if layer.asset_id != asset_id
            ]
        
        del self.background_assets[asset_id]
        self._save_data()
        return True
    
    def create_scene_background(self, background_data: SceneBackground) -> bool:
        """Create a new scene background."""
        if background_data.id in self.scene_backgrounds:
            return False
        
        self.scene_backgrounds[background_data.id] = background_data
        self._save_data()
        return True
    
    def get_scene_background(self, background_id: str) -> Optional[SceneBackground]:
        """Get a scene background by ID."""
        return self.scene_backgrounds.get(background_id)
    
    def update_scene_background(self, background_data: SceneBackground) -> bool:
        """Update an existing scene background."""
        if background_data.id not in self.scene_backgrounds:
            return False
        
        self.scene_backgrounds[background_data.id] = background_data
        self._save_data()
        return True
    
    def delete_scene_background(self, background_id: str) -> bool:
        """Delete a scene background."""
        if background_id not in self.scene_backgrounds:
            return False
        
        del self.scene_backgrounds[background_id]
        self._save_data()
        return True
    
    def get_backgrounds_by_category(self, category: str) -> List[BackgroundAsset]:
        """Get all background assets in a specific category."""
        return [
            asset for asset in self.background_assets.values()
            if asset.category == category
        ]
    
    def get_backgrounds_by_mood(self, mood: str) -> List[BackgroundAsset]:
        """Get all background assets matching a mood."""
        return [
            asset for asset in self.background_assets.values()
            if asset.mood == mood
        ]
    
    def get_backgrounds_by_time(self, time_of_day: str) -> List[BackgroundAsset]:
        """Get all background assets for a time of day."""
        return [
            asset for asset in self.background_assets.values()
            if asset.time_of_day == time_of_day or asset.time_of_day == "any"
        ]
    
    def search_backgrounds(self, query: str) -> List[BackgroundAsset]:
        """Search backgrounds by name, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for asset in self.background_assets.values():
            if (query_lower in asset.name.lower() or
                query_lower in asset.description.lower() or
                any(query_lower in tag.lower() for tag in asset.tags)):
                results.append(asset)
        
        return results
    
    def suggest_background_for_scene(self, scene_context: Dict[str, Any]) -> Optional[str]:
        """Suggest a background based on scene context."""
        # Extract context information
        mood = scene_context.get("mood", "neutral")
        time = scene_context.get("time_of_day", "any")
        category = scene_context.get("category", "general")
        
        # Find matching backgrounds
        candidates = []
        
        for asset in self.background_assets.values():
            score = 0
            
            # Exact matches get higher scores
            if asset.mood == mood:
                score += 3
            if asset.time_of_day == time:
                score += 2
            if asset.category == category:
                score += 2
            
            # "any" is always acceptable
            if asset.time_of_day == "any":
                score += 1
            
            if score > 0:
                candidates.append((asset.id, score))
        
        if candidates:
            # Sort by score and return the best match
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        # Fallback to first available background
        if self.background_assets:
            return next(iter(self.background_assets.keys()))
        
        return None
    
    def create_environmental_effect(self, effect_data: EnvironmentalEffect) -> bool:
        """Create a new environmental effect."""
        if effect_data.id in self.environmental_effects:
            return False
        
        self.environmental_effects[effect_data.id] = effect_data
        self._save_data()
        return True
    
    def get_environmental_effect(self, effect_id: str) -> Optional[EnvironmentalEffect]:
        """Get an environmental effect by ID."""
        return self.environmental_effects.get(effect_id)
    
    def get_effect_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get predefined environmental effect configurations."""
        return {
            "rain": {
                "name": "Rain",
                "effect_type": "weather",
                "config": {
                    "particle_count": 200,
                    "fall_speed": 300,
                    "wind": 50,
                    "opacity": 0.7,
                    "color": "#89CDF1"
                }
            },
            "snow": {
                "name": "Snow",
                "effect_type": "weather", 
                "config": {
                    "particle_count": 100,
                    "fall_speed": 100,
                    "wind": 20,
                    "opacity": 0.8,
                    "color": "#ffffff"
                }
            },
            "leaves": {
                "name": "Falling Leaves",
                "effect_type": "particles",
                "config": {
                    "particle_count": 50,
                    "fall_speed": 80,
                    "wind": 100,
                    "opacity": 0.9,
                    "colors": ["#ff6b35", "#f7931e", "#ffb700"]
                }
            },
            "sparkles": {
                "name": "Magic Sparkles",
                "effect_type": "particles",
                "config": {
                    "particle_count": 30,
                    "movement": "float",
                    "opacity": 0.6,
                    "color": "#ffd700",
                    "size_range": [2, 6]
                }
            },
            "fog": {
                "name": "Fog Overlay",
                "effect_type": "lighting",
                "config": {
                    "opacity": 0.3,
                    "color": "#e0e0e0",
                    "movement": "drift",
                    "density": 0.5
                }
            }
        }
    
    def export_backgrounds_for_html(self) -> Dict[str, Any]:
        """Export background data for HTML game export."""
        export_data = {
            "background_assets": {},
            "scene_backgrounds": {},
            "environmental_effects": {}
        }
        
        # Export background assets with base64-encoded images
        for asset_id, asset in self.background_assets.items():
            asset_export = asset.to_dict()
            
            if asset.file_path and os.path.exists(asset.file_path):
                try:
                    with open(asset.file_path, 'rb') as f:
                        image_data = base64.b64encode(f.read()).decode('utf-8')
                    
                    # Detect image format
                    ext = os.path.splitext(asset.file_path)[1].lower()
                    if ext in ['.jpg', '.jpeg']:
                        mime_type = 'image/jpeg'
                    elif ext == '.png':
                        mime_type = 'image/png'
                    elif ext == '.gif':
                        mime_type = 'image/gif'
                    elif ext == '.webp':
                        mime_type = 'image/webp'
                    else:
                        mime_type = 'image/png'
                    
                    asset_export["image_data"] = f"data:{mime_type};base64,{image_data}"
                    
                except Exception as e:
                    print(f"Error encoding background image {asset.file_path}: {e}")
                    asset_export["image_data"] = None
            else:
                asset_export["image_data"] = None
            
            export_data["background_assets"][asset_id] = asset_export
        
        # Export scene backgrounds
        export_data["scene_backgrounds"] = {
            bg_id: background.to_dict()
            for bg_id, background in self.scene_backgrounds.items()
        }
        
        # Export environmental effects
        export_data["environmental_effects"] = {
            effect_id: effect.to_dict()
            for effect_id, effect in self.environmental_effects.items()
        }
        
        return export_data
    
    def get_available_categories(self) -> List[str]:
        """Get list of all available background categories."""
        categories = set()
        for asset in self.background_assets.values():
            categories.add(asset.category)
        return sorted(list(categories))
    
    def get_available_moods(self) -> List[str]:
        """Get list of all available moods."""
        moods = set()
        for asset in self.background_assets.values():
            moods.add(asset.mood)
        return sorted(list(moods))
    
    def get_available_times(self) -> List[str]:
        """Get list of all available time periods."""
        times = set()
        for asset in self.background_assets.values():
            times.add(asset.time_of_day)
        return sorted(list(times))
    
    def cleanup(self):
        """Clean up resources and save data."""
        self._save_data()