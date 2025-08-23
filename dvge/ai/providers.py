"""AI Provider Implementations for DVGE."""

import asyncio
import json
import random
import time
from typing import Dict, Any, Optional
from .ai_service import AIProvider, AIRequest, AIResponse


class MockAIProvider(AIProvider):
    """Mock AI provider for testing and demonstration purposes."""
    
    def __init__(self, name: str = "mock", config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.responses = {
            "dialogue": [
                "That's an interesting perspective. What makes you think that?",
                "I understand your concerns, but have you considered the alternatives?",
                "Perhaps we should look at this from a different angle.",
                "Your experience with this situation has been quite unique.",
                "Let me share what I've learned about similar circumstances."
            ],
            "character": [
                "A mysterious figure with a hidden past and noble intentions.",
                "A skilled artisan who values tradition but embraces innovation.",
                "An optimistic explorer driven by curiosity and wonder.",
                "A wise mentor carrying the weight of difficult decisions.",
                "A determined individual fighting for what they believe is right."
            ],
            "story": [
                "The discovery of an ancient artifact sets off a chain of unexpected events.",
                "A long-forgotten alliance resurfaces when the kingdom faces its darkest hour.",
                "The protagonist must choose between personal happiness and duty to others.",
                "A mysterious stranger arrives with knowledge that could change everything.",
                "The truth about the past emerges, challenging everything believed to be true."
            ]
        }
    
    def validate_config(self) -> bool:
        """Mock provider is always valid."""
        return True
    
    async def generate_content(self, request: AIRequest) -> AIResponse:
        """Generate mock content based on request type."""
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Determine content type from request
        content_type = "dialogue"
        if "character" in request.prompt.lower():
            content_type = "character"
        elif "story" in request.prompt.lower() or "plot" in request.prompt.lower():
            content_type = "story"
        
        # Generate mock response
        responses = self.responses.get(content_type, self.responses["dialogue"])
        content = random.choice(responses)
        
        # Add some variation based on context
        if request.context.get("character_name"):
            content = f"[{request.context['character_name']}]: {content}"
        
        return AIResponse(
            content=content,
            success=True,
            metadata={
                "mock_type": content_type,
                "simulated_tokens": len(content.split()),
                "simulated_cost": 0.001
            }
        )


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider for AI content generation."""
    
    def __init__(self, name: str = "openai", config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.api_key = self.config.get("api_key", "")
        self.model = self.config.get("model", "gpt-3.5-turbo")
        self.base_url = self.config.get("base_url", "https://api.openai.com/v1")
    
    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        return bool(self.api_key)
    
    async def generate_content(self, request: AIRequest) -> AIResponse:
        """Generate content using OpenAI API."""
        if not self.validate_config():
            return AIResponse(
                content="",
                success=False,
                error="OpenAI API key not configured"
            )
        
        try:
            # Try to import openai
            try:
                import openai
            except ImportError:
                return AIResponse(
                    content="",
                    success=False,
                    error="OpenAI library not installed. Run: pip install openai"
                )
            
            # Configure client
            client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            # Build messages
            messages = []
            
            # Add system context if available
            if request.context:
                system_prompt = self._build_system_prompt(request.context)
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
            
            # Add user prompt
            messages.append({"role": "user", "content": request.prompt})
            
            # Make API call
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                **request.parameters
            )
            
            # Extract content
            content = response.choices[0].message.content
            
            return AIResponse(
                content=content,
                success=True,
                metadata={
                    "model": self.model,
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                    "finish_reason": response.choices[0].finish_reason
                }
            )
            
        except Exception as e:
            return AIResponse(
                content="",
                success=False,
                error=f"OpenAI API error: {str(e)}"
            )
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt from context."""
        parts = []
        
        if context.get("project_name"):
            parts.append(f"You are helping with a game project called '{context['project_name']}'.")
        
        if context.get("character_name"):
            parts.append(f"Focus on the character '{context['character_name']}'.")
        
        if context.get("scene_description"):
            parts.append(f"Current scene: {context['scene_description']}")
        
        if context.get("writing_style"):
            parts.append(f"Writing style: {context['writing_style']}")
        
        parts.append("Generate content that is creative, engaging, and appropriate for the context.")
        
        return " ".join(parts)


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider for AI content generation."""
    
    def __init__(self, name: str = "anthropic", config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.api_key = self.config.get("api_key", "")
        self.model = self.config.get("model", "claude-3-haiku-20240307")
        self.base_url = self.config.get("base_url", "https://api.anthropic.com")
    
    def validate_config(self) -> bool:
        """Validate Anthropic configuration."""
        return bool(self.api_key)
    
    async def generate_content(self, request: AIRequest) -> AIResponse:
        """Generate content using Anthropic API."""
        if not self.validate_config():
            return AIResponse(
                content="",
                success=False,
                error="Anthropic API key not configured"
            )
        
        try:
            # Try to import anthropic
            try:
                import anthropic
            except ImportError:
                return AIResponse(
                    content="",
                    success=False,
                    error="Anthropic library not installed. Run: pip install anthropic"
                )
            
            # Configure client
            client = anthropic.AsyncAnthropic(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            # Build system prompt
            system_prompt = ""
            if request.context:
                system_prompt = self._build_system_prompt(request.context)
            
            # Make API call
            response = await client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=[{"role": "user", "content": request.prompt}],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                **request.parameters
            )
            
            # Extract content
            content = response.content[0].text
            
            return AIResponse(
                content=content,
                success=True,
                metadata={
                    "model": self.model,
                    "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                    "stop_reason": response.stop_reason
                }
            )
            
        except Exception as e:
            return AIResponse(
                content="",
                success=False,
                error=f"Anthropic API error: {str(e)}"
            )
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt from context."""
        parts = []
        
        parts.append("You are an AI assistant helping with game development and creative writing.")
        
        if context.get("project_name"):
            parts.append(f"You are working on a game project called '{context['project_name']}'.")
        
        if context.get("character_name"):
            parts.append(f"Focus on the character '{context['character_name']}'.")
        
        if context.get("scene_description"):
            parts.append(f"Current scene context: {context['scene_description']}")
        
        if context.get("writing_style"):
            parts.append(f"Match this writing style: {context['writing_style']}")
        
        parts.append("Provide creative, engaging, and contextually appropriate content.")
        
        return " ".join(parts)


class LocalAIProvider(AIProvider):
    """Local AI provider for offline content generation."""
    
    def __init__(self, name: str = "local", config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.model_path = self.config.get("model_path", "")
        self.endpoint = self.config.get("endpoint", "http://localhost:11434")  # Ollama default
        self.model_name = self.config.get("model_name", "llama2")
    
    def validate_config(self) -> bool:
        """Validate local AI configuration."""
        # Check if endpoint is configured and not empty
        return bool(self.endpoint and self.endpoint.strip())
    
    async def generate_content(self, request: AIRequest) -> AIResponse:
        """Generate content using local AI model."""
        try:
            # Try to use ollama if available
            try:
                import ollama
                
                # Build prompt with context
                full_prompt = request.prompt
                if request.context:
                    context_str = self._build_context_string(request.context)
                    full_prompt = f"{context_str}\n\n{request.prompt}"
                
                # Make request to local model
                response = await ollama.AsyncClient().generate(
                    model=self.model_name,
                    prompt=full_prompt,
                    options={
                        'temperature': request.temperature,
                        'num_predict': request.max_tokens,
                        **request.parameters
                    }
                )
                
                return AIResponse(
                    content=response['response'],
                    success=True,
                    metadata={
                        "model": self.model_name,
                        "local": True,
                        "eval_count": response.get('eval_count', 0)
                    }
                )
                
            except ImportError:
                # Fallback to HTTP request if ollama library not available
                import aiohttp
                
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": self.model_name,
                        "prompt": request.prompt,
                        "stream": False,
                        "options": {
                            "temperature": request.temperature,
                            "num_predict": request.max_tokens
                        }
                    }
                    
                    async with session.post(
                        f"{self.endpoint}/api/generate",
                        json=payload,
                        timeout=30
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return AIResponse(
                                content=data.get('response', ''),
                                success=True,
                                metadata={
                                    "model": self.model_name,
                                    "local": True,
                                    "endpoint": self.endpoint
                                }
                            )
                        else:
                            return AIResponse(
                                content="",
                                success=False,
                                error=f"Local AI server error: {response.status}"
                            )
            
        except Exception as e:
            return AIResponse(
                content="",
                success=False,
                error=f"Local AI error: {str(e)}"
            )
    
    def _build_context_string(self, context: Dict[str, Any]) -> str:
        """Build context string for local model."""
        parts = []
        
        if context.get("project_name"):
            parts.append(f"Game Project: {context['project_name']}")
        
        if context.get("character_name"):
            parts.append(f"Character: {context['character_name']}")
        
        if context.get("scene_description"):
            parts.append(f"Scene: {context['scene_description']}")
        
        if context.get("writing_style"):
            parts.append(f"Style: {context['writing_style']}")
        
        return "Context: " + ", ".join(parts) if parts else ""


# Provider registry for easy access
PROVIDER_CLASSES = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "local": LocalAIProvider,
    "mock": MockAIProvider
}


def create_provider(provider_type: str, name: str = None, config: Dict[str, Any] = None) -> Optional[AIProvider]:
    """Factory function to create AI providers."""
    if provider_type in PROVIDER_CLASSES:
        provider_class = PROVIDER_CLASSES[provider_type]
        return provider_class(name or provider_type, config)
    return None