"""AI-Powered Story Templates - Dynamic template generation based on user preferences."""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import time

from .enhanced_generators import StoryContext, IntelligentDialogueEngine, create_enhanced_ai_system
from .ai_service import AIService, AIRequest


class TemplateGenre(Enum):
    """Supported template genres."""
    FANTASY = "fantasy"
    SCI_FI = "sci_fi"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    HORROR = "horror"
    ADVENTURE = "adventure"
    DRAMA = "drama"
    COMEDY = "comedy"
    THRILLER = "thriller"
    HISTORICAL = "historical"
    MODERN = "modern"
    CYBERPUNK = "cyberpunk"


class TemplateComplexity(Enum):
    """Template complexity levels."""
    SIMPLE = "simple"        # 3-5 nodes, linear story
    MODERATE = "moderate"    # 5-10 nodes, some branching
    COMPLEX = "complex"      # 10-20 nodes, multiple branches
    EPIC = "epic"           # 20+ nodes, complex branching


class TemplateTheme(Enum):
    """Common story themes."""
    GOOD_VS_EVIL = "good_vs_evil"
    COMING_OF_AGE = "coming_of_age"
    REDEMPTION = "redemption"
    LOVE_CONQUERS_ALL = "love_conquers_all"
    POWER_CORRUPTS = "power_corrupts"
    IDENTITY_QUEST = "identity_quest"
    SURVIVAL = "survival"
    JUSTICE = "justice"
    SACRIFICE = "sacrifice"
    DISCOVERY = "discovery"
    BETRAYAL = "betrayal"
    FAMILY_BONDS = "family_bonds"


@dataclass
class TemplatePreferences:
    """User preferences for template generation."""
    genre: TemplateGenre
    complexity: TemplateComplexity
    themes: List[TemplateTheme]
    tone: str = "balanced"  # light, balanced, dark
    length: str = "medium"  # short, medium, long
    character_count: int = 3
    setting: str = ""
    special_requirements: str = ""
    target_audience: str = "general"  # young, general, mature
    interactive_elements: List[str] = None  # combat, puzzles, romance, etc.
    
    def __post_init__(self):
        if self.interactive_elements is None:
            self.interactive_elements = []


@dataclass 
class GeneratedTemplate:
    """A complete generated story template."""
    id: str
    name: str
    description: str
    preferences: TemplatePreferences
    nodes: Dict[str, Dict[str, Any]]
    characters: Dict[str, Dict[str, Any]]
    story_structure: Dict[str, Any]
    metadata: Dict[str, Any]
    creation_timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "preferences": {
                "genre": self.preferences.genre.value,
                "complexity": self.preferences.complexity.value,
                "themes": [theme.value for theme in self.preferences.themes],
                "tone": self.preferences.tone,
                "length": self.preferences.length,
                "character_count": self.preferences.character_count,
                "setting": self.preferences.setting,
                "special_requirements": self.preferences.special_requirements,
                "target_audience": self.preferences.target_audience,
                "interactive_elements": self.preferences.interactive_elements
            },
            "nodes": self.nodes,
            "characters": self.characters,
            "story_structure": self.story_structure,
            "metadata": self.metadata,
            "creation_timestamp": self.creation_timestamp
        }


