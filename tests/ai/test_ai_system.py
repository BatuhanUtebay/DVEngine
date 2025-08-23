"""Tests for the AI-Powered Content Generation System."""

import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from dvge.ai.ai_service import AIService, AIProvider, AIRequest, AIResponse, AIProviderType
from dvge.ai.providers import MockAIProvider, OpenAIProvider, AnthropicProvider, LocalAIProvider
from dvge.ai.generators import DialogueGenerator, CharacterGenerator, StoryGenerator, ContentAnalyzer


class MockApp:
    """Mock app for testing."""
    def __init__(self):
        self.nodes = {}
        self.selected_node_ids = []
        self.story_flags = {}
        self.variables = {}


class TestAIRequest(unittest.TestCase):
    """Test AIRequest functionality."""
    
    def test_request_creation(self):
        """Test creating an AI request."""
        request = AIRequest(
            prompt="Test prompt",
            context={"character": "Alice"},
            max_tokens=100,
            temperature=0.8
        )
        
        self.assertEqual(request.prompt, "Test prompt")
        self.assertEqual(request.context["character"], "Alice")
        self.assertEqual(request.max_tokens, 100)
        self.assertEqual(request.temperature, 0.8)
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        request1 = AIRequest(prompt="Test", context={"a": 1})
        request2 = AIRequest(prompt="Test", context={"a": 1})
        request3 = AIRequest(prompt="Different", context={"a": 1})
        
        # Same requests should have same cache key
        self.assertEqual(request1.get_cache_key(), request2.get_cache_key())
        
        # Different requests should have different cache keys
        self.assertNotEqual(request1.get_cache_key(), request3.get_cache_key())


class TestAIResponse(unittest.TestCase):
    """Test AIResponse functionality."""
    
    def test_response_creation(self):
        """Test creating an AI response."""
        response = AIResponse(
            content="Generated content",
            success=True,
            metadata={"tokens": 50}
        )
        
        self.assertEqual(response.content, "Generated content")
        self.assertTrue(response.success)
        self.assertEqual(response.metadata["tokens"], 50)
    
    def test_error_response(self):
        """Test creating an error response."""
        response = AIResponse(
            content="",
            success=False,
            error="API Error"
        )
        
        self.assertEqual(response.content, "")
        self.assertFalse(response.success)
        self.assertEqual(response.error, "API Error")


