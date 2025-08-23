# dvge/features/sprite_system.py

"""Visual Novel Mode - Character sprite management system."""

import os
import json
import uuid
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class SpriteVariant:
    """Represents a sprite variant (expression/pose)."""
    id: str
    name: str
    file_path: str
    expression: str = "neutral"  # neutral, happy, sad, angry, surprised, etc.
    pose: str = "default"        # default, pointing, crossed_arms, etc.
    layer_order: int = 0         # For layered composition
    offset_x: int = 0           # Position offset from center
    offset_y: int = 0
    scale: float = 1.0          # Scale multiplier
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpriteVariant':
        return cls(**data)


@dataclass
class CharacterSprite:
    """Represents a character's sprite collection."""
    id: str
    character_name: str
    default_variant: str  # ID of default variant
    variants: Dict[str, SpriteVariant]
    base_scale: float = 1.0
    base_position: Tuple[int, int] = (0, 0)  # Default position on screen
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "character_name": self.character_name,
            "default_variant": self.default_variant,
            "variants": {vid: variant.to_dict() for vid, variant in self.variants.items()},
            "base_scale": self.base_scale,
            "base_position": self.base_position,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterSprite':
        variants = {
            vid: SpriteVariant.from_dict(variant_data)
            for vid, variant_data in data.get("variants", {}).items()
        }
        return cls(
            id=data["id"],
            character_name=data["character_name"],
            default_variant=data["default_variant"],
            variants=variants,
            base_scale=data.get("base_scale", 1.0),
            base_position=tuple(data.get("base_position", [0, 0])),
            description=data.get("description", "")
        )


@dataclass
class SpriteLayer:
    """Represents a sprite layer in a scene."""
    character_id: str
    variant_id: str
    position: Tuple[int, int] = (0, 0)  # Screen position
    scale: float = 1.0
    opacity: float = 1.0
    z_index: int = 0
    visible: bool = True
    transition_in: str = "fade"    # fade, slide_left, slide_right, etc.
    transition_out: str = "fade"
    transition_duration: float = 0.3  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpriteLayer':
        return cls(**data)


