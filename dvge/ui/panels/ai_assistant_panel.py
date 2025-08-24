"""AI Assistant Panel for DVGE."""

import customtkinter as ctk
from tkinter import messagebox, scrolledtext
from typing import Dict, Any, Optional, List
import threading
import json


class AIAssistantPanel(ctk.CTkFrame):
    """Panel for AI-powered content generation and assistance."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        # Initialize AI service
        try:
            from ...ai import AIService
            from ...ai.generators import DialogueGenerator, CharacterGenerator, StoryGenerator, ContentAnalyzer
            
            self.ai_service = AIService(app)
            self.dialogue_generator = DialogueGenerator(self.ai_service)
            self.character_generator = CharacterGenerator(self.ai_service)
            self.story_generator = StoryGenerator(self.ai_service)
            self.content_analyzer = ContentAnalyzer(self.ai_service)
            
        except ImportError as e:
            print(f"Warning: AI features not available: {e}")
            self.ai_service = None
        
        self.chat_history = []
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the AI assistant panel UI."""
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_label = ctk.CTkLabel(
            self, 
            text="AI Assistant", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.grid(row=0, column=0, pady=(10, 5), sticky="ew")
        
        if not self.ai_service:
            # Show error message if AI not available
            error_label = ctk.CTkLabel(
                self,
                text="AI features are not available.\nInstall required packages: pip install openai anthropic ollama",
                font=ctk.CTkFont(size=12),
                text_color="red"
            )
            error_label.grid(row=1, column=0, pady=20, sticky="nsew")
            return
        
        # Create notebook for different AI features
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Set up tabs
        self.setup_suggestions_tab()  # Add suggestions tab first
        self.setup_chat_tab()
        self.setup_dialogue_tab()
        self.setup_character_tab()
        self.setup_story_tab()
        self.setup_analysis_tab()
        self.setup_settings_tab()
    
    def setup_chat_tab(self):
        """Set up the interactive chat tab."""
        tab = self.notebook.add("Chat")
        
        # Chat display area
        self.chat_display = ctk.CTkTextbox(tab, height=300)
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        # Input frame
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Chat input
        self.chat_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask me anything about your story, characters, or dialogue..."
        )
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        self.chat_input.bind("<Return>", self.send_chat_message)
        
        # Send button
        send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self.send_chat_message,
            width=80
        )
        send_button.pack(side="right", padx=(0, 10), pady=10)
        
        # Quick actions frame
        actions_frame = ctk.CTkFrame(tab)
        actions_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Configure actions frame grid
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        
        # Quick actions label
        ctk.CTkLabel(
            actions_frame,
            text="Quick Actions:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
        
        # Quick action buttons
        quick_actions = [
            ("Help with current node", self.help_with_current_node),
            ("Suggest dialogue improvements", self.suggest_dialogue_improvements),
            ("Analyze story so far", self.analyze_story_progress),
            ("Clear chat", self.clear_chat)
        ]
        
        for i, (text, command) in enumerate(quick_actions):
            row = (i // 2) + 1  # Start from row 1 (after label)
            col = i % 2
            
            button = ctk.CTkButton(
                actions_frame,
                text=text,
                command=command,
                width=200,
                height=30
            )
            button.grid(row=row, column=col, padx=5, pady=2, sticky="ew")
    
    def setup_suggestions_tab(self):
        """Set up the contextual suggestions tab."""
        tab = self.notebook.add("Suggestions")
        
        # Import and create contextual suggestions widget
        try:
            from ..contextual_suggestions_widget import ContextualSuggestionsWidget
            
            self.suggestions_widget = ContextualSuggestionsWidget(tab, self.app)
            self.suggestions_widget.pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            print(f"Failed to initialize contextual suggestions: {e}")
            # Show error message in tab
            error_label = ctk.CTkLabel(
                tab,
                text="Contextual suggestions not available.\nError initializing suggestions widget.",
                font=ctk.CTkFont(size=12),
                text_color="red"
            )
            error_label.pack(pady=20)
            self.suggestions_widget = None
    
    def setup_dialogue_tab(self):
        """Set up the dialogue generation tab."""
        tab = self.notebook.add("Dialogue")
        
        # Character selection
        char_frame = ctk.CTkFrame(tab)
        char_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(char_frame, text="Character:").pack(side="left", padx=(10, 5))
        
        self.character_var = ctk.StringVar()
        self.character_entry = ctk.CTkEntry(
            char_frame,
            textvariable=self.character_var,
            placeholder_text="Character name"
        )
        self.character_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Context frame
        context_frame = ctk.CTkFrame(tab)
        context_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(context_frame, text="Context:").pack(anchor="w", padx=10, pady=(10, 5))
        
        self.context_text = ctk.CTkTextbox(context_frame, height=80)
        self.context_text.pack(fill="x", padx=10, pady=(0, 10))
        
        # Dialogue actions
        dialogue_actions = ctk.CTkFrame(tab)
        dialogue_actions.pack(fill="x", padx=10, pady=(0, 10))
        
        # Configure dialogue actions frame grid
        dialogue_actions.grid_columnconfigure(0, weight=1)
        dialogue_actions.grid_columnconfigure(1, weight=1)
        
        # Action buttons
        actions = [
            ("Generate Dialogue Line", self.generate_dialogue_line),
            ("Generate Player Options", self.generate_player_options),
            ("Improve Selected Text", self.improve_dialogue),
            ("Generate Conversation", self.generate_conversation)
        ]
        
        for i, (text, command) in enumerate(actions):
            row = i // 2
            col = i % 2
            
            button = ctk.CTkButton(
                dialogue_actions,
                text=text,
                command=command,
                width=200,
                height=35
            )
            button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # Results area
        ctk.CTkLabel(tab, text="Generated Content:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.dialogue_results = ctk.CTkTextbox(tab, height=200)
        self.dialogue_results.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def setup_character_tab(self):
        """Set up the character development tab."""
        tab = self.notebook.add("Character")
        
        # Character name input
        name_frame = ctk.CTkFrame(tab)
        name_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(name_frame, text="Character Name:").pack(side="left", padx=(10, 5))
        
        self.char_name_var = ctk.StringVar()
        char_name_entry = ctk.CTkEntry(
            name_frame,
            textvariable=self.char_name_var,
            placeholder_text="Enter character name"
        )
        char_name_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
        
        # Character actions
        char_actions = ctk.CTkFrame(tab)
        char_actions.pack(fill="x", padx=10, pady=(0, 10))
        
        # Configure character actions frame grid
        actions = [
            ("Generate Profile", self.generate_character_profile),
            ("Generate Backstory", self.generate_character_backstory),
            ("Analyze Voice", self.analyze_character_voice),
            ("Character Relationships", self.generate_character_relationships)
        ]
        
        for i in range(len(actions)):
            char_actions.grid_columnconfigure(i, weight=1)
        
        for i, (text, command) in enumerate(actions):
            button = ctk.CTkButton(
                char_actions,
                text=text,
                command=command,
                width=150,
                height=35
            )
            button.grid(row=0, column=i, padx=5, pady=10, sticky="ew")
        
        # Results area
        ctk.CTkLabel(tab, text="Character Information:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.character_results = ctk.CTkTextbox(tab, height=300)
        self.character_results.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def setup_story_tab(self):
        """Set up the story development tab."""
        tab = self.notebook.add("Story")
        
        # Story premise input
        premise_frame = ctk.CTkFrame(tab)
        premise_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(premise_frame, text="Story Premise:").pack(anchor="w", padx=10, pady=(10, 5))
        
        self.premise_text = ctk.CTkTextbox(premise_frame, height=60)
        self.premise_text.pack(fill="x", padx=10, pady=(0, 10))
        
        # Story actions
        story_actions = ctk.CTkFrame(tab)
        story_actions.pack(fill="x", padx=10, pady=(0, 10))
        
        # Configure story actions frame grid
        story_actions.grid_columnconfigure(0, weight=1)
        story_actions.grid_columnconfigure(1, weight=1)
        
        actions = [
            ("Generate Plot Outline", self.generate_plot_outline),
            ("Suggest Developments", self.suggest_plot_developments),
            ("Create Scene Description", self.generate_scene_description),
            ("Find Plot Holes", self.find_plot_holes)
        ]
        
        for i, (text, command) in enumerate(actions):
            row = i // 2
            col = i % 2
            
            button = ctk.CTkButton(
                story_actions,
                text=text,
                command=command,
                width=200,
                height=35
            )
            button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # Results area
        ctk.CTkLabel(tab, text="Story Development:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.story_results = ctk.CTkTextbox(tab, height=250)
        self.story_results.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def setup_analysis_tab(self):
        """Set up the content analysis tab."""
        tab = self.notebook.add("Analysis")
        
        # Analysis type selection
        type_frame = ctk.CTkFrame(tab)
        type_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(type_frame, text="Analysis Type:").pack(side="left", padx=(10, 5))
        
        self.analysis_type_var = ctk.StringVar(value="dialogue")
        analysis_dropdown = ctk.CTkOptionMenu(
            type_frame,
            variable=self.analysis_type_var,
            values=["dialogue", "story", "character", "pacing"]
        )
        analysis_dropdown.pack(side="left", padx=5)
        
        # Content input
        content_frame = ctk.CTkFrame(tab)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(content_frame, text="Content to Analyze:").pack(anchor="w", padx=10, pady=(10, 5))
        
        self.analysis_content = ctk.CTkTextbox(content_frame, height=150)
        self.analysis_content.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        
        # Analysis buttons
        analysis_buttons = ctk.CTkFrame(content_frame)
        analysis_buttons.pack(fill="x", padx=10, pady=(5, 10))
        
        analyze_button = ctk.CTkButton(
            analysis_buttons,
            text="Analyze Content",
            command=self.analyze_content,
            height=35
        )
        analyze_button.pack(side="left", padx=(0, 5))
        
        suggestions_button = ctk.CTkButton(
            analysis_buttons,
            text="Get Suggestions",
            command=self.get_content_suggestions,
            height=35
        )
        suggestions_button.pack(side="left", padx=5)
        
        # Results area
        ctk.CTkLabel(tab, text="Analysis Results:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.analysis_results = ctk.CTkTextbox(tab, height=200)
        self.analysis_results.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def setup_settings_tab(self):
        """Set up the AI settings tab."""
        tab = self.notebook.add("Settings")
        
        # Provider selection
        provider_frame = ctk.CTkFrame(tab)
        provider_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(provider_frame, text="AI Provider:").pack(side="left", padx=(10, 5))
        
        self.provider_var = ctk.StringVar(value=self.ai_service.default_provider or "mock")
        provider_dropdown = ctk.CTkOptionMenu(
            provider_frame,
            variable=self.provider_var,
            values=self.ai_service.get_available_providers(),
            command=self.on_provider_changed
        )
        provider_dropdown.pack(side="left", padx=5)
        
        # API key configuration
        api_frame = ctk.CTkFrame(tab)
        api_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(api_frame, text="API Configuration:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        # OpenAI API Key
        openai_frame = ctk.CTkFrame(api_frame)
        openai_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(openai_frame, text="OpenAI API Key:").pack(side="left", padx=(10, 5))
        
        self.openai_key_var = ctk.StringVar()
        openai_entry = ctk.CTkEntry(
            openai_frame,
            textvariable=self.openai_key_var,
            show="*",
            placeholder_text="sk-..."
        )
        openai_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
        
        # Anthropic API Key
        anthropic_frame = ctk.CTkFrame(api_frame)
        anthropic_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(anthropic_frame, text="Anthropic API Key:").pack(side="left", padx=(10, 5))
        
        self.anthropic_key_var = ctk.StringVar()
        anthropic_entry = ctk.CTkEntry(
            anthropic_frame,
            textvariable=self.anthropic_key_var,
            show="*",
            placeholder_text="sk-ant-..."
        )
        anthropic_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
        
        # Settings buttons
        settings_buttons = ctk.CTkFrame(tab)
        settings_buttons.pack(fill="x", padx=10, pady=10)
        
        save_button = ctk.CTkButton(
            settings_buttons,
            text="Save Settings",
            command=self.save_ai_settings
        )
        save_button.pack(side="left", padx=(10, 5))
        
        test_button = ctk.CTkButton(
            settings_buttons,
            text="Test Connection",
            command=self.test_ai_connection
        )
        test_button.pack(side="left", padx=5)
        
        # Usage statistics
        stats_frame = ctk.CTkFrame(tab)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(stats_frame, text="Usage Statistics:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.stats_text = ctk.CTkTextbox(stats_frame, height=150)
        self.stats_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        refresh_stats_button = ctk.CTkButton(
            stats_frame,
            text="Refresh Statistics",
            command=self.refresh_statistics
        )
        refresh_stats_button.pack(pady=(0, 10))
        
        # Load initial settings
        self.load_ai_settings()
        self.refresh_statistics()
    
    def send_chat_message(self, event=None):
        """Send a chat message to the AI."""
        message = self.chat_input.get().strip()
        if not message:
            return
        
        # Clear input
        self.chat_input.delete(0, "end")
        
        # Add user message to chat
        self.add_chat_message("You", message)
        
        # Generate AI response in background
        def generate_response():
            try:
                # Build context from current project state
                context = self.get_current_context()
                
                from ...ai import AIRequest
                request = AIRequest(
                    prompt=message,
                    context=context,
                    max_tokens=300,
                    temperature=0.8
                )
                
                response = self.ai_service.generate_content_sync(request)
                
                if response.success:
                    self.add_chat_message("AI Assistant", response.content)
                else:
                    self.add_chat_message("AI Assistant", f"Sorry, I encountered an error: {response.error}")
                    
            except Exception as e:
                self.add_chat_message("AI Assistant", f"Error: {str(e)}")
        
        # Run in background thread
        thread = threading.Thread(target=generate_response)
        thread.daemon = True
        thread.start()
    
    def add_chat_message(self, sender: str, message: str):
        """Add a message to the chat display."""
        timestamp = __import__('datetime').datetime.now().strftime("%H:%M")
        formatted_message = f"[{timestamp}] {sender}: {message}\n\n"
        
        self.chat_display.insert("end", formatted_message)
        self.chat_display.see("end")
        
        # Add to history
        self.chat_history.append({
            "sender": sender,
            "message": message,
            "timestamp": timestamp
        })
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get context from current project state."""
        context = {}
        
        # Add project name if available
        if hasattr(self.app, 'current_project_file') and self.app.current_project_file:
            import os
            context["project_name"] = os.path.splitext(os.path.basename(self.app.current_project_file))[0]
        
        # Add current node info if selected
        if hasattr(self.app, 'selected_node_ids') and self.app.selected_node_ids:
            selected_id = self.app.selected_node_ids[0]
            if selected_id in self.app.nodes:
                node = self.app.nodes[selected_id]
                context["current_node"] = {
                    "id": selected_id,
                    "type": getattr(node, 'node_type', 'dialogue'),
                    "text": getattr(node, 'text', ''),
                    "npc": getattr(node, 'npc', '')
                }
        
        # Add story flags and variables
        if hasattr(self.app, 'story_flags'):
            context["story_flags"] = list(self.app.story_flags.keys())
        
        if hasattr(self.app, 'variables'):
            context["variables"] = list(self.app.variables.keys())
        
        return context
    
    def help_with_current_node(self):
        """Provide help with the currently selected node."""
        if not hasattr(self.app, 'selected_node_ids') or not self.app.selected_node_ids:
            self.add_chat_message("AI Assistant", "Please select a node first.")
            return
        
        node_id = self.app.selected_node_ids[0]
        if node_id not in self.app.nodes:
            self.add_chat_message("AI Assistant", "Selected node not found.")
            return
        
        node = self.app.nodes[node_id]
        node_text = getattr(node, 'text', '')
        node_npc = getattr(node, 'npc', '')
        
        if node_text:
            message = f"Can you help me improve this dialogue for {node_npc}: \"{node_text}\""
        else:
            message = f"Can you help me create dialogue for a {node_npc} character in this scene?"
        
        self.chat_input.delete(0, "end")
        self.chat_input.insert(0, message)
        self.send_chat_message()
    
    def suggest_dialogue_improvements(self):
        """Suggest improvements for dialogue in the project."""
        message = "Can you analyze the dialogue in my current project and suggest improvements for character voice consistency and engagement?"
        self.chat_input.delete(0, "end")
        self.chat_input.insert(0, message)
        self.send_chat_message()
    
    def analyze_story_progress(self):
        """Analyze the story progress so far."""
        message = "Can you analyze the story flow and pacing in my current project? Are there any areas that need improvement?"
        self.chat_input.delete(0, "end")
        self.chat_input.insert(0, message)
        self.send_chat_message()
    
    def clear_chat(self):
        """Clear the chat history."""
        self.chat_display.delete("1.0", "end")
        self.chat_history.clear()
    
    def generate_dialogue_line(self):
        """Generate a dialogue line for the specified character."""
        character = self.character_var.get().strip()
        if not character:
            messagebox.showwarning("Missing Character", "Please enter a character name.")
            return
        
        context_text = self.context_text.get("1.0", "end").strip()
        context = {"situation": context_text} if context_text else {}
        
        def generate():
            try:
                dialogue = self.dialogue_generator.generate_dialogue_line(character, context)
                self.display_dialogue_result(f"Dialogue for {character}:", dialogue)
            except Exception as e:
                self.display_dialogue_result("Error:", str(e))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def generate_player_options(self):
        """Generate multiple dialogue options for player choice."""
        context_text = self.context_text.get("1.0", "end").strip()
        context = {"situation": context_text} if context_text else {}
        
        def generate():
            try:
                options = self.dialogue_generator.generate_dialogue_options(context, count=3)
                result = "Player dialogue options:\n" + "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)])
                self.display_dialogue_result("Generated Options:", result)
            except Exception as e:
                self.display_dialogue_result("Error:", str(e))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def improve_dialogue(self):
        """Improve selected dialogue text."""
        # Get selected text from dialogue results or current node
        selected_text = ""
        try:
            selected_text = self.dialogue_results.selection_get()
        except:
            # No selection in results, try current node
            if hasattr(self.app, 'selected_node_ids') and self.app.selected_node_ids:
                node_id = self.app.selected_node_ids[0]
                if node_id in self.app.nodes:
                    selected_text = getattr(self.app.nodes[node_id], 'text', '')
        
        if not selected_text:
            messagebox.showwarning("No Text Selected", "Please select text to improve or select a node with dialogue.")
            return
        
        def improve():
            try:
                improved = self.dialogue_generator.improve_dialogue(selected_text, "general")
                self.display_dialogue_result("Improved Dialogue:", improved)
            except Exception as e:
                self.display_dialogue_result("Error:", str(e))
        
        threading.Thread(target=improve, daemon=True).start()
    
    def generate_conversation(self):
        """Generate a multi-turn conversation."""
        character = self.character_var.get().strip()
        if not character:
            messagebox.showwarning("Missing Character", "Please enter a character name.")
            return
        
        context_text = self.context_text.get("1.0", "end").strip()
        topic = context_text if context_text else "general conversation"
        
        def generate():
            try:
                conversation = self.dialogue_generator.generate_conversation([character, "Player"], topic, 4)
                result = "Generated Conversation:\n\n"
                for turn in conversation:
                    result += f"{turn['character']}: {turn['dialogue']}\n"
                self.display_dialogue_result("Conversation:", result)
            except Exception as e:
                self.display_dialogue_result("Error:", str(e))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def display_dialogue_result(self, title: str, content: str):
        """Display dialogue generation result."""
        formatted_result = f"\n=== {title} ===\n{content}\n"
        self.dialogue_results.insert("end", formatted_result)
        self.dialogue_results.see("end")
    
    def generate_character_profile(self):
        """Generate a character profile."""
        character_name = self.char_name_var.get().strip()
        if not character_name:
            messagebox.showwarning("Missing Name", "Please enter a character name.")
            return
        
        def generate():
            try:
                profile = self.character_generator.generate_character_profile(character_name)
                
                if "error" in profile:
                    result = f"Error: {profile['error']}"
                else:
                    result = f"Character Profile for {character_name}:\n\n"
                    for section, content in profile.items():
                        if content:
                            result += f"{section.title()}: {content}\n\n"
                
                self.display_character_result("Character Profile", result)
            except Exception as e:
                self.display_character_result("Error", str(e))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def generate_character_backstory(self):
        """Generate character backstory."""
        character_name = self.char_name_var.get().strip()
        if not character_name:
            messagebox.showwarning("Missing Name", "Please enter a character name.")
            return
        
        def generate():
            try:
                backstory = self.character_generator.generate_character_backstory(character_name)
                self.display_character_result(f"Backstory for {character_name}", backstory)
            except Exception as e:
                self.display_character_result("Error", str(e))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def analyze_character_voice(self):
        """Analyze character voice from dialogue samples."""
        character_name = self.char_name_var.get().strip()
        if not character_name:
            messagebox.showwarning("Missing Name", "Please enter a character name.")
            return
        
        # Get dialogue samples from project
        dialogue_samples = []
        for node in self.app.nodes.values():
            if hasattr(node, 'npc') and hasattr(node, 'text'):
                if node.npc.lower() == character_name.lower() and node.text:
                    dialogue_samples.append(node.text)
        
        if not dialogue_samples:
            messagebox.showwarning("No Dialogue Found", f"No dialogue found for character '{character_name}' in the current project.")
            return
        
        def analyze():
            try:
                analysis = self.character_generator.analyze_character_voice(character_name, dialogue_samples)
                
                if "error" in analysis:
                    result = f"Error: {analysis['error']}"
                else:
                    result = f"Voice Analysis for {character_name}:\n\n"
                    for aspect, content in analysis.items():
                        if content and aspect != "overall_score":
                            result += f"{aspect.replace('_', ' ').title()}: {content}\n\n"
                
                self.display_character_result("Voice Analysis", result)
            except Exception as e:
                self.display_character_result("Error", str(e))
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def generate_character_relationships(self):
        """Generate character relationship suggestions."""
        character_name = self.char_name_var.get().strip()
        if not character_name:
            messagebox.showwarning("Missing Name", "Please enter a character name.")
            return
        
        # Get other characters from project
        other_characters = set()
        for node in self.app.nodes.values():
            if hasattr(node, 'npc') and node.npc and node.npc != character_name:
                other_characters.add(node.npc)
        
        context = {"other_characters": list(other_characters)} if other_characters else {}
        
        prompt = f"Suggest interesting relationships and dynamics between {character_name} and other characters in the story."
        if other_characters:
            prompt += f" Other characters include: {', '.join(other_characters)}"
        
        def generate():
            try:
                from ...ai import AIRequest
                request = AIRequest(
                    prompt=prompt,
                    context=context,
                    max_tokens=300,
                    temperature=0.8
                )
                
                response = self.ai_service.generate_content_sync(request)
                
                if response.success:
                    self.display_character_result("Character Relationships", response.content)
                else:
                    self.display_character_result("Error", response.error)
            except Exception as e:
                self.display_character_result("Error", str(e))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def display_character_result(self, title: str, content: str):
        """Display character generation result."""
        formatted_result = f"\n=== {title} ===\n{content}\n"
        self.character_results.insert("end", formatted_result)
        self.character_results.see("end")
    
    def generate_plot_outline(self):
        """Generate a plot outline."""
        premise = self.premise_text.get("1.0", "end").strip()
        if not premise:
            messagebox.showwarning("Missing Premise", "Please enter a story premise.")
            return
        
        def generate():
            try:
                outline = self.story_generator.generate_plot_outline(premise, "medium")
                result = "Plot Outline:\n\n"
                for i, point in enumerate(outline, 1):
                    result += f"{i}. {point}\n"
                self.display_story_result("Plot Outline", result)
            except Exception as e:
                self.display_story_result("Error", str(e))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def suggest_plot_developments(self):
        """Suggest plot developments."""
        current_situation = self.premise_text.get("1.0", "end").strip()
        if not current_situation:
            messagebox.showwarning("Missing Situation", "Please describe the current situation.")
            return
        
        def generate():
            try:
                suggestions = self.story_generator.suggest_plot_developments(current_situation)
                result = "Plot Development Suggestions:\n\n"
                for i, suggestion in enumerate(suggestions, 1):
                    result += f"{i}. {suggestion}\n"
                self.display_story_result("Plot Developments", result)
            except Exception as e:
                self.display_story_result("Error", str(e))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def generate_scene_description(self):
        """Generate a scene description."""
        location = self.premise_text.get("1.0", "end").strip()
        if not location:
            messagebox.showwarning("Missing Location", "Please enter a location or scene setting.")
            return
        
        def generate():
            try:
                description = self.story_generator.generate_scene_description(location)
                self.display_story_result("Scene Description", description)
            except Exception as e:
                self.display_story_result("Error", str(e))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def find_plot_holes(self):
        """Find potential plot holes."""
        # Get story outline from premise or project nodes
        story_text = self.premise_text.get("1.0", "end").strip()
        
        if not story_text:
            # Build story from project nodes
            story_points = []
            for node_id, node in self.app.nodes.items():
                if hasattr(node, 'text') and node.text:
                    story_points.append(f"{node.text}")
            
            if not story_points:
                messagebox.showwarning("No Story Content", "Please enter story content or ensure your project has dialogue nodes.")
                return
        else:
            story_points = [story_text]
        
        def analyze():
            try:
                plot_holes = self.content_analyzer.find_plot_holes(story_points)
                if plot_holes:
                    result = "Potential Plot Issues:\n\n"
                    for i, issue in enumerate(plot_holes, 1):
                        result += f"{i}. {issue}\n"
                else:
                    result = "No significant plot holes detected in the current story outline."
                self.display_story_result("Plot Analysis", result)
            except Exception as e:
                self.display_story_result("Error", str(e))
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def display_story_result(self, title: str, content: str):
        """Display story generation result."""
        formatted_result = f"\n=== {title} ===\n{content}\n"
        self.story_results.insert("end", formatted_result)
        self.story_results.see("end")
    
    def analyze_content(self):
        """Analyze the provided content."""
        content = self.analysis_content.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("No Content", "Please enter content to analyze.")
            return
        
        analysis_type = self.analysis_type_var.get()
        
        def analyze():
            try:
                if analysis_type == "pacing":
                    analysis = self.content_analyzer.analyze_story_pacing(content)
                    if "error" in analysis:
                        result = f"Error: {analysis['error']}"
                    else:
                        result = "Pacing Analysis:\n\n"
                        for aspect, content_text in analysis.items():
                            if content_text:
                                result += f"{aspect.replace('_', ' ').title()}: {content_text}\n\n"
                else:
                    # General content analysis
                    from ...ai import AIRequest
                    prompt = f"Analyze this {analysis_type} content and provide detailed feedback: {content}"
                    
                    request = AIRequest(
                        prompt=prompt,
                        max_tokens=400,
                        temperature=0.5
                    )
                    
                    response = self.ai_service.generate_content_sync(request)
                    result = response.content if response.success else f"Error: {response.error}"
                
                self.display_analysis_result("Content Analysis", result)
            except Exception as e:
                self.display_analysis_result("Error", str(e))
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def get_content_suggestions(self):
        """Get improvement suggestions for content."""
        content = self.analysis_content.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("No Content", "Please enter content to analyze.")
            return
        
        content_type = self.analysis_type_var.get()
        
        def generate():
            try:
                suggestions = self.content_analyzer.suggest_improvements(content, content_type)
                result = f"Improvement Suggestions for {content_type}:\n\n"
                for i, suggestion in enumerate(suggestions, 1):
                    result += f"{i}. {suggestion}\n"
                self.display_analysis_result("Improvement Suggestions", result)
            except Exception as e:
                self.display_analysis_result("Error", str(e))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def display_analysis_result(self, title: str, content: str):
        """Display analysis result."""
        formatted_result = f"\n=== {title} ===\n{content}\n"
        self.analysis_results.insert("end", formatted_result)
        self.analysis_results.see("end")
    
    def on_provider_changed(self, provider_name: str):
        """Handle provider change."""
        self.ai_service.set_default_provider(provider_name)
    
    def save_ai_settings(self):
        """Save AI provider settings."""
        # Configure OpenAI
        openai_key = self.openai_key_var.get().strip()
        if openai_key:
            self.ai_service.configure_provider("openai", {"api_key": openai_key})
        
        # Configure Anthropic
        anthropic_key = self.anthropic_key_var.get().strip()
        if anthropic_key:
            self.ai_service.configure_provider("anthropic", {"api_key": anthropic_key})
        
        messagebox.showinfo("Settings Saved", "AI settings have been saved.")
    
    def test_ai_connection(self):
        """Test the AI connection."""
        def test():
            try:
                from ...ai import AIRequest
                request = AIRequest(
                    prompt="Hello, this is a test message. Please respond with 'Connection successful!'",
                    max_tokens=50,
                    temperature=0.1
                )
                
                response = self.ai_service.generate_content_sync(request)
                
                if response.success:
                    messagebox.showinfo("Connection Test", f"✓ Connection successful!\nProvider: {response.provider}")
                else:
                    messagebox.showerror("Connection Test", f"✗ Connection failed:\n{response.error}")
            except Exception as e:
                messagebox.showerror("Connection Test", f"✗ Test failed:\n{str(e)}")
        
        threading.Thread(target=test, daemon=True).start()
    
    def load_ai_settings(self):
        """Load AI settings from app configuration."""
        # This would load from app settings in a real implementation
        pass
    
    def refresh_statistics(self):
        """Refresh usage statistics."""
        try:
            stats = self.ai_service.get_usage_stats()
            
            stats_text = f"""Usage Statistics:

Total Requests: {stats['total_requests']}
Successful Requests: {stats['successful_requests']}
Success Rate: {stats['success_rate']:.1%}
Cache Size: {stats['cache_size']} entries

Provider Usage:"""
            
            for provider, count in stats['provider_usage'].items():
                stats_text += f"\n  {provider}: {count} requests"
            
            stats_text += f"\n\nAvailable Providers: {', '.join(stats['available_providers'])}"
            stats_text += f"\nDefault Provider: {stats['default_provider']}"
            
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", stats_text)
            
        except Exception as e:
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", f"Error loading statistics: {str(e)}")
    
    def on_node_selected(self, node_id: str):
        """Handle node selection (called by main app)."""
        if node_id in self.app.nodes:
            node = self.app.nodes[node_id]
            
            # Auto-fill character name if it's a dialogue node
            if hasattr(node, 'npc') and node.npc:
                self.character_var.set(node.npc)
                self.char_name_var.set(node.npc)
            
            # Auto-fill context with node text
            if hasattr(node, 'text') and node.text:
                self.context_text.delete("1.0", "end")
                self.context_text.insert("1.0", f"Current dialogue: {node.text}")
                
                # Fill analysis content too
                self.analysis_content.delete("1.0", "end")
                self.analysis_content.insert("1.0", node.text)