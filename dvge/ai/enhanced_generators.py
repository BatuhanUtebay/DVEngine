"""Enhanced AI Content Generators for DVGE - Next-Generation Intelligence."""

import json
import re
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass
from .ai_service import AIService, AIRequest, AIResponse
from .generators import DialogueGenerator, CharacterGenerator, StoryGenerator


@dataclass
class StoryContext:
    """Complete story context for AI generation."""
    nodes: Dict[str, Any] = None
    characters: Dict[str, Dict[str, Any]] = None
    relationships: Dict[str, Dict[str, Any]] = None
    story_flags: Dict[str, bool] = None
    variables: Dict[str, Any] = None
    themes: List[str] = None
    genre: str = "general"
    tone: str = "neutral"
    pacing: str = "medium"
    
    def __post_init__(self):
        """Initialize default values."""
        if self.nodes is None:
            self.nodes = {}
        if self.characters is None:
            self.characters = {}
        if self.relationships is None:
            self.relationships = {}
        if self.story_flags is None:
            self.story_flags = {}
        if self.variables is None:
            self.variables = {}
        if self.themes is None:
            self.themes = []


class IntelligentDialogueEngine:
    """Advanced dialogue generation with deep context awareness."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.base_generator = DialogueGenerator(ai_service)
        
    def generate_contextual_dialogue(self, 
                                   character: str,
                                   situation: str,
                                   story_context: StoryContext,
                                   emotional_state: str = "neutral",
                                   relationship_context: str = None) -> str:
        """Generate dialogue with full story context and emotional intelligence."""
        
        # Build comprehensive context prompt
        context_prompt = self._build_context_prompt(character, story_context)
        
        prompt = f"""Generate dialogue for {character} in this situation: {situation}

CHARACTER CONTEXT:
{context_prompt}

EMOTIONAL STATE: {emotional_state}
STORY TONE: {story_context.tone}
GENRE: {story_context.genre}

RELATIONSHIP CONTEXT: {relationship_context or 'Not specified'}

CURRENT STORY FLAGS: {self._format_story_flags(story_context.story_flags)}

Generate dialogue that:
1. Perfectly matches {character}'s established voice and personality
2. Reflects their current emotional state ({emotional_state})
3. Considers their relationships and story history
4. Maintains consistency with the {story_context.genre} genre and {story_context.tone} tone
5. Advances the story naturally

Return only the dialogue line without formatting."""

        request = AIRequest(
            prompt=prompt,
            context={
                "character": character,
                "emotional_state": emotional_state,
                "story_context": story_context.__dict__
            },
            max_tokens=150,
            temperature=0.8
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            return self._clean_dialogue(response.content, character)
        return f"[AI Error: {response.error}]"
    
    def generate_branching_dialogue_tree(self,
                                       character: str,
                                       situation: str, 
                                       story_context: StoryContext,
                                       depth: int = 3,
                                       choices_per_level: int = 3) -> Dict[str, Any]:
        """Generate a complete branching dialogue tree with intelligent choices."""
        
        prompt = f"""Generate a {depth}-level branching dialogue tree for {character} in this situation: {situation}

CONTEXT:
{self._build_context_prompt(character, story_context)}

Create a dialogue tree with {choices_per_level} meaningful player choices at each level.
Each branch should:
1. Lead to distinctly different story outcomes
2. Reflect different player personality/approach options
3. Have natural consequences that affect future interactions
4. Maintain {character}'s voice consistency

Format as JSON:
{{
  "root": {{
    "character_line": "Initial dialogue",
    "player_choices": [
      {{
        "text": "Player choice 1",
        "tone": "aggressive/diplomatic/curious/etc",
        "response": {{
          "character_line": "Character's response",
          "player_choices": [...] // Continue for {depth} levels
        }}
      }}
    ]
  }}
}}"""

        request = AIRequest(
            prompt=prompt,
            context={
                "character": character,
                "depth": depth,
                "story_context": story_context.__dict__
            },
            max_tokens=800,
            temperature=0.7
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                return self._parse_dialogue_tree_fallback(response.content)
        
        return {"error": response.error}
    
    def enhance_dialogue_with_subtext(self,
                                    original_dialogue: str,
                                    character: str,
                                    hidden_motivation: str,
                                    story_context: StoryContext) -> str:
        """Add subtext and deeper meaning to dialogue."""
        
        prompt = f"""Enhance this dialogue with subtext and deeper meaning:

ORIGINAL: "{original_dialogue}"
CHARACTER: {character}
HIDDEN MOTIVATION: {hidden_motivation}