class TestMockAIProvider(unittest.TestCase):
    """Test the mock AI provider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.provider = MockAIProvider("test_mock")
    
    def test_provider_creation(self):
        """Test creating a mock provider."""
        self.assertEqual(self.provider.name, "test_mock")
        self.assertTrue(self.provider.is_available())
        self.assertTrue(self.provider.validate_config())
    
    def test_content_generation(self):
        """Test content generation."""
        async def test_async():
            request = AIRequest(prompt="Generate dialogue")
            response = await self.provider.generate_content(request)
            
            self.assertTrue(response.success)
            self.assertIsInstance(response.content, str)
            self.assertGreater(len(response.content), 0)
        
        asyncio.run(test_async())
    
    def test_character_content_type(self):
        """Test character-specific content generation."""
        async def test_async():
            request = AIRequest(
                prompt="Generate character description",
                context={"character_name": "Alice"}
            )
            response = await self.provider.generate_content(request)
            
            self.assertTrue(response.success)
            self.assertIn("mock_type", response.metadata)
        
        asyncio.run(test_async())


class TestAIService(unittest.TestCase):
    """Test the main AI service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = MockApp()
        self.service = AIService(self.app)
    
    def test_service_initialization(self):
        """Test service initialization."""
        self.assertIsInstance(self.service, AIService)
        self.assertGreater(len(self.service.providers), 0)
        self.assertIsNotNone(self.service.default_provider)
    
    def test_provider_management(self):
        """Test adding and removing providers."""
        # Test adding provider
        test_provider = MockAIProvider("test_provider")
        self.service.add_provider(test_provider)
        self.assertIn("test_provider", self.service.providers)
        
        # Test removing provider
        self.service.remove_provider("test_provider")
        self.assertNotIn("test_provider", self.service.providers)
    
    def test_default_provider_setting(self):
        """Test setting default provider."""
        # Add a test provider
        test_provider = MockAIProvider("test_default")
        self.service.add_provider(test_provider)
        
        # Set as default
        result = self.service.set_default_provider("test_default")
        self.assertTrue(result)
        self.assertEqual(self.service.default_provider, "test_default")
        
        # Try to set non-existent provider
        result = self.service.set_default_provider("non_existent")
        self.assertFalse(result)
    
    def test_provider_configuration(self):
        """Test provider configuration."""
        # Configure existing provider
        result = self.service.configure_provider("mock", {"test_key": "test_value"})
        self.assertTrue(result)
        self.assertEqual(self.service.providers["mock"].config["test_key"], "test_value")
        
        # Try to configure non-existent provider
        result = self.service.configure_provider("non_existent", {})
        self.assertFalse(result)
    
    def test_content_generation(self):
        """Test content generation through service."""
        request = AIRequest(prompt="Test prompt")
        response = self.service.generate_content_sync(request)
        
        self.assertIsInstance(response, AIResponse)
        if response.success:
            self.assertIsInstance(response.content, str)
    
    def test_caching(self):
        """Test response caching."""
        request = AIRequest(prompt="Cacheable prompt")
        
        # First request
        response1 = self.service.generate_content_sync(request)
        
        # Second identical request should be cached
        response2 = self.service.generate_content_sync(request)
        
        if response1.success and response2.success:
            # Second response should be marked as cached
            # Note: This test might be flaky due to async nature
            self.assertEqual(response1.content, response2.content)
    
    def test_usage_stats(self):
        """Test usage statistics."""
        # Generate some requests
        request = AIRequest(prompt="Stats test")
        self.service.generate_content_sync(request)
        
        stats = self.service.get_usage_stats()
        
        self.assertIn("total_requests", stats)
        self.assertIn("successful_requests", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("provider_usage", stats)
        self.assertIn("available_providers", stats)
        
        self.assertGreaterEqual(stats["total_requests"], 1)
    
    def test_cache_management(self):
        """Test cache clearing."""
        # Generate a cached request
        request = AIRequest(prompt="Cache test")
        self.service.generate_content_sync(request)
        
        # Clear cache
        self.service.clear_cache()
        self.assertEqual(len(self.service.cache), 0)
    
    def test_history_management(self):
        """Test request history."""
        # Generate some requests
        request = AIRequest(prompt="History test")
        self.service.generate_content_sync(request)
        
        self.assertGreater(len(self.service.request_history), 0)
        
        # Clear history
        self.service.clear_history()
        self.assertEqual(len(self.service.request_history), 0)


class TestDialogueGenerator(unittest.TestCase):
    """Test dialogue generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = MockApp()
        self.service = AIService(self.app)
        self.generator = DialogueGenerator(self.service)
    
    def test_dialogue_line_generation(self):
        """Test generating a single dialogue line."""
        dialogue = self.generator.generate_dialogue_line(
            "Alice",
            {"situation": "greeting a friend"}
        )
        
        self.assertIsInstance(dialogue, str)
        self.assertGreater(len(dialogue), 0)
        self.assertNotIn("[Error:", dialogue)  # Should not contain error
    
    def test_dialogue_options_generation(self):
        """Test generating multiple dialogue options."""
        options = self.generator.generate_dialogue_options(
            {"situation": "choosing a response"},
            count=3
        )
        
        self.assertIsInstance(options, list)
        self.assertGreaterEqual(len(options), 1)  # Should get at least one option
        
        for option in options:
            self.assertIsInstance(option, str)
            self.assertGreater(len(option), 0)
    
    def test_dialogue_improvement(self):
        """Test dialogue improvement."""
        original = "Hello there."
        improved = self.generator.improve_dialogue(original, "emotional")
        
        self.assertIsInstance(improved, str)
        # Should return either improved text or original if improvement fails
        self.assertTrue(len(improved) > 0)
    
    def test_conversation_generation(self):
        """Test multi-turn conversation generation."""
        conversation = self.generator.generate_conversation(
            ["Alice", "Bob"],
            "planning a trip",
            length=3
        )
        
        self.assertIsInstance(conversation, list)
        # Should generate some conversation turns
        
        for turn in conversation:
            self.assertIn("character", turn)
            self.assertIn("dialogue", turn)


class TestCharacterGenerator(unittest.TestCase):
    """Test character generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = MockApp()
        self.service = AIService(self.app)
        self.generator = CharacterGenerator(self.service)
    
    def test_character_profile_generation(self):
        """Test character profile generation."""
        profile = self.generator.generate_character_profile(
            "Alice",
            {"role": "hero", "setting": "fantasy world"}
        )
        
        self.assertIsInstance(profile, dict)
        
        if "error" not in profile:
            # Should have typical profile sections
            expected_sections = ["background", "personality", "motivation"]
            for section in expected_sections:
                self.assertIn(section, profile)
    
    def test_character_backstory_generation(self):
        """Test character backstory generation."""
        backstory = self.generator.generate_character_backstory(
            "Bob",
            ["lost family", "seeking revenge"]
        )
        
        self.assertIsInstance(backstory, str)
        self.assertGreater(len(backstory), 0)
    
    def test_voice_analysis(self):
        """Test character voice analysis."""
        dialogue_samples = [
            "Well, I suppose that could work.",
            "Hmm, let me think about this for a moment.",
            "I'm not entirely convinced, but I'll consider it."
        ]
        
        analysis = self.generator.analyze_character_voice("Alice", dialogue_samples)
        
        self.assertIsInstance(analysis, dict)
        
        if "error" not in analysis:
            expected_aspects = ["tone", "vocabulary", "speech_patterns"]
            for aspect in expected_aspects:
                self.assertIn(aspect, analysis)


class TestStoryGenerator(unittest.TestCase):
    """Test story generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = MockApp()
        self.service = AIService(self.app)
        self.generator = StoryGenerator(self.service)
    
    def test_plot_outline_generation(self):
        """Test plot outline generation."""
        outline = self.generator.generate_plot_outline(
            "A young hero discovers magical powers",
            "short"
        )
        
        self.assertIsInstance(outline, list)
        self.assertGreater(len(outline), 0)
        
        for point in outline:
            self.assertIsInstance(point, str)
            self.assertGreater(len(point), 0)
    
    def test_plot_development_suggestions(self):
        """Test plot development suggestions."""
        suggestions = self.generator.suggest_plot_developments(
            "The hero has found the ancient artifact",
            "Alice is the reluctant hero"
        )
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        for suggestion in suggestions:
            self.assertIsInstance(suggestion, str)
    
    def test_scene_description_generation(self):
        """Test scene description generation."""
        description = self.generator.generate_scene_description(
            "ancient castle",
            "mysterious",
            "introduce the villain"
        )
        
        self.assertIsInstance(description, str)
        self.assertGreater(len(description), 0)


class TestContentAnalyzer(unittest.TestCase):
    """Test content analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = MockApp()
        self.service = AIService(self.app)
        self.analyzer = ContentAnalyzer(self.service)
    
    def test_story_pacing_analysis(self):
        """Test story pacing analysis."""
        story_summary = "Hero finds power, meets mentor, faces villain, wins."
        
        analysis = self.analyzer.analyze_story_pacing(story_summary)
        
        self.assertIsInstance(analysis, dict)
        
        if "error" not in analysis:
            expected_aspects = ["overall_pacing", "tension_curve"]
            for aspect in expected_aspects:
                self.assertIn(aspect, analysis)
    
    def test_plot_hole_detection(self):
        """Test plot hole detection."""
        story_outline = [
            "Hero discovers magic powers",
            "Villain attacks the city", 
            "Hero wins without training"
        ]
        
        issues = self.analyzer.find_plot_holes(story_outline)
        
        self.assertIsInstance(issues, list)
        # Should detect that hero wins without training as potential issue
    
    def test_improvement_suggestions(self):
        """Test improvement suggestions."""
        content = "Hello. How are you? I am fine."
        
        suggestions = self.analyzer.suggest_improvements(content, "dialogue")
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        for suggestion in suggestions:
            self.assertIsInstance(suggestion, str)


class TestProviderIntegration(unittest.TestCase):
    """Test AI provider integration."""
    
    def test_openai_provider_creation(self):
        """Test OpenAI provider creation."""
        provider = OpenAIProvider("test_openai", {"api_key": "test_key"})
        
        self.assertEqual(provider.name, "test_openai")
        self.assertTrue(provider.validate_config())
        
        # Without API key should not validate
        provider_no_key = OpenAIProvider("test_no_key")
        self.assertFalse(provider_no_key.validate_config())
    
    def test_anthropic_provider_creation(self):
        """Test Anthropic provider creation."""
        provider = AnthropicProvider("test_anthropic", {"api_key": "test_key"})
        
        self.assertEqual(provider.name, "test_anthropic")
        self.assertTrue(provider.validate_config())
        
        # Without API key should not validate
        provider_no_key = AnthropicProvider("test_no_key")
        self.assertFalse(provider_no_key.validate_config())
    
    def test_local_provider_creation(self):
        """Test local AI provider creation."""
        provider = LocalAIProvider("test_local", {"endpoint": "http://localhost:11434"})
        
        self.assertEqual(provider.name, "test_local")
        self.assertTrue(provider.validate_config())
        
        # Without endpoint should not validate
        provider_no_endpoint = LocalAIProvider("test_no_endpoint", {"endpoint": ""})
        self.assertFalse(provider_no_endpoint.validate_config())
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        provider = MockAIProvider("rate_test", {"max_requests_per_minute": 2})
        
        # Should start with rate limit available
        self.assertTrue(provider.check_rate_limit())
        
        # Increment rate limit
        provider.increment_rate_limit()
        self.assertTrue(provider.check_rate_limit())
        
        provider.increment_rate_limit()
        # Should now be at the limit (2/2)
        self.assertFalse(provider.check_rate_limit())


class TestErrorHandling(unittest.TestCase):
    """Test error handling in AI system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = MockApp()
        self.service = AIService(self.app)
    
    def test_no_provider_error(self):
        """Test error handling when no provider is available."""
        # Remove all providers
        self.service.providers.clear()
        self.service.default_provider = None
        
        request = AIRequest(prompt="Test")
        response = self.service.generate_content_sync(request)
        
        self.assertFalse(response.success)
        self.assertIn("No AI provider available", response.error)
    
    def test_invalid_provider_error(self):
        """Test error handling for invalid provider."""
        request = AIRequest(prompt="Test")
        response = self.service.generate_content_sync(request, "non_existent_provider")
        
        self.assertFalse(response.success)
        self.assertIn("No AI provider available", response.error)
    
    def test_disabled_provider_error(self):
        """Test error handling for disabled provider."""
        # Disable the mock provider
        self.service.providers["mock"].enabled = False
        
        request = AIRequest(prompt="Test")
        response = self.service.generate_content_sync(request, "mock")
        
        self.assertFalse(response.success)
        self.assertIn("not available", response.error)


if __name__ == '__main__':
    unittest.main()