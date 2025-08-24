"""AI Template Generation Dialog for DVGE."""

import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Dict, Any, Optional
import json
import time


class AITemplateDialog(ctk.CTkToplevel):
    """Dialog for generating story templates using AI."""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.result = None
        self.generated_template = None
        
        # Window configuration
        self.title("AI Template Generator")
        self.geometry("700x800")
        self.minsize(600, 700)
        self.configure(fg_color=("#F0F0F0", "#2B2B2B"))
        
        # Make modal
        self.transient(app)
        self.grab_set()
        
        # Center on parent
        self.center_on_parent()
        
        # Setup UI
        self.setup_ui()
        
        # Focus on first input
        self.after(100, lambda: self.genre_entry.focus())
        
    def center_on_parent(self):
        """Center the dialog on the parent window."""
        self.update_idletasks()
        parent_x = self.app.winfo_rootx()
        parent_y = self.app.winfo_rooty()
        parent_width = self.app.winfo_width()
        parent_height = self.app.winfo_height()
        
        x = parent_x + (parent_width - self.winfo_width()) // 2
        y = parent_y + (parent_height - self.winfo_height()) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Set up the dialog UI."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        ctk.CTkLabel(
            header_frame,
            text="🤖",
            font=ctk.CTkFont(size=24)
        ).grid(row=0, column=0, padx=(10, 5), pady=10)
        
        # Title
        ctk.CTkLabel(
            header_frame,
            text="AI Template Generator",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=1, sticky="w", padx=(5, 10), pady=10)
        
        # Description
        ctk.CTkLabel(
            header_frame,
            text="Generate a complete story template with AI assistance",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray70")
        ).grid(row=1, column=1, sticky="w", padx=(5, 10))
        
        # Main content
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Template preferences section
        self.create_preferences_section(main_frame)
        
        # Generated template preview section
        self.create_preview_section(main_frame)
        
        # Buttons
        self.create_buttons()
    
    def create_preferences_section(self, parent):
        """Create the template preferences section."""
        # Preferences frame
        prefs_frame = ctk.CTkFrame(parent)
        prefs_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        prefs_frame.grid_columnconfigure(1, weight=1)
        
        # Section header
        ctk.CTkLabel(
            prefs_frame,
            text="Template Preferences",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))
        
        row = 1
        
        # Genre
        ctk.CTkLabel(prefs_frame, text="Genre:").grid(
            row=row, column=0, sticky="w", padx=(15, 5), pady=5
        )
        self.genre_entry = ctk.CTkEntry(
            prefs_frame,
            placeholder_text="e.g., Fantasy, Sci-Fi, Mystery, Romance..."
        )
        self.genre_entry.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=5)
        row += 1
        
        # Setting
        ctk.CTkLabel(prefs_frame, text="Setting:").grid(
            row=row, column=0, sticky="w", padx=(15, 5), pady=5
        )
        self.setting_entry = ctk.CTkEntry(
            prefs_frame,
            placeholder_text="e.g., Medieval castle, Space station, Modern city..."
        )
        self.setting_entry.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=5)
        row += 1
        
        # Tone
        ctk.CTkLabel(prefs_frame, text="Tone:").grid(
            row=row, column=0, sticky="w", padx=(15, 5), pady=5
        )
        self.tone_var = ctk.StringVar(value="Adventurous")
        self.tone_menu = ctk.CTkOptionMenu(
            prefs_frame,
            variable=self.tone_var,
            values=["Adventurous", "Dark", "Lighthearted", "Mysterious", "Romantic", "Dramatic", "Comedic"]
        )
        self.tone_menu.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=5)
        row += 1
        
        # Template size
        ctk.CTkLabel(prefs_frame, text="Template Size:").grid(
            row=row, column=0, sticky="w", padx=(15, 5), pady=5
        )
        self.size_var = ctk.StringVar(value="Medium")
        self.size_menu = ctk.CTkOptionMenu(
            prefs_frame,
            variable=self.size_var,
            values=["Small (5-10 nodes)", "Medium (15-25 nodes)", "Large (30-50 nodes)"]
        )
        self.size_menu.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=5)
        row += 1
        
        # Main character description
        ctk.CTkLabel(prefs_frame, text="Main Character:").grid(
            row=row, column=0, sticky="nw", padx=(15, 5), pady=5
        )
        self.character_text = ctk.CTkTextbox(
            prefs_frame,
            height=60,
            placeholder_text="Describe the main character (optional)..."
        )
        self.character_text.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=5)
        row += 1
        
        # Story concept
        ctk.CTkLabel(prefs_frame, text="Story Concept:").grid(
            row=row, column=0, sticky="nw", padx=(15, 5), pady=5
        )
        self.concept_text = ctk.CTkTextbox(
            prefs_frame,
            height=80,
            placeholder_text="Describe your story idea, themes, or specific elements you want included..."
        )
        self.concept_text.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=5)
        row += 1
        
        # Generate button
        self.generate_button = ctk.CTkButton(
            prefs_frame,
            text="🧠 Generate Template with AI",
            command=self.generate_template,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#4CAF50", "#45A049"),
            hover_color=("#45A049", "#3E8E41")
        )
        self.generate_button.grid(row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=15)
    
    def create_preview_section(self, parent):
        """Create the template preview section."""
        # Preview frame
        preview_frame = ctk.CTkFrame(parent)
        preview_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        # Section header
        self.preview_header = ctk.CTkLabel(
            preview_frame,
            text="Generated Template Preview",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.preview_header.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        # Preview text area
        self.preview_text = ctk.CTkTextbox(
            preview_frame,
            height=300,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.preview_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Initial placeholder
        self.preview_text.insert("1.0", "Generated template will appear here...\n\n" + 
                                "Click 'Generate Template with AI' to create a custom story template based on your preferences.")
        self.preview_text.configure(state="disabled")
    
    def create_buttons(self):
        """Create the dialog buttons."""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=100,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        cancel_button.grid(row=0, column=0, padx=(0, 10))
        
        # Apply button (initially disabled)
        self.apply_button = ctk.CTkButton(
            button_frame,
            text="Apply Template",
            command=self.apply_template,
            width=120,
            state="disabled"
        )
        self.apply_button.grid(row=0, column=2, padx=(10, 0))
    
    def generate_template(self):
        """Generate a template using AI."""
        # Validate input
        if not self.genre_entry.get().strip():
            messagebox.showwarning("Missing Information", "Please specify a genre for your story.")
            self.genre_entry.focus()
            return
        
        # Disable generate button and show loading
        self.generate_button.configure(text="🧠 Generating Template...", state="disabled")
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", "🤖 AI is crafting your story template...\n\nThis may take a few moments.")
        self.preview_text.configure(state="disabled")
        
        # Run generation in background thread
        def generate_worker():
            try:
                success = self._generate_template_with_ai()
                
                # Update UI in main thread
                self.after(0, lambda: self._on_generation_complete(success))
                
            except Exception as e:
                self.after(0, lambda: self._on_generation_error(str(e)))
        
        thread = threading.Thread(target=generate_worker, daemon=True)
        thread.start()
    
    def _generate_template_with_ai(self) -> bool:
        """Generate template using AI service."""
        try:
            # Check if AI service is available
            if not hasattr(self.app, 'ai_service') or not self.app.ai_service:
                raise Exception("AI service is not available")
            
            if not self.app.ai_service.is_enhanced_ai_available():
                raise Exception("Enhanced AI features are not available")
            
            # Prepare template preferences
            preferences = {
                'genre': self.genre_entry.get().strip(),
                'setting': self.setting_entry.get().strip(),
                'tone': self.tone_var.get(),
                'template_size': self.size_var.get(),
                'main_character': self.character_text.get("1.0", "end").strip(),
                'story_concept': self.concept_text.get("1.0", "end").strip()
            }
            
            # Generate template using AI
            template_manager = self.app.ai_service.template_manager
            if template_manager:
                self.generated_template = template_manager.generate_template(preferences)
                return True
            else:
                raise Exception("Template manager not available")
                
        except Exception as e:
            print(f"Template generation error: {e}")
            raise e
        
        return False
    
    def _on_generation_complete(self, success: bool):
        """Handle completed template generation."""
        # Re-enable generate button
        self.generate_button.configure(text="🧠 Generate Template with AI", state="normal")
        
        if success and self.generated_template:
            # Show generated template
            self.preview_text.configure(state="normal")
            self.preview_text.delete("1.0", "end")
            
            # Format template for display
            template_text = self._format_template_for_display(self.generated_template)
            self.preview_text.insert("1.0", template_text)
            self.preview_text.configure(state="disabled")
            
            # Enable apply button
            self.apply_button.configure(state="normal")
            
            # Update header
            self.preview_header.configure(text=f"Generated Template: {self.generated_template.get('name', 'Custom Template')}")
            
        else:
            self._show_generation_error("Failed to generate template. Please try again.")
    
    def _on_generation_error(self, error_message: str):
        """Handle template generation error."""
        self.generate_button.configure(text="🧠 Generate Template with AI", state="normal")
        self._show_generation_error(f"Error generating template: {error_message}")
    
    def _show_generation_error(self, message: str):
        """Show error message in preview area."""
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", f"❌ {message}\n\nPlease check your preferences and try again.")
        self.preview_text.configure(state="disabled")
        
        messagebox.showerror("Generation Error", message)
    
    def _format_template_for_display(self, template: Dict[str, Any]) -> str:
        """Format the generated template for display."""
        lines = []
        
        lines.append(f"📖 Template: {template.get('name', 'Custom Template')}")
        lines.append(f"📝 Description: {template.get('description', 'AI-generated template')}")
        lines.append("")
        
        if 'nodes' in template and template['nodes']:
            lines.append(f"🎭 Story Nodes: {len(template['nodes'])} nodes")
            lines.append("")
            
            # Show first few nodes as preview
            for i, node in enumerate(template['nodes'][:5]):
                node_text = node.get('text', 'No text')[:100]
                if len(node_text) == 100:
                    node_text += "..."
                lines.append(f"Node {i+1}: {node_text}")
            
            if len(template['nodes']) > 5:
                lines.append(f"... and {len(template['nodes']) - 5} more nodes")
            
            lines.append("")
        
        if 'characters' in template and template['characters']:
            lines.append(f"👥 Characters: {len(template['characters'])}")
            for char in template['characters']:
                lines.append(f"• {char.get('name', 'Unnamed')}: {char.get('description', 'No description')}")
            lines.append("")
        
        if 'variables' in template and template['variables']:
            lines.append(f"🔧 Variables: {len(template['variables'])}")
            for var_name, var_value in template['variables'].items():
                lines.append(f"• {var_name}: {var_value}")
            lines.append("")
        
        if 'story_flags' in template and template['story_flags']:
            lines.append(f"🚩 Story Flags: {len(template['story_flags'])}")
            lines.append("")
        
        lines.append("✨ This template is ready to be applied to your project!")
        
        return "\n".join(lines)
    
    def apply_template(self):
        """Apply the generated template."""
        if not self.generated_template:
            messagebox.showwarning("No Template", "No template has been generated yet.")
            return
        
        # Confirm application
        response = messagebox.askyesno(
            "Apply Template",
            f"Apply the generated template '{self.generated_template.get('name', 'Custom Template')}'?\n\n" + 
            "This will replace your current project content. This action can be undone.",
            icon="question"
        )
        
        if response:
            self.result = {
                'action': 'apply_template',
                'template': self.generated_template
            }
            self.destroy()
    
    def cancel(self):
        """Cancel the dialog."""
        self.result = {'action': 'cancel'}
        self.destroy()
    
    def show(self) -> Optional[Dict[str, Any]]:
        """Show the dialog and return the result."""
        # Wait for dialog to close
        self.wait_window()
        return self.result