class AITemplateGenerator:
    """Generates complete story templates using AI."""
    
    def __init__(self, ai_service: AIService):
        """Initialize template generator."""
        self.ai_service = ai_service
        self.enhanced_ai = create_enhanced_ai_system(ai_service)
        self.dialogue_engine = self.enhanced_ai['dialogue_engine']
        
    def generate_template(self, preferences: TemplatePreferences) -> GeneratedTemplate:
        """Generate a complete story template based on preferences."""
        
        # Generate template ID and basic info
        template_id = str(uuid.uuid4())
        template_name = self._generate_template_name(preferences)
        template_description = self._generate_template_description(preferences)
        
        # Generate story structure
        story_structure = self._generate_story_structure(preferences)
        
        # Generate characters
        characters = self._generate_characters(preferences, story_structure)
        
        # Generate nodes based on structure
        nodes = self._generate_story_nodes(preferences, story_structure, characters)
        
        # Generate metadata
        metadata = self._generate_template_metadata(preferences, story_structure)
        
        # Create template object
        template = GeneratedTemplate(
            id=template_id,
            name=template_name,
            description=template_description,
            preferences=preferences,
            nodes=nodes,
            characters=characters,
            story_structure=story_structure,
            metadata=metadata,
            creation_timestamp=time.time()
        )
        
        return template
    
    def _generate_template_name(self, preferences: TemplatePreferences) -> str:
        """Generate an engaging template name."""
        
        genre_descriptors = {
            TemplateGenre.FANTASY: ["Mystical", "Enchanted", "Magical", "Epic"],
            TemplateGenre.SCI_FI: ["Galactic", "Future", "Cyber", "Quantum"],
            TemplateGenre.MYSTERY: ["Hidden", "Secret", "Shadow", "Mysterious"],
            TemplateGenre.ROMANCE: ["Passionate", "Tender", "Romantic", "Heartfelt"],
            TemplateGenre.HORROR: ["Dark", "Haunted", "Nightmare", "Terror"],
            TemplateGenre.ADVENTURE: ["Epic", "Daring", "Bold", "Heroic"],
            TemplateGenre.DRAMA: ["Intense", "Emotional", "Deep", "Dramatic"],
            TemplateGenre.THRILLER: ["Suspenseful", "Tense", "Edge", "Thrilling"]
        }
        
        prompt = f"""Generate a compelling title for a {preferences.genre.value} interactive story template with these characteristics:

Genre: {preferences.genre.value}
Complexity: {preferences.complexity.value}  
Themes: {', '.join([theme.value.replace('_', ' ') for theme in preferences.themes])}
Tone: {preferences.tone}
Setting: {preferences.setting or 'flexible setting'}

Create a title that:
1. Captures the essence of the genre and themes
2. Is engaging and memorable
3. Indicates it's interactive/choice-based
4. Is 2-6 words long
5. Avoids clichés

Return only the title, no additional text."""

        request = AIRequest(
            prompt=prompt,
            max_tokens=50,
            temperature=0.8
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            title = response.content.strip().strip('"\'')
            return title
        
        # Fallback name generation
        descriptors = genre_descriptors.get(preferences.genre, ["Interactive"])
        return f"{descriptors[0]} {preferences.genre.value.title()} Story"
    
    def _generate_template_description(self, preferences: TemplatePreferences) -> str:
        """Generate a template description."""
        
        prompt = f"""Create a compelling description for an interactive story template with these specifications:

Genre: {preferences.genre.value}
Complexity: {preferences.complexity.value}
Themes: {', '.join([theme.value.replace('_', ' ') for theme in preferences.themes])}
Tone: {preferences.tone}
Target Audience: {preferences.target_audience}
Character Count: {preferences.character_count}
Setting: {preferences.setting or 'flexible setting'}
Interactive Elements: {', '.join(preferences.interactive_elements) or 'choice-based narrative'}

Write a 2-3 sentence description that:
1. Explains what kind of story this template creates
2. Highlights the key themes and genre elements
3. Mentions the interactive aspects
4. Appeals to writers who might use this template

Keep it engaging and professional."""

        request = AIRequest(
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            return response.content.strip()
        
        # Fallback description
        return f"A {preferences.complexity.value} {preferences.genre.value} interactive story template featuring {', '.join([t.value.replace('_', ' ') for t in preferences.themes])}."
    
    def _generate_story_structure(self, preferences: TemplatePreferences) -> Dict[str, Any]:
        """Generate the overall story structure."""
        
        # Determine node count based on complexity
        node_counts = {
            TemplateComplexity.SIMPLE: (3, 5),
            TemplateComplexity.MODERATE: (5, 10),
            TemplateComplexity.COMPLEX: (10, 20),
            TemplateComplexity.EPIC: (20, 50)
        }
        
        min_nodes, max_nodes = node_counts[preferences.complexity]
        target_nodes = min_nodes + (max_nodes - min_nodes) // 2  # Take middle of range
        
        prompt = f"""Design a story structure for a {preferences.genre.value} interactive story with these parameters:

Genre: {preferences.genre.value}
Complexity: {preferences.complexity.value}
Target Nodes: {target_nodes}
Themes: {', '.join([theme.value.replace('_', ' ') for theme in preferences.themes])}
Tone: {preferences.tone}
Setting: {preferences.setting or 'flexible setting'}
Character Count: {preferences.character_count}

Create a story structure with:
1. Clear beginning, middle, and end sections
2. Appropriate branching points for player choices
3. Character development moments
4. Thematic elements woven throughout
5. Satisfying multiple endings

Format as JSON with this structure:
{{
  "act_structure": {{
    "act1": {{"description": "...", "node_count": X, "key_events": [...]}},
    "act2": {{"description": "...", "node_count": X, "key_events": [...]}},
    "act3": {{"description": "...", "node_count": X, "key_events": [...]}}
  }},
  "key_decision_points": [...],
  "character_arcs": [...],
  "thematic_moments": [...],
  "ending_types": [...]
}}"""

        request = AIRequest(
            prompt=prompt,
            max_tokens=600,
            temperature=0.7
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            try:
                structure = json.loads(response.content)
                return structure
            except json.JSONDecodeError:
                pass
        
        # Fallback structure
        return self._create_fallback_structure(preferences, target_nodes)
    
    def _create_fallback_structure(self, preferences: TemplatePreferences, target_nodes: int) -> Dict[str, Any]:
        """Create a fallback story structure."""
        act1_nodes = max(1, target_nodes // 4)
        act2_nodes = max(2, target_nodes // 2)
        act3_nodes = max(1, target_nodes - act1_nodes - act2_nodes)
        
        return {
            "act_structure": {
                "act1": {
                    "description": f"Introduction to the {preferences.genre.value} world and characters",
                    "node_count": act1_nodes,
                    "key_events": ["Opening scene", "Character introduction", "Inciting incident"]
                },
                "act2": {
                    "description": "Main conflicts and character development",
                    "node_count": act2_nodes,
                    "key_events": ["Rising action", "Major choice points", "Character growth"]
                },
                "act3": {
                    "description": "Climax and resolution",
                    "node_count": act3_nodes,
                    "key_events": ["Climactic confrontation", "Resolution", "Ending"]
                }
            },
            "key_decision_points": ["Character choice", "Moral dilemma", "Story direction"],
            "character_arcs": [f"Character development for {preferences.character_count} main characters"],
            "thematic_moments": [theme.value.replace('_', ' ') for theme in preferences.themes],
            "ending_types": ["Positive outcome", "Bittersweet ending", "Player choice determines outcome"]
        }
    
    def _generate_characters(self, preferences: TemplatePreferences, story_structure: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Generate character profiles for the template."""
        
        characters = {}
        
        prompt = f"""Create {preferences.character_count} distinct characters for a {preferences.genre.value} interactive story:

Story Context:
- Genre: {preferences.genre.value}
- Themes: {', '.join([theme.value.replace('_', ' ') for theme in preferences.themes])}
- Tone: {preferences.tone}
- Setting: {preferences.setting or 'flexible setting'}
- Target Audience: {preferences.target_audience}

For each character, provide:
1. Name (appropriate for genre/setting)
2. Role (protagonist, antagonist, mentor, etc.)
3. Personality traits (3-4 key traits)
4. Background (2-3 sentences)
5. Goals and motivations
6. Speaking style/voice
7. Character arc potential

Format as JSON:
{{
  "character_1": {{
    "name": "...",
    "role": "...",
    "personality": [...],
    "background": "...",
    "goals": "...",
    "speaking_style": "...",
    "arc": "..."
  }},
  ...
}}

Create diverse, interesting characters that fit the genre and themes."""

        request = AIRequest(
            prompt=prompt,
            max_tokens=800,
            temperature=0.8
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            try:
                characters_data = json.loads(response.content)
                return characters_data
            except json.JSONDecodeError:
                pass
        
        # Fallback character creation
        return self._create_fallback_characters(preferences)
    
    def _create_fallback_characters(self, preferences: TemplatePreferences) -> Dict[str, Dict[str, Any]]:
        """Create fallback characters."""
        characters = {}
        
        character_roles = ["protagonist", "mentor", "antagonist", "ally", "rival"]
        
        for i in range(preferences.character_count):
            role = character_roles[i % len(character_roles)]
            characters[f"character_{i+1}"] = {
                "name": f"Character {i+1}",
                "role": role,
                "personality": ["determined", "complex", "engaging"],
                "background": f"A {role} in the {preferences.genre.value} story with an interesting history.",
                "goals": f"Pursues objectives relevant to their role as {role}",
                "speaking_style": "Distinctive voice appropriate for their role",
                "arc": f"Develops throughout the story as a {role} character"
            }
        
        return characters
    
    def _generate_story_nodes(self, 
                            preferences: TemplatePreferences, 
                            story_structure: Dict[str, Any], 
                            characters: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Generate the actual story nodes."""
        
        nodes = {}
        
        # Get act structure
        act_structure = story_structure.get("act_structure", {})
        
        node_counter = 1
        
        # Generate nodes for each act
        for act_name, act_data in act_structure.items():
            act_nodes = self._generate_act_nodes(
                preferences, 
                act_data, 
                characters, 
                node_counter, 
                act_name
            )
            nodes.update(act_nodes)
            node_counter += len(act_nodes)
        
        # Connect nodes with choices
        self._connect_nodes_with_choices(nodes, story_structure)
        
        return nodes
    
    def _generate_act_nodes(self, 
                          preferences: TemplatePreferences,
                          act_data: Dict[str, Any], 
                          characters: Dict[str, Dict[str, Any]],
                          start_id: int, 
                          act_name: str) -> Dict[str, Dict[str, Any]]:
        """Generate nodes for a specific act."""
        
        nodes = {}
        node_count = act_data.get("node_count", 1)
        act_description = act_data.get("description", "")
        key_events = act_data.get("key_events", [])
        
        # Create story context
        story_context = StoryContext(
            characters=characters,
            genre=preferences.genre.value,
            tone=preferences.tone,
            themes=[theme.value for theme in preferences.themes]
        )
        
        for i in range(node_count):
            node_id = f"node_{start_id + i}"
            
            # Determine event type for this node
            if i < len(key_events):
                event_type = key_events[i]
            else:
                event_type = "story development"
            
            # Select character for this node
            character_name = self._select_character_for_node(characters, i, act_name)
            
            # Generate node content
            node = self._generate_single_node(
                preferences, 
                story_context, 
                character_name,
                event_type,
                act_description,
                node_id
            )
            
            nodes[node_id] = node
        
        return nodes
    
    def _generate_single_node(self, 
                            preferences: TemplatePreferences,
                            story_context: StoryContext,
                            character_name: str,
                            event_type: str,
                            act_description: str,
                            node_id: str) -> Dict[str, Any]:
        """Generate a single story node."""
        
        prompt = f"""Create dialogue and content for a {preferences.genre.value} story node:

Context:
- Character: {character_name}
- Event Type: {event_type}
- Act Description: {act_description}
- Genre: {preferences.genre.value}
- Tone: {preferences.tone}
- Themes: {', '.join([theme.value.replace('_', ' ') for theme in preferences.themes])}

Generate:
1. Engaging dialogue or narrative text (2-4 sentences)
2. 2-3 player choice options that fit the situation
3. Brief description of the scene/situation

Keep the content:
- Appropriate for the genre and tone
- Engaging and immersive
- True to the character's voice
- Connected to the themes

Format the response as:
TEXT: [main dialogue/narrative]
CHOICES: [choice 1] | [choice 2] | [choice 3]
SCENE: [brief scene description]"""

        request = AIRequest(
            prompt=prompt,
            context={"character": character_name, "event": event_type},
            max_tokens=300,
            temperature=0.8
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        # Parse response
        text, choices, scene = self._parse_node_response(response.content if response.success else "")
        
        # Create node structure
        node = {
            "node_type": "dialogue",
            "game_data": {
                "text": text,
                "character": character_name,
                "choices": self._format_choices(choices, node_id),
                "scene_description": scene
            },
            "metadata": {
                "event_type": event_type,
                "generated": True,
                "template_node": True
            }
        }
        
        return node
    
    def _parse_node_response(self, content: str) -> Tuple[str, List[str], str]:
        """Parse AI response into text, choices, and scene."""
        lines = content.split('\\n')
        text = ""
        choices = []
        scene = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("TEXT:"):
                current_section = "text"
                text = line[5:].strip()
            elif line.startswith("CHOICES:"):
                current_section = "choices"
                choice_text = line[8:].strip()
                if '|' in choice_text:
                    choices = [c.strip() for c in choice_text.split('|')]
            elif line.startswith("SCENE:"):
                current_section = "scene"
                scene = line[6:].strip()
            elif current_section == "text" and line:
                text += " " + line
            elif current_section == "scene" and line:
                scene += " " + line
        
        # Fallback content
        if not text:
            text = "An engaging moment in the story unfolds."
        if not choices:
            choices = ["Continue", "Ask questions", "Take action"]
        if not scene:
            scene = "The scene is set for an important story moment."
        
        return text, choices, scene
    
    def _format_choices(self, choice_texts: List[str], node_id: str) -> List[Dict[str, Any]]:
        """Format choices for node structure."""
        choices = []
        
        for i, choice_text in enumerate(choice_texts):
            choices.append({
                "id": f"{node_id}_choice_{i}",
                "text": choice_text,
                "target_node": None,  # Will be connected later
                "conditions": {},
                "effects": {}
            })
        
        return choices
    
    def _select_character_for_node(self, characters: Dict[str, Dict[str, Any]], node_index: int, act_name: str) -> str:
        """Select appropriate character for a node."""
        character_list = list(characters.keys())
        
        if not character_list:
            return "Narrator"
        
        # Rotate through characters, favoring protagonist in act1
        if act_name == "act1" and node_index == 0:
            # First node should be protagonist if available
            for char_id, char_data in characters.items():
                if char_data.get("role") == "protagonist":
                    return char_data.get("name", char_id)
        
        # Default rotation through characters
        char_id = character_list[node_index % len(character_list)]
        return characters[char_id].get("name", char_id)
    
    def _connect_nodes_with_choices(self, nodes: Dict[str, Dict[str, Any]], story_structure: Dict[str, Any]):
        """Connect nodes by setting choice targets."""
        node_ids = list(nodes.keys())
        
        for i, node_id in enumerate(node_ids):
            node = nodes[node_id]
            choices = node.get("game_data", {}).get("choices", [])
            
            # Connect choices to next nodes
            for j, choice in enumerate(choices):
                if i + 1 < len(node_ids):  # Not the last node
                    # Simple linear connection with some branching
                    if j == 0 or len(choices) == 1:
                        # Main path
                        choice["target_node"] = node_ids[i + 1]
                    else:
                        # Branch to alternative paths
                        target_index = min(i + j + 1, len(node_ids) - 1)
                        choice["target_node"] = node_ids[target_index]
                else:
                    # Last node - choices lead to endings
                    choice["target_node"] = None  # End of story
    
    def _generate_template_metadata(self, 
                                  preferences: TemplatePreferences, 
                                  story_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate template metadata."""
        
        return {
            "generator_version": "1.0",
            "estimated_playtime": self._estimate_playtime(preferences),
            "difficulty_level": preferences.complexity.value,
            "content_warnings": self._generate_content_warnings(preferences),
            "recommended_age": self._get_age_recommendation(preferences),
            "tags": self._generate_tags(preferences),
            "branching_factor": self._calculate_branching_factor(story_structure),
            "character_count": preferences.character_count,
            "theme_focus": [theme.value for theme in preferences.themes],
            "customization_notes": self._generate_customization_notes(preferences)
        }
    
    def _estimate_playtime(self, preferences: TemplatePreferences) -> str:
        """Estimate playtime for the template."""
        complexity_times = {
            TemplateComplexity.SIMPLE: "5-10 minutes",
            TemplateComplexity.MODERATE: "10-20 minutes", 
            TemplateComplexity.COMPLEX: "20-45 minutes",
            TemplateComplexity.EPIC: "45+ minutes"
        }
        return complexity_times[preferences.complexity]
    
    def _generate_content_warnings(self, preferences: TemplatePreferences) -> List[str]:
        """Generate appropriate content warnings."""
        warnings = []
        
        if preferences.genre == TemplateGenre.HORROR:
            warnings.extend(["scary content", "suspense"])
        elif preferences.genre == TemplateGenre.THRILLER:
            warnings.append("intense situations")
        
        if preferences.tone == "dark":
            warnings.append("mature themes")
        
        if "combat" in preferences.interactive_elements:
            warnings.append("fantasy violence")
        
        if preferences.target_audience == "mature":
            warnings.append("mature content")
        
        return warnings
    
    def _get_age_recommendation(self, preferences: TemplatePreferences) -> str:
        """Get age recommendation."""
        if preferences.target_audience == "young":
            return "8+"
        elif preferences.target_audience == "mature":
            return "16+"
        else:
            return "12+"
    
    def _generate_tags(self, preferences: TemplatePreferences) -> List[str]:
        """Generate tags for the template."""
        tags = [preferences.genre.value, preferences.complexity.value]
        tags.extend([theme.value for theme in preferences.themes])
        tags.extend(preferences.interactive_elements)
        tags.append(preferences.tone)
        return list(set(tags))  # Remove duplicates
    
    def _calculate_branching_factor(self, story_structure: Dict[str, Any]) -> float:
        """Calculate average branching factor."""
        # Simplified calculation - would be more sophisticated in real implementation
        decision_points = len(story_structure.get("key_decision_points", []))
        total_acts = len(story_structure.get("act_structure", {}))
        return round(decision_points / max(total_acts, 1), 1)
    
    def _generate_customization_notes(self, preferences: TemplatePreferences) -> str:
        """Generate notes for customizing the template."""
        notes = []
        
        notes.append(f"This {preferences.genre.value} template is designed to be easily customizable.")
        
        if preferences.setting:
            notes.append(f"The {preferences.setting} setting can be adapted to similar environments.")
        
        notes.append("Character names, backgrounds, and dialogue can be modified to fit your vision.")
        
        if preferences.interactive_elements:
            elements_text = ', '.join(preferences.interactive_elements)
            notes.append(f"Interactive elements ({elements_text}) can be expanded or simplified as needed.")
        
        return " ".join(notes)


# Template management and utilities

class AITemplateManager:
    """Manages AI-generated templates."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.generator = AITemplateGenerator(ai_service)
        self.cached_templates: Dict[str, GeneratedTemplate] = {}
    
    def create_template_from_preferences(self, preferences: TemplatePreferences) -> GeneratedTemplate:
        """Create a new template from user preferences."""
        template = self.generator.generate_template(preferences)
        self.cached_templates[template.id] = template
        return template
    
    def get_template_suggestions(self, user_context: Dict[str, Any]) -> List[TemplatePreferences]:
        """Get template suggestions based on user context."""
        # This would analyze user's previous projects, preferences, etc.
        # For now, return some popular combinations
        
        suggestions = [
            TemplatePreferences(
                genre=TemplateGenre.FANTASY,
                complexity=TemplateComplexity.MODERATE,
                themes=[TemplateTheme.GOOD_VS_EVIL, TemplateTheme.COMING_OF_AGE],
                tone="balanced",
                character_count=3,
                setting="Medieval fantasy realm"
            ),
            TemplatePreferences(
                genre=TemplateGenre.SCI_FI,
                complexity=TemplateComplexity.COMPLEX,
                themes=[TemplateTheme.IDENTITY_QUEST, TemplateTheme.DISCOVERY],
                tone="balanced",
                character_count=4,
                setting="Space station or colony"
            ),
            TemplatePreferences(
                genre=TemplateGenre.MYSTERY,
                complexity=TemplateComplexity.COMPLEX,
                themes=[TemplateTheme.JUSTICE, TemplateTheme.BETRAYAL],
                tone="dark",
                character_count=5,
                setting="Small town with secrets"
            )
        ]
        
        return suggestions
    
    def save_template(self, template: GeneratedTemplate, filepath: str):
        """Save template to file."""
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template.to_dict(), f, indent=2)
    
    def load_template(self, filepath: str) -> Optional[GeneratedTemplate]:
        """Load template from file."""
        try:
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Reconstruct template object
            # This is simplified - full implementation would properly deserialize
            return None  # Placeholder
        except Exception as e:
            print(f"Error loading template: {e}")
            return None


# Factory function
def create_ai_template_system(ai_service: AIService) -> AITemplateManager:
    """Create AI template management system."""
    return AITemplateManager(ai_service)