# dvge/ai/tts_providers.py

"""Text-to-Speech providers for the Voice Acting Pipeline."""

import os
import abc
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json


class TTSProvider(abc.ABC):
    """Abstract base class for TTS providers."""
    
    def __init__(self, name: str):
        self.name = name
        self.is_configured = False
        self._rate_limit_calls = []
        self.max_calls_per_minute = 60
    
    @abc.abstractmethod
    def configure(self, config: Dict[str, Any]) -> bool:
        """Configure the provider with API keys and settings."""
        pass
    
    @abc.abstractmethod
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices from this provider."""
        pass
    
    @abc.abstractmethod
    def synthesize_speech(self, text: str, voice_id: str, 
                         output_path: str, **kwargs) -> bool:
        """Synthesize speech from text using specified voice."""
        pass
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        current_time = time.time()
        
        # Remove calls older than 1 minute
        self._rate_limit_calls = [
            call_time for call_time in self._rate_limit_calls
            if current_time - call_time < 60
        ]
        
        if len(self._rate_limit_calls) >= self.max_calls_per_minute:
            return False
        
        self._rate_limit_calls.append(current_time)
        return True
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": self.name,
            "is_configured": self.is_configured,
            "rate_limit": self.max_calls_per_minute,
            "current_usage": len(self._rate_limit_calls)
        }


class OpenAITTSProvider(TTSProvider):
    """OpenAI TTS provider."""
    
    def __init__(self):
        super().__init__("OpenAI TTS")
        self.client = None
        self.max_calls_per_minute = 50  # Conservative limit
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """Configure OpenAI TTS with API key."""
        try:
            import openai
            api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                return False
            
            self.client = openai.OpenAI(api_key=api_key)
            
            # Test configuration
            self.get_available_voices()
            self.is_configured = True
            return True
            
        except Exception as e:
            print(f"Failed to configure OpenAI TTS: {e}")
            return False
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get available OpenAI voices."""
        if not self.client:
            return []
        
        return [
            {"id": "alloy", "name": "Alloy", "gender": "neutral", "language": "en"},
            {"id": "echo", "name": "Echo", "gender": "male", "language": "en"},
            {"id": "fable", "name": "Fable", "gender": "neutral", "language": "en"},
            {"id": "onyx", "name": "Onyx", "gender": "male", "language": "en"},
            {"id": "nova", "name": "Nova", "gender": "female", "language": "en"},
            {"id": "shimmer", "name": "Shimmer", "gender": "female", "language": "en"},
        ]
    
    def synthesize_speech(self, text: str, voice_id: str, 
                         output_path: str, **kwargs) -> bool:
        """Synthesize speech using OpenAI TTS."""
        if not self.client or not self._check_rate_limit():
            return False
        
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice_id,
                input=text[:4096],  # OpenAI limit
                response_format="wav"
            )
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return True
            
        except Exception as e:
            print(f"OpenAI TTS synthesis failed: {e}")
            return False


class AzureTTSProvider(TTSProvider):
    """Azure Cognitive Services TTS provider."""
    
    def __init__(self):
        super().__init__("Azure TTS")
        self.subscription_key = None
        self.region = None
        self.max_calls_per_minute = 200  # Azure limit
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """Configure Azure TTS."""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            self.subscription_key = config.get("subscription_key") or os.getenv("AZURE_SPEECH_KEY")
            self.region = config.get("region") or os.getenv("AZURE_SPEECH_REGION", "eastus")
            
            if not self.subscription_key:
                return False
            
            # Test configuration
            speech_config = speechsdk.SpeechConfig(
                subscription=self.subscription_key, 
                region=self.region
            )
            
            self.is_configured = True
            return True
            
        except Exception as e:
            print(f"Failed to configure Azure TTS: {e}")
            return False
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get available Azure voices (subset)."""
        if not self.is_configured:
            return []
        
        return [
            {"id": "en-US-AriaNeural", "name": "Aria (Neural)", "gender": "female", "language": "en-US"},
            {"id": "en-US-JennyNeural", "name": "Jenny (Neural)", "gender": "female", "language": "en-US"},
            {"id": "en-US-GuyNeural", "name": "Guy (Neural)", "gender": "male", "language": "en-US"},
            {"id": "en-US-DavisNeural", "name": "Davis (Neural)", "gender": "male", "language": "en-US"},
            {"id": "en-US-AmberNeural", "name": "Amber (Neural)", "gender": "female", "language": "en-US"},
            {"id": "en-US-AnaNeural", "name": "Ana (Neural)", "gender": "female", "language": "en-US"},
            {"id": "en-US-AndrewNeural", "name": "Andrew (Neural)", "gender": "male", "language": "en-US"},
            {"id": "en-US-EmmaNeural", "name": "Emma (Neural)", "gender": "female", "language": "en-US"},
            {"id": "en-US-BrianNeural", "name": "Brian (Neural)", "gender": "male", "language": "en-US"},
        ]
    
    def synthesize_speech(self, text: str, voice_id: str, 
                         output_path: str, **kwargs) -> bool:
        """Synthesize speech using Azure TTS."""
        if not self.is_configured or not self._check_rate_limit():
            return False
        
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            speech_config = speechsdk.SpeechConfig(
                subscription=self.subscription_key, 
                region=self.region
            )
            speech_config.speech_synthesis_voice_name = voice_id
            speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
            )
            
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=speechsdk.audio.AudioOutputConfig(filename=output_path)
            )
            
            # Add emotion support through SSML if specified
            emotion = kwargs.get("emotion", "neutral")
            if emotion != "neutral":
                ssml_text = f"""
                <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
                    <voice name="{voice_id}">
                        <mstts:express-as style="{emotion}">
                            {text}
                        </mstts:express-as>
                    </voice>
                </speak>
                """
                result = synthesizer.speak_ssml(ssml_text)
            else:
                result = synthesizer.speak_text(text)
            
            return result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted
            
        except Exception as e:
            print(f"Azure TTS synthesis failed: {e}")
            return False


class GoogleTTSProvider(TTSProvider):
    """Google Cloud Text-to-Speech provider."""
    
    def __init__(self):
        super().__init__("Google TTS")
        self.client = None
        self.max_calls_per_minute = 1000  # Google limit
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """Configure Google TTS."""
        try:
            from google.cloud import texttospeech
            
            # Google uses service account JSON file or environment variable
            credentials_path = config.get("credentials_path") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            
            if credentials_path and Path(credentials_path).exists():
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            
            self.client = texttospeech.TextToSpeechClient()
            
            # Test configuration
            self.get_available_voices()
            self.is_configured = True
            return True
            
        except Exception as e:
            print(f"Failed to configure Google TTS: {e}")
            return False
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get available Google voices (subset)."""
        if not self.client:
            return []
        
        try:
            response = self.client.list_voices()
            voices = []
            
            # Filter for English voices only
            for voice in response.voices:
                if voice.language_codes[0].startswith('en'):
                    voices.append({
                        "id": voice.name,
                        "name": voice.name,
                        "gender": voice.ssml_gender.name.lower(),
                        "language": voice.language_codes[0]
                    })
            
            return voices[:20]  # Limit to first 20 for UI
            
        except Exception as e:
            print(f"Failed to get Google voices: {e}")
            return []
    
    def synthesize_speech(self, text: str, voice_id: str, 
                         output_path: str, **kwargs) -> bool:
        """Synthesize speech using Google TTS."""
        if not self.client or not self._check_rate_limit():
            return False
        
        try:
            from google.cloud import texttospeech
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                name=voice_id,
                language_code="en-US"
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16
            )
            
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            with open(output_path, 'wb') as f:
                f.write(response.audio_content)
            
            return True
            
        except Exception as e:
            print(f"Google TTS synthesis failed: {e}")
            return False


class MockTTSProvider(TTSProvider):
    """Mock TTS provider for testing."""
    
    def __init__(self):
        super().__init__("Mock TTS")
        self.is_configured = True
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """Mock configuration always succeeds."""
        return True
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get mock voices for testing."""
        return [
            {"id": "mock_male", "name": "Mock Male", "gender": "male", "language": "en"},
            {"id": "mock_female", "name": "Mock Female", "gender": "female", "language": "en"},
            {"id": "mock_neutral", "name": "Mock Neutral", "gender": "neutral", "language": "en"},
        ]
    
    def synthesize_speech(self, text: str, voice_id: str, 
                         output_path: str, **kwargs) -> bool:
        """Create a mock audio file."""
        try:
            # Create a minimal WAV file header (44 bytes) + 1 second of silence
            sample_rate = 16000
            duration = 1  # 1 second
            num_samples = sample_rate * duration
            
            with open(output_path, 'wb') as f:
                # WAV header
                f.write(b'RIFF')
                f.write((36 + num_samples * 2).to_bytes(4, 'little'))
                f.write(b'WAVE')
                f.write(b'fmt ')
                f.write((16).to_bytes(4, 'little'))
                f.write((1).to_bytes(2, 'little'))  # PCM
                f.write((1).to_bytes(2, 'little'))  # Mono
                f.write(sample_rate.to_bytes(4, 'little'))
                f.write((sample_rate * 2).to_bytes(4, 'little'))
                f.write((2).to_bytes(2, 'little'))
                f.write((16).to_bytes(2, 'little'))
                f.write(b'data')
                f.write((num_samples * 2).to_bytes(4, 'little'))
                
                # Silent audio data
                f.write(b'\x00' * (num_samples * 2))
            
            return True
            
        except Exception as e:
            print(f"Mock TTS failed: {e}")
            return False


class TTSProviderManager:
    """Manages multiple TTS providers."""
    
    def __init__(self):
        self.providers: Dict[str, TTSProvider] = {}
        self.config_file = Path.home() / ".dvge" / "tts_config.json"
        
        # Initialize providers
        self._initialize_providers()
        self._load_configurations()
    
    def _initialize_providers(self):
        """Initialize all available TTS providers."""
        self.providers = {
            "openai": OpenAITTSProvider(),
            "azure": AzureTTSProvider(),
            "google": GoogleTTSProvider(),
            "mock": MockTTSProvider()  # Always available for testing
        }
    
    def _load_configurations(self):
        """Load provider configurations from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    configs = json.load(f)
                
                for provider_name, config in configs.items():
                    if provider_name in self.providers:
                        self.providers[provider_name].configure(config)
                        
        except Exception as e:
            print(f"Error loading TTS configurations: {e}")
    
    def save_configurations(self):
        """Save provider configurations to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            configs = {}
            # Note: We don't save actual API keys, just configuration flags
            for name, provider in self.providers.items():
                if provider.is_configured and name != "mock":
                    configs[name] = {"configured": True}
            
            with open(self.config_file, 'w') as f:
                json.dump(configs, f, indent=2)
                
        except Exception as e:
            print(f"Error saving TTS configurations: {e}")
    
    def configure_provider(self, provider_name: str, config: Dict[str, Any]) -> bool:
        """Configure a specific provider."""
        if provider_name not in self.providers:
            return False
        
        success = self.providers[provider_name].configure(config)
        if success:
            self.save_configurations()
        return success
    
    def get_available_providers(self) -> List[str]:
        """Get list of configured providers."""
        return [
            name for name, provider in self.providers.items()
            if provider.is_configured
        ]
    
    def get_provider(self, provider_name: str) -> Optional[TTSProvider]:
        """Get a specific provider."""
        return self.providers.get(provider_name)
    
    def get_all_voices(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get voices from all configured providers."""
        all_voices = {}
        
        for name, provider in self.providers.items():
            if provider.is_configured:
                voices = provider.get_available_voices()
                all_voices[name] = voices
        
        return all_voices
    
    def generate_speech(self, text: str, voice_profile, 
                       output_path: str, emotion: str = "neutral") -> bool:
        """Generate speech using the appropriate provider."""
        provider = self.providers.get(voice_profile.provider)
        
        if not provider or not provider.is_configured:
            # Fall back to mock provider for testing
            provider = self.providers["mock"]
        
        return provider.synthesize_speech(
            text=text,
            voice_id=voice_profile.voice_id,
            output_path=output_path,
            emotion=emotion,
            speed=voice_profile.speed,
            pitch=voice_profile.pitch,
            volume=voice_profile.volume
        )
    
    def get_provider_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all providers."""
        return {
            name: provider.get_provider_info()
            for name, provider in self.providers.items()
        }
    
    def cleanup(self):
        """Clean up all providers."""
        self.save_configurations()
        # Individual providers can implement cleanup if needed