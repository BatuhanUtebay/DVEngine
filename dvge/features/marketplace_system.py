# dvge/features/marketplace_system.py

"""Community Marketplace - Core marketplace management system."""

import json
import os
import hashlib
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
from enum import Enum


class ContentType(Enum):
    """Types of content available in the marketplace."""
    TEMPLATE = "template"
    ASSET_PACK = "asset_pack"
    SPRITE = "sprite"
    BACKGROUND = "background"
    VOICE_PACK = "voice_pack"
    MUSIC = "music"
    SOUND_EFFECT = "sound_effect"
    THEME = "theme"
    PLUGIN = "plugin"
    COMPLETE_GAME = "complete_game"


class ContentCategory(Enum):
    """Content categories for organization."""
    FANTASY = "fantasy"
    SCI_FI = "sci_fi"
    MODERN = "modern"
    HORROR = "horror"
    ROMANCE = "romance"
    COMEDY = "comedy"
    DRAMA = "drama"
    ADVENTURE = "adventure"
    MYSTERY = "mystery"
    EDUCATIONAL = "educational"
    ABSTRACT = "abstract"
    GENERAL = "general"


class ContentRating(Enum):
    """Content rating system."""
    EVERYONE = "everyone"
    TEEN = "teen"
    MATURE = "mature"
    ADULT = "adult"


@dataclass
class MarketplaceUser:
    """Represents a marketplace user."""
    id: str
    username: str
    display_name: str
    email: str = ""
    profile_image: Optional[str] = None
    bio: str = ""
    website: Optional[str] = None
    reputation_score: int = 0
    upload_count: int = 0
    download_count: int = 0
    created_at: str = ""
    verified: bool = False
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketplaceUser':
        return cls(**data)


@dataclass
class ContentMetadata:
    """Metadata for marketplace content."""
    id: str
    title: str
    description: str
    author_id: str
    author_name: str
    content_type: str = ContentType.TEMPLATE.value
    category: str = ContentCategory.GENERAL.value
    tags: List[str] = None
    rating: str = ContentRating.EVERYONE.value
    version: str = "1.0.0"
    file_size: int = 0
    download_count: int = 0
    rating_average: float = 0.0
    rating_count: int = 0
    created_at: str = ""
    updated_at: str = ""
    preview_images: List[str] = None
    dependencies: List[str] = None
    compatibility_version: str = ""
    license: str = "CC BY 4.0"
    price: float = 0.0  # 0.0 for free content
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.preview_images is None:
            self.preview_images = []
        if self.dependencies is None:
            self.dependencies = []
        if not self.created_at:
            now = datetime.now(timezone.utc).isoformat()
            self.created_at = now
            self.updated_at = now
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentMetadata':
        return cls(**data)


@dataclass
class ContentRatingEntry:
    """Represents a user rating for content."""
    id: str
    content_id: str
    user_id: str
    rating: int  # 1-5 stars
    review: str = ""
    created_at: str = ""
    helpful_votes: int = 0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentRatingEntry':
        return cls(**data)


@dataclass
class DownloadRecord:
    """Record of content downloads."""
    id: str
    content_id: str
    user_id: str
    download_time: str = ""
    ip_address: Optional[str] = None
    
    def __post_init__(self):
        if not self.download_time:
            self.download_time = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DownloadRecord':
        return cls(**data)


