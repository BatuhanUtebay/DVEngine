# dvge/features/voice_system.py

"""Voice Acting Pipeline - Core voice management system."""

import os
import json
import uuid
import hashlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import base64


@dataclass
class VoiceProfile:
    """Represents a voice profile with metadata."""
    id: str
    name: str
    provider: str  # 'azure', 'aws', 'google', 'openai', 'local'
    voice_id: str  # Provider-specific voice ID
    language: str = "en-US"
    gender: str = "neutral"  # 'male', 'female', 'neutral'
    age_range: str = "adult"  # 'child', 'teen', 'adult', 'elderly'
    style: str = "neutral"  # 'neutral', 'cheerful', 'sad', 'angry', etc.
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0
    description: str = ""
    is_favorite: bool = False
    usage_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoiceProfile':
        return cls(**data)


@dataclass
class VoiceAsset:
    """Represents a generated voice asset."""
    id: str
    text: str
    voice_profile_id: str
    file_path: str
    duration: float = 0.0
    file_size: int = 0
    text_hash: str = ""
    created_timestamp: float = 0.0
    character_id: Optional[str] = None
    node_id: Optional[str] = None
    emotion: str = "neutral"
    
    def __post_init__(self):
        if not self.text_hash:
            self.text_hash = hashlib.md5(self.text.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoiceAsset':
        return cls(**data)


class VoiceManager:
    """Central voice asset management system."""
    
    def __init__(self, app=None):
        self.app = app
        self.voice_profiles: Dict[str, VoiceProfile] = {}
        self.voice_assets: Dict[str, VoiceAsset] = {}
        self.character_voice_assignments: Dict[str, str] = {}  # character_id -> voice_profile_id
        
        # Storage paths
        self.voice_data_dir = Path.home() / ".dvge" / "voice_data"
        self.voice_assets_dir = self.voice_data_dir / "assets"
        self.voice_profiles_file = self.voice_data_dir / "voice_profiles.json"
        self.voice_assignments_file = self.voice_data_dir / "character_assignments.json"
        self.voice_assets_file = self.voice_data_dir / "voice_assets.json"
        
        self._ensure_directories()
        self._load_data()
        
        # Initialize TTS providers
        self._initialize_tts_providers()
    
    def _ensure_directories(self):
        """Create necessary directories for voice data storage."""
        self.voice_data_dir.mkdir(parents=True, exist_ok=True)
        self.voice_assets_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_data(self):
        """Load voice profiles and assets from disk."""
        try:
            # Load voice profiles
            if self.voice_profiles_file.exists():
                with open(self.voice_profiles_file, 'r', encoding='utf-8') as f:
                    profiles_data = json.load(f)
                    self.voice_profiles = {
                        pid: VoiceProfile.from_dict(data) 
                        for pid, data in profiles_data.items()
                    }
            
            # Load character assignments
            if self.voice_assignments_file.exists():
                with open(self.voice_assignments_file, 'r', encoding='utf-8') as f:
                    self.character_voice_assignments = json.load(f)
            
            # Load voice assets
            if self.voice_assets_file.exists():
                with open(self.voice_assets_file, 'r', encoding='utf-8') as f:
                    assets_data = json.load(f)
                    self.voice_assets = {
                        aid: VoiceAsset.from_dict(data)
                        for aid, data in assets_data.items()
                    }
                    
        except Exception as e:
            print(f"Error loading voice data: {e}")
    
    def _save_data(self):
        """Save voice profiles and assets to disk."""
        try:
            # Save voice profiles
            with open(self.voice_profiles_file, 'w', encoding='utf-8') as f:
                json.dump({
                    pid: profile.to_dict() 
                    for pid, profile in self.voice_profiles.items()
                }, f, indent=2)
            
            # Save character assignments
            with open(self.voice_assignments_file, 'w', encoding='utf-8') as f:
                json.dump(self.character_voice_assignments, f, indent=2)
            
            # Save voice assets
            with open(self.voice_assets_file, 'w', encoding='utf-8') as f:
                json.dump({
                    aid: asset.to_dict()
                    for aid, asset in self.voice_assets.items()
                }, f, indent=2)
                
        except Exception as e:
            print(f"Error saving voice data: {e}")
    
    def _initialize_tts_providers(self):
        """Initialize available TTS providers."""
        try:
            from ..ai.tts_providers import TTSProviderManager
            self.tts_manager = TTSProviderManager()
        except ImportError:
            print("TTS providers not available, voice generation disabled")
            self.tts_manager = None
    
    def add_voice_profile(self, profile: VoiceProfile) -> bool:
        """Add a new voice profile."""
        if profile.id in self.voice_profiles:
            return False
        
        self.voice_profiles[profile.id] = profile
        self._save_data()
        return True
    
    def get_voice_profile(self, profile_id: str) -> Optional[VoiceProfile]:
        """Get a voice profile by ID."""
        return self.voice_profiles.get(profile_id)
    
    def update_voice_profile(self, profile: VoiceProfile) -> bool:
        """Update an existing voice profile."""
        if profile.id not in self.voice_profiles:
            return False
        
        self.voice_profiles[profile.id] = profile
        self._save_data()
        return True
    
    def delete_voice_profile(self, profile_id: str) -> bool:
        """Delete a voice profile and its associated assets."""
        if profile_id not in self.voice_profiles:
            return False
        
        # Delete associated voice assets
        assets_to_delete = [
            aid for aid, asset in self.voice_assets.items()
            if asset.voice_profile_id == profile_id
        ]
        
        for asset_id in assets_to_delete:
            self.delete_voice_asset(asset_id)
        
        # Remove character assignments using this profile
        self.character_voice_assignments = {
            char_id: vid for char_id, vid in self.character_voice_assignments.items()
            if vid != profile_id
        }
        
        del self.voice_profiles[profile_id]
        self._save_data()
        return True
    
    def assign_voice_to_character(self, character_id: str, voice_profile_id: str) -> bool:
        """Assign a voice profile to a character."""
        if voice_profile_id not in self.voice_profiles:
            return False
        
        self.character_voice_assignments[character_id] = voice_profile_id
        self._save_data()
        return True
    
    def get_character_voice(self, character_id: str) -> Optional[VoiceProfile]:
        """Get the voice profile assigned to a character."""
        voice_id = self.character_voice_assignments.get(character_id)
        if voice_id:
            return self.voice_profiles.get(voice_id)
        return None
    
    def generate_voice_asset(self, text: str, voice_profile_id: str, 
                           character_id: Optional[str] = None, 
                           node_id: Optional[str] = None,
                           emotion: str = "neutral") -> Optional[str]:
        """Generate a voice asset from text using specified voice profile."""
        if not self.tts_manager:
            print("TTS manager not available")
            return None
        
        profile = self.get_voice_profile(voice_profile_id)
        if not profile:
            print(f"Voice profile {voice_profile_id} not found")
            return None
        
        try:
            # Generate unique ID for this asset
            asset_id = str(uuid.uuid4())
            
            # Generate file path
            file_name = f"{asset_id}.wav"
            file_path = self.voice_assets_dir / file_name
            
            # Generate audio using TTS provider
            success = self.tts_manager.generate_speech(
                text=text,
                voice_profile=profile,
                output_path=str(file_path),
                emotion=emotion
            )
            
            if success and file_path.exists():
                # Create voice asset record
                import time
                asset = VoiceAsset(
                    id=asset_id,
                    text=text,
                    voice_profile_id=voice_profile_id,
                    file_path=str(file_path),
                    file_size=file_path.stat().st_size,
                    created_timestamp=time.time(),
                    character_id=character_id,
                    node_id=node_id,
                    emotion=emotion
                )
                
                self.voice_assets[asset_id] = asset
                
                # Update usage count
                profile.usage_count += 1
                self.voice_profiles[voice_profile_id] = profile
                
                self._save_data()
                return asset_id
            else:
                print("Failed to generate voice asset")
                return None
                
        except Exception as e:
            print(f"Error generating voice asset: {e}")
            return None
    
    def get_voice_asset(self, asset_id: str) -> Optional[VoiceAsset]:
        """Get a voice asset by ID."""
        return self.voice_assets.get(asset_id)
    
    def delete_voice_asset(self, asset_id: str) -> bool:
        """Delete a voice asset and its file."""
        asset = self.voice_assets.get(asset_id)
        if not asset:
            return False
        
        try:
            # Delete the audio file
            file_path = Path(asset.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # Remove from assets
            del self.voice_assets[asset_id]
            self._save_data()
            return True
            
        except Exception as e:
            print(f"Error deleting voice asset: {e}")
            return False
    
    def get_assets_for_character(self, character_id: str) -> List[VoiceAsset]:
        """Get all voice assets for a specific character."""
        return [
            asset for asset in self.voice_assets.values()
            if asset.character_id == character_id
        ]
    
    def get_assets_for_node(self, node_id: str) -> List[VoiceAsset]:
        """Get all voice assets for a specific node."""
        return [
            asset for asset in self.voice_assets.values()
            if asset.node_id == node_id
        ]
    
    def batch_generate_for_project(self, progress_callback=None) -> Dict[str, Any]:
        """Batch generate voice assets for all dialogue in the current project."""
        if not self.app or not self.app.nodes:
            return {"success": False, "error": "No project loaded"}
        
        results = {
            "success": True,
            "generated": 0,
            "skipped": 0,
            "errors": 0,
            "details": []
        }
        
        total_nodes = len(self.app.nodes)
        processed = 0
        
        for node_id, node in self.app.nodes.items():
            if hasattr(node, 'text') and node.text:
                # Check if this node has a character assigned
                character_id = getattr(node, 'character', None)
                if character_id and character_id in self.character_voice_assignments:
                    voice_profile_id = self.character_voice_assignments[character_id]
                    
                    # Check if asset already exists
                    existing_assets = self.get_assets_for_node(node_id)
                    text_hash = hashlib.md5(node.text.encode()).hexdigest()
                    
                    if any(asset.text_hash == text_hash for asset in existing_assets):
                        results["skipped"] += 1
                    else:
                        # Generate new asset
                        asset_id = self.generate_voice_asset(
                            text=node.text,
                            voice_profile_id=voice_profile_id,
                            character_id=character_id,
                            node_id=node_id
                        )
                        
                        if asset_id:
                            results["generated"] += 1
                            results["details"].append(f"Generated voice for node {node_id}")
                        else:
                            results["errors"] += 1
                            results["details"].append(f"Failed to generate voice for node {node_id}")
            
            processed += 1
            if progress_callback:
                progress_callback(processed, total_nodes)
        
        return results
    
    def export_voice_data_for_html(self) -> Dict[str, Any]:
        """Export voice data for HTML game export."""
        export_data = {
            "voice_profiles": {
                pid: profile.to_dict() 
                for pid, profile in self.voice_profiles.items()
            },
            "character_assignments": self.character_voice_assignments.copy(),
            "voice_assets": {}
        }
        
        # Include base64-encoded audio data for assets
        for asset_id, asset in self.voice_assets.items():
            try:
                file_path = Path(asset.file_path)
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        audio_data = base64.b64encode(f.read()).decode('utf-8')
                        export_data["voice_assets"][asset_id] = {
                            **asset.to_dict(),
                            "audio_data": audio_data
                        }
            except Exception as e:
                print(f"Error encoding voice asset {asset_id}: {e}")
        
        return export_data
    
    def get_available_providers(self) -> List[str]:
        """Get list of available TTS providers."""
        if self.tts_manager:
            return self.tts_manager.get_available_providers()
        return []
    
    def cleanup(self):
        """Clean up resources and save data."""
        self._save_data()
        if self.tts_manager:
            self.tts_manager.cleanup()