"""Core AI Service Infrastructure for DVGE."""

import json
import time
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import threading
from datetime import datetime, timedelta


class AIProviderType(Enum):
    """Supported AI provider types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    MOCK = "mock"  # For testing


@dataclass
class AIRequest:
    """Request for AI content generation."""
    prompt: str
    context: Dict[str, Any] = None
    parameters: Dict[str, Any] = None
    request_type: str = "generate"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.parameters is None:
            self.parameters = {}
    
    def get_cache_key(self) -> str:
        """Generate cache key for this request."""
        cache_data = {
            "prompt": self.prompt,
            "context": self.context,
            "parameters": self.parameters,
            "request_type": self.request_type,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()


@dataclass 
class AIResponse:
    """Response from AI content generation."""
    content: str
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    provider: str = ""
    request_id: str = ""
    cached: bool = False
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.enabled = True
        self.rate_limit_requests = 0
        self.rate_limit_reset = time.time()
        
    @abstractmethod
    async def generate_content(self, request: AIRequest) -> AIResponse:
        """Generate content using this AI provider."""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the provider configuration."""
        pass
    
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured."""
        return self.enabled and self.validate_config()
    
    def check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        current_time = time.time()
        if current_time > self.rate_limit_reset:
            self.rate_limit_requests = 0
            self.rate_limit_reset = current_time + 60  # Reset every minute
        
        max_requests = self.config.get("max_requests_per_minute", 50)
        return self.rate_limit_requests < max_requests
    
    def increment_rate_limit(self):
        """Increment the rate limit counter."""
        self.rate_limit_requests += 1


class AIService:
    """Main AI service that manages providers and handles requests."""
    
    def __init__(self, app):
        self.app = app
        self.providers: Dict[str, AIProvider] = {}
        self.default_provider: Optional[str] = None
        self.cache: Dict[str, tuple] = {}  # cache_key -> (response, timestamp)
        self.cache_ttl = 3600  # 1 hour cache
        self.request_history: List[Dict[str, Any]] = []
        self.max_history = 100
        
        # Initialize default providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize default AI providers."""
        try:
            from .providers import OpenAIProvider, AnthropicProvider, LocalAIProvider, MockAIProvider
            
            # Add providers with default configs
            self.add_provider(OpenAIProvider("openai"))
            self.add_provider(AnthropicProvider("anthropic"))
            self.add_provider(LocalAIProvider("local"))
            self.add_provider(MockAIProvider("mock"))  # For testing
            
            # Set default provider
            self.set_default_provider("mock")  # Safe default for testing
            
        except ImportError as e:
            print(f"Warning: Could not initialize AI providers: {e}")
        
        # Initialize enhanced AI systems
        self._initialize_enhanced_systems()
    
    def _initialize_enhanced_systems(self):
        """Initialize enhanced AI content generation systems."""
        try:
            from .enhanced_generators import create_enhanced_ai_system
            from .contextual_suggestions import create_contextual_assistant
            from .story_templates import create_ai_template_system
            
            # Create enhanced AI systems
            self.enhanced_systems = create_enhanced_ai_system(self)
            self.contextual_assistant = create_contextual_assistant(self)
            self.template_manager = create_ai_template_system(self)
            
            print("Enhanced AI systems initialized successfully")
            
        except ImportError as e:
            print(f"Warning: Could not initialize enhanced AI systems: {e}")
            self.enhanced_systems = None
            self.contextual_assistant = None
            self.template_manager = None
        except Exception as e:
            print(f"Error initializing enhanced AI systems: {e}")
            self.enhanced_systems = None
            self.contextual_assistant = None
            self.template_manager = None
    
    def is_enhanced_ai_available(self) -> bool:
        """Check if enhanced AI systems are available."""
        return (
            hasattr(self, 'enhanced_systems') and 
            self.enhanced_systems is not None and
            hasattr(self, 'contextual_assistant') and 
            self.contextual_assistant is not None
        )
    
    def add_provider(self, provider: AIProvider):
        """Add an AI provider to the service."""
        self.providers[provider.name] = provider
        
        # Set as default if it's the first available provider
        if self.default_provider is None and provider.is_available():
            self.default_provider = provider.name
    
    def remove_provider(self, name: str):
        """Remove an AI provider from the service."""
        if name in self.providers:
            del self.providers[name]
            if self.default_provider == name:
                self.default_provider = None
                # Set new default from available providers
                for provider_name, provider in self.providers.items():
                    if provider.is_available():
                        self.default_provider = provider_name
                        break
    
    def set_default_provider(self, name: str):
        """Set the default AI provider."""
        if name in self.providers and self.providers[name].is_available():
            self.default_provider = name
            return True
        return False
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [name for name, provider in self.providers.items() if provider.is_available()]
    
    def configure_provider(self, name: str, config: Dict[str, Any]):
        """Configure an AI provider."""
        if name in self.providers:
            self.providers[name].config.update(config)
            return True
        return False
    
    async def generate_content(self, request: AIRequest, provider_name: Optional[str] = None) -> AIResponse:
        """Generate content using specified or default provider."""
        # Use specified provider or default
        provider_name = provider_name or self.default_provider
        
        if not provider_name or provider_name not in self.providers:
            return AIResponse(
                content="",
                success=False,
                error="No AI provider available",
                provider="none"
            )
        
        provider = self.providers[provider_name]
        
        if not provider.is_available():
            return AIResponse(
                content="",
                success=False,
                error=f"Provider '{provider_name}' is not available",
                provider=provider_name
            )
        
        # Check cache first
        cache_key = request.get_cache_key()
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            cached_response.cached = True
            return cached_response
        
        # Check rate limits
        if not provider.check_rate_limit():
            return AIResponse(
                content="",
                success=False,
                error="Rate limit exceeded. Please try again later.",
                provider=provider_name
            )
        
        try:
            # Generate content
            response = await provider.generate_content(request)
            response.provider = provider_name
            
            # Increment rate limit
            provider.increment_rate_limit()
            
            # Cache successful responses
            if response.success:
                self._cache_response(cache_key, response)
            
            # Add to history
            self._add_to_history(request, response)
            
            return response
            
        except Exception as e:
            error_response = AIResponse(
                content="",
                success=False,
                error=f"Provider error: {str(e)}",
                provider=provider_name
            )
            self._add_to_history(request, error_response)
            return error_response
    
    def generate_content_sync(self, request: AIRequest, provider_name: Optional[str] = None) -> AIResponse:
        """Synchronous wrapper for generate_content."""
        try:
            # Try to get the current running loop
            try:
                loop = asyncio.get_running_loop()
                # If we're already in an async context, run in thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.generate_content(request, provider_name))
                    return future.result(timeout=30)
            except RuntimeError:
                # No running loop, safe to use asyncio.run
                return asyncio.run(self.generate_content(request, provider_name))
        except Exception:
            # Fallback for any other issues
            return asyncio.run(self.generate_content(request, provider_name))
    
    def _get_cached_response(self, cache_key: str) -> Optional[AIResponse]:
        """Get response from cache if available and not expired."""
        if cache_key in self.cache:
            response, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return response
            else:
                # Remove expired entry
                del self.cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: AIResponse):
        """Cache a response."""
        self.cache[cache_key] = (response, time.time())
        
        # Clean old cache entries if cache is getting large
        if len(self.cache) > 1000:
            self._cleanup_cache()
    
    def _cleanup_cache(self):
        """Clean up expired cache entries."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.cache_ttl
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def _add_to_history(self, request: AIRequest, response: AIResponse):
        """Add request/response to history."""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "request": asdict(request),
            "response": asdict(response)
        }
        
        self.request_history.append(history_entry)
        
        # Keep only the most recent entries
        if len(self.request_history) > self.max_history:
            self.request_history = self.request_history[-self.max_history:]
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        total_requests = len(self.request_history)
        successful_requests = sum(1 for entry in self.request_history if entry["response"]["success"])
        
        provider_usage = {}
        for entry in self.request_history:
            provider = entry["response"]["provider"]
            provider_usage[provider] = provider_usage.get(provider, 0) + 1
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "provider_usage": provider_usage,
            "cache_size": len(self.cache),
            "available_providers": self.get_available_providers(),
            "default_provider": self.default_provider
        }
    
    def clear_cache(self):
        """Clear the response cache."""
        self.cache.clear()
    
    def clear_history(self):
        """Clear the request history."""
        self.request_history.clear()
    
    def export_settings(self) -> Dict[str, Any]:
        """Export AI service settings."""
        return {
            "default_provider": self.default_provider,
            "provider_configs": {
                name: provider.config for name, provider in self.providers.items()
            },
            "cache_ttl": self.cache_ttl,
            "max_history": self.max_history
        }
    
    def import_settings(self, settings: Dict[str, Any]):
        """Import AI service settings."""
        if "default_provider" in settings:
            self.set_default_provider(settings["default_provider"])
        
        if "provider_configs" in settings:
            for name, config in settings["provider_configs"].items():
                self.configure_provider(name, config)
        
        if "cache_ttl" in settings:
            self.cache_ttl = settings["cache_ttl"]
        
        if "max_history" in settings:
            self.max_history = settings["max_history"]