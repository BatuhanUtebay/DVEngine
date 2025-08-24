"""Contextual AI Suggestions System - Intelligent, real-time story assistance."""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time

from .enhanced_generators import StoryContext, IntelligentDialogueEngine, StoryIntelligenceAnalyzer
from .ai_service import AIService, AIRequest


class SuggestionContext(Enum):
    """Different contexts where AI suggestions can be triggered."""
    NODE_CREATION = "node_creation"
    NODE_EDITING = "node_editing" 
    CHOICE_CREATION = "choice_creation"
    CHARACTER_DIALOGUE = "character_dialogue"
    STORY_STRUCTURE = "story_structure"
    PROJECT_START = "project_start"
    PROJECT_COMPLETE = "project_complete"


class SuggestionPriority(Enum):
    """Priority levels for AI suggestions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AISuggestion:
    """A single AI suggestion with metadata."""
    id: str
    context: SuggestionContext
    priority: SuggestionPriority
    title: str
    description: str
    action_text: str
    action_callback: Optional[callable] = None
    dismissible: bool = True
    auto_apply: bool = False
    metadata: Dict[str, Any] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}


class ContextualAIAssistant:
    """Provides intelligent, contextual suggestions throughout the DVGE workflow."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.dialogue_engine = IntelligentDialogueEngine(ai_service)
        self.story_analyzer = StoryIntelligenceAnalyzer(ai_service)
        
        # Suggestion history and state
        self.suggestion_history: List[AISuggestion] = []
        self.active_suggestions: Dict[str, AISuggestion] = {}
        self.dismissed_suggestions: set = set()
        self.user_preferences = {
            'suggestion_frequency': 'medium',  # low, medium, high
            'auto_suggestions': True,
            'preferred_contexts': list(SuggestionContext),
            'min_priority': SuggestionPriority.LOW
        }
        
    def analyze_current_context(self, 
                              app_state: Dict[str, Any], 
                              current_action: str = None) -> List[AISuggestion]:
        """Analyze current application state and generate contextual suggestions."""
        
        suggestions = []
        
        # Determine current context
        context = self._determine_context(app_state, current_action)
        
        # Generate suggestions based on context
        if context == SuggestionContext.PROJECT_START:
            suggestions.extend(self._get_project_start_suggestions(app_state))
        elif context == SuggestionContext.NODE_CREATION:
            suggestions.extend(self._get_node_creation_suggestions(app_state))
        elif context == SuggestionContext.NODE_EDITING:
            suggestions.extend(self._get_node_editing_suggestions(app_state))
        elif context == SuggestionContext.CHOICE_CREATION:
            suggestions.extend(self._get_choice_creation_suggestions(app_state))
        elif context == SuggestionContext.CHARACTER_DIALOGUE:
            suggestions.extend(self._get_character_dialogue_suggestions(app_state))
        elif context == SuggestionContext.STORY_STRUCTURE:
            suggestions.extend(self._get_story_structure_suggestions(app_state))
        elif context == SuggestionContext.PROJECT_COMPLETE:
            suggestions.extend(self._get_project_completion_suggestions(app_state))
        
        # Filter suggestions based on user preferences
        suggestions = self._filter_suggestions(suggestions)
        
        # Update active suggestions
        self._update_active_suggestions(suggestions)
        
        return suggestions
    
    def _determine_context(self, app_state: Dict[str, Any], current_action: str = None) -> SuggestionContext:
        """Determine the current context for suggestions."""
        
        # Check if project is just starting
        if not app_state.get('nodes') or len(app_state.get('nodes', {})) == 0:
            return SuggestionContext.PROJECT_START
        
        # Check if project seems complete
        if self._is_project_complete(app_state):
            return SuggestionContext.PROJECT_COMPLETE
        
        # Check current action context
        if current_action:
            if 'create_node' in current_action:
                return SuggestionContext.NODE_CREATION
            elif 'edit_node' in current_action:
                return SuggestionContext.NODE_EDITING
            elif 'add_choice' in current_action:
                return SuggestionContext.CHOICE_CREATION
        
        # Check selected node type
        selected_nodes = app_state.get('selected_nodes', [])
        if selected_nodes:
            node = app_state.get('nodes', {}).get(selected_nodes[0])
            if node and node.get('game_data', {}).get('character'):
                return SuggestionContext.CHARACTER_DIALOGUE
        
        # Default to story structure context
        return SuggestionContext.STORY_STRUCTURE
    
    def _get_project_start_suggestions(self, app_state: Dict[str, Any]) -> List[AISuggestion]:
        """Generate suggestions for new projects."""
        suggestions = []
        
        # Suggest using story templates
        suggestions.append(AISuggestion(
            id="project_start_template",
            context=SuggestionContext.PROJECT_START,
            priority=SuggestionPriority.HIGH,
            title="Start with a Story Template",
            description="AI can generate a complete story structure based on your preferences. This gives you a solid foundation to build upon.",
            action_text="Generate Story Template",
            action_callback=lambda: self._generate_story_template(app_state),
            metadata={"category": "template", "estimated_time": "2 minutes"}
        ))
        
        # Suggest setting up character profiles
        suggestions.append(AISuggestion(
            id="project_start_characters",
            context=SuggestionContext.PROJECT_START, 
            priority=SuggestionPriority.MEDIUM,
            title="Define Your Main Characters",
            description="Create detailed character profiles to ensure consistent voices throughout your story.",
            action_text="Create Character Profiles",
            action_callback=lambda: self._create_character_profiles(app_state),
            metadata={"category": "character", "estimated_time": "5 minutes"}
        ))
        
        # Suggest setting story theme and tone
        suggestions.append(AISuggestion(
            id="project_start_theme",
            context=SuggestionContext.PROJECT_START,
            priority=SuggestionPriority.MEDIUM,
            title="Establish Story Theme and Tone",
            description="Define your story's genre, themes, and tone to get more targeted AI assistance.",
            action_text="Set Theme & Tone", 
            action_callback=lambda: self._setup_story_theme(app_state),
            metadata={"category": "setup", "estimated_time": "3 minutes"}
        ))
        
        return suggestions
    
    def _get_node_creation_suggestions(self, app_state: Dict[str, Any]) -> List[AISuggestion]:
        """Generate suggestions when creating new nodes."""
        suggestions = []
        
        # Analyze story flow to suggest node type
        existing_nodes = app_state.get('nodes', {})
        
        if len(existing_nodes) == 0:
            # First node suggestions
            suggestions.append(AISuggestion(
                id="first_node_dialogue",
                context=SuggestionContext.NODE_CREATION,
                priority=SuggestionPriority.HIGH,
                title="Start with an Engaging Opening",
                description="Your first node sets the tone for the entire story. Let AI help create a compelling opening.",
                action_text="Generate Opening Scene",
                action_callback=lambda: self._generate_opening_scene(app_state)
            ))
        else:
            # Suggest node types based on story structure
            suggestions.extend(self._suggest_next_node_types(existing_nodes))
        
        return suggestions
    
    def _get_node_editing_suggestions(self, app_state: Dict[str, Any]) -> List[AISuggestion]:
        """Generate suggestions for node editing."""
        suggestions = []
        
        selected_nodes = app_state.get('selected_nodes', [])
        if not selected_nodes:
            return suggestions
        
        current_node = app_state.get('nodes', {}).get(selected_nodes[0])
        if not current_node:
            return suggestions
        
        game_data = current_node.get('game_data', {})
        
        # Check dialogue quality
        if game_data.get('text'):
            suggestions.append(AISuggestion(
                id="enhance_dialogue",
                context=SuggestionContext.NODE_EDITING,
                priority=SuggestionPriority.MEDIUM,
                title="Enhance Dialogue Quality",
                description="AI can improve this dialogue to be more engaging and character-appropriate.",
                action_text="Enhance with AI",
                action_callback=lambda: self._enhance_node_dialogue(current_node)
            ))
        
        # Check for missing choices
        choices = game_data.get('choices', [])
        if len(choices) < 2 and game_data.get('text'):
            suggestions.append(AISuggestion(
                id="add_choices",
                context=SuggestionContext.NODE_EDITING,
                priority=SuggestionPriority.HIGH,
                title="Add Player Choices",
                description="This node could benefit from player choices to increase engagement and branching.",
                action_text="Generate Choices",
                action_callback=lambda: self._generate_node_choices(current_node)
            ))
        
        # Character consistency check
        if game_data.get('character'):
            character_name = game_data['character']
            dialogue_count = self._count_character_dialogue(app_state, character_name)
            
            if dialogue_count >= 3:  # Need multiple samples for analysis
                suggestions.append(AISuggestion(
                    id="check_voice_consistency",
                    context=SuggestionContext.NODE_EDITING,
                    priority=SuggestionPriority.LOW,
                    title="Check Character Voice Consistency",
                    description=f"Analyze {character_name}'s voice consistency across all dialogue.",
                    action_text="Analyze Voice",
                    action_callback=lambda: self._analyze_character_voice(app_state, character_name)
                ))
        
        return suggestions
    
    def _get_choice_creation_suggestions(self, app_state: Dict[str, Any]) -> List[AISuggestion]:
        """Generate suggestions for choice creation."""
        suggestions = []
        
        # Suggest meaningful choice consequences
        suggestions.append(AISuggestion(
            id="meaningful_choices",
            context=SuggestionContext.CHOICE_CREATION,
            priority=SuggestionPriority.HIGH,
            title="Create Meaningful Consequences",
            description="Make sure each choice leads to different outcomes that matter to the player.",
            action_text="Analyze Choice Impact",
            action_callback=lambda: self._analyze_choice_consequences(app_state)
        ))
        
        # Suggest personality-based choices
        suggestions.append(AISuggestion(
            id="personality_choices",
            context=SuggestionContext.CHOICE_CREATION,
            priority=SuggestionPriority.MEDIUM,
            title="Add Personality-Based Options",
            description="Include choices that reflect different player personality types (aggressive, diplomatic, curious, etc.).",
            action_text="Generate Personality Choices",
            action_callback=lambda: self._generate_personality_choices(app_state)
        ))
        
        return suggestions
    
    def _get_character_dialogue_suggestions(self, app_state: Dict[str, Any]) -> List[AISuggestion]:
        """Generate suggestions for character dialogue."""
        suggestions = []
        
        selected_nodes = app_state.get('selected_nodes', [])
        if not selected_nodes:
            return suggestions
        
        current_node = app_state.get('nodes', {}).get(selected_nodes[0])
        character = current_node.get('game_data', {}).get('character')
        
        if not character:
            return suggestions
        
        # Voice guide generation
        suggestions.append(AISuggestion(
            id="create_voice_guide",
            context=SuggestionContext.CHARACTER_DIALOGUE,
            priority=SuggestionPriority.MEDIUM,
            title="Create Character Voice Guide",
            description=f"Generate a comprehensive voice guide for {character} to ensure consistent writing.",
            action_text="Create Voice Guide",
            action_callback=lambda: self._create_voice_guide(app_state, character)
        ))
        
        # Emotional range suggestion
        suggestions.append(AISuggestion(
            id="expand_emotional_range",
            context=SuggestionContext.CHARACTER_DIALOGUE,
            priority=SuggestionPriority.LOW,
            title="Expand Emotional Range",
            description=f"Show {character} expressing different emotions to create a more dynamic character.",
            action_text="Generate Emotional Variants",
            action_callback=lambda: self._generate_emotional_variants(app_state, character)
        ))
        
        return suggestions
    
    def _get_story_structure_suggestions(self, app_state: Dict[str, Any]) -> List[AISuggestion]:
        """Generate suggestions for overall story structure."""
        suggestions = []
        
        nodes = app_state.get('nodes', {})
        node_count = len(nodes)
        
        # Pacing analysis
        if node_count >= 5:
            suggestions.append(AISuggestion(
                id="analyze_pacing",
                context=SuggestionContext.STORY_STRUCTURE,
                priority=SuggestionPriority.MEDIUM,
                title="Analyze Story Pacing",
                description="Check if your story has good pacing and emotional rhythm.",
                action_text="Analyze Pacing",
                action_callback=lambda: self._analyze_story_pacing(app_state)
            ))
        
        # Plot hole detection
        if node_count >= 3:
            suggestions.append(AISuggestion(
                id="detect_plot_holes",
                context=SuggestionContext.STORY_STRUCTURE,
                priority=SuggestionPriority.HIGH,
                title="Check for Plot Holes",
                description="AI can identify logical inconsistencies and continuity issues in your story.",
                action_text="Find Plot Issues",
                action_callback=lambda: self._detect_plot_holes(app_state)
            ))
        
        # Branching quality
        if node_count >= 4:
            suggestions.append(AISuggestion(
                id="improve_branching",
                context=SuggestionContext.STORY_STRUCTURE,
                priority=SuggestionPriority.MEDIUM,
                title="Improve Story Branching",
                description="Analyze the quality and meaningfulness of your story branches.",
                action_text="Analyze Branching",
                action_callback=lambda: self._analyze_branching_quality(app_state)
            ))
        
        return suggestions
    
    def _get_project_completion_suggestions(self, app_state: Dict[str, Any]) -> List[AISuggestion]:
        """Generate suggestions for project completion."""
        suggestions = []
        
        # Final quality check
        suggestions.append(AISuggestion(
            id="final_quality_check",
            context=SuggestionContext.PROJECT_COMPLETE,
            priority=SuggestionPriority.CRITICAL,
            title="Final Quality Assessment",
            description="Run a comprehensive AI analysis before publishing your story.",
            action_text="Run Final Check",
            action_callback=lambda: self._run_final_quality_check(app_state)
        ))
        
        # Export optimization
        suggestions.append(AISuggestion(
            id="optimize_export",
            context=SuggestionContext.PROJECT_COMPLETE,
            priority=SuggestionPriority.HIGH,
            title="Optimize for Export",
            description="Ensure your story is optimized for the best player experience.",
            action_text="Optimize Story",
            action_callback=lambda: self._optimize_for_export(app_state)
        ))
        
        # Playtesting suggestions
        suggestions.append(AISuggestion(
            id="playtesting_tips",
            context=SuggestionContext.PROJECT_COMPLETE,
            priority=SuggestionPriority.MEDIUM,
            title="Playtesting Recommendations",
            description="Get AI-generated tips for effective playtesting of your interactive story.",
            action_text="Get Testing Tips",
            action_callback=lambda: self._get_playtesting_tips(app_state)
        ))
        
        return suggestions
    
    def _filter_suggestions(self, suggestions: List[AISuggestion]) -> List[AISuggestion]:
        """Filter suggestions based on user preferences and history."""
        filtered = []
        
        for suggestion in suggestions:
            # Skip dismissed suggestions
            if suggestion.id in self.dismissed_suggestions:
                continue
            
            # Check priority preference
            if suggestion.priority.value < self.user_preferences['min_priority'].value:
                continue
            
            # Check context preferences
            if suggestion.context not in self.user_preferences['preferred_contexts']:
                continue
            
            # Avoid duplicate active suggestions
            if suggestion.id in self.active_suggestions:
                continue
            
            filtered.append(suggestion)
        
        # Limit number of suggestions based on frequency preference
        frequency = self.user_preferences['suggestion_frequency']
        max_suggestions = {'low': 1, 'medium': 3, 'high': 5}[frequency]
        
        # Sort by priority and take top suggestions
        filtered.sort(key=lambda s: ['critical', 'high', 'medium', 'low'].index(s.priority.value))
        return filtered[:max_suggestions]
    
    def _update_active_suggestions(self, suggestions: List[AISuggestion]):
        """Update the active suggestions list."""
        for suggestion in suggestions:
            self.active_suggestions[suggestion.id] = suggestion
            self.suggestion_history.append(suggestion)
        
        # Clean up old suggestions (keep last 50)
        if len(self.suggestion_history) > 50:
            self.suggestion_history = self.suggestion_history[-50:]
    
    def dismiss_suggestion(self, suggestion_id: str, permanent: bool = False):
        """Dismiss a suggestion."""
        if suggestion_id in self.active_suggestions:
            del self.active_suggestions[suggestion_id]
        
        if permanent:
            self.dismissed_suggestions.add(suggestion_id)
    
    def apply_suggestion(self, suggestion_id: str) -> bool:
        """Apply a suggestion if it has an action callback."""
        if suggestion_id in self.active_suggestions:
            suggestion = self.active_suggestions[suggestion_id]
            if suggestion.action_callback:
                try:
                    suggestion.action_callback()
                    self.dismiss_suggestion(suggestion_id)
                    return True
                except Exception as e:
                    print(f"Error applying suggestion {suggestion_id}: {e}")
                    return False
        return False
    
    # Helper methods for suggestion callbacks (simplified implementations)
    
    def _is_project_complete(self, app_state: Dict[str, Any]) -> bool:
        """Check if project seems complete."""
        nodes = app_state.get('nodes', {})
        if len(nodes) < 3:
            return False
        
        # Check if there are ending nodes and good branching
        has_endings = any(
            len(node.get('game_data', {}).get('choices', [])) == 0 
            for node in nodes.values()
        )
        
        return has_endings and len(nodes) >= 5
    
    def _count_character_dialogue(self, app_state: Dict[str, Any], character: str) -> int:
        """Count dialogue instances for a character."""
        count = 0
        for node in app_state.get('nodes', {}).values():
            game_data = node.get('game_data', {})
            if game_data.get('character') == character and game_data.get('text'):
                count += 1
        return count
    
    def _suggest_next_node_types(self, existing_nodes: Dict[str, Any]) -> List[AISuggestion]:
        """Suggest appropriate next node types based on story structure."""
        suggestions = []
        
        # Analyze existing node types
        node_types = {}
        for node in existing_nodes.values():
            node_type = node.get('node_type', 'dialogue')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        total_nodes = len(existing_nodes)
        dialogue_ratio = node_types.get('dialogue', 0) / total_nodes
        
        # Suggest variety if too much dialogue
        if dialogue_ratio > 0.7 and total_nodes > 3:
            suggestions.append(AISuggestion(
                id="add_variety_nodes",
                context=SuggestionContext.NODE_CREATION,
                priority=SuggestionPriority.MEDIUM,
                title="Add Story Variety",
                description="Your story is mostly dialogue. Consider adding action, choices, or special events.",
                action_text="Suggest Node Types",
                action_callback=lambda: self._suggest_variety_nodes(existing_nodes)
            ))
        
        return suggestions
    
    # Placeholder callback implementations (would be fully implemented in real system)
    
    def _generate_story_template(self, app_state: Dict[str, Any]):
        """Generate AI story template."""
        print("Generating story template...")
    
    def _create_character_profiles(self, app_state: Dict[str, Any]):
        """Create character profiles."""
        print("Creating character profiles...")
    
    def _setup_story_theme(self, app_state: Dict[str, Any]):
        """Setup story theme and tone."""
        print("Setting up story theme...")
    
    def _generate_opening_scene(self, app_state: Dict[str, Any]):
        """Generate opening scene."""
        print("Generating opening scene...")
    
    def _enhance_node_dialogue(self, node: Dict[str, Any]):
        """Enhance node dialogue."""
        print("Enhancing dialogue...")
    
    def _generate_node_choices(self, node: Dict[str, Any]):
        """Generate choices for node."""
        print("Generating choices...")
    
    def _analyze_character_voice(self, app_state: Dict[str, Any], character: str):
        """Analyze character voice consistency."""
        print(f"Analyzing {character}'s voice...")
    
    def _analyze_choice_consequences(self, app_state: Dict[str, Any]):
        """Analyze choice consequences."""
        print("Analyzing choice consequences...")
    
    def _generate_personality_choices(self, app_state: Dict[str, Any]):
        """Generate personality-based choices."""
        print("Generating personality choices...")
    
    def _create_voice_guide(self, app_state: Dict[str, Any], character: str):
        """Create character voice guide."""
        print(f"Creating voice guide for {character}...")
    
    def _generate_emotional_variants(self, app_state: Dict[str, Any], character: str):
        """Generate emotional dialogue variants."""
        print(f"Generating emotional variants for {character}...")
    
    def _analyze_story_pacing(self, app_state: Dict[str, Any]):
        """Analyze story pacing."""
        print("Analyzing story pacing...")
    
    def _detect_plot_holes(self, app_state: Dict[str, Any]):
        """Detect plot holes."""
        print("Detecting plot holes...")
    
    def _analyze_branching_quality(self, app_state: Dict[str, Any]):
        """Analyze branching quality."""
        print("Analyzing branching quality...")
    
    def _run_final_quality_check(self, app_state: Dict[str, Any]):
        """Run final quality check."""
        print("Running final quality check...")
    
    def _optimize_for_export(self, app_state: Dict[str, Any]):
        """Optimize for export."""
        print("Optimizing for export...")
    
    def _get_playtesting_tips(self, app_state: Dict[str, Any]):
        """Get playtesting tips."""
        print("Getting playtesting tips...")
    
    def _suggest_variety_nodes(self, existing_nodes: Dict[str, Any]):
        """Suggest variety in node types."""
        print("Suggesting node variety...")


