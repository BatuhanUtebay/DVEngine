"""Smart AI Integration for DVGE UI - Contextual AI assistance throughout the editor."""

import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, Any, List, Optional, Callable
import threading
import time

from ..ai.enhanced_generators import (
    create_enhanced_ai_system, 
    StoryContext,
    IntelligentDialogueEngine,
    StoryIntelligenceAnalyzer,
    CharacterConsistencyEngine,
    BatchAIOperations
)


class AIIntegrationManager:
    """Manages AI integration throughout the DVGE UI."""
    
    def __init__(self, app):
        """Initialize AI integration manager."""
        self.app = app
        self.enhanced_ai = None
        self.ai_buttons = {}  # Track AI-enhanced buttons
        self.suggestion_widgets = {}  # Track suggestion displays
        self.current_suggestions = {}  # Current AI suggestions
        
        # Initialize enhanced AI system
        self._initialize_enhanced_ai()
        
        # Track which nodes have AI enhancements available
        self.node_ai_status = {}
        
    def _initialize_enhanced_ai(self):
        """Initialize the enhanced AI system."""
        try:
            if hasattr(self.app, 'ai_service') and self.app.ai_service:
                self.enhanced_ai = create_enhanced_ai_system(self.app.ai_service)
                print("Enhanced AI system initialized successfully")
                return True
        except Exception as e:
            print(f"Failed to initialize enhanced AI system: {e}")
            self.enhanced_ai = None
        return False
    
    def is_ai_available(self) -> bool:
        """Check if enhanced AI system is available."""
        return self.enhanced_ai is not None
    
    def add_ai_enhancements_to_node_editor(self, node_editor_frame):
        """Add AI enhancement buttons to the node editor."""
        if not self.is_ai_available():
            return
            
        # Create AI enhancement frame
        ai_frame = ctk.CTkFrame(node_editor_frame)
        ai_frame.pack(fill="x", padx=5, pady=5)
        
        # AI header
        ai_label = ctk.CTkLabel(
            ai_frame, 
            text="🤖 AI Assistance",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        ai_label.pack(pady=5)
        
        # Create button frame
        button_frame = ctk.CTkFrame(ai_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=5)
        
        # AI Enhancement Buttons
        buttons = [
            ("✨ Enhance Dialogue", self._enhance_current_dialogue, "Improve the current dialogue with AI"),
            ("🎭 Character Voice", self._check_character_voice, "Check character voice consistency"),
            ("🌳 Generate Choices", self._generate_choices, "Generate player choice options"),
            ("🔍 Smart Suggestions", self._show_smart_suggestions, "Get contextual AI suggestions")
        ]
        
        # Arrange buttons in grid
        for i, (text, command, tooltip) in enumerate(buttons):
            btn = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                width=120,
                height=30,
                font=ctk.CTkFont(size=11)
            )
            btn.grid(row=i//2, column=i%2, padx=2, pady=2, sticky="ew")
            
            # Add tooltip (simplified)
            self._add_tooltip(btn, tooltip)
            
            # Track button
            self.ai_buttons[text] = btn
        
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Suggestions display area
        self.suggestions_text = ctk.CTkTextbox(
            ai_frame,
            height=80,
            fg_color=("#F0F0F0", "#2B2B2B"),
            text_color=("#333333", "#CCCCCC")
        )
        self.suggestions_text.pack(fill="x", padx=5, pady=5)
        self.suggestions_text.insert("1.0", "💡 AI suggestions will appear here...")
        
        return ai_frame
    
    def add_batch_ai_menu(self, menu_bar):
        """Add batch AI operations to the menu bar."""
        if not self.is_ai_available():
            return
            
        # Create AI menu
        ai_menu = ctk.CTkOptionMenu(menu_bar, values=["AI Tools"])
        
        # Would need to integrate with tkinter menu system
        # This is a simplified version - full implementation would add to existing menu
        pass
    
    def _enhance_current_dialogue(self):
        """Enhance the currently selected dialogue with AI."""
        if not self.is_ai_available():
            self._show_ai_unavailable()
            return
            
        current_node = self._get_current_node()
        if not current_node:
            messagebox.showwarning("No Node Selected", "Please select a node to enhance.")
            return
        
        game_data = current_node.get('game_data', {})
        current_text = game_data.get('text', '')
        
        if not current_text.strip():
            messagebox.showwarning("No Text", "The selected node has no text to enhance.")
            return
        
        # Show loading state
        self._set_ai_status("Enhancing dialogue with AI...")
        
        # Run AI enhancement in background
        def enhance_worker():
            try:
                # Build story context
                story_context = self._build_current_story_context()
                
                # Get character info
                character = game_data.get('character', 'Character')
                
                # Enhance dialogue
                dialogue_engine = self.enhanced_ai['dialogue_engine']
                enhanced_text = dialogue_engine.enhance_dialogue_with_subtext(
                    current_text,
                    character,
                    "engage and intrigue the player",
                    story_context
                )
                
                # Update UI on main thread
                self.app.after(0, lambda: self._apply_dialogue_enhancement(enhanced_text, current_text))
                
            except Exception as e:
                self.app.after(0, lambda: self._show_ai_error(f"Enhancement failed: {str(e)}"))
        
        thread = threading.Thread(target=enhance_worker)
        thread.daemon = True
        thread.start()
    
    def _check_character_voice(self):
        """Check character voice consistency for current node."""
        if not self.is_ai_available():
            self._show_ai_unavailable()
            return
            
        current_node = self._get_current_node()
        if not current_node:
            messagebox.showwarning("No Node Selected", "Please select a node to analyze.")
            return
        
        # Get character dialogue samples from all nodes
        character = current_node.get('game_data', {}).get('character', 'Unknown')
        dialogue_samples = self._get_character_dialogue_samples(character)
        
        if len(dialogue_samples) < 2:
            messagebox.showinfo(
                "Insufficient Data", 
                f"Need at least 2 dialogue samples for {character} to analyze voice consistency."
            )
            return
        
        self._set_ai_status("Analyzing character voice consistency...")
        
        def analyze_worker():
            try:
                character_engine = self.enhanced_ai['character_engine']
                
                # Get character profile (simplified)
                character_profile = self._get_character_profile(character)
                
                # Analyze consistency
                analysis = character_engine.analyze_character_consistency(
                    character,
                    dialogue_samples,
                    character_profile
                )
                
                # Show results on main thread
                self.app.after(0, lambda: self._show_voice_analysis(character, analysis))
                
            except Exception as e:
                self.app.after(0, lambda: self._show_ai_error(f"Voice analysis failed: {str(e)}"))
        
        thread = threading.Thread(target=analyze_worker)
        thread.daemon = True
        thread.start()
    
    def _generate_choices(self):
        """Generate player choices for the current node."""
        if not self.is_ai_available():
            self._show_ai_unavailable()
            return
            
        current_node = self._get_current_node()
        if not current_node:
            messagebox.showwarning("No Node Selected", "Please select a node to add choices to.")
            return
        
        game_data = current_node.get('game_data', {})
        situation = game_data.get('text', '')
        character = game_data.get('character', 'Character')
        
        if not situation.strip():
            messagebox.showwarning("No Context", "The node needs some text to generate appropriate choices.")
            return
        
        self._set_ai_status("Generating player choices...")
        
        def generate_worker():
            try:
                dialogue_engine = self.enhanced_ai['dialogue_engine']
                story_context = self._build_current_story_context()
                
                # Generate branching dialogue (simplified to just get choices)
                tree = dialogue_engine.generate_branching_dialogue_tree(
                    character, situation, story_context, depth=1, choices_per_level=3
                )
                
                if tree and 'root' in tree and 'player_choices' in tree['root']:
                    choices = [choice['text'] for choice in tree['root']['player_choices']]
                    self.app.after(0, lambda: self._apply_generated_choices(choices))
                else:
                    self.app.after(0, lambda: self._show_ai_error("Failed to generate choices"))
                
            except Exception as e:
                self.app.after(0, lambda: self._show_ai_error(f"Choice generation failed: {str(e)}"))
        
        thread = threading.Thread(target=generate_worker)
        thread.daemon = True
        thread.start()
    
    def _show_smart_suggestions(self):
        """Show contextual AI suggestions for the current situation."""
        if not self.is_ai_available():
            self._show_ai_unavailable()
            return
            
        current_node = self._get_current_node()
        if not current_node:
            self._set_ai_status("💡 Select a node to get AI suggestions...")
            return
        
        self._set_ai_status("Generating smart suggestions...")
        
        def suggest_worker():
            try:
                story_analyzer = self.enhanced_ai['story_analyzer']
                story_context = self._build_current_story_context()
                
                # Get story improvement suggestions
                suggestions = story_analyzer.suggest_story_improvements(
                    {self._get_current_node_id(): current_node},
                    story_context,
                    "engagement"
                )
                
                # Format and show suggestions
                formatted_suggestions = self._format_suggestions(suggestions)
                self.app.after(0, lambda: self._display_suggestions(formatted_suggestions))
                
            except Exception as e:
                self.app.after(0, lambda: self._show_ai_error(f"Suggestion generation failed: {str(e)}"))
        
        thread = threading.Thread(target=suggest_worker)
        thread.daemon = True
        thread.start()
    
    def run_batch_story_analysis(self):
        """Run comprehensive batch analysis of the entire story."""
        if not self.is_ai_available():
            self._show_ai_unavailable()
            return
            
        if not self.app.nodes:
            messagebox.showwarning("No Story", "Create some story nodes first before running analysis.")
            return
        
        # Show progress dialog
        progress_dialog = self._create_progress_dialog("Analyzing Story", "Running comprehensive AI story analysis...")
        
        def analyze_worker():
            try:
                batch_ops = self.enhanced_ai['batch_operations']
                story_context = self._build_current_story_context()
                
                # Run batch analysis
                analysis = batch_ops.batch_analyze_story_quality(
                    self.app.nodes,
                    story_context
                )
                
                # Close progress and show results
                self.app.after(0, lambda: progress_dialog.destroy())
                self.app.after(0, lambda: self._show_story_analysis_results(analysis))
                
            except Exception as e:
                self.app.after(0, lambda: progress_dialog.destroy())
                self.app.after(0, lambda: self._show_ai_error(f"Story analysis failed: {str(e)}"))
        
        thread = threading.Thread(target=analyze_worker)
        thread.daemon = True
        thread.start()
    
    def run_batch_dialogue_improvement(self):
        """Run batch dialogue improvement across all nodes."""
        if not self.is_ai_available():
            self._show_ai_unavailable()
            return
            
        if not self.app.nodes:
            messagebox.showwarning("No Story", "Create some story nodes first.")
            return
        
        # Confirm batch operation
        response = messagebox.askyesno(
            "Batch Improvement",
            f"This will attempt to improve dialogue in all {len(self.app.nodes)} nodes. Continue?"
        )
        
        if not response:
            return
        
        progress_dialog = self._create_progress_dialog("Improving Dialogue", "Enhancing dialogue with AI...")
        
        def improve_worker():
            try:
                batch_ops = self.enhanced_ai['batch_operations']
                
                # Get character context
                character_context = self._build_character_context()
                
                # Run batch improvement
                results = batch_ops.batch_improve_dialogue(
                    self.app.nodes,
                    "engaging",
                    character_context
                )
                
                # Apply improvements and show results
                self.app.after(0, lambda: progress_dialog.destroy())
                self.app.after(0, lambda: self._apply_batch_improvements(results))
                
            except Exception as e:
                self.app.after(0, lambda: progress_dialog.destroy())
                self.app.after(0, lambda: self._show_ai_error(f"Batch improvement failed: {str(e)}"))
        
        thread = threading.Thread(target=improve_worker)
        thread.daemon = True
        thread.start()
    
    # Helper methods for UI integration
    
    def _get_current_node(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected node."""
        if hasattr(self.app, 'selected_nodes') and self.app.selected_nodes:
            node_id = list(self.app.selected_nodes)[0]
            return self.app.nodes.get(node_id)
        return None
    
    def _get_current_node_id(self) -> Optional[str]:
        """Get the currently selected node ID."""
        if hasattr(self.app, 'selected_nodes') and self.app.selected_nodes:
            return list(self.app.selected_nodes)[0]
        return None
    
    def _build_current_story_context(self) -> StoryContext:
        """Build story context from current project state."""
        # Get project settings
        genre = self.app.project_settings.get('genre', 'general')
        tone = self.app.project_settings.get('tone', 'neutral')
        
        # Extract themes (simplified)
        themes = self.app.project_settings.get('themes', [])
        
        # Get character info
        characters = self._build_character_context()
        
        return StoryContext(
            nodes=self.app.nodes,
            characters=characters,
            story_flags=self.app.story_flags,
            variables=getattr(self.app, 'variables', {}),
            themes=themes,
            genre=genre,
            tone=tone
        )
    
    def _build_character_context(self) -> Dict[str, Dict[str, Any]]:
        """Build character context from existing nodes."""
        characters = {}
        
        for node_id, node in self.app.nodes.items():
            game_data = node.get('game_data', {})
            character = game_data.get('character')
            
            if character and character not in characters:
                characters[character] = {
                    'name': character,
                    'dialogue_samples': [],
                    'personality': 'Unknown',
                    'background': 'Unknown'
                }
            
            # Collect dialogue samples
            if character and game_data.get('text'):
                characters[character]['dialogue_samples'].append(game_data['text'])
        
        return characters
    
    def _get_character_dialogue_samples(self, character: str) -> List[str]:
        """Get all dialogue samples for a character."""
        samples = []
        
        for node in self.app.nodes.values():
            game_data = node.get('game_data', {})
            if game_data.get('character') == character and game_data.get('text'):
                samples.append(game_data['text'])
        
        return samples
    
    def _get_character_profile(self, character: str) -> Dict[str, str]:
        """Get character profile (simplified version)."""
        return {
            'name': character,
            'personality': 'Determined',  # Would be extracted from character data
            'background': 'Unknown',
            'speech_style': 'Casual'
        }
    
    def _set_ai_status(self, message: str):
        """Update AI status display."""
        if hasattr(self, 'suggestions_text'):
            self.suggestions_text.delete("1.0", "end")
            self.suggestions_text.insert("1.0", message)
    
    def _apply_dialogue_enhancement(self, enhanced_text: str, original_text: str):
        """Apply dialogue enhancement to current node."""
        if enhanced_text != original_text:
            # Show preview dialog
            preview_dialog = AIEnhancementPreviewDialog(
                self.app,
                "Dialogue Enhancement",
                original_text,
                enhanced_text,
                lambda: self._accept_enhancement(enhanced_text)
            )
        else:
            self._set_ai_status("✨ Dialogue is already well-optimized!")
    
    def _accept_enhancement(self, enhanced_text: str):
        """Accept and apply the AI enhancement."""
        current_node = self._get_current_node()
        if current_node:
            current_node['game_data']['text'] = enhanced_text
            # Trigger UI update
            if hasattr(self.app, 'refresh_node_editor'):
                self.app.refresh_node_editor()
            self._set_ai_status("✅ Enhancement applied successfully!")
    
    def _apply_generated_choices(self, choices: List[str]):
        """Apply generated choices to current node."""
        if choices:
            preview_dialog = ChoicePreviewDialog(
                self.app,
                "Generated Choices",
                choices,
                lambda selected_choices: self._accept_choices(selected_choices)
            )
        else:
            self._set_ai_status("❌ Failed to generate suitable choices")
    
    def _accept_choices(self, choices: List[str]):
        """Accept and add generated choices to current node."""
        current_node = self._get_current_node()
        if current_node:
            game_data = current_node.get('game_data', {})
            if 'choices' not in game_data:
                game_data['choices'] = []
            
            # Add new choices
            for i, choice_text in enumerate(choices):
                game_data['choices'].append({
                    'id': f"ai_choice_{int(time.time())}_{i}",
                    'text': choice_text,
                    'target_node': None  # User will connect these
                })
            
            # Trigger UI update
            if hasattr(self.app, 'refresh_node_editor'):
                self.app.refresh_node_editor()
            
            self._set_ai_status(f"✅ Added {len(choices)} AI-generated choices!")
    
    def _show_voice_analysis(self, character: str, analysis: Dict[str, Any]):
        """Show character voice analysis results."""
        dialog = VoiceAnalysisDialog(self.app, character, analysis)
    
    def _display_suggestions(self, suggestions: str):
        """Display AI suggestions."""
        self._set_ai_status(f"💡 AI Suggestions:\\n{suggestions}")
    
    def _format_suggestions(self, suggestions: List[Dict[str, str]]) -> str:
        """Format suggestions for display."""
        if not suggestions:
            return "No specific suggestions available."
        
        formatted = []
        for i, suggestion in enumerate(suggestions[:3], 1):  # Limit to top 3
            improvement = suggestion.get('improvement', 'General improvement')
            reason = suggestion.get('reason', 'Will enhance the story')
            formatted.append(f"{i}. {improvement} - {reason}")
        
        return "\\n".join(formatted)
    
    def _show_story_analysis_results(self, analysis: Dict[str, Any]):
        """Show comprehensive story analysis results."""
        dialog = StoryAnalysisDialog(self.app, analysis)
    
    def _apply_batch_improvements(self, results: Dict[str, Any]):
        """Apply batch dialogue improvements."""
        if results.get('improvements'):
            # Show preview dialog for batch changes
            dialog = BatchImprovementDialog(
                self.app,
                results,
                lambda accepted_improvements: self._accept_batch_improvements(accepted_improvements)
            )
        else:
            messagebox.showinfo("Batch Improvement", f"Analysis complete: {results.get('summary', 'No improvements needed')}")
    
    def _accept_batch_improvements(self, improvements: Dict[str, Dict[str, str]]):
        """Accept and apply batch improvements."""
        for node_id, improvement in improvements.items():
            if node_id in self.app.nodes:
                self.app.nodes[node_id]['game_data']['text'] = improvement['improved']
        
        # Trigger full UI refresh
        if hasattr(self.app, 'refresh_canvas'):
            self.app.refresh_canvas()
        
        messagebox.showinfo("Batch Improvement", f"Applied improvements to {len(improvements)} nodes!")
    
    def _show_ai_unavailable(self):
        """Show AI unavailable message."""
        messagebox.showwarning(
            "AI Unavailable",
            "Enhanced AI features are not available. Please check your AI service configuration."
        )
    
    def _show_ai_error(self, error_message: str):
        """Show AI error message."""
        messagebox.showerror("AI Error", error_message)
        self._set_ai_status(f"❌ {error_message}")
    
    def _add_tooltip(self, widget, text: str):
        """Add simple tooltip to widget."""
        def show_tooltip(event):
            # Simplified tooltip - full implementation would create proper tooltip widget
            pass
    
    def _create_progress_dialog(self, title: str, message: str):
        """Create a simple progress dialog."""
        dialog = ctk.CTkToplevel(self.app)
        dialog.title(title)
        dialog.geometry("300x100")
        
        label = ctk.CTkLabel(dialog, text=message)
        label.pack(pady=20)
        
        progress = ctk.CTkProgressBar(dialog, mode="indeterminate")
        progress.pack(pady=10)
        progress.start()
        
        return dialog


# Dialog classes for AI features

class AIEnhancementPreviewDialog(ctk.CTkToplevel):
    """Dialog to preview AI enhancements before applying."""
    
    def __init__(self, parent, title: str, original: str, enhanced: str, accept_callback: Callable):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("600x400")
        self.accept_callback = accept_callback
        
        # Create layout
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text=title, font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=10)
        
        # Comparison frame
        comparison_frame = ctk.CTkFrame(main_frame)
        comparison_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Original text
        original_label = ctk.CTkLabel(comparison_frame, text="Original:", font=ctk.CTkFont(weight="bold"))
        original_label.pack(anchor="w", padx=10, pady=(10,5))
        
        original_text = ctk.CTkTextbox(comparison_frame, height=100)
        original_text.pack(fill="x", padx=10, pady=5)
        original_text.insert("1.0", original)
        original_text.configure(state="disabled")
        
        # Enhanced text
        enhanced_label = ctk.CTkLabel(comparison_frame, text="AI Enhanced:", font=ctk.CTkFont(weight="bold"))
        enhanced_label.pack(anchor="w", padx=10, pady=(10,5))
        
        enhanced_text = ctk.CTkTextbox(comparison_frame, height=100)
        enhanced_text.pack(fill="x", padx=10, pady=5)
        enhanced_text.insert("1.0", enhanced)
        enhanced_text.configure(state="disabled")
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        accept_btn = ctk.CTkButton(button_frame, text="✅ Accept Enhancement", command=self._accept)
        accept_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="❌ Cancel", command=self.destroy)
        cancel_btn.pack(side="left", padx=10)
    
    def _accept(self):
        """Accept the enhancement."""
        self.accept_callback()
        self.destroy()


class ChoicePreviewDialog(ctk.CTkToplevel):
    """Dialog to preview and select generated choices."""
    
    def __init__(self, parent, title: str, choices: List[str], accept_callback: Callable):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("500x400")
        self.choices = choices
        self.accept_callback = accept_callback
        self.choice_vars = []
        
        # Create layout
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text=title, font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=10)
        
        # Instructions
        instructions = ctk.CTkLabel(main_frame, text="Select which choices to add to your node:")
        instructions.pack(pady=5)
        
        # Choices frame
        choices_frame = ctk.CTkScrollableFrame(main_frame)
        choices_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add checkboxes for each choice
        for i, choice in enumerate(choices):
            var = ctk.StringVar(value=choice)
            checkbox = ctk.CTkCheckBox(
                choices_frame, 
                text=choice,
                variable=var,
                onvalue=choice,
                offvalue=""
            )
            checkbox.pack(anchor="w", pady=5, padx=10)
            checkbox.select()  # Select all by default
            self.choice_vars.append(var)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        accept_btn = ctk.CTkButton(button_frame, text="✅ Add Selected Choices", command=self._accept)
        accept_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="❌ Cancel", command=self.destroy)
        cancel_btn.pack(side="left", padx=10)
    
    def _accept(self):
        """Accept selected choices."""
        selected_choices = [var.get() for var in self.choice_vars if var.get()]
        if selected_choices:
            self.accept_callback(selected_choices)
        self.destroy()


class VoiceAnalysisDialog(ctk.CTkToplevel):
    """Dialog to show character voice analysis results."""
    
    def __init__(self, parent, character: str, analysis: Dict[str, Any]):
        super().__init__(parent)
        
        self.title(f"Voice Analysis: {character}")
        self.geometry("600x500")
        
        # Create layout
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text=f"🎭 Character Voice Analysis: {character}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Consistency score
        score = analysis.get('consistency_score', 0)
        score_label = ctk.CTkLabel(
            main_frame,
            text=f"Overall Consistency Score: {score:.1f}/10",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        score_label.pack(pady=5)
        
        # Analysis results
        results_frame = ctk.CTkScrollableFrame(main_frame)
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        sections = [
            ("Voice Consistency", analysis.get('voice_consistency', '')),
            ("Personality Alignment", analysis.get('personality_alignment', '')),
            ("Speech Patterns", analysis.get('speech_patterns', '')),
            ("Improvements", analysis.get('improvements', ''))
        ]
        
        for section_title, section_content in sections:
            if section_content:
                section_label = ctk.CTkLabel(
                    results_frame,
                    text=section_title,
                    font=ctk.CTkFont(weight="bold")
                )
                section_label.pack(anchor="w", pady=(10,5))
                
                content_text = ctk.CTkTextbox(results_frame, height=80)
                content_text.pack(fill="x", pady=5)
                content_text.insert("1.0", section_content)
                content_text.configure(state="disabled")
        
        # Close button
        close_btn = ctk.CTkButton(main_frame, text="Close", command=self.destroy)
        close_btn.pack(pady=10)


class StoryAnalysisDialog(ctk.CTkToplevel):
    """Dialog to show comprehensive story analysis results."""
    
    def __init__(self, parent, analysis: Dict[str, Any]):
        super().__init__(parent)
        
        self.title("Story Analysis Results")
        self.geometry("700x600")
        
        # Create layout
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="📊 Comprehensive Story Analysis",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Overall score
        score = analysis.get('overall_score', 0)
        score_color = "#2ECC71" if score >= 7 else "#F39C12" if score >= 5 else "#E74C3C"
        
        score_label = ctk.CTkLabel(
            main_frame,
            text=f"Overall Quality Score: {score:.1f}/10",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=score_color
        )
        score_label.pack(pady=5)
        
        # Summary
        summary = analysis.get('summary', 'Analysis complete')
        summary_label = ctk.CTkLabel(main_frame, text=summary)
        summary_label.pack(pady=5)
        
        # Tabbed results
        tabview = ctk.CTkTabview(main_frame)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Structure Analysis Tab
        if 'structure' in analysis:
            structure_tab = tabview.add("Structure")
            structure_text = ctk.CTkTextbox(structure_tab)
            structure_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            structure_content = analysis['structure'].get('summary', 'Structure analysis completed')
            structure_text.insert("1.0", structure_content)
            structure_text.configure(state="disabled")
        
        # Plot Holes Tab  
        if 'plot_holes' in analysis:
            holes_tab = tabview.add("Plot Issues")
            holes_text = ctk.CTkTextbox(holes_tab)
            holes_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            holes = analysis['plot_holes']
            if holes and not holes[0].get('error'):
                holes_content = f"Found {len(holes)} potential issues:\\n\\n"
                for i, hole in enumerate(holes, 1):
                    holes_content += f"{i}. {hole.get('description', 'Issue detected')}\\n"
                    if hole.get('suggested_fix'):
                        holes_content += f"   Fix: {hole['suggested_fix']}\\n\\n"
            else:
                holes_content = "No significant plot holes detected."
            
            holes_text.insert("1.0", holes_content)
            holes_text.configure(state="disabled")
        
        # Improvements Tab
        if 'improvements' in analysis:
            improvements_tab = tabview.add("Suggestions")
            improvements_text = ctk.CTkTextbox(improvements_tab)
            improvements_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            improvements = analysis['improvements']
            if improvements and not improvements[0].get('error'):
                imp_content = f"AI Suggestions for Enhancement:\\n\\n"
                for i, improvement in enumerate(improvements, 1):
                    imp_content += f"{i}. {improvement.get('improvement', 'Enhancement available')}\\n"
                    imp_content += f"   Reason: {improvement.get('reason', 'Will improve story')}\\n"
                    if improvement.get('priority'):
                        imp_content += f"   Priority: {improvement['priority']}\\n\\n"
            else:
                imp_content = "No specific improvement suggestions at this time."
            
            improvements_text.insert("1.0", imp_content)
            improvements_text.configure(state="disabled")
        
        # Close button
        close_btn = ctk.CTkButton(main_frame, text="Close", command=self.destroy)
        close_btn.pack(pady=10)


class BatchImprovementDialog(ctk.CTkToplevel):
    """Dialog to preview and accept batch improvements."""
    
    def __init__(self, parent, results: Dict[str, Any], accept_callback: Callable):
        super().__init__(parent)
        
        self.title("Batch Improvement Results")
        self.geometry("800x600")
        self.results = results
        self.accept_callback = accept_callback
        self.selected_improvements = {}
        
        # Create layout
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title and summary
        title_label = ctk.CTkLabel(
            main_frame,
            text="🚀 Batch Dialogue Improvements",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=10)
        
        summary = results.get('summary', 'Improvement analysis complete')
        summary_label = ctk.CTkLabel(main_frame, text=summary)
        summary_label.pack(pady=5)
        
        # Instructions
        instructions = ctk.CTkLabel(
            main_frame,
            text="Review the improvements below and select which ones to apply:"
        )
        instructions.pack(pady=5)
        
        # Improvements list
        improvements_frame = ctk.CTkScrollableFrame(main_frame)
        improvements_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        improvements = results.get('improvements', {})
        for node_id, improvement in improvements.items():
            self._create_improvement_preview(improvements_frame, node_id, improvement)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # Select all/none buttons
        select_all_btn = ctk.CTkButton(
            button_frame, 
            text="Select All", 
            command=self._select_all,
            width=100
        )
        select_all_btn.pack(side="left", padx=5)
        
        select_none_btn = ctk.CTkButton(
            button_frame,
            text="Select None", 
            command=self._select_none,
            width=100
        )
        select_none_btn.pack(side="left", padx=5)
        
        # Apply/Cancel buttons
        apply_btn = ctk.CTkButton(
            button_frame,
            text="✅ Apply Selected",
            command=self._apply_selected,
            width=120
        )
        apply_btn.pack(side="right", padx=5)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=self.destroy,
            width=80
        )
        cancel_btn.pack(side="right", padx=5)
    
    def _create_improvement_preview(self, parent, node_id: str, improvement: Dict[str, str]):
        """Create preview widget for a single improvement."""
        # Container frame
        container = ctk.CTkFrame(parent)
        container.pack(fill="x", padx=5, pady=5)
        
        # Checkbox and node ID
        var = ctk.BooleanVar(value=True)  # Selected by default
        checkbox = ctk.CTkCheckBox(
            container,
            text=f"Node: {node_id}",
            variable=var,
            font=ctk.CTkFont(weight="bold")
        )
        checkbox.pack(anchor="w", padx=10, pady=5)
        
        # Store variable for later access
        self.selected_improvements[node_id] = {'var': var, 'improvement': improvement}
        
        # Original text
        original_label = ctk.CTkLabel(container, text="Original:", font=ctk.CTkFont(size=10, weight="bold"))
        original_label.pack(anchor="w", padx=20)
        
        original_text = ctk.CTkTextbox(container, height=60, font=ctk.CTkFont(size=10))
        original_text.pack(fill="x", padx=20, pady=2)
        original_text.insert("1.0", improvement.get('original', ''))
        original_text.configure(state="disabled")
        
        # Improved text
        improved_label = ctk.CTkLabel(container, text="AI Improved:", font=ctk.CTkFont(size=10, weight="bold"))
        improved_label.pack(anchor="w", padx=20)
        
        improved_text = ctk.CTkTextbox(container, height=60, font=ctk.CTkFont(size=10))
        improved_text.pack(fill="x", padx=20, pady=2)
        improved_text.insert("1.0", improvement.get('improved', ''))
        improved_text.configure(state="disabled")
    
    def _select_all(self):
        """Select all improvements."""
        for node_data in self.selected_improvements.values():
            node_data['var'].set(True)
    
    def _select_none(self):
        """Deselect all improvements."""
        for node_data in self.selected_improvements.values():
            node_data['var'].set(False)
    
    def _apply_selected(self):
        """Apply selected improvements."""
        selected = {}
        for node_id, node_data in self.selected_improvements.items():
            if node_data['var'].get():
                selected[node_id] = node_data['improvement']
        
        if selected:
            self.accept_callback(selected)
            self.destroy()
        else:
            messagebox.showwarning("No Selection", "Please select at least one improvement to apply.")