@dataclass
class SpriteScene:
    """Represents a complete sprite scene configuration."""
    id: str
    name: str
    layers: List[SpriteLayer]
    background_id: Optional[str] = None
    scene_transition: str = "fade"
    scene_duration: float = 0.5
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "layers": [layer.to_dict() for layer in self.layers],
            "background_id": self.background_id,
            "scene_transition": self.scene_transition,
            "scene_duration": self.scene_duration,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpriteScene':
        layers = [SpriteLayer.from_dict(layer_data) for layer_data in data.get("layers", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            layers=layers,
            background_id=data.get("background_id"),
            scene_transition=data.get("scene_transition", "fade"),
            scene_duration=data.get("scene_duration", 0.5),
            description=data.get("description", "")
        )


class SpriteManager:
    """Central sprite management system for Visual Novel Mode."""
    
    def __init__(self, app=None):
        self.app = app
        self.character_sprites: Dict[str, CharacterSprite] = {}
        self.sprite_scenes: Dict[str, SpriteScene] = {}
        
        # Storage paths
        self.sprite_data_dir = Path.home() / ".dvge" / "sprite_data"
        self.sprite_assets_dir = self.sprite_data_dir / "assets"
        self.character_sprites_file = self.sprite_data_dir / "character_sprites.json"
        self.sprite_scenes_file = self.sprite_data_dir / "sprite_scenes.json"
        
        self._ensure_directories()
        self._load_data()
    
    def _ensure_directories(self):
        """Create necessary directories for sprite data storage."""
        self.sprite_data_dir.mkdir(parents=True, exist_ok=True)
        self.sprite_assets_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_data(self):
        """Load sprite data from disk."""
        try:
            # Load character sprites
            if self.character_sprites_file.exists():
                with open(self.character_sprites_file, 'r', encoding='utf-8') as f:
                    sprites_data = json.load(f)
                    self.character_sprites = {
                        sid: CharacterSprite.from_dict(data)
                        for sid, data in sprites_data.items()
                    }
            
            # Load sprite scenes
            if self.sprite_scenes_file.exists():
                with open(self.sprite_scenes_file, 'r', encoding='utf-8') as f:
                    scenes_data = json.load(f)
                    self.sprite_scenes = {
                        sid: SpriteScene.from_dict(data)
                        for sid, data in scenes_data.items()
                    }
                    
        except Exception as e:
            print(f"Error loading sprite data: {e}")
    
    def _save_data(self):
        """Save sprite data to disk."""
        try:
            # Save character sprites
            with open(self.character_sprites_file, 'w', encoding='utf-8') as f:
                json.dump({
                    sid: sprite.to_dict()
                    for sid, sprite in self.character_sprites.items()
                }, f, indent=2)
            
            # Save sprite scenes
            with open(self.sprite_scenes_file, 'w', encoding='utf-8') as f:
                json.dump({
                    sid: scene.to_dict()
                    for sid, scene in self.sprite_scenes.items()
                }, f, indent=2)
                
        except Exception as e:
            print(f"Error saving sprite data: {e}")
    
    def create_character_sprite(self, character_name: str, sprite_data: CharacterSprite) -> bool:
        """Create a new character sprite."""
        if sprite_data.id in self.character_sprites:
            return False
        
        self.character_sprites[sprite_data.id] = sprite_data
        self._save_data()
        return True
    
    def get_character_sprite(self, sprite_id: str) -> Optional[CharacterSprite]:
        """Get a character sprite by ID."""
        return self.character_sprites.get(sprite_id)
    
    def get_character_sprite_by_name(self, character_name: str) -> Optional[CharacterSprite]:
        """Get a character sprite by character name."""
        for sprite in self.character_sprites.values():
            if sprite.character_name == character_name:
                return sprite
        return None
    
    def update_character_sprite(self, sprite_data: CharacterSprite) -> bool:
        """Update an existing character sprite."""
        if sprite_data.id not in self.character_sprites:
            return False
        
        self.character_sprites[sprite_data.id] = sprite_data
        self._save_data()
        return True
    
    def delete_character_sprite(self, sprite_id: str) -> bool:
        """Delete a character sprite and all its variants."""
        if sprite_id not in self.character_sprites:
            return False
        
        sprite = self.character_sprites[sprite_id]
        
        # Delete associated image files
        for variant in sprite.variants.values():
            try:
                if os.path.exists(variant.file_path):
                    os.remove(variant.file_path)
            except Exception as e:
                print(f"Error deleting sprite file {variant.file_path}: {e}")
        
        # Remove from scenes that use this sprite
        for scene in self.sprite_scenes.values():
            scene.layers = [
                layer for layer in scene.layers
                if layer.character_id != sprite_id
            ]
        
        del self.character_sprites[sprite_id]
        self._save_data()
        return True
    
    def add_sprite_variant(self, sprite_id: str, variant: SpriteVariant) -> bool:
        """Add a new variant to an existing character sprite."""
        if sprite_id not in self.character_sprites:
            return False
        
        sprite = self.character_sprites[sprite_id]
        sprite.variants[variant.id] = variant
        self._save_data()
        return True
    
    def update_sprite_variant(self, sprite_id: str, variant: SpriteVariant) -> bool:
        """Update a sprite variant."""
        if sprite_id not in self.character_sprites:
            return False
        
        sprite = self.character_sprites[sprite_id]
        if variant.id not in sprite.variants:
            return False
        
        sprite.variants[variant.id] = variant
        self._save_data()
        return True
    
    def delete_sprite_variant(self, sprite_id: str, variant_id: str) -> bool:
        """Delete a sprite variant."""
        if sprite_id not in self.character_sprites:
            return False
        
        sprite = self.character_sprites[sprite_id]
        if variant_id not in sprite.variants:
            return False
        
        # Don't allow deletion of the default variant
        if sprite.default_variant == variant_id:
            return False
        
        variant = sprite.variants[variant_id]
        
        # Delete the image file
        try:
            if os.path.exists(variant.file_path):
                os.remove(variant.file_path)
        except Exception as e:
            print(f"Error deleting sprite file {variant.file_path}: {e}")
        
        del sprite.variants[variant_id]
        self._save_data()
        return True
    
    def create_sprite_scene(self, scene_data: SpriteScene) -> bool:
        """Create a new sprite scene."""
        if scene_data.id in self.sprite_scenes:
            return False
        
        self.sprite_scenes[scene_data.id] = scene_data
        self._save_data()
        return True
    
    def get_sprite_scene(self, scene_id: str) -> Optional[SpriteScene]:
        """Get a sprite scene by ID."""
        return self.sprite_scenes.get(scene_id)
    
    def update_sprite_scene(self, scene_data: SpriteScene) -> bool:
        """Update an existing sprite scene."""
        if scene_data.id not in self.sprite_scenes:
            return False
        
        self.sprite_scenes[scene_data.id] = scene_data
        self._save_data()
        return True
    
    def delete_sprite_scene(self, scene_id: str) -> bool:
        """Delete a sprite scene."""
        if scene_id not in self.sprite_scenes:
            return False
        
        del self.sprite_scenes[scene_id]
        self._save_data()
        return True
    
    def get_scenes_using_character(self, character_id: str) -> List[SpriteScene]:
        """Get all scenes that use a specific character."""
        scenes = []
        for scene in self.sprite_scenes.values():
            for layer in scene.layers:
                if layer.character_id == character_id:
                    scenes.append(scene)
                    break
        return scenes
    
    def import_sprite_from_file(self, sprite_id: str, variant_name: str, 
                               file_path: str, expression: str = "neutral", 
                               pose: str = "default") -> Optional[str]:
        """Import a sprite variant from an image file."""
        if not os.path.exists(file_path):
            return None
        
        try:
            # Copy file to sprite assets directory
            file_ext = os.path.splitext(file_path)[1]
            new_filename = f"{sprite_id}_{variant_name}_{expression}_{pose}{file_ext}"
            new_path = self.sprite_assets_dir / new_filename
            
            import shutil
            shutil.copy2(file_path, new_path)
            
            # Create variant
            variant_id = str(uuid.uuid4())
            variant = SpriteVariant(
                id=variant_id,
                name=variant_name,
                file_path=str(new_path),
                expression=expression,
                pose=pose,
                description=f"Imported from {os.path.basename(file_path)}"
            )
            
            if self.add_sprite_variant(sprite_id, variant):
                return variant_id
            else:
                # Clean up copied file if adding variant failed
                try:
                    os.remove(new_path)
                except:
                    pass
                return None
                
        except Exception as e:
            print(f"Error importing sprite: {e}")
            return None
    
    def generate_scene_for_node(self, node_id: str) -> Optional[str]:
        """Generate a sprite scene based on dialogue node characters."""
        if not self.app or not self.app.nodes:
            return None
        
        node = self.app.nodes.get(node_id)
        if not node:
            return None
        
        # Get characters mentioned in this node
        characters = set()
        if hasattr(node, 'character') and node.character:
            characters.add(node.character)
        
        # Check for other characters in dialogue text
        if hasattr(node, 'text') and node.text:
            # Simple heuristic: look for character names in known sprites
            text_lower = node.text.lower()
            for sprite in self.character_sprites.values():
                if sprite.character_name.lower() in text_lower:
                    characters.add(sprite.character_name)
        
        if not characters:
            return None
        
        # Create scene with characters
        scene_id = str(uuid.uuid4())
        layers = []
        x_positions = self._calculate_character_positions(len(characters))
        
        for i, character in enumerate(characters):
            sprite = self.get_character_sprite_by_name(character)
            if sprite and sprite.variants:
                layer = SpriteLayer(
                    character_id=sprite.id,
                    variant_id=sprite.default_variant,
                    position=(x_positions[i], 0),
                    z_index=i
                )
                layers.append(layer)
        
        scene = SpriteScene(
            id=scene_id,
            name=f"Scene for Node {node_id}",
            layers=layers,
            description=f"Auto-generated scene for dialogue node {node_id}"
        )
        
        if self.create_sprite_scene(scene):
            return scene_id
        return None
    
    def _calculate_character_positions(self, count: int) -> List[int]:
        """Calculate optimal positions for multiple characters."""
        if count == 1:
            return [0]  # Center
        elif count == 2:
            return [-200, 200]  # Left and right
        elif count == 3:
            return [-300, 0, 300]  # Left, center, right
        else:
            # Distribute evenly across screen
            spacing = 600 // max(count - 1, 1)
            return [i * spacing - 300 for i in range(count)]
    
    def export_sprites_for_html(self) -> Dict[str, Any]:
        """Export sprite data for HTML game export."""
        export_data = {
            "character_sprites": {},
            "sprite_scenes": {}
        }
        
        # Export character sprites with base64-encoded images
        for sprite_id, sprite in self.character_sprites.items():
            sprite_export = sprite.to_dict()
            
            # Encode variant images
            for variant_id, variant in sprite.variants.items():
                try:
                    if os.path.exists(variant.file_path):
                        with open(variant.file_path, 'rb') as f:
                            image_data = base64.b64encode(f.read()).decode('utf-8')
                            
                        # Detect image format
                        ext = os.path.splitext(variant.file_path)[1].lower()
                        if ext in ['.jpg', '.jpeg']:
                            mime_type = 'image/jpeg'
                        elif ext == '.png':
                            mime_type = 'image/png'
                        elif ext == '.gif':
                            mime_type = 'image/gif'
                        elif ext == '.webp':
                            mime_type = 'image/webp'
                        else:
                            mime_type = 'image/png'  # default
                        
                        sprite_export["variants"][variant_id]["image_data"] = f"data:{mime_type};base64,{image_data}"
                        
                except Exception as e:
                    print(f"Error encoding sprite image {variant.file_path}: {e}")
                    sprite_export["variants"][variant_id]["image_data"] = None
            
            export_data["character_sprites"][sprite_id] = sprite_export
        
        # Export sprite scenes
        export_data["sprite_scenes"] = {
            scene_id: scene.to_dict()
            for scene_id, scene in self.sprite_scenes.items()
        }
        
        return export_data
    
    def get_available_expressions(self) -> List[str]:
        """Get list of all available expressions across sprites."""
        expressions = set()
        for sprite in self.character_sprites.values():
            for variant in sprite.variants.values():
                expressions.add(variant.expression)
        return sorted(list(expressions))
    
    def get_available_poses(self) -> List[str]:
        """Get list of all available poses across sprites."""
        poses = set()
        for sprite in self.character_sprites.values():
            for variant in sprite.variants.values():
                poses.add(variant.pose)
        return sorted(list(poses))
    
    def get_character_names(self) -> List[str]:
        """Get list of all character names that have sprites."""
        return [sprite.character_name for sprite in self.character_sprites.values()]
    
    def cleanup(self):
        """Clean up resources and save data."""
        self._save_data()