class SmartSuggestionDisplay:
    """UI component for displaying contextual AI suggestions."""
    
    def __init__(self, parent_widget, ai_assistant: ContextualAIAssistant):
        """Initialize suggestion display."""
        self.parent = parent_widget
        self.ai_assistant = ai_assistant
        self.suggestion_widgets = {}
        self.update_callback = None
    
    def update_suggestions(self, app_state: Dict[str, Any], current_action: str = None):
        """Update displayed suggestions based on current context."""
        # Get new suggestions
        new_suggestions = self.ai_assistant.analyze_current_context(app_state, current_action)
        
        # Clear existing suggestions
        self._clear_suggestion_widgets()
        
        # Display new suggestions
        for suggestion in new_suggestions:
            self._create_suggestion_widget(suggestion)
    
    def _clear_suggestion_widgets(self):
        """Clear existing suggestion widgets."""
        for widget in self.suggestion_widgets.values():
            widget.destroy()
        self.suggestion_widgets.clear()
    
    def _create_suggestion_widget(self, suggestion: AISuggestion):
        """Create UI widget for a suggestion."""
        # This would create the actual UI widget
        # Implementation depends on the UI framework being used
        pass
    
    def set_update_callback(self, callback: callable):
        """Set callback for when suggestions are applied."""
        self.update_callback = callback


# Factory function to create contextual AI assistant
def create_contextual_assistant(ai_service: AIService) -> ContextualAIAssistant:
    """Create and configure contextual AI assistant."""
    return ContextualAIAssistant(ai_service)