"""AI Story Analysis Dialog for DVGE."""

import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Dict, Any, List
import json


class AIAnalysisDialog(ctk.CTkToplevel):
    """Dialog for AI-powered story analysis."""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.analysis_results = None
        
        # Window configuration
        self.title("AI Story Analysis")
        self.geometry("800x700")
        self.minsize(700, 600)
        self.configure(fg_color=("#F0F0F0", "#2B2B2B"))
        
        # Make modal
        self.transient(app)
        self.grab_set()
        
        # Center on parent
        self.center_on_parent()
        
        # Setup UI
        self.setup_ui()
        
        # Auto-run analysis
        self.after(500, self.run_analysis)
        
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
            text="🔍",
            font=ctk.CTkFont(size=24)
        ).grid(row=0, column=0, padx=(10, 5), pady=10)
        
        # Title and description
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="ew", padx=(5, 10), pady=10)
        title_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            title_frame,
            text="AI Story Analysis",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Comprehensive analysis of your story structure, pacing, and quality",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray70"),
            anchor="w"
        ).grid(row=1, column=0, sticky="w")
        
        # Analysis sections
        self.create_analysis_sections()
        
        # Buttons
        self.create_buttons()
    
    def create_analysis_sections(self):
        """Create the analysis results sections."""
        # Main content frame
        content_frame = ctk.CTkScrollableFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Overview section
        self.create_overview_section(content_frame, 0)
        
        # Structure analysis section
        self.create_structure_section(content_frame, 1)
        
        # Character analysis section
        self.create_character_section(content_frame, 2)
        
        # Pacing analysis section
        self.create_pacing_section(content_frame, 3)
        
        # Issues and recommendations section
        self.create_recommendations_section(content_frame, 4)
    
    def create_overview_section(self, parent, row):
        """Create the story overview section."""
        section_frame = ctk.CTkFrame(parent)
        section_frame.grid(row=row, column=0, sticky="ew", pady=(0, 15))
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        ctk.CTkLabel(
            section_frame,
            text="📊 Story Overview",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        # Overview text
        self.overview_text = ctk.CTkTextbox(
            section_frame,
            height=100,
            font=ctk.CTkFont(size=12)
        )
        self.overview_text.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.overview_text.insert("1.0", "Analyzing story overview...")
        self.overview_text.configure(state="disabled")
    
    def create_structure_section(self, parent, row):
        """Create the story structure analysis section."""
        section_frame = ctk.CTkFrame(parent)
        section_frame.grid(row=row, column=0, sticky="ew", pady=(0, 15))
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        ctk.CTkLabel(
            section_frame,
            text="🏗️ Story Structure",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        # Structure analysis
        self.structure_text = ctk.CTkTextbox(
            section_frame,
            height=120,
            font=ctk.CTkFont(size=12)
        )
        self.structure_text.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.structure_text.insert("1.0", "Analyzing story structure...")
        self.structure_text.configure(state="disabled")
    
    def create_character_section(self, parent, row):
        """Create the character analysis section."""
        section_frame = ctk.CTkFrame(parent)
        section_frame.grid(row=row, column=0, sticky="ew", pady=(0, 15))
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        ctk.CTkLabel(
            section_frame,
            text="👥 Character Analysis",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        # Character analysis
        self.character_text = ctk.CTkTextbox(
            section_frame,
            height=100,
            font=ctk.CTkFont(size=12)
        )
        self.character_text.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.character_text.insert("1.0", "Analyzing characters...")
        self.character_text.configure(state="disabled")
    
    def create_pacing_section(self, parent, row):
        """Create the pacing analysis section."""
        section_frame = ctk.CTkFrame(parent)
        section_frame.grid(row=row, column=0, sticky="ew", pady=(0, 15))
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        ctk.CTkLabel(
            section_frame,
            text="⏱️ Pacing Analysis",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        # Pacing analysis
        self.pacing_text = ctk.CTkTextbox(
            section_frame,
            height=100,
            font=ctk.CTkFont(size=12)
        )
        self.pacing_text.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.pacing_text.insert("1.0", "Analyzing pacing...")
        self.pacing_text.configure(state="disabled")
    
    def create_recommendations_section(self, parent, row):
        """Create the recommendations section."""
        section_frame = ctk.CTkFrame(parent)
        section_frame.grid(row=row, column=0, sticky="ew", pady=(0, 15))
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        ctk.CTkLabel(
            section_frame,
            text="💡 Issues & Recommendations",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        # Recommendations
        self.recommendations_text = ctk.CTkTextbox(
            section_frame,
            height=150,
            font=ctk.CTkFont(size=12)
        )
        self.recommendations_text.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.recommendations_text.insert("1.0", "Generating recommendations...")
        self.recommendations_text.configure(state="disabled")
    
    def create_buttons(self):
        """Create the dialog buttons."""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Refresh analysis button
        self.refresh_button = ctk.CTkButton(
            button_frame,
            text="🔄 Refresh Analysis",
            command=self.run_analysis,
            width=150
        )
        self.refresh_button.grid(row=0, column=0, padx=(0, 10))
        
        # Close button
        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.destroy,
            width=100
        )
        close_button.grid(row=0, column=2)
    
    def run_analysis(self):
        """Run the AI story analysis."""
        # Disable refresh button
        self.refresh_button.configure(text="🔄 Analyzing...", state="disabled")
        
        # Reset all text areas
        text_areas = [
            (self.overview_text, "Analyzing story overview..."),
            (self.structure_text, "Analyzing story structure..."),
            (self.character_text, "Analyzing characters..."),
            (self.pacing_text, "Analyzing pacing..."),
            (self.recommendations_text, "Generating recommendations...")
        ]
        
        for text_widget, placeholder in text_areas:
            text_widget.configure(state="normal")
            text_widget.delete("1.0", "end")
            text_widget.insert("1.0", placeholder)
            text_widget.configure(state="disabled")
        
        # Run analysis in background
        def analysis_worker():
            try:
                success = self._run_ai_analysis()
                self.after(0, lambda: self._on_analysis_complete(success))
            except Exception as e:
                self.after(0, lambda: self._on_analysis_error(str(e)))
        
        thread = threading.Thread(target=analysis_worker, daemon=True)
        thread.start()
    
    def _run_ai_analysis(self) -> bool:
        """Run the actual AI analysis."""
        try:
            # Check if AI service is available
            if not hasattr(self.app, 'ai_service') or not self.app.ai_service:
                raise Exception("AI service is not available")
            
            if not self.app.ai_service.is_enhanced_ai_available():
                raise Exception("Enhanced AI features are not available")
            
            # Get story analyzer
            analyzer = self.app.ai_service.enhanced_systems.story_analyzer
            
            if not analyzer:
                raise Exception("Story analyzer not available")
            
            # Prepare story data for analysis
            story_data = {
                'nodes': self.app.nodes,
                'variables': self.app.variables,
                'story_flags': self.app.story_flags,
                'quests': self.app.quests,
                'player_stats': self.app.player_stats
            }
            
            # Run comprehensive analysis
            self.analysis_results = analyzer.analyze_complete_story(story_data)
            
            return True
            
        except Exception as e:
            print(f"Analysis error: {e}")
            raise e
    
    def _on_analysis_complete(self, success: bool):
        """Handle completed analysis."""
        # Re-enable refresh button
        self.refresh_button.configure(text="🔄 Refresh Analysis", state="normal")
        
        if success and self.analysis_results:
            self._display_analysis_results()
        else:
            self._show_analysis_error("Analysis failed. Please try again.")
    
    def _on_analysis_error(self, error_message: str):
        """Handle analysis error."""
        self.refresh_button.configure(text="🔄 Refresh Analysis", state="normal")
        self._show_analysis_error(f"Error during analysis: {error_message}")
    
    def _display_analysis_results(self):
        """Display the analysis results in the UI."""
        if not self.analysis_results:
            return
        
        # Update overview
        overview = self.analysis_results.get('overview', 'No overview available')
        self.overview_text.configure(state="normal")
        self.overview_text.delete("1.0", "end")
        self.overview_text.insert("1.0", overview)
        self.overview_text.configure(state="disabled")
        
        # Update structure analysis
        structure = self.analysis_results.get('structure_analysis', 'No structure analysis available')
        self.structure_text.configure(state="normal")
        self.structure_text.delete("1.0", "end")
        self.structure_text.insert("1.0", structure)
        self.structure_text.configure(state="disabled")
        
        # Update character analysis
        characters = self.analysis_results.get('character_analysis', 'No character analysis available')
        self.character_text.configure(state="normal")
        self.character_text.delete("1.0", "end")
        self.character_text.insert("1.0", characters)
        self.character_text.configure(state="disabled")
        
        # Update pacing analysis
        pacing = self.analysis_results.get('pacing_analysis', 'No pacing analysis available')
        self.pacing_text.configure(state="normal")
        self.pacing_text.delete("1.0", "end")
        self.pacing_text.insert("1.0", pacing)
        self.pacing_text.configure(state="disabled")
        
        # Update recommendations
        recommendations = self.analysis_results.get('recommendations', 'No recommendations available')
        if isinstance(recommendations, list):
            recommendations = "\n\n".join(f"• {rec}" for rec in recommendations)
        
        self.recommendations_text.configure(state="normal")
        self.recommendations_text.delete("1.0", "end")
        self.recommendations_text.insert("1.0", recommendations)
        self.recommendations_text.configure(state="disabled")
    
    def _show_analysis_error(self, message: str):
        """Show error message in all text areas."""
        error_text = f"❌ {message}\n\nPlease check that:\n• Your project has story nodes\n• AI service is properly configured\n• Network connection is available"
        
        text_areas = [
            self.overview_text, self.structure_text, self.character_text,
            self.pacing_text, self.recommendations_text
        ]
        
        for text_widget in text_areas:
            text_widget.configure(state="normal")
            text_widget.delete("1.0", "end")
            text_widget.insert("1.0", error_text)
            text_widget.configure(state="disabled")
        
        messagebox.showerror("Analysis Error", message)