class MarketplaceManager:
    """Central marketplace management system."""
    
    def __init__(self, app=None):
        self.app = app
        self.current_user: Optional[MarketplaceUser] = None
        self.content_catalog: Dict[str, ContentMetadata] = {}
        self.user_ratings: Dict[str, List[ContentRatingEntry]] = {}  # content_id -> ratings
        self.download_history: List[DownloadRecord] = []
        self.featured_content: List[str] = []  # content_ids
        
        # Storage paths
        self.marketplace_data_dir = Path.home() / ".dvge" / "marketplace_data"
        self.content_cache_dir = self.marketplace_data_dir / "content_cache"
        self.user_data_file = self.marketplace_data_dir / "user_data.json"
        self.catalog_file = self.marketplace_data_dir / "content_catalog.json"
        self.ratings_file = self.marketplace_data_dir / "content_ratings.json"
        self.downloads_file = self.marketplace_data_dir / "download_history.json"
        
        # Mock API settings (would be real endpoints in production)
        self.api_base_url = "https://api.dvge-marketplace.com/v1"
        self.api_key = None
        
        self._ensure_directories()
        self._load_local_data()
    
    def _ensure_directories(self):
        """Create necessary directories for marketplace data storage."""
        self.marketplace_data_dir.mkdir(parents=True, exist_ok=True)
        self.content_cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_local_data(self):
        """Load marketplace data from local cache."""
        try:
            # Load user data
            if self.user_data_file.exists():
                with open(self.user_data_file, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                    if user_data:
                        self.current_user = MarketplaceUser.from_dict(user_data)
            
            # Load content catalog
            if self.catalog_file.exists():
                with open(self.catalog_file, 'r', encoding='utf-8') as f:
                    catalog_data = json.load(f)
                    self.content_catalog = {
                        cid: ContentMetadata.from_dict(data)
                        for cid, data in catalog_data.items()
                    }
            
            # Load ratings
            if self.ratings_file.exists():
                with open(self.ratings_file, 'r', encoding='utf-8') as f:
                    ratings_data = json.load(f)
                    self.user_ratings = {
                        cid: [ContentRatingEntry.from_dict(rating_data) for rating_data in ratings]
                        for cid, ratings in ratings_data.items()
                    }
            
            # Load download history
            if self.downloads_file.exists():
                with open(self.downloads_file, 'r', encoding='utf-8') as f:
                    downloads_data = json.load(f)
                    self.download_history = [
                        DownloadRecord.from_dict(download_data)
                        for download_data in downloads_data
                    ]
                    
        except Exception as e:
            print(f"Error loading marketplace data: {e}")
    
    def _save_local_data(self):
        """Save marketplace data to local cache."""
        try:
            # Save user data
            with open(self.user_data_file, 'w', encoding='utf-8') as f:
                json.dump(
                    self.current_user.to_dict() if self.current_user else None,
                    f, indent=2
                )
            
            # Save content catalog
            with open(self.catalog_file, 'w', encoding='utf-8') as f:
                json.dump({
                    cid: content.to_dict()
                    for cid, content in self.content_catalog.items()
                }, f, indent=2)
            
            # Save ratings
            with open(self.ratings_file, 'w', encoding='utf-8') as f:
                json.dump({
                    cid: [rating.to_dict() for rating in ratings]
                    for cid, ratings in self.user_ratings.items()
                }, f, indent=2)
            
            # Save download history
            with open(self.downloads_file, 'w', encoding='utf-8') as f:
                json.dump([
                    download.to_dict()
                    for download in self.download_history
                ], f, indent=2)
                
        except Exception as e:
            print(f"Error saving marketplace data: {e}")
    
    def login_user(self, username: str, password: str) -> bool:
        """Login to the marketplace (mock implementation)."""
        # In a real implementation, this would authenticate with the API
        # For now, we'll create a mock user for testing
        
        if username == "demo_user":
            self.current_user = MarketplaceUser(
                id="demo_user_001",
                username=username,
                display_name="Demo User",
                email="demo@example.com",
                bio="Demo user for testing marketplace functionality",
                reputation_score=42,
                upload_count=3,
                download_count=15,
                verified=True
            )
            self._save_local_data()
            return True
        
        return False
    
    def logout_user(self):
        """Logout current user."""
        self.current_user = None
        self._save_local_data()
    
    def is_logged_in(self) -> bool:
        """Check if a user is currently logged in."""
        return self.current_user is not None
    
    def register_user(self, username: str, email: str, password: str, display_name: str = "") -> bool:
        """Register a new user (mock implementation)."""
        # In a real implementation, this would register with the API
        user_id = str(uuid.uuid4())
        
        self.current_user = MarketplaceUser(
            id=user_id,
            username=username,
            display_name=display_name or username,
            email=email,
            reputation_score=0,
            upload_count=0,
            download_count=0
        )
        
        self._save_local_data()
        return True
    
    def search_content(self, query: str = "", content_type: Optional[str] = None,
                      category: Optional[str] = None, tags: Optional[List[str]] = None,
                      sort_by: str = "popularity", limit: int = 20) -> List[ContentMetadata]:
        """Search for content in the marketplace."""
        results = list(self.content_catalog.values())
        
        # Apply filters
        if query:
            query_lower = query.lower()
            results = [
                content for content in results
                if (query_lower in content.title.lower() or
                    query_lower in content.description.lower() or
                    query_lower in content.author_name.lower() or
                    any(query_lower in tag.lower() for tag in content.tags))
            ]
        
        if content_type:
            results = [content for content in results if content.content_type == content_type]
        
        if category:
            results = [content for content in results if content.category == category]
        
        if tags:
            tag_set = set(tag.lower() for tag in tags)
            results = [
                content for content in results
                if tag_set.intersection(set(tag.lower() for tag in content.tags))
            ]
        
        # Sort results
        if sort_by == "popularity":
            results.sort(key=lambda x: x.download_count, reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda x: x.rating_average, reverse=True)
        elif sort_by == "newest":
            results.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_by == "title":
            results.sort(key=lambda x: x.title.lower())
        
        return results[:limit]
    
    def get_content_by_id(self, content_id: str) -> Optional[ContentMetadata]:
        """Get content metadata by ID."""
        return self.content_catalog.get(content_id)
    
    def get_featured_content(self) -> List[ContentMetadata]:
        """Get featured content for the homepage."""
        featured = []
        for content_id in self.featured_content:
            content = self.content_catalog.get(content_id)
            if content:
                featured.append(content)
        return featured
    
    def get_content_ratings(self, content_id: str) -> List[ContentRatingEntry]:
        """Get user ratings for specific content."""
        return self.user_ratings.get(content_id, [])
    
    def add_content_rating(self, content_id: str, rating: int, review: str = "") -> bool:
        """Add a rating for content."""
        if not self.current_user:
            return False
        
        # Check if user already rated this content
        existing_ratings = self.get_content_ratings(content_id)
        for existing_rating in existing_ratings:
            if existing_rating.user_id == self.current_user.id:
                # Update existing rating
                existing_rating.rating = rating
                existing_rating.review = review
                existing_rating.created_at = datetime.now(timezone.utc).isoformat()
                self._update_content_rating_average(content_id)
                self._save_local_data()
                return True
        
        # Add new rating
        rating_entry = ContentRatingEntry(
            id=str(uuid.uuid4()),
            content_id=content_id,
            user_id=self.current_user.id,
            rating=rating,
            review=review
        )
        
        if content_id not in self.user_ratings:
            self.user_ratings[content_id] = []
        
        self.user_ratings[content_id].append(rating_entry)
        self._update_content_rating_average(content_id)
        self._save_local_data()
        return True
    
    def _update_content_rating_average(self, content_id: str):
        """Update the average rating for content."""
        content = self.content_catalog.get(content_id)
        if not content:
            return
        
        ratings = self.get_content_ratings(content_id)
        if ratings:
            total_rating = sum(rating.rating for rating in ratings)
            content.rating_average = total_rating / len(ratings)
            content.rating_count = len(ratings)
        else:
            content.rating_average = 0.0
            content.rating_count = 0
    
    def download_content(self, content_id: str) -> Optional[str]:
        """Download content from the marketplace."""
        content = self.get_content_by_id(content_id)
        if not content:
            return None
        
        # In a real implementation, this would download from the API
        # For now, we'll simulate by checking if cached locally
        
        cache_path = self.content_cache_dir / f"{content_id}.json"
        
        if cache_path.exists():
            # Record download
            download_record = DownloadRecord(
                id=str(uuid.uuid4()),
                content_id=content_id,
                user_id=self.current_user.id if self.current_user else "anonymous"
            )
            
            self.download_history.append(download_record)
            
            # Update download count
            content.download_count += 1
            
            self._save_local_data()
            return str(cache_path)
        
        return None
    
    def upload_content(self, metadata: ContentMetadata, content_data: Dict[str, Any]) -> bool:
        """Upload content to the marketplace."""
        if not self.current_user:
            return False
        
        # Set author information
        metadata.author_id = self.current_user.id
        metadata.author_name = self.current_user.display_name
        
        # Calculate file size
        metadata.file_size = len(json.dumps(content_data).encode('utf-8'))
        
        # Save to local cache
        cache_path = self.content_cache_dir / f"{metadata.id}.json"
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": metadata.to_dict(),
                "content": content_data
            }, f, indent=2)
        
        # Add to catalog
        self.content_catalog[metadata.id] = metadata
        
        # Update user upload count
        self.current_user.upload_count += 1
        
        self._save_local_data()
        return True
    
    def get_user_uploads(self, user_id: Optional[str] = None) -> List[ContentMetadata]:
        """Get content uploaded by a specific user."""
        target_user_id = user_id or (self.current_user.id if self.current_user else None)
        if not target_user_id:
            return []
        
        return [
            content for content in self.content_catalog.values()
            if content.author_id == target_user_id
        ]
    
    def get_user_downloads(self, user_id: Optional[str] = None) -> List[DownloadRecord]:
        """Get download history for a specific user."""
        target_user_id = user_id or (self.current_user.id if self.current_user else None)
        if not target_user_id:
            return []
        
        return [
            download for download in self.download_history
            if download.user_id == target_user_id
        ]
    
    def create_content_from_project(self, title: str, description: str,
                                  content_type: str, category: str,
                                  tags: List[str]) -> Optional[str]:
        """Create marketplace content from the current project."""
        if not self.app or not self.current_user:
            return None
        
        # Export current project data
        try:
            project_data = {
                "nodes": {nid: node.to_dict() for nid, node in self.app.nodes.items()},
                "player_stats": getattr(self.app, 'player_stats', {}),
                "player_inventory": getattr(self.app, 'player_inventory', []),
                "story_flags": getattr(self.app, 'story_flags', {}),
                "variables": getattr(self.app, 'variables', {}),
                "quests": {
                    qid: quest.to_dict()
                    for qid, quest in getattr(self.app, 'quests', {}).items()
                },
                "project_settings": getattr(self.app, 'project_settings', {})
            }
            
            # Create content metadata
            content_id = str(uuid.uuid4())
            metadata = ContentMetadata(
                id=content_id,
                title=title,
                description=description,
                author_id=self.current_user.id,
                author_name=self.current_user.display_name,
                content_type=content_type,
                category=category,
                tags=tags,
                compatibility_version="1.0.0"  # Engine version
            )
            
            # Upload content
            if self.upload_content(metadata, project_data):
                return content_id
            
        except Exception as e:
            print(f"Error creating marketplace content: {e}")
        
        return None
    
    def install_content(self, content_id: str) -> bool:
        """Install downloaded content into the current project."""
        if not self.app:
            return False
        
        cache_path = self.content_cache_dir / f"{content_id}.json"
        if not cache_path.exists():
            return False
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                content_package = json.load(f)
            
            metadata = ContentMetadata.from_dict(content_package["metadata"])
            content_data = content_package["content"]
            
            # Install based on content type
            if metadata.content_type == ContentType.TEMPLATE.value:
                self._install_template(content_data)
            elif metadata.content_type == ContentType.ASSET_PACK.value:
                self._install_asset_pack(content_data)
            elif metadata.content_type == ContentType.PLUGIN.value:
                self._install_plugin(content_data)
            
            return True
            
        except Exception as e:
            print(f"Error installing content: {e}")
            return False
    
    def _install_template(self, template_data: Dict[str, Any]):
        """Install a template into the current project."""
        if not self.app:
            return
        
        # Clear current project and load template data
        from ..models import DialogueNode, Quest
        
        # Load nodes
        if "nodes" in template_data:
            self.app.nodes.clear()
            for node_id, node_data in template_data["nodes"].items():
                # Create node based on type
                if node_data.get("node_type") == "dialogue":
                    node = DialogueNode.from_dict(node_data)
                    self.app.nodes[node_id] = node
        
        # Load other project data
        self.app.player_stats = template_data.get("player_stats", {})
        self.app.player_inventory = template_data.get("player_inventory", [])
        self.app.story_flags = template_data.get("story_flags", {})
        self.app.variables = template_data.get("variables", {})
        self.app.project_settings = template_data.get("project_settings", {})
        
        # Load quests
        if "quests" in template_data:
            self.app.quests = {
                qid: Quest.from_dict(quest_data)
                for qid, quest_data in template_data["quests"].items()
            }
        
        # Refresh UI
        if hasattr(self.app, 'canvas_manager'):
            self.app.canvas_manager.redraw_all_nodes()
        if hasattr(self.app, 'properties_panel'):
            self.app.properties_panel.update_all_panels()
    
    def _install_asset_pack(self, asset_data: Dict[str, Any]):
        """Install an asset pack."""
        # This would install sprites, backgrounds, sounds, etc.
        # Implementation depends on asset type
        pass
    
    def _install_plugin(self, plugin_data: Dict[str, Any]):
        """Install a plugin."""
        # This would install and activate a plugin
        pass
    
    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get overall marketplace statistics."""
        total_content = len(self.content_catalog)
        total_downloads = sum(content.download_count for content in self.content_catalog.values())
        
        # Content by type
        by_type = {}
        for content in self.content_catalog.values():
            by_type[content.content_type] = by_type.get(content.content_type, 0) + 1
        
        # Content by category
        by_category = {}
        for content in self.content_catalog.values():
            by_category[content.category] = by_category.get(content.category, 0) + 1
        
        return {
            "total_content": total_content,
            "total_downloads": total_downloads,
            "content_by_type": by_type,
            "content_by_category": by_category,
            "featured_count": len(self.featured_content),
            "user_uploads": len(self.get_user_uploads()) if self.current_user else 0,
            "user_downloads": len(self.get_user_downloads()) if self.current_user else 0
        }
    
    def populate_sample_content(self):
        """Populate marketplace with sample content for demonstration."""
        sample_content = [
            ContentMetadata(
                id="template_001",
                title="Fantasy Adventure Template",
                description="A complete template for fantasy adventure games with medieval settings, character stats, and quest system.",
                author_id="sample_author_001",
                author_name="Fantasy Creator",
                content_type=ContentType.TEMPLATE.value,
                category=ContentCategory.FANTASY.value,
                tags=["fantasy", "adventure", "medieval", "quests"],
                rating_average=4.7,
                rating_count=23,
                download_count=156,
                version="2.1.0"
            ),
            ContentMetadata(
                id="sprites_001",
                title="Modern Character Sprites",
                description="Collection of modern character sprites with multiple expressions and poses for contemporary stories.",
                author_id="sample_author_002", 
                author_name="Pixel Artist Pro",
                content_type=ContentType.SPRITE.value,
                category=ContentCategory.MODERN.value,
                tags=["sprites", "characters", "modern", "expressions"],
                rating_average=4.3,
                rating_count=45,
                download_count=289,
                version="1.5.0"
            ),
            ContentMetadata(
                id="backgrounds_001",
                title="Sci-Fi Environments Pack",
                description="High-quality science fiction backgrounds including spaceships, alien worlds, and futuristic cities.",
                author_id="sample_author_003",
                author_name="Sci-Fi Studios",
                content_type=ContentType.BACKGROUND.value,
                category=ContentCategory.SCI_FI.value,
                tags=["backgrounds", "sci-fi", "space", "futuristic"],
                rating_average=4.9,
                rating_count=67,
                download_count=412,
                version="3.0.0"
            )
        ]
        
        for content in sample_content:
            self.content_catalog[content.id] = content
        
        self.featured_content = ["template_001", "backgrounds_001"]
        self._save_local_data()
    
    def export_for_sharing(self) -> Dict[str, Any]:
        """Export marketplace data for sharing between installations."""
        return {
            "content_catalog": {
                cid: content.to_dict()
                for cid, content in self.content_catalog.items()
            },
            "user_ratings": {
                cid: [rating.to_dict() for rating in ratings]
                for cid, ratings in self.user_ratings.items()
            },
            "featured_content": self.featured_content.copy()
        }
    
    def cleanup(self):
        """Clean up resources and save data."""
        self._save_local_data()