CHARACTER CONTEXT:
{self._build_context_prompt(character, story_context)}

Rewrite the dialogue to:
1. Keep the surface meaning intact
2. Add layers of subtext that hint at the hidden motivation
3. Use the character's speaking patterns and personality
4. Create emotional resonance and depth
5. Make it more engaging and memorable

Return only the enhanced dialogue line."""

        request = AIRequest(
            prompt=prompt,
            context={
                "character": character,
                "hidden_motivation": hidden_motivation,
                "story_context": story_context.__dict__
            },
            max_tokens=120,
            temperature=0.8
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            return self._clean_dialogue(response.content, character)
        return original_dialogue
    
    def _build_context_prompt(self, character: str, story_context: StoryContext) -> str:
        """Build comprehensive context prompt for character."""
        context_parts = []
        
        # Character information
        if character in story_context.characters:
            char_info = story_context.characters[character]
            if char_info.get('personality'):
                context_parts.append(f"Personality: {char_info['personality']}")
            if char_info.get('background'):
                context_parts.append(f"Background: {char_info['background']}")
            if char_info.get('speech_style'):
                context_parts.append(f"Speech Style: {char_info['speech_style']}")
        
        # Relationship context
        if character in story_context.relationships:
            rel_info = story_context.relationships[character]
            context_parts.append(f"Relationships: {json.dumps(rel_info, indent=2)}")
        
        # Current story themes
        if story_context.themes:
            context_parts.append(f"Story Themes: {', '.join(story_context.themes)}")
        
        return "\n".join(context_parts) if context_parts else "No specific context available"
    
    def _format_story_flags(self, flags: Dict[str, bool]) -> str:
        """Format story flags for context."""
        if not flags:
            return "None set"
        
        active_flags = [flag for flag, value in flags.items() if value]
        return ", ".join(active_flags) if active_flags else "None active"
    
    def _clean_dialogue(self, raw_dialogue: str, character: str) -> str:
        """Clean and format dialogue output."""
        dialogue = raw_dialogue.strip()
        # Remove quotes
        dialogue = re.sub(r'^["\']|["\']$', '', dialogue)
        # Remove character name prefix
        dialogue = re.sub(f'^{re.escape(character)}:?\\s*', '', dialogue, flags=re.IGNORECASE)
        # Remove common AI prefixes
        dialogue = re.sub(r'^(Here\'s the dialogue:|Dialogue:|Response:)\\s*', '', dialogue, flags=re.IGNORECASE)
        return dialogue.strip()
    
    def _parse_dialogue_tree_fallback(self, content: str) -> Dict[str, Any]:
        """Fallback parser for dialogue tree if JSON parsing fails."""
        return {
            "root": {
                "character_line": "Generated dialogue tree parsing failed",
                "player_choices": [
                    {
                        "text": "Continue",
                        "tone": "neutral",
                        "response": {
                            "character_line": "Fallback response",
                            "player_choices": []
                        }
                    }
                ]
            },
            "raw_content": content
        }


class StoryIntelligenceAnalyzer:
    """Advanced story structure and narrative analysis."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        
    def analyze_story_structure(self, nodes: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive story structure analysis."""
        
        # Build story graph representation
        story_summary = self._build_story_summary(nodes)
        
        prompt = f"""Analyze this interactive story structure for narrative quality and coherence:

STORY SUMMARY:
{story_summary}

Provide analysis in these categories:

1. PACING ANALYSIS:
   - Overall pacing (fast/medium/slow)
   - Pacing issues or imbalances
   - Suggested improvements

2. PLOT COHERENCE:
   - Logical consistency
   - Plot holes or gaps
   - Character motivation consistency
   - Cause-and-effect relationships

3. BRANCHING QUALITY:
   - Meaningful choice consequences  
   - Branch variety and depth
   - Dead-end paths or railroading
   - Choice significance

4. NARRATIVE STRUCTURE:
   - Beginning/middle/end balance
   - Tension and conflict development
   - Character arc progression
   - Theme consistency

5. ENGAGEMENT FACTORS:
   - Player agency and impact
   - Emotional resonance
   - Surprise and unpredictability
   - Replay value

6. TECHNICAL ISSUES:
   - Unreachable nodes
   - Missing connections
   - Inconsistent variables/flags

Return detailed analysis with specific examples and actionable suggestions."""

        request = AIRequest(
            prompt=prompt,
            context={"node_count": len(nodes)},
            max_tokens=800,
            temperature=0.3
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            return self._parse_story_analysis(response.content)
        
        return {"error": response.error}
    
    def detect_plot_holes(self, nodes: Dict[str, Any], story_context: StoryContext) -> List[Dict[str, Any]]:
        """Detect logical inconsistencies and plot holes."""
        
        # Analyze story logic
        story_logic = self._extract_story_logic(nodes, story_context)
        
        prompt = f"""Analyze this story for plot holes, logical inconsistencies, and narrative problems:

STORY LOGIC:
{story_logic}

Find and report:

1. LOGICAL INCONSISTENCIES:
   - Contradictory information
   - Impossible sequences of events
   - Character knowledge issues

2. CONTINUITY ERRORS:
   - Forgotten plot threads
   - Inconsistent character behavior
   - Setting contradictions

3. CAUSALITY PROBLEMS:
   - Effects without causes
   - Actions without consequences
   - Timeline issues

4. CHARACTER ISSUES:
   - Motivation inconsistencies
   - Personality contradictions
   - Relationship problems

For each issue found, provide:
- Specific location/node references
- Description of the problem
- Severity level (minor/moderate/major)
- Suggested fix

Format as structured list with clear categories."""

        request = AIRequest(
            prompt=prompt,
            context={"story_context": story_context.__dict__},
            max_tokens=600,
            temperature=0.2
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            return self._parse_plot_holes(response.content)
        
        return [{"error": response.error}]
    
    def suggest_story_improvements(self, 
                                 nodes: Dict[str, Any], 
                                 story_context: StoryContext,
                                 focus_area: str = "overall") -> List[Dict[str, str]]:
        """Generate specific, actionable story improvement suggestions."""
        
        focus_prompts = {
            "pacing": "Focus on story pacing and rhythm issues",
            "character": "Focus on character development and consistency",
            "plot": "Focus on plot structure and coherence",
            "choices": "Focus on player choices and branching quality",
            "engagement": "Focus on player engagement and emotional impact",
            "overall": "Provide comprehensive improvement suggestions"
        }
        
        story_summary = self._build_story_summary(nodes)
        focus_instruction = focus_prompts.get(focus_area, focus_prompts["overall"])
        
        prompt = f"""Provide specific, actionable suggestions to improve this interactive story.

{focus_instruction}

STORY SUMMARY:
{story_summary}

STORY CONTEXT:
Genre: {story_context.genre}
Tone: {story_context.tone}
Themes: {', '.join(story_context.themes)}

For each suggestion, provide:
1. IMPROVEMENT: Specific change to make
2. REASON: Why this will improve the story
3. IMPLEMENTATION: How to implement the change
4. IMPACT: Expected effect on player experience
5. PRIORITY: High/Medium/Low

Focus on practical, implementable suggestions that will meaningfully enhance the story."""

        request = AIRequest(
            prompt=prompt,
            context={
                "focus_area": focus_area,
                "story_context": story_context.__dict__
            },
            max_tokens=700,
            temperature=0.4
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            return self._parse_improvement_suggestions(response.content)
        
        return [{"error": response.error}]
    
    def _build_story_summary(self, nodes: Dict[str, Any]) -> str:
        """Build concise story summary for analysis."""
        summary_parts = []
        summary_parts.append(f"Total Nodes: {len(nodes)}")
        
        # Categorize nodes
        node_types = {}
        choice_counts = []
        
        for node_id, node in nodes.items():
            node_type = node.get('node_type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
            
            # Count choices
            choices = node.get('game_data', {}).get('choices', [])
            choice_counts.append(len(choices))
        
        summary_parts.append(f"Node Types: {json.dumps(node_types)}")
        
        if choice_counts:
            avg_choices = sum(choice_counts) / len(choice_counts)
            summary_parts.append(f"Average Choices per Node: {avg_choices:.1f}")
            summary_parts.append(f"Max Choices in Single Node: {max(choice_counts)}")
        
        return "\n".join(summary_parts)
    
    def _extract_story_logic(self, nodes: Dict[str, Any], story_context: StoryContext) -> str:
        """Extract logical flow and dependencies from story."""
        logic_parts = []
        
        # Variable dependencies
        if story_context.variables:
            logic_parts.append(f"Story Variables: {json.dumps(story_context.variables, indent=2)}")
        
        # Flag dependencies
        if story_context.story_flags:
            logic_parts.append(f"Story Flags: {json.dumps(story_context.story_flags, indent=2)}")
        
        # Node connections (simplified)
        connections = []
        for node_id, node in nodes.items():
            game_data = node.get('game_data', {})
            if 'choices' in game_data:
                for choice in game_data['choices']:
                    target = choice.get('target_node')
                    if target:
                        connections.append(f"{node_id} -> {target}")
        
        if connections:
            logic_parts.append(f"Story Flow (sample): {'; '.join(connections[:10])}")
        
        return "\n".join(logic_parts)
    
    def _parse_story_analysis(self, content: str) -> Dict[str, Any]:
        """Parse story analysis response into structured data."""
        sections = {
            "pacing": "",
            "plot_coherence": "",
            "branching_quality": "",
            "narrative_structure": "",
            "engagement_factors": "",
            "technical_issues": "",
            "overall_score": 0,
            "summary": ""
        }
        
        # Simple parsing by looking for section headers
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if any(section.upper().replace('_', ' ') in line.upper() for section in sections.keys()):
                for section in sections.keys():
                    if section.upper().replace('_', ' ') in line.upper():
                        current_section = section
                        break
            elif current_section and line:
                if sections[current_section]:
                    sections[current_section] += " " + line
                else:
                    sections[current_section] = line
        
        sections["summary"] = content[:200] + "..." if len(content) > 200 else content
        return sections
    
    def _parse_plot_holes(self, content: str) -> List[Dict[str, Any]]:
        """Parse plot hole detection response."""
        plot_holes = []
        
        # Simple parsing - look for structured issues
        lines = content.split('\n')
        current_hole = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_hole:
                    plot_holes.append(current_hole)
                    current_hole = {}
                continue
            
            # Look for issue indicators
            if any(indicator in line.lower() for indicator in ['issue:', 'problem:', 'inconsistency:', 'error:']):
                current_hole['description'] = line
                current_hole['severity'] = 'moderate'  # default
                current_hole['category'] = 'plot'
            elif 'severity' in line.lower():
                if 'major' in line.lower():
                    current_hole['severity'] = 'major'
                elif 'minor' in line.lower():
                    current_hole['severity'] = 'minor'
            elif 'fix' in line.lower() or 'suggest' in line.lower():
                current_hole['suggested_fix'] = line
        
        if current_hole:
            plot_holes.append(current_hole)
        
        # If no structured parsing worked, create generic entry
        if not plot_holes and content:
            plot_holes.append({
                "description": "Analysis completed - see full content for details",
                "severity": "unknown",
                "category": "general",
                "full_analysis": content
            })
        
        return plot_holes
    
    def _parse_improvement_suggestions(self, content: str) -> List[Dict[str, str]]:
        """Parse improvement suggestions into structured format."""
        suggestions = []
        
        lines = content.split('\n')
        current_suggestion = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_suggestion and len(current_suggestion) >= 3:  # Minimum viable suggestion
                    suggestions.append(current_suggestion)
                    current_suggestion = {}
                continue
            
            # Parse structured suggestion format
            for field in ['improvement:', 'reason:', 'implementation:', 'impact:', 'priority:']:
                if line.lower().startswith(field):
                    key = field[:-1]  # Remove colon
                    value = line[len(field):].strip()
                    current_suggestion[key] = value
                    break
            else:
                # Add to description if no field matched
                if 'description' not in current_suggestion:
                    current_suggestion['description'] = line
                else:
                    current_suggestion['description'] += " " + line
        
        if current_suggestion and len(current_suggestion) >= 2:
            suggestions.append(current_suggestion)
        
        # Fallback if no structured suggestions found
        if not suggestions and content:
            suggestions.append({
                "improvement": "General story enhancement",
                "reason": "AI analysis completed",
                "implementation": "See full analysis for details",
                "priority": "medium",
                "full_analysis": content
            })
        
        return suggestions


class CharacterConsistencyEngine:
    """Advanced character voice and personality consistency checking."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.base_generator = CharacterGenerator(ai_service)
        
    def analyze_character_consistency(self, 
                                   character_name: str,
                                   dialogue_samples: List[str],
                                   character_profile: Dict[str, str]) -> Dict[str, Any]:
        """Deep analysis of character voice consistency across dialogue samples."""
        
        samples_text = "\n".join([f"{i+1}. {sample}" for i, sample in enumerate(dialogue_samples)])
        profile_text = json.dumps(character_profile, indent=2)
        
        prompt = f"""Analyze the voice consistency of '{character_name}' across these dialogue samples:

CHARACTER PROFILE:
{profile_text}

DIALOGUE SAMPLES:
{samples_text}

Provide detailed analysis:

1. VOICE CONSISTENCY:
   - Overall consistency score (1-10)
   - Consistent elements across samples
   - Inconsistent elements or variations
   - Most/least consistent samples

2. PERSONALITY ALIGNMENT:
   - How well dialogue matches stated personality
   - Personality traits clearly expressed
   - Traits that seem missing or contradicted

3. SPEECH PATTERNS:
   - Consistent vocabulary and word choice
   - Sentence structure patterns
   - Unique speaking mannerisms
   - Formality level consistency

4. EMOTIONAL RANGE:
   - Emotional expressions observed
   - Consistency in emotional responses
   - Believable emotional variation

5. IMPROVEMENT RECOMMENDATIONS:
   - Specific dialogue lines that need adjustment
   - Character voice elements to strengthen
   - Suggestions for better consistency

Provide specific examples and actionable feedback."""

        request = AIRequest(
            prompt=prompt,
            context={
                "character_name": character_name,
                "sample_count": len(dialogue_samples)
            },
            max_tokens=700,
            temperature=0.3
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            return self._parse_consistency_analysis(response.content, len(dialogue_samples))
        
        return {"error": response.error, "character": character_name}
    
    def generate_character_voice_guide(self,
                                     character_name: str,
                                     existing_dialogue: List[str],
                                     character_context: Dict[str, Any]) -> Dict[str, str]:
        """Generate comprehensive voice guide for consistent character writing."""
        
        dialogue_examples = "\n".join([f"- {line}" for line in existing_dialogue[:10]])  # Limit examples
        context_text = json.dumps(character_context, indent=2)
        
        prompt = f"""Create a comprehensive voice guide for writing '{character_name}' consistently:

CHARACTER CONTEXT:
{context_text}

EXISTING DIALOGUE EXAMPLES:
{dialogue_examples}

Create a detailed voice guide with:

1. CORE VOICE ELEMENTS:
   - Primary speaking style and tone
   - Typical vocabulary and word choices
   - Sentence structure preferences
   - Unique speech patterns or mannerisms

2. EMOTIONAL EXPRESSIONS:
   - How they express different emotions
   - Typical reactions to various situations
   - Emotional range and intensity patterns

3. RELATIONSHIP DYNAMICS:
   - How they speak to different types of people
   - Formal vs informal speech patterns
   - Authority and respect levels

4. DO'S AND DON'TS:
   - Things this character would definitely say
   - Things they would never say
   - Common mistakes to avoid

5. SAMPLE PHRASES:
   - Signature phrases or expressions
   - Typical greetings and farewells
   - Common reactions and responses

6. CONTEXT ADAPTATIONS:
   - How their speech changes in different situations
   - Stress/calm variations
   - Public vs private speaking differences

Make this a practical reference guide for consistent character writing."""

        request = AIRequest(
            prompt=prompt,
            context={
                "character_name": character_name,
                "dialogue_count": len(existing_dialogue)
            },
            max_tokens=800,
            temperature=0.4
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            return self._parse_voice_guide(response.content)
        
        return {"error": response.error}
    
    def validate_character_dialogue(self,
                                  character_name: str,
                                  new_dialogue: str,
                                  voice_guide: Dict[str, str],
                                  context: str = "") -> Dict[str, Any]:
        """Validate new dialogue against established character voice."""
        
        voice_summary = self._summarize_voice_guide(voice_guide)
        
        prompt = f"""Validate this new dialogue for '{character_name}' against their established voice:

NEW DIALOGUE: "{new_dialogue}"

CONTEXT: {context or 'No specific context provided'}

ESTABLISHED VOICE GUIDE:
{voice_summary}

Analysis:

1. VOICE MATCH:
   - Does this dialogue match the character's established voice? (Yes/No/Partially)
   - Specific elements that match well
   - Elements that seem inconsistent

2. AUTHENTICITY:
   - Does this sound like something the character would actually say?
   - Believability score (1-10)
   - Emotional authenticity

3. CONSISTENCY ISSUES:
   - Any vocabulary that seems wrong for this character
   - Tone or formality level issues
   - Personality contradictions

4. IMPROVEMENT SUGGESTIONS:
   - How to make this dialogue more authentic
   - Alternative phrasings that would fit better
   - Elements to emphasize or adjust

5. APPROVAL STATUS:
   - APPROVED/NEEDS_REVISION/REJECTED
   - Confidence level in assessment

Provide specific, actionable feedback."""

        request = AIRequest(
            prompt=prompt,
            context={
                "character_name": character_name,
                "validation_context": context
            },
            max_tokens=400,
            temperature=0.2
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            return self._parse_dialogue_validation(response.content)
        
        return {"error": response.error, "status": "ERROR"}
    
    def _parse_consistency_analysis(self, content: str, sample_count: int) -> Dict[str, Any]:
        """Parse character consistency analysis."""
        analysis = {
            "consistency_score": 0,
            "voice_consistency": "",
            "personality_alignment": "",
            "speech_patterns": "",
            "emotional_range": "",
            "improvements": "",
            "sample_count": sample_count,
            "overall_assessment": ""
        }
        
        # Extract consistency score
        score_match = re.search(r'(\d+(?:\.\d+)?)/10|(\d+(?:\.\d+)?) out of 10', content)
        if score_match:
            analysis["consistency_score"] = float(score_match.group(1) or score_match.group(2))
        
        # Parse sections
        current_section = None
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            found_section = False
            for section in ['voice consistency', 'personality alignment', 'speech patterns', 
                          'emotional range', 'improvement', 'recommendation']:
                if section in line.lower():
                    current_section = section.replace(' ', '_').replace('improvement', 'improvements')
                    found_section = True
                    break
            
            if not found_section and current_section and current_section in analysis:
                if analysis[current_section]:
                    analysis[current_section] += " " + line
                else:
                    analysis[current_section] = line
        
        analysis["overall_assessment"] = content[:200] + "..." if len(content) > 200 else content
        return analysis
    
    def _parse_voice_guide(self, content: str) -> Dict[str, str]:
        """Parse voice guide into structured sections."""
        guide = {
            "core_voice": "",
            "emotional_expressions": "",
            "relationship_dynamics": "",
            "dos_and_donts": "",
            "sample_phrases": "",
            "context_adaptations": "",
            "summary": ""
        }
        
        current_section = None
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            section_map = {
                'core voice': 'core_voice',
                'emotional': 'emotional_expressions', 
                'relationship': 'relationship_dynamics',
                'dos and donts': 'dos_and_donts',
                'sample phrase': 'sample_phrases',
                'context': 'context_adaptations'
            }
            
            found_header = False
            for header, section_key in section_map.items():
                if header in line.lower():
                    current_section = section_key
                    found_header = True
                    break
            
            if not found_header and current_section and current_section in guide:
                if guide[current_section]:
                    guide[current_section] += " " + line
                else:
                    guide[current_section] = line
        
        guide["summary"] = content[:300] + "..." if len(content) > 300 else content
        return guide
    
    def _summarize_voice_guide(self, voice_guide: Dict[str, str]) -> str:
        """Summarize voice guide for validation prompt."""
        summary_parts = []
        
        if voice_guide.get('core_voice'):
            summary_parts.append(f"Core Voice: {voice_guide['core_voice'][:200]}")
        
        if voice_guide.get('dos_and_donts'):
            summary_parts.append(f"Guidelines: {voice_guide['dos_and_donts'][:150]}")
        
        if voice_guide.get('sample_phrases'):
            summary_parts.append(f"Sample Phrases: {voice_guide['sample_phrases'][:100]}")
        
        return "\n".join(summary_parts) if summary_parts else "No voice guide available"
    
    def _parse_dialogue_validation(self, content: str) -> Dict[str, Any]:
        """Parse dialogue validation response."""
        validation = {
            "voice_match": "unknown",
            "authenticity_score": 0,
            "consistency_issues": [],
            "improvements": "",
            "status": "NEEDS_REVIEW",
            "confidence": 0.5
        }
        
        # Extract status
        if "APPROVED" in content:
            validation["status"] = "APPROVED"
        elif "REJECTED" in content:
            validation["status"] = "REJECTED"
        elif "NEEDS_REVISION" in content:
            validation["status"] = "NEEDS_REVISION"
        
        # Extract scores
        auth_score = re.search(r'(\d+(?:\.\d+)?)/10', content)
        if auth_score:
            validation["authenticity_score"] = float(auth_score.group(1))
        
        # Extract voice match
        if "Yes" in content and "match" in content.lower():
            validation["voice_match"] = "yes"
        elif "No" in content and "match" in content.lower():
            validation["voice_match"] = "no"
        elif "Partially" in content:
            validation["voice_match"] = "partially"
        
        # Extract improvements section
        lines = content.split('\n')
        in_improvements = False
        improvements = []
        
        for line in lines:
            if 'improvement' in line.lower() or 'suggestion' in line.lower():
                in_improvements = True
                continue
            elif in_improvements and line.strip():
                improvements.append(line.strip())
        
        validation["improvements"] = " ".join(improvements) if improvements else "No specific improvements suggested"
        
        return validation


class BatchAIOperations:
    """Batch AI operations for mass content improvement and generation."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.dialogue_engine = IntelligentDialogueEngine(ai_service)
        self.story_analyzer = StoryIntelligenceAnalyzer(ai_service)
        
    def batch_improve_dialogue(self,
                             nodes: Dict[str, Any],
                             improvement_type: str = "general",
                             character_context: Dict[str, Dict[str, Any]] = None) -> Dict[str, Any]:
        """Improve dialogue across all nodes in batch."""
        
        results = {
            "processed": 0,
            "improved": 0,
            "errors": 0,
            "improvements": {},
            "summary": ""
        }
        
        character_context = character_context or {}
        
        for node_id, node in nodes.items():
            try:
                game_data = node.get('game_data', {})
                text = game_data.get('text', '')
                
                if text and len(text.strip()) > 10:  # Only process substantial text
                    # Determine character if possible
                    character = game_data.get('character', 'Unknown')
                    
                    # Build story context for this node
                    story_context = self._build_node_context(node, nodes, character_context)
                    
                    # Improve the dialogue
                    if character in character_context:
                        improved = self.dialogue_engine.enhance_dialogue_with_subtext(
                            text, character, "engage the player", story_context
                        )
                    else:
                        # Fallback to basic improvement
                        improved = self._basic_dialogue_improvement(text, improvement_type)
                    
                    if improved != text:
                        results["improvements"][node_id] = {
                            "original": text,
                            "improved": improved,
                            "character": character
                        }
                        results["improved"] += 1
                    
                    results["processed"] += 1
                    
            except Exception as e:
                results["errors"] += 1
                print(f"Error processing node {node_id}: {e}")
        
        results["summary"] = f"Processed {results['processed']} nodes, improved {results['improved']}, {results['errors']} errors"
        return results
    
    def batch_generate_missing_choices(self,
                                     nodes: Dict[str, Any],
                                     min_choices: int = 2,
                                     story_context: StoryContext = None) -> Dict[str, Any]:
        """Generate missing player choices for nodes that need them."""
        
        results = {
            "nodes_processed": 0,
            "choices_generated": 0,
            "new_choices": {},
            "errors": []
        }
        
        story_context = story_context or StoryContext()
        
        for node_id, node in nodes.items():
            try:
                game_data = node.get('game_data', {})
                current_choices = game_data.get('choices', [])
                
                if len(current_choices) < min_choices:
                    # Generate additional choices
                    situation = game_data.get('text', 'A story situation')
                    character = game_data.get('character', 'Character')
                    
                    # Use context-aware choice generation
                    needed_choices = min_choices - len(current_choices)
                    
                    new_choices = self._generate_contextual_choices(
                        situation, character, needed_choices, story_context
                    )
                    
                    if new_choices:
                        results["new_choices"][node_id] = new_choices
                        results["choices_generated"] += len(new_choices)
                
                results["nodes_processed"] += 1
                
            except Exception as e:
                results["errors"].append(f"Node {node_id}: {str(e)}")
        
        return results
    
    def batch_analyze_story_quality(self,
                                   nodes: Dict[str, Any],
                                   story_context: StoryContext = None) -> Dict[str, Any]:
        """Comprehensive batch analysis of story quality metrics."""
        
        story_context = story_context or StoryContext(nodes=nodes)
        
        # Run multiple analysis types
        analyses = {}
        
        try:
            # Structure analysis
            analyses["structure"] = self.story_analyzer.analyze_story_structure(nodes)
        except Exception as e:
            analyses["structure"] = {"error": str(e)}
        
        try:
            # Plot hole detection
            analyses["plot_holes"] = self.story_analyzer.detect_plot_holes(nodes, story_context)
        except Exception as e:
            analyses["plot_holes"] = [{"error": str(e)}]
        
        try:
            # Improvement suggestions
            analyses["improvements"] = self.story_analyzer.suggest_story_improvements(
                nodes, story_context, "overall"
            )
        except Exception as e:
            analyses["improvements"] = [{"error": str(e)}]
        
        # Calculate overall quality score
        analyses["overall_score"] = self._calculate_quality_score(analyses)
        
        # Generate summary
        analyses["summary"] = self._generate_analysis_summary(analyses)
        
        return analyses
    
    def _build_node_context(self, 
                          node: Dict[str, Any], 
                          all_nodes: Dict[str, Any], 
                          character_context: Dict[str, Dict[str, Any]]) -> StoryContext:
        """Build story context for a specific node."""
        return StoryContext(
            nodes=all_nodes,
            characters=character_context,
            genre="general",  # Could be extracted from project settings
            tone="neutral"
        )
    
    def _basic_dialogue_improvement(self, text: str, improvement_type: str) -> str:
        """Basic dialogue improvement without character context."""
        prompt = f"Improve this dialogue to be more {improvement_type}: \"{text}\"\n\nReturn only the improved dialogue."
        
        request = AIRequest(
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            improved = response.content.strip()
            improved = re.sub(r'^["\']|["\']$', '', improved)
            return improved
        
        return text  # Return original if improvement fails
    
    def _generate_contextual_choices(self, 
                                   situation: str, 
                                   character: str, 
                                   count: int,
                                   story_context: StoryContext) -> List[str]:
        """Generate contextual player choices."""
        prompt = f"""Generate {count} player choice options for this situation: {situation}
        
Character involved: {character}
Story genre: {story_context.genre}
Story tone: {story_context.tone}

Create {count} distinct, meaningful choices that:
1. Lead to different story outcomes
2. Represent different player approaches/personalities
3. Are appropriate for the situation and tone
4. Give the player meaningful agency

Return each choice on a separate line, without numbering."""

        request = AIRequest(
            prompt=prompt,
            max_tokens=200,
            temperature=0.8
        )
        
        response = self.ai_service.generate_content_sync(request)
        
        if response.success:
            lines = response.content.strip().split('\n')
            choices = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    choices.append(line)
            return choices[:count]
        
        return []
    
    def _calculate_quality_score(self, analyses: Dict[str, Any]) -> float:
        """Calculate overall story quality score from analyses."""
        scores = []
        
        # Extract scores from different analyses
        if "structure" in analyses and isinstance(analyses["structure"], dict):
            if "overall_score" in analyses["structure"]:
                scores.append(analyses["structure"]["overall_score"])
        
        # Score based on plot holes (fewer = better)
        if "plot_holes" in analyses and isinstance(analyses["plot_holes"], list):
            hole_count = len([hole for hole in analyses["plot_holes"] if not hole.get("error")])
            # Convert to score (0 holes = 10, 5+ holes = 5)
            hole_score = max(5, 10 - hole_count)
            scores.append(hole_score)
        
        # Score based on number of improvement suggestions (fewer = better)
        if "improvements" in analyses and isinstance(analyses["improvements"], list):
            improvement_count = len([imp for imp in analyses["improvements"] if not imp.get("error")])
            improvement_score = max(5, 10 - improvement_count * 0.5)
            scores.append(improvement_score)
        
        return sum(scores) / len(scores) if scores else 5.0  # Default to middle score
    
    def _generate_analysis_summary(self, analyses: Dict[str, Any]) -> str:
        """Generate human-readable summary of all analyses."""
        summary_parts = []
        
        # Overall score
        score = analyses.get("overall_score", 0)
        if score >= 8:
            summary_parts.append(f"Excellent story quality (Score: {score:.1f}/10)")
        elif score >= 6:
            summary_parts.append(f"Good story quality (Score: {score:.1f}/10)")
        elif score >= 4:
            summary_parts.append(f"Fair story quality (Score: {score:.1f}/10)")
        else:
            summary_parts.append(f"Story needs improvement (Score: {score:.1f}/10)")
        
        # Plot holes
        if "plot_holes" in analyses:
            hole_count = len([h for h in analyses["plot_holes"] if not h.get("error")])
            if hole_count == 0:
                summary_parts.append("No plot holes detected")
            else:
                summary_parts.append(f"{hole_count} potential plot issue(s) found")
        
        # Improvements
        if "improvements" in analyses:
            improvement_count = len([i for i in analyses["improvements"] if not i.get("error")])
            if improvement_count > 0:
                summary_parts.append(f"{improvement_count} improvement suggestion(s) available")
        
        return ". ".join(summary_parts) + "."


# Initialize enhanced generators with AI service
def create_enhanced_ai_system(ai_service: AIService) -> Dict[str, Any]:
    """Factory function to create the complete enhanced AI system."""
    
    return {
        "dialogue_engine": IntelligentDialogueEngine(ai_service),
        "story_analyzer": StoryIntelligenceAnalyzer(ai_service),
        "character_engine": CharacterConsistencyEngine(ai_service),
        "batch_operations": BatchAIOperations(ai_service),
        "ai_service": ai_service
    }