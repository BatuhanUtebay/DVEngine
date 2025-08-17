# dvge/ui/windows/style_customizer.py

"""Advanced HTML export style customization window."""

import tkinter as tk
import tkinter.simpledialog
from tkinter import ttk, colorchooser, filedialog, messagebox
import customtkinter as ctk
import json
import os
from typing import Dict, Any, Optional
import re


class StyleCustomizer(ctk.CTkToplevel):
    """Advanced customization window for HTML export styling."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.parent = parent
        
        # Window setup
        self.title("Advanced HTML Export Customization")
        self.geometry("1200x800")
        self.resizable(True, True)
        
        # Style settings storage
        self.style_settings = self.load_default_settings()
        self.export_profiles = self.load_export_profiles()
        
        # Current preview HTML
        self.preview_html = ""
        
        self.setup_ui()
        self.load_current_settings()
        
    def load_default_settings(self) -> Dict[str, Any]:
        """Load default style settings."""
        return {
            # Colors
            "background_color": "#ffffff",
            "text_color": "#333333",
            "accent_color": "#007bff",
            "choice_color": "#0056b3",
            "choice_hover_color": "#004085",
            "npc_name_color": "#2c3e50",
            
            # Typography
            "font_family": "Georgia, serif",
            "font_size": "16px",
            "line_height": "1.6",
            "heading_font": "Arial, sans-serif",
            "heading_size": "24px",
            
            # Layout
            "max_width": "800px",
            "padding": "40px",
            "margin": "20px auto",
            "border_radius": "8px",
            
            # Background
            "background_type": "solid",  # solid, gradient, image, pattern
            "background_image": "",
            "background_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "background_pattern": "none",
            
            # Animations
            "enable_animations": True,
            "typing_effect": False,
            "typing_speed": 50,
            "transition_duration": "0.3s",
            "fade_in_effect": True,
            
            # Advanced
            "custom_css": "",
            "mobile_responsive": True,
            "high_contrast": False,
            "dark_mode": False,
            
            # Export options
            "minify_css": False,
            "include_analytics": False,
            "embed_fonts": True
        }
    
    def load_export_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load saved export profiles."""
        profile_file = os.path.join(os.path.dirname(__file__), "../../data/export_profiles.json")
        if os.path.exists(profile_file):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Default profiles
        return {
            "Default": self.load_default_settings(),
            "Dark Mode": {
                **self.load_default_settings(),
                "background_color": "#1a1a1a",
                "text_color": "#e0e0e0",
                "accent_color": "#4a9eff",
                "choice_color": "#357abd",
                "npc_name_color": "#64b5f6",
                "dark_mode": True
            },
            "Terminal": {
                **self.load_default_settings(),
                "background_color": "#000000",
                "text_color": "#00ff00",
                "accent_color": "#00ff00",
                "choice_color": "#00cc00",
                "font_family": "Courier New, monospace",
                "background_type": "solid"
            },
            "Fantasy": {
                **self.load_default_settings(),
                "background_color": "#f4f1e8",
                "text_color": "#3d2914",
                "accent_color": "#8b4513",
                "choice_color": "#a0522d",
                "font_family": "Cinzel, serif",
                "border_radius": "15px"
            }
        }
    
    def setup_ui(self):
        """Setup the user interface."""
        # Create main container with scrolling
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create notebook for different customization categories
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create tabs
        self.create_colors_tab()
        self.create_typography_tab()
        self.create_layout_tab()
        self.create_background_tab()
        self.create_animations_tab()
        self.create_advanced_tab()
        self.create_profiles_tab()
        
        # Create preview and control buttons
        self.create_bottom_controls()
    
    def create_colors_tab(self):
        """Create colors customization tab."""
        colors_frame = ttk.Frame(self.notebook)
        self.notebook.add(colors_frame, text="Colors")
        
        # Create scrollable frame
        canvas = tk.Canvas(colors_frame)
        scrollbar = ttk.Scrollbar(colors_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Color settings
        color_settings = [
            ("Background Color", "background_color"),
            ("Text Color", "text_color"),
            ("Accent Color", "accent_color"),
            ("Choice Button Color", "choice_color"),
            ("Choice Hover Color", "choice_hover_color"),
            ("NPC Name Color", "npc_name_color")
        ]
        
        self.color_vars = {}
        for i, (label, key) in enumerate(color_settings):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(frame, text=label).pack(side="left")
            
            color_frame = ttk.Frame(frame)
            color_frame.pack(side="right")
            
            # Color preview
            color_preview = tk.Label(color_frame, width=3, height=1, relief="solid", borderwidth=1)
            color_preview.pack(side="left", padx=(0, 5))
            
            # Color button
            color_btn = ttk.Button(color_frame, text="Choose", 
                                 command=lambda k=key, p=color_preview: self.choose_color(k, p))
            color_btn.pack(side="left")
            
            self.color_vars[key] = color_preview
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_typography_tab(self):
        """Create typography customization tab."""
        typo_frame = ttk.Frame(self.notebook)
        self.notebook.add(typo_frame, text="Typography")
        
        # Font family
        ttk.Label(typo_frame, text="Font Family:").pack(anchor="w", padx=10, pady=(10, 5))
        self.font_family_var = tk.StringVar()
        font_combo = ttk.Combobox(typo_frame, textvariable=self.font_family_var, values=[
            "Georgia, serif",
            "Arial, sans-serif",
            "Times New Roman, serif",
            "Helvetica, sans-serif",
            "Courier New, monospace",
            "Verdana, sans-serif",
            "Trebuchet MS, sans-serif",
            "Comic Sans MS, cursive",
            "Impact, sans-serif",
            "Cinzel, serif",
            "Roboto, sans-serif"
        ])
        font_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        # Font size
        ttk.Label(typo_frame, text="Font Size:").pack(anchor="w", padx=10, pady=(0, 5))
        self.font_size_var = tk.StringVar()
        font_size_frame = ttk.Frame(typo_frame)
        font_size_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Entry(font_size_frame, textvariable=self.font_size_var, width=10).pack(side="left")
        ttk.Label(font_size_frame, text="px").pack(side="left", padx=(5, 0))
        
        # Line height
        ttk.Label(typo_frame, text="Line Height:").pack(anchor="w", padx=10, pady=(0, 5))
        self.line_height_var = tk.StringVar()
        ttk.Entry(typo_frame, textvariable=self.line_height_var, width=10).pack(anchor="w", padx=10, pady=(0, 10))
        
        # Heading font
        ttk.Label(typo_frame, text="Heading Font:").pack(anchor="w", padx=10, pady=(0, 5))
        self.heading_font_var = tk.StringVar()
        heading_combo = ttk.Combobox(typo_frame, textvariable=self.heading_font_var, values=[
            "Arial, sans-serif",
            "Georgia, serif",
            "Times New Roman, serif",
            "Helvetica, sans-serif",
            "Verdana, sans-serif",
            "Trebuchet MS, sans-serif",
            "Impact, sans-serif",
            "Cinzel, serif"
        ])
        heading_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        # Heading size
        ttk.Label(typo_frame, text="Heading Size:").pack(anchor="w", padx=10, pady=(0, 5))
        self.heading_size_var = tk.StringVar()
        heading_size_frame = ttk.Frame(typo_frame)
        heading_size_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Entry(heading_size_frame, textvariable=self.heading_size_var, width=10).pack(side="left")
        ttk.Label(heading_size_frame, text="px").pack(side="left", padx=(5, 0))
    
    def create_layout_tab(self):
        """Create layout customization tab."""
        layout_frame = ttk.Frame(self.notebook)
        self.notebook.add(layout_frame, text="Layout")
        
        # Max width
        ttk.Label(layout_frame, text="Max Width:").pack(anchor="w", padx=10, pady=(10, 5))
        self.max_width_var = tk.StringVar()
        width_frame = ttk.Frame(layout_frame)
        width_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Entry(width_frame, textvariable=self.max_width_var, width=10).pack(side="left")
        ttk.Label(width_frame, text="px").pack(side="left", padx=(5, 0))
        
        # Padding
        ttk.Label(layout_frame, text="Padding:").pack(anchor="w", padx=10, pady=(0, 5))
        self.padding_var = tk.StringVar()
        padding_frame = ttk.Frame(layout_frame)
        padding_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Entry(padding_frame, textvariable=self.padding_var, width=10).pack(side="left")
        ttk.Label(padding_frame, text="px").pack(side="left", padx=(5, 0))
        
        # Margin
        ttk.Label(layout_frame, text="Margin:").pack(anchor="w", padx=10, pady=(0, 5))
        self.margin_var = tk.StringVar()
        ttk.Entry(layout_frame, textvariable=self.margin_var).pack(fill="x", padx=10, pady=(0, 10))
        
        # Border radius
        ttk.Label(layout_frame, text="Border Radius:").pack(anchor="w", padx=10, pady=(0, 5))
        self.border_radius_var = tk.StringVar()
        radius_frame = ttk.Frame(layout_frame)
        radius_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Entry(radius_frame, textvariable=self.border_radius_var, width=10).pack(side="left")
        ttk.Label(radius_frame, text="px").pack(side="left", padx=(5, 0))
        
        # Mobile responsive
        self.mobile_responsive_var = tk.BooleanVar()
        ttk.Checkbutton(layout_frame, text="Mobile Responsive", 
                       variable=self.mobile_responsive_var).pack(anchor="w", padx=10, pady=5)
    
    def create_background_tab(self):
        """Create background customization tab."""
        bg_frame = ttk.Frame(self.notebook)
        self.notebook.add(bg_frame, text="Background")
        
        # Background type
        ttk.Label(bg_frame, text="Background Type:").pack(anchor="w", padx=10, pady=(10, 5))
        self.bg_type_var = tk.StringVar()
        bg_type_combo = ttk.Combobox(bg_frame, textvariable=self.bg_type_var, values=[
            "solid", "gradient", "image", "pattern"
        ])
        bg_type_combo.pack(fill="x", padx=10, pady=(0, 10))
        bg_type_combo.bind("<<ComboboxSelected>>", self.on_bg_type_changed)
        
        # Background image
        self.bg_image_frame = ttk.LabelFrame(bg_frame, text="Background Image")
        self.bg_image_frame.pack(fill="x", padx=10, pady=5)
        
        self.bg_image_var = tk.StringVar()
        ttk.Entry(self.bg_image_frame, textvariable=self.bg_image_var).pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Button(self.bg_image_frame, text="Browse", command=self.browse_bg_image).pack(side="right", padx=5, pady=5)
        
        # Background gradient
        self.bg_gradient_frame = ttk.LabelFrame(bg_frame, text="Background Gradient")
        self.bg_gradient_frame.pack(fill="x", padx=10, pady=5)
        
        self.bg_gradient_var = tk.StringVar()
        ttk.Entry(self.bg_gradient_frame, textvariable=self.bg_gradient_var).pack(fill="x", padx=5, pady=5)
        
        # Gradient presets
        gradient_presets = ttk.Frame(self.bg_gradient_frame)
        gradient_presets.pack(fill="x", padx=5, pady=5)
        
        presets = [
            ("Blue Purple", "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"),
            ("Sunset", "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"),
            ("Ocean", "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"),
            ("Forest", "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)")
        ]
        
        for name, gradient in presets:
            ttk.Button(gradient_presets, text=name, 
                      command=lambda g=gradient: self.bg_gradient_var.set(g)).pack(side="left", padx=2)
        
        # Background pattern
        self.bg_pattern_frame = ttk.LabelFrame(bg_frame, text="Background Pattern")
        self.bg_pattern_frame.pack(fill="x", padx=10, pady=5)
        
        self.bg_pattern_var = tk.StringVar()
        pattern_combo = ttk.Combobox(self.bg_pattern_frame, textvariable=self.bg_pattern_var, values=[
            "none", "dots", "grid", "diagonal", "hexagon", "triangles"
        ])
        pattern_combo.pack(fill="x", padx=5, pady=5)
    
    def create_animations_tab(self):
        """Create animations customization tab."""
        anim_frame = ttk.Frame(self.notebook)
        self.notebook.add(anim_frame, text="Animations")
        
        # Enable animations
        self.enable_animations_var = tk.BooleanVar()
        ttk.Checkbutton(anim_frame, text="Enable Animations", 
                       variable=self.enable_animations_var).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Typing effect
        self.typing_effect_var = tk.BooleanVar()
        ttk.Checkbutton(anim_frame, text="Typing Effect", 
                       variable=self.typing_effect_var).pack(anchor="w", padx=10, pady=5)
        
        # Typing speed
        ttk.Label(anim_frame, text="Typing Speed (ms):").pack(anchor="w", padx=10, pady=(10, 5))
        self.typing_speed_var = tk.StringVar()
        ttk.Entry(anim_frame, textvariable=self.typing_speed_var, width=10).pack(anchor="w", padx=10, pady=(0, 10))
        
        # Transition duration
        ttk.Label(anim_frame, text="Transition Duration:").pack(anchor="w", padx=10, pady=(0, 5))
        self.transition_duration_var = tk.StringVar()
        ttk.Entry(anim_frame, textvariable=self.transition_duration_var, width=10).pack(anchor="w", padx=10, pady=(0, 10))
        
        # Fade in effect
        self.fade_in_effect_var = tk.BooleanVar()
        ttk.Checkbutton(anim_frame, text="Fade In Effect", 
                       variable=self.fade_in_effect_var).pack(anchor="w", padx=10, pady=5)
    
    def create_advanced_tab(self):
        """Create advanced customization tab."""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="Advanced")
        
        # Custom CSS
        ttk.Label(advanced_frame, text="Custom CSS:").pack(anchor="w", padx=10, pady=(10, 5))
        
        css_frame = ttk.Frame(advanced_frame)
        css_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # CSS text area with scrollbar
        self.custom_css_text = tk.Text(css_frame, height=15, wrap="none")
        css_scrollbar_y = ttk.Scrollbar(css_frame, orient="vertical", command=self.custom_css_text.yview)
        css_scrollbar_x = ttk.Scrollbar(css_frame, orient="horizontal", command=self.custom_css_text.xview)
        
        self.custom_css_text.configure(yscrollcommand=css_scrollbar_y.set, xscrollcommand=css_scrollbar_x.set)
        
        self.custom_css_text.grid(row=0, column=0, sticky="nsew")
        css_scrollbar_y.grid(row=0, column=1, sticky="ns")
        css_scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        css_frame.grid_rowconfigure(0, weight=1)
        css_frame.grid_columnconfigure(0, weight=1)
        
        # CSS buttons
        css_buttons = ttk.Frame(advanced_frame)
        css_buttons.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(css_buttons, text="Load CSS File", command=self.load_css_file).pack(side="left", padx=(0, 5))
        ttk.Button(css_buttons, text="Save CSS File", command=self.save_css_file).pack(side="left", padx=5)
        ttk.Button(css_buttons, text="Reset CSS", command=self.reset_css).pack(side="left", padx=5)
        
        # Advanced options
        options_frame = ttk.LabelFrame(advanced_frame, text="Advanced Options")
        options_frame.pack(fill="x", padx=10, pady=10)
        
        self.high_contrast_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="High Contrast Mode", 
                       variable=self.high_contrast_var).pack(anchor="w", padx=5, pady=2)
        
        self.dark_mode_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Dark Mode", 
                       variable=self.dark_mode_var).pack(anchor="w", padx=5, pady=2)
        
        self.minify_css_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Minify CSS", 
                       variable=self.minify_css_var).pack(anchor="w", padx=5, pady=2)
        
        self.embed_fonts_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Embed Web Fonts", 
                       variable=self.embed_fonts_var).pack(anchor="w", padx=5, pady=2)
    
    def create_profiles_tab(self):
        """Create export profiles management tab."""
        profiles_frame = ttk.Frame(self.notebook)
        self.notebook.add(profiles_frame, text="Profiles")
        
        # Profile selection
        profile_select_frame = ttk.Frame(profiles_frame)
        profile_select_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(profile_select_frame, text="Profile:").pack(side="left")
        
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(profile_select_frame, textvariable=self.profile_var, 
                                         values=list(self.export_profiles.keys()))
        self.profile_combo.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.profile_combo.bind("<<ComboboxSelected>>", self.load_profile)
        
        # Profile buttons
        profile_buttons = ttk.Frame(profiles_frame)
        profile_buttons.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(profile_buttons, text="Load Profile", command=self.load_selected_profile).pack(side="left", padx=(0, 5))
        ttk.Button(profile_buttons, text="Save Profile", command=self.save_current_profile).pack(side="left", padx=5)
        ttk.Button(profile_buttons, text="Delete Profile", command=self.delete_profile).pack(side="left", padx=5)
        ttk.Button(profile_buttons, text="Export Profile", command=self.export_profile).pack(side="left", padx=5)
        ttk.Button(profile_buttons, text="Import Profile", command=self.import_profile).pack(side="left", padx=5)
        
        # Profile description
        ttk.Label(profiles_frame, text="Profile Description:").pack(anchor="w", padx=10, pady=(20, 5))
        self.profile_desc_text = tk.Text(profiles_frame, height=4)
        self.profile_desc_text.pack(fill="x", padx=10, pady=(0, 10))
    
    def create_bottom_controls(self):
        """Create bottom control buttons."""
        controls_frame = ctk.CTkFrame(self)
        controls_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Preview button
        preview_btn = ctk.CTkButton(controls_frame, text="Preview Changes", command=self.preview_changes)
        preview_btn.pack(side="left", padx=5, pady=10)
        
        # Apply button
        apply_btn = ctk.CTkButton(controls_frame, text="Apply Settings", command=self.apply_settings)
        apply_btn.pack(side="left", padx=5, pady=10)
        
        # Reset button
        reset_btn = ctk.CTkButton(controls_frame, text="Reset to Default", command=self.reset_to_default)
        reset_btn.pack(side="left", padx=5, pady=10)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(controls_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="right", padx=5, pady=10)
    
    def choose_color(self, color_key: str, preview_label: tk.Label):
        """Open color chooser and update color setting."""
        current_color = self.style_settings.get(color_key, "#ffffff")
        color = colorchooser.askcolor(color=current_color, title=f"Choose {color_key.replace('_', ' ').title()}")
        
        if color[1]:  # If user didn't cancel
            self.style_settings[color_key] = color[1]
            preview_label.configure(bg=color[1])
    
    def on_bg_type_changed(self, event=None):
        """Handle background type change."""
        bg_type = self.bg_type_var.get()
        
        # Show/hide relevant frames
        if bg_type == "image":
            self.bg_image_frame.pack(fill="x", padx=10, pady=5)
            self.bg_gradient_frame.pack_forget()
            self.bg_pattern_frame.pack_forget()
        elif bg_type == "gradient":
            self.bg_image_frame.pack_forget()
            self.bg_gradient_frame.pack(fill="x", padx=10, pady=5)
            self.bg_pattern_frame.pack_forget()
        elif bg_type == "pattern":
            self.bg_image_frame.pack_forget()
            self.bg_gradient_frame.pack_forget()
            self.bg_pattern_frame.pack(fill="x", padx=10, pady=5)
        else:  # solid
            self.bg_image_frame.pack_forget()
            self.bg_gradient_frame.pack_forget()
            self.bg_pattern_frame.pack_forget()
    
    def browse_bg_image(self):
        """Browse for background image."""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.svg"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=filetypes
        )
        
        if filename:
            self.bg_image_var.set(filename)
    
    def load_css_file(self):
        """Load CSS from file."""
        filename = filedialog.askopenfilename(
            title="Load CSS File",
            filetypes=[("CSS files", "*.css"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                    self.custom_css_text.delete(1.0, tk.END)
                    self.custom_css_text.insert(1.0, css_content)
            except IOError as e:
                messagebox.showerror("Error", f"Failed to load CSS file: {e}")
    
    def save_css_file(self):
        """Save CSS to file."""
        filename = filedialog.asksaveasfilename(
            title="Save CSS File",
            defaultextension=".css",
            filetypes=[("CSS files", "*.css"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                css_content = self.custom_css_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(css_content)
                messagebox.showinfo("Success", "CSS file saved successfully!")
            except IOError as e:
                messagebox.showerror("Error", f"Failed to save CSS file: {e}")
    
    def reset_css(self):
        """Reset custom CSS."""
        if messagebox.askyesno("Reset CSS", "Are you sure you want to clear all custom CSS?"):
            self.custom_css_text.delete(1.0, tk.END)
    
    def load_current_settings(self):
        """Load current settings into UI controls."""
        # Update color previews
        for key, preview in self.color_vars.items():
            color = self.style_settings.get(key, "#ffffff")
            preview.configure(bg=color)
        
        # Update typography
        self.font_family_var.set(self.style_settings.get("font_family", "Georgia, serif"))
        self.font_size_var.set(self.style_settings.get("font_size", "16px").replace("px", ""))
        self.line_height_var.set(self.style_settings.get("line_height", "1.6"))
        self.heading_font_var.set(self.style_settings.get("heading_font", "Arial, sans-serif"))
        self.heading_size_var.set(self.style_settings.get("heading_size", "24px").replace("px", ""))
        
        # Update layout
        self.max_width_var.set(self.style_settings.get("max_width", "800px").replace("px", ""))
        self.padding_var.set(self.style_settings.get("padding", "40px").replace("px", ""))
        self.margin_var.set(self.style_settings.get("margin", "20px auto"))
        self.border_radius_var.set(self.style_settings.get("border_radius", "8px").replace("px", ""))
        self.mobile_responsive_var.set(self.style_settings.get("mobile_responsive", True))
        
        # Update background
        self.bg_type_var.set(self.style_settings.get("background_type", "solid"))
        self.bg_image_var.set(self.style_settings.get("background_image", ""))
        self.bg_gradient_var.set(self.style_settings.get("background_gradient", ""))
        self.bg_pattern_var.set(self.style_settings.get("background_pattern", "none"))
        self.on_bg_type_changed()
        
        # Update animations
        self.enable_animations_var.set(self.style_settings.get("enable_animations", True))
        self.typing_effect_var.set(self.style_settings.get("typing_effect", False))
        self.typing_speed_var.set(str(self.style_settings.get("typing_speed", 50)))
        self.transition_duration_var.set(self.style_settings.get("transition_duration", "0.3s"))
        self.fade_in_effect_var.set(self.style_settings.get("fade_in_effect", True))
        
        # Update advanced
        self.custom_css_text.delete(1.0, tk.END)
        self.custom_css_text.insert(1.0, self.style_settings.get("custom_css", ""))
        self.high_contrast_var.set(self.style_settings.get("high_contrast", False))
        self.dark_mode_var.set(self.style_settings.get("dark_mode", False))
        self.minify_css_var.set(self.style_settings.get("minify_css", False))
        self.embed_fonts_var.set(self.style_settings.get("embed_fonts", True))
    
    def collect_settings(self) -> Dict[str, Any]:
        """Collect current settings from UI controls."""
        settings = self.style_settings.copy()
        
        # Typography
        settings["font_family"] = self.font_family_var.get()
        settings["font_size"] = f"{self.font_size_var.get()}px"
        settings["line_height"] = self.line_height_var.get()
        settings["heading_font"] = self.heading_font_var.get()
        settings["heading_size"] = f"{self.heading_size_var.get()}px"
        
        # Layout
        settings["max_width"] = f"{self.max_width_var.get()}px"
        settings["padding"] = f"{self.padding_var.get()}px"
        settings["margin"] = self.margin_var.get()
        settings["border_radius"] = f"{self.border_radius_var.get()}px"
        settings["mobile_responsive"] = self.mobile_responsive_var.get()
        
        # Background
        settings["background_type"] = self.bg_type_var.get()
        settings["background_image"] = self.bg_image_var.get()
        settings["background_gradient"] = self.bg_gradient_var.get()
        settings["background_pattern"] = self.bg_pattern_var.get()
        
        # Animations
        settings["enable_animations"] = self.enable_animations_var.get()
        settings["typing_effect"] = self.typing_effect_var.get()
        settings["typing_speed"] = int(self.typing_speed_var.get() or 50)
        settings["transition_duration"] = self.transition_duration_var.get()
        settings["fade_in_effect"] = self.fade_in_effect_var.get()
        
        # Advanced
        settings["custom_css"] = self.custom_css_text.get(1.0, tk.END).strip()
        settings["high_contrast"] = self.high_contrast_var.get()
        settings["dark_mode"] = self.dark_mode_var.get()
        settings["minify_css"] = self.minify_css_var.get()
        settings["embed_fonts"] = self.embed_fonts_var.get()
        
        return settings
    
    def preview_changes(self):
        """Generate and show preview of HTML with current settings."""
        settings = self.collect_settings()
        
        # Generate sample HTML for preview
        from ...core.html_exporter import HTMLExporter
        exporter = HTMLExporter(self.app)
        
        # Apply custom settings to exporter
        exporter.style_settings = settings
        
        # Generate preview HTML
        preview_html = exporter.generate_preview_html()
        
        # Open preview window
        self.show_preview_window(preview_html)
    
    def show_preview_window(self, html_content: str):
        """Show HTML preview in a new window."""
        preview_window = ctk.CTkToplevel(self)
        preview_window.title("HTML Export Preview")
        preview_window.geometry("900x700")
        
        # Create HTML display (simplified - in real implementation, you'd want a proper web view)
        text_widget = tk.Text(preview_window, wrap="word")
        scrollbar = ttk.Scrollbar(preview_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        text_widget.insert(1.0, html_content)
        text_widget.configure(state="disabled")
    
    def apply_settings(self):
        """Apply current settings to the main application."""
        self.style_settings = self.collect_settings()
        
        # Save settings to the app
        if hasattr(self.app, 'html_export_settings'):
            self.app.html_export_settings = self.style_settings
        
        messagebox.showinfo("Success", "Style settings applied successfully!")
        self.destroy()
    
    def reset_to_default(self):
        """Reset all settings to default values."""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to default?"):
            self.style_settings = self.load_default_settings()
            self.load_current_settings()
    
    def load_profile(self, event=None):
        """Load selected profile."""
        profile_name = self.profile_var.get()
        if profile_name in self.export_profiles:
            self.style_settings = self.export_profiles[profile_name].copy()
            self.load_current_settings()
    
    def load_selected_profile(self):
        """Load the currently selected profile."""
        self.load_profile()
    
    def save_current_profile(self):
        """Save current settings as a new profile."""
        profile_name = tk.simpledialog.askstring("Save Profile", "Enter profile name:")
        if profile_name:
            settings = self.collect_settings()
            self.export_profiles[profile_name] = settings
            
            # Update combo box
            self.profile_combo['values'] = list(self.export_profiles.keys())
            self.profile_var.set(profile_name)
            
            # Save to file
            self.save_export_profiles()
            messagebox.showinfo("Success", f"Profile '{profile_name}' saved successfully!")
    
    def delete_profile(self):
        """Delete the selected profile."""
        profile_name = self.profile_var.get()
        if profile_name and profile_name in self.export_profiles:
            if profile_name == "Default":
                messagebox.showwarning("Cannot Delete", "Cannot delete the default profile.")
                return
            
            if messagebox.askyesno("Delete Profile", f"Are you sure you want to delete profile '{profile_name}'?"):
                del self.export_profiles[profile_name]
                
                # Update combo box
                self.profile_combo['values'] = list(self.export_profiles.keys())
                self.profile_var.set("Default")
                
                # Save to file
                self.save_export_profiles()
                messagebox.showinfo("Success", f"Profile '{profile_name}' deleted successfully!")
    
    def export_profile(self):
        """Export profile to JSON file."""
        profile_name = self.profile_var.get()
        if profile_name and profile_name in self.export_profiles:
            filename = filedialog.asksaveasfilename(
                title="Export Profile",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.export_profiles[profile_name], f, indent=2)
                    messagebox.showinfo("Success", "Profile exported successfully!")
                except IOError as e:
                    messagebox.showerror("Error", f"Failed to export profile: {e}")
    
    def import_profile(self):
        """Import profile from JSON file."""
        filename = filedialog.askopenfilename(
            title="Import Profile",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                
                # Ask for profile name
                profile_name = tk.simpledialog.askstring("Import Profile", "Enter name for imported profile:")
                if profile_name:
                    self.export_profiles[profile_name] = profile_data
                    
                    # Update combo box
                    self.profile_combo['values'] = list(self.export_profiles.keys())
                    self.profile_var.set(profile_name)
                    
                    # Save to file
                    self.save_export_profiles()
                    messagebox.showinfo("Success", "Profile imported successfully!")
                    
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showerror("Error", f"Failed to import profile: {e}")
    
    def save_export_profiles(self):
        """Save export profiles to file."""
        try:
            profile_file = os.path.join(os.path.dirname(__file__), "../../data/export_profiles.json")
            os.makedirs(os.path.dirname(profile_file), exist_ok=True)
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(self.export_profiles, f, indent=2)
        except IOError:
            pass  # Fail silently if we can't save