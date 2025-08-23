"""AI Content Generators for DVGE."""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from .ai_service import AIService, AIRequest, AIResponse


class DialogueGenerator:
    """Generate dialogue content using AI."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    def generate_dialogue_line(self, character_name: str, context: Dict[str, Any] = None) -> str:
        """Generate a single dialogue line for a character."""
        context = context or {}
        
        prompt = f"Generate a dialogue line for the character '{character_name}'."
        
        if context.get("situation"):
            prompt += f" The situation is: {context['situation']}"
        
        if context.get("mood"):
            prompt += f" The character's mood is: {context['mood']}"
        
        if context.get("previous_dialogue"):
            prompt += f" This is in response to: \"{context['previous_dialogue']}\""
        
        prompt += " Generate only the dialogue line without any additional formatting or context."
        
        request = AIRequest(
            prompt=prompt,
            context={
                "character_name": character_name,
                "project_name": context.get("project_name", ""),
                **context
            },
            max_tokens=100,
            temperature=0.8
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            # Clean up the response
            dialogue = response.content.strip()
            # Remove quotes if present
            dialogue = re.sub(r'^["\']|["\']$', '', dialogue)
            # Remove character name prefix if present
            dialogue = re.sub(f'^{re.escape(character_name)}:?\\s*', '', dialogue, flags=re.IGNORECASE)
            return dialogue
        
        return f"[Error: {response.error}]"
    
    def generate_dialogue_options(self, context: Dict[str, Any] = None, count: int = 3) -> List[str]:
        """Generate multiple dialogue options for player choices."""
        context = context or {}
        
        prompt = f"Generate {count} different dialogue options for a player character to choose from."
        
        if context.get("situation"):
            prompt += f" The situation is: {context['situation']}"
        
        if context.get("character_talking_to"):
            prompt += f" The player is talking to: {context['character_talking_to']}"
        
        if context.get("player_goal"):
            prompt += f" The player's goal is: {context['player_goal']}"
        
        prompt += f" Return exactly {count} options, each on a separate line, numbered 1-{count}."
        
        request = AIRequest(
            prompt=prompt,
            context=context,
            max_tokens=200,
            temperature=0.9
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            # Parse numbered options
            lines = response.content.strip().split('\n')
            options = []
            for line in lines:
                # Remove numbering and clean up
                clean_line = re.sub(r'^\d+[.)]\s*', '', line.strip())
                if clean_line:
                    options.append(clean_line)
            
            return options[:count]  # Ensure we don't exceed requested count
        
        return [f"[Error: {response.error}]"]
    
    def improve_dialogue(self, original_dialogue: str, improvement_type: str = "general") -> str:
        """Improve existing dialogue."""
        improvement_prompts = {
            "general": "Improve this dialogue to make it more engaging and natural",
            "concise": "Make this dialogue more concise while preserving its meaning",
            "emotional": "Add more emotional depth to this dialogue",
            "formal": "Make this dialogue more formal and polite",
            "casual": "Make this dialogue more casual and conversational",
            "dramatic": "Add more dramatic tension to this dialogue"
        }
        
        base_prompt = improvement_prompts.get(improvement_type, improvement_prompts["general"])
        prompt = f"{base_prompt}: \"{original_dialogue}\"\n\nProvide only the improved dialogue without any additional formatting or explanation."
        
        request = AIRequest(
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            improved = response.content.strip()
            # Remove quotes if present
            improved = re.sub(r'^["\']|["\']$', '', improved)
            return improved
        
        return original_dialogue  # Return original if improvement fails
    
    def generate_conversation(self, participants: List[str], topic: str, length: int = 5) -> List[Dict[str, str]]:
        """Generate a multi-turn conversation between characters."""
        prompt = f"Generate a {length}-turn conversation between {', '.join(participants)} about '{topic}'."
        prompt += f" Format each line as 'Character: dialogue'. Make it natural and engaging."
        
        request = AIRequest(
            prompt=prompt,
            context={"participants": participants, "topic": topic},
            max_tokens=300,
            temperature=0.8
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        conversation = []
        if response.success:
            lines = response.content.strip().split('\n')
            for line in lines:
                if ':' in line:
                    character, dialogue = line.split(':', 1)
                    conversation.append({
                        "character": character.strip(),
                        "dialogue": dialogue.strip()
                    })
        
        return conversation


class CharacterGenerator:
    """Generate character-related content using AI."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    def generate_character_profile(self, character_name: str, context: Dict[str, Any] = None) -> Dict[str, str]:
        """Generate a comprehensive character profile."""
        context = context or {}
        
        prompt = f"Create a detailed character profile for '{character_name}'."
        
        if context.get("role"):
            prompt += f" Their role is: {context['role']}"
        
        if context.get("setting"):
            prompt += f" The setting is: {context['setting']}"
        
        prompt += """ Include the following sections:
        - Background: Their history and origins
        - Personality: Key personality traits and characteristics
        - Motivation: What drives them and their goals
        - Relationships: How they relate to others
        - Appearance: Physical description
        - Speech: How they talk and express themselves"""
        
        request = AIRequest(
            prompt=prompt,
            context={"character_name": character_name, **context},
            max_tokens=500,
            temperature=0.7
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            # Parse the profile into sections
            profile = self._parse_character_profile(response.content)
            return profile
        
        return {"error": response.error}
    
    def analyze_character_voice(self, character_name: str, dialogue_samples: List[str]) -> Dict[str, Any]:
        """Analyze a character's voice and speaking patterns."""
        samples_text = "\n".join([f"- {sample}" for sample in dialogue_samples])
        
        prompt = f"""Analyze the speaking voice and patterns of '{character_name}' based on these dialogue samples:

{samples_text}

Provide analysis in these categories:
- Tone: Overall tone and attitude
- Vocabulary: Word choice and complexity
- Speech Patterns: How they structure sentences
- Personality Indicators: What their speech reveals about their personality
- Consistency: How consistent their voice is across samples"""
        
        request = AIRequest(
            prompt=prompt,
            context={"character_name": character_name},
            max_tokens=400,
            temperature=0.5
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            analysis = self._parse_voice_analysis(response.content)
            return analysis
        
        return {"error": response.error}
    
    def generate_character_backstory(self, character_name: str, key_points: List[str] = None) -> str:
        """Generate a character backstory."""
        prompt = f"Create an engaging backstory for the character '{character_name}'."
        
        if key_points:
            prompt += f" Include these key elements: {', '.join(key_points)}"
        
        prompt += " Make it 2-3 paragraphs that explain their origins, formative experiences, and how they became who they are today."
        
        request = AIRequest(
            prompt=prompt,
            context={"character_name": character_name},
            max_tokens=300,
            temperature=0.8
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        return response.content if response.success else f"Error: {response.error}"
    
    def _parse_character_profile(self, content: str) -> Dict[str, str]:
        """Parse character profile content into sections."""
        sections = {
            "background": "",
            "personality": "",
            "motivation": "",
            "relationships": "",
            "appearance": "",
            "speech": ""
        }
        
        # Simple parsing - look for section headers
        current_section = None
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a section header
            for section in sections.keys():
                if section.lower() in line.lower() and ':' in line:
                    current_section = section
                    # Extract content after the colon
                    _, content_part = line.split(':', 1)
                    sections[section] = content_part.strip()
                    break
            else:
                # Add to current section
                if current_section:
                    if sections[current_section]:
                        sections[current_section] += " " + line
                    else:
                        sections[current_section] = line
        
        return sections
    
    def _parse_voice_analysis(self, content: str) -> Dict[str, Any]:
        """Parse voice analysis content."""
        analysis = {
            "tone": "",
            "vocabulary": "",
            "speech_patterns": "",
            "personality_indicators": "",
            "consistency": "",
            "overall_score": 0
        }
        
        # Simple parsing similar to character profile
        current_section = None
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            for key in analysis.keys():
                section_name = key.replace('_', ' ')
                if section_name.lower() in line.lower() and ':' in line:
                    current_section = key
                    _, content_part = line.split(':', 1)
                    analysis[key] = content_part.strip()
                    break
            else:
                if current_section and current_section != "overall_score":
                    if analysis[current_section]:
                        analysis[current_section] += " " + line
                    else:
                        analysis[current_section] = line
        
        return analysis


class StoryGenerator:
    """Generate story and plot content using AI."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    def generate_plot_outline(self, premise: str, length: str = "short") -> List[str]:
        """Generate a plot outline based on a premise."""
        length_specs = {
            "short": "3-5 major plot points",
            "medium": "7-10 major plot points", 
            "long": "12-15 major plot points"
        }
        
        spec = length_specs.get(length, length_specs["short"])
        
        prompt = f"""Create a plot outline with {spec} for this premise: {premise}
        
Format each plot point as a numbered list item. Focus on major story beats and character development moments."""
        
        request = AIRequest(
            prompt=prompt,
            max_tokens=400,
            temperature=0.7
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            # Parse numbered list
            lines = response.content.strip().split('\n')
            plot_points = []
            for line in lines:
                clean_line = re.sub(r'^\d+[.)]\s*', '', line.strip())
                if clean_line:
                    plot_points.append(clean_line)
            return plot_points
        
        return [f"Error: {response.error}"]
    
    def suggest_plot_developments(self, current_situation: str, character_context: str = "") -> List[str]:
        """Suggest possible plot developments from the current situation."""
        prompt = f"Given this current situation: {current_situation}"
        
        if character_context:
            prompt += f"\nCharacter context: {character_context}"
        
        prompt += "\n\nSuggest 3-5 possible plot developments or story directions. Each should be a compelling next step that creates tension or advances the story."
        
        request = AIRequest(
            prompt=prompt,
            max_tokens=300,
            temperature=0.8
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            # Parse suggestions
            lines = response.content.strip().split('\n')
            suggestions = []
            for line in lines:
                clean_line = re.sub(r'^\d+[.)]\s*[-•]\s*', '', line.strip())
                if clean_line and len(clean_line) > 10:  # Filter out very short lines
                    suggestions.append(clean_line)
            return suggestions
        
        return [f"Error: {response.error}"]
    
    def generate_scene_description(self, location: str, mood: str = "", purpose: str = "") -> str:
        """Generate a scene description for a location."""
        prompt = f"Describe the scene at: {location}"
        
        if mood:
            prompt += f" The mood should be: {mood}"
        
        if purpose:
            prompt += f" This scene is meant to: {purpose}"
        
        prompt += " Create a vivid, immersive description that sets the atmosphere."
        
        request = AIRequest(
            prompt=prompt,
            max_tokens=200,
            temperature=0.8
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        return response.content if response.success else f"Error: {response.error}"


class ContentAnalyzer:
    """Analyze existing content for improvements and insights."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    def analyze_story_pacing(self, story_summary: str) -> Dict[str, Any]:
        """Analyze the pacing of a story."""
        prompt = f"""Analyze the pacing of this story summary: {story_summary}

Provide analysis on:
- Overall pacing: Is it too fast, too slow, or well-balanced?
- Tension curve: How tension builds and releases
- Character development: Pacing of character growth
- Plot progression: How quickly major events unfold
- Recommendations: Specific suggestions for improvement

Format your response with clear sections for each analysis point."""
        
        request = AIRequest(
            prompt=prompt,
            max_tokens=400,
            temperature=0.5
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            return self._parse_pacing_analysis(response.content)
        
        return {"error": response.error}
    
    def find_plot_holes(self, story_outline: List[str]) -> List[str]:
        """Identify potential plot holes in a story outline."""
        outline_text = "\n".join([f"{i+1}. {point}" for i, point in enumerate(story_outline)])
        
        prompt = f"""Review this story outline for potential plot holes, inconsistencies, or logical problems:

{outline_text}

List any plot holes or issues you find, explaining why each one is problematic."""
        
        request = AIRequest(
            prompt=prompt,
            max_tokens=300,
            temperature=0.3  # Lower temperature for analytical tasks
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            # Parse issues from response
            lines = response.content.strip().split('\n')
            issues = []
            for line in lines:
                clean_line = re.sub(r'^\d+[.)]\s*[-•]\s*', '', line.strip())
                if clean_line and len(clean_line) > 20:  # Filter out short lines
                    issues.append(clean_line)
            return issues
        
        return [f"Error: {response.error}"]
    
    def suggest_improvements(self, content: str, content_type: str = "dialogue") -> List[str]:
        """Suggest improvements for content."""
        type_prompts = {
            "dialogue": "Analyze this dialogue and suggest improvements for naturalness, character voice, and engagement",
            "description": "Analyze this description and suggest improvements for clarity, vividness, and atmosphere",
            "story": "Analyze this story segment and suggest improvements for pacing, tension, and character development"
        }
        
        base_prompt = type_prompts.get(content_type, type_prompts["dialogue"])
        prompt = f"{base_prompt}: {content}\n\nProvide 3-5 specific suggestions for improvement."
        
        request = AIRequest(
            prompt=prompt,
            max_tokens=250,
            temperature=0.6
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            # Parse suggestions
            lines = response.content.strip().split('\n')
            suggestions = []
            for line in lines:
                clean_line = re.sub(r'^\d+[.)]\s*[-•]\s*', '', line.strip())
                if clean_line and len(clean_line) > 15:
                    suggestions.append(clean_line)
            return suggestions
        
        return [f"Error: {response.error}"]
    
    def _parse_pacing_analysis(self, content: str) -> Dict[str, str]:
        """Parse pacing analysis into structured data."""
        analysis = {
            "overall_pacing": "",
            "tension_curve": "",
            "character_development": "",
            "plot_progression": "",
            "recommendations": ""
        }
        
        # Simple section parsing
        current_section = None
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            for key in analysis.keys():
                section_name = key.replace('_', ' ')
                if section_name.lower() in line.lower() and ':' in line:
                    current_section = key
                    _, content_part = line.split(':', 1)
                    analysis[key] = content_part.strip()
                    break
            else:
                if current_section:
                    if analysis[current_section]:
                        analysis[current_section] += " " + line
                    else:
                        analysis[current_section] = line
        
        return analysis