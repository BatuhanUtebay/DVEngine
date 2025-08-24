"""Contextual AI Suggestions Widget for DVGE."""

import customtkinter as ctk
from tkinter import messagebox
import threading
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Import AISuggestion for type checking
try:
    from ...ai.contextual_suggestions import AISuggestion
except ImportError:
    AISuggestion = None

@dataclass
class SuggestionItem:
    """Represents a single AI suggestion."""
    title: str
    description: str
    action_type: str
    priority: int = 1
    action_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.action_data is None:
            self.action_data = {}


class ContextualSuggestionsWidget(ctk.CTkFrame):
    """Widget that shows contextual AI suggestions based on current editing context."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_suggestions = []
        self.suggestion_widgets = []
        self.update_in_progress = False
        self.last_context_hash = None
        
        # Set up the widget
        self.setup_ui()
        
        # Start contextual monitoring
        self.start_contextual_monitoring()
    
    def setup_ui(self):
        """Set up the suggestions widget UI."""
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="💡 Smart Suggestions",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.header_frame,
            text="🔄",
            command=self.force_refresh_suggestions,
            width=30,
            height=30
        )
        self.refresh_button.grid(row=0, column=1, sticky="e")
        
        # Suggestions container
        self.suggestions_frame = ctk.CTkScrollableFrame(self, height=200)
        self.suggestions_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.grid_rowconfigure(1, weight=1)
        
        # Initial placeholder
        self.show_placeholder()
    
    def show_placeholder(self):
        """Show placeholder text when no suggestions are available."""
        self.clear_suggestions_display()
        
        placeholder = ctk.CTkLabel(
            self.suggestions_frame,
            text="🤖 AI will analyze your work and suggest improvements...\n\nStart editing nodes to see contextual suggestions!",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray70"),
            justify="center"
        )
        placeholder.pack(pady=20)
        self.suggestion_widgets.append(placeholder)
    
    def clear_suggestions_display(self):
        """Clear all suggestion widgets from display."""
        for widget in self.suggestion_widgets:
            widget.destroy()
        self.suggestion_widgets.clear()
    
    def update_suggestions(self, suggestions: List[SuggestionItem]):
        """Update the displayed suggestions."""
        if self.update_in_progress:
            return
        
        self.current_suggestions = suggestions
        self.display_suggestions()
    
    def display_suggestions(self):
        """Display the current suggestions in the UI."""
        self.clear_suggestions_display()
        
        if not self.current_suggestions:
            self.show_placeholder()
            return
        
        # Sort suggestions by priority (higher priority first)
        sorted_suggestions = sorted(
            self.current_suggestions, 
            key=lambda x: x.priority, 
            reverse=True
        )
        
        for i, suggestion in enumerate(sorted_suggestions[:5]):  # Show max 5 suggestions
            self.create_suggestion_widget(suggestion, i)
    
    def create_suggestion_widget(self, suggestion: SuggestionItem, index: int):
        """Create a widget for a single suggestion."""
        # Suggestion frame
        suggestion_frame = ctk.CTkFrame(self.suggestions_frame)
        suggestion_frame.pack(fill="x", padx=5, pady=3)
        
        # Configure grid
        suggestion_frame.grid_columnconfigure(0, weight=1)
        
        # Priority indicator color
        priority_colors = {
            3: ("red", "pink"),      # High priority
            2: ("orange", "yellow"),  # Medium priority
            1: ("green", "lightgreen") # Normal priority
        }
        indicator_color = priority_colors.get(suggestion.priority, ("blue", "lightblue"))
        
        # Priority indicator
        priority_frame = ctk.CTkFrame(
            suggestion_frame, 
            width=4, 
            fg_color=indicator_color[0]
        )
        priority_frame.grid(row=0, column=0, sticky="ns", padx=(5, 0))
        
        # Content frame
        content_frame = ctk.CTkFrame(suggestion_frame, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text=suggestion.title,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
            justify="left"
        )
        title_label.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        
        # Description
        desc_label = ctk.CTkLabel(
            content_frame,
            text=suggestion.description,
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray80"),
            anchor="w",
            justify="left",
            wraplength=250
        )
        desc_label.grid(row=1, column=0, sticky="ew")
        
        # Action button
        if suggestion.action_type != "info":
            action_button = ctk.CTkButton(
                content_frame,
                text="Apply",
                command=lambda s=suggestion: self.apply_suggestion(s),
                width=60,
                height=25,
                font=ctk.CTkFont(size=10)
            )
            action_button.grid(row=0, column=1, rowspan=2, sticky="e", padx=(5, 0))
        
        self.suggestion_widgets.append(suggestion_frame)
    
    def apply_suggestion(self, suggestion: SuggestionItem):
        """Apply a suggestion to the current project."""
        try:
            if suggestion.action_type == "enhance_dialogue":
                self._apply_dialogue_enhancement(suggestion)
            elif suggestion.action_type == "add_choices":
                self._apply_add_choices(suggestion)
            elif suggestion.action_type == "improve_flow":
                self._apply_improve_flow(suggestion)
            elif suggestion.action_type == "character_consistency":
                self._apply_character_consistency(suggestion)
            else:
                messagebox.showinfo("Suggestion", f"Applied: {suggestion.title}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply suggestion: {str(e)}")
    
    def _apply_dialogue_enhancement(self, suggestion: SuggestionItem):
        """Apply dialogue enhancement suggestion."""
        node_id = suggestion.action_data.get("node_id")
        enhanced_text = suggestion.action_data.get("enhanced_text")
        
        if node_id and enhanced_text and node_id in self.app.nodes:
            # Apply the enhancement
            node = self.app.nodes[node_id]
            if hasattr(node, 'game_data') and 'text' in node.game_data:
                # Save state for undo
                self.app.state_manager.save_state("AI Enhancement Applied")
                
                # Update node text
                node.game_data['text'] = enhanced_text
                
                # Refresh UI
                self.app.properties_panel.update_properties_panel()
                self.app.canvas_manager.redraw_all_nodes()
                
                messagebox.showinfo("Enhancement Applied", "Dialogue has been enhanced!")
            else:
                messagebox.showwarning("Error", "Could not find text to enhance in selected node.")
        else:
            messagebox.showwarning("Error", "Enhancement data not available.")
    
    def _apply_add_choices(self, suggestion: SuggestionItem):
        """Apply add choices suggestion."""
        node_id = suggestion.action_data.get("node_id")
        new_choices = suggestion.action_data.get("choices", [])
        
        if node_id and new_choices and node_id in self.app.nodes:
            node = self.app.nodes[node_id]
            if hasattr(node, 'options'):
                # Save state for undo
                self.app.state_manager.save_state("AI Choices Added")
                
                # Add new choices
                for choice_text in new_choices:
                    node.options.append({
                        'text': choice_text,
                        'nextNode': '',
                        'conditions': []
                    })
                
                # Refresh UI
                self.app.properties_panel.update_properties_panel()
                
                messagebox.showinfo("Choices Added", f"Added {len(new_choices)} new choice options!")
            else:
                messagebox.showwarning("Error", "Selected node doesn't support choices.")
        else:
            messagebox.showwarning("Error", "Choice data not available.")
    
    def _apply_improve_flow(self, suggestion: SuggestionItem):
        """Apply story flow improvement suggestion."""
        messagebox.showinfo("Flow Improvement", suggestion.description)
    
    def _apply_character_consistency(self, suggestion: SuggestionItem):
        """Apply character consistency suggestion."""
        messagebox.showinfo("Character Consistency", suggestion.description)
    
    def start_contextual_monitoring(self):
        """Start monitoring the editing context for suggestions."""
        def monitor_loop():
            while True:
                try:
                    if hasattr(self.app, 'ai_service') and self.app.ai_service:
                        if self.app.ai_service.is_enhanced_ai_available():
                            self.update_contextual_suggestions()
                except Exception as e:
                    print(f"Error in contextual monitoring: {e}")
                
                time.sleep(5)  # Check every 5 seconds
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def update_contextual_suggestions(self):
        """Update suggestions based on current context."""
        if self.update_in_progress:
            return
        
        try:
            self.update_in_progress = True
            
            # Get current context
            current_context = self.get_current_context()
            context_hash = str(hash(str(current_context)))
            
            # Skip if context hasn't changed
            if context_hash == self.last_context_hash:
                return
            
            self.last_context_hash = context_hash
            
            # Get contextual suggestions from AI
            if hasattr(self.app, 'ai_service') and self.app.ai_service and self.app.ai_service.contextual_assistant:
                suggestions = self.app.ai_service.contextual_assistant.analyze_current_context(
                    current_context,
                    "editing"
                )
                
                # Convert to SuggestionItem objects
                suggestion_items = self.convert_ai_suggestions(suggestions)
                
                # Update UI in main thread
                self.after(0, lambda: self.update_suggestions(suggestion_items))
                
        except Exception as e:
            print(f"Error updating contextual suggestions: {e}")
        finally:
            self.update_in_progress = False
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get the current editing context."""
        context = {
            "selected_nodes": self.app.selected_node_ids,
            "active_node": self.app.active_node_id,
            "total_nodes": len(self.app.nodes),
            "project_settings": self.app.project_settings,
            "current_time": time.time()
        }
        
        # Add current node details
        if self.app.active_node_id and self.app.active_node_id in self.app.nodes:
            active_node = self.app.nodes[self.app.active_node_id]
            context["active_node_data"] = {
                "node_type": active_node.__class__.__name__,
                "has_text": bool(getattr(active_node, 'game_data', {}).get('text', '')),
                "has_choices": bool(getattr(active_node, 'options', [])),
                "text_length": len(getattr(active_node, 'game_data', {}).get('text', ''))
            }
        
        return context
    
    def convert_ai_suggestions(self, ai_suggestions) -> List[SuggestionItem]:
        """Convert AI suggestions to SuggestionItem objects."""
        suggestion_items = []
        
        for suggestion in ai_suggestions[:5]:  # Limit to 5 suggestions
            try:
                # Check if it's an AISuggestion dataclass or a dictionary
                if hasattr(suggestion, 'title'):
                    # It's an AISuggestion dataclass
                    title = suggestion.title
                    description = suggestion.description
                    action_type = getattr(suggestion, 'action_text', 'info')
                    priority = self._convert_priority_to_int(suggestion.priority)
                    action_data = suggestion.metadata or {}
                else:
                    # It's a dictionary
                    title = suggestion.get('title', 'AI Suggestion')
                    description = suggestion.get('description', 'No description available')
                    action_type = suggestion.get('action_type', 'info')
                    priority = suggestion.get('priority', 1)
                    action_data = suggestion.get('action_data', {})
                
                suggestion_item = SuggestionItem(
                    title=title,
                    description=description,
                    action_type=action_type,
                    priority=priority,
                    action_data=action_data
                )
                suggestion_items.append(suggestion_item)
                
            except Exception as e:
                print(f"Error converting suggestion: {e}")
                continue
        
        return suggestion_items
    
    def _convert_priority_to_int(self, priority) -> int:
        """Convert priority enum to integer for UI display."""
        if hasattr(priority, 'value'):
            priority_str = priority.value.lower()
        else:
            priority_str = str(priority).lower()
        
        priority_map = {
            'low': 1,
            'medium': 2, 
            'high': 3,
            'critical': 4
        }
        
        return priority_map.get(priority_str, 1)
    
    def force_refresh_suggestions(self):
        """Force refresh of contextual suggestions."""
        self.last_context_hash = None  # Force update
        
        def refresh_worker():
            self.update_contextual_suggestions()
        
        # Run in background thread
        refresh_thread = threading.Thread(target=refresh_worker, daemon=True)
        refresh_thread.start()
        
        # Show loading state briefly
        self.title_label.configure(text="💡 Updating suggestions...")
        self.after(2000, lambda: self.title_label.configure(text="💡 Smart Suggestions"))