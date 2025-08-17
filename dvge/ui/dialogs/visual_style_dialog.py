"""Visual style configuration dialog for customizing node appearance."""

import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser, messagebox
import json
from typing import Dict, Any, Optional
from ..canvas.node_themes import theme_manager, NodeTheme


class VisualStyleDialog:
    """Dialog for configuring visual styles and themes."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.current_theme = None
        self.preview_node_id = None
        
        self._create_dialog()
        self._load_themes()
        
    def _create_dialog(self):
        """Create the visual style configuration dialog."""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Visual Style Configuration")
        self.dialog.geometry("1000x700")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+{}+{}".format(
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        # Main container
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Visual Style Configuration",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Content frame (horizontal layout)
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Left side - Theme list
        self._create_theme_list(content_frame)
        
        # Middle - Theme editor
        self._create_theme_editor(content_frame)
        
        # Right side - Preview
        self._create_preview_panel(content_frame)
        
        # Bottom buttons
        self._create_buttons(main_frame)
    
    def _create_theme_list(self, parent):
        """Create the theme selection list."""
        left_frame = ctk.CTkFrame(parent)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        
        # Theme list header
        list_label = ctk.CTkLabel(left_frame, text="Themes", font=ctk.CTkFont(size=16, weight="bold"))
        list_label.pack(pady=(10, 5))
        
        # Theme listbox
        self.theme_listbox = tk.Listbox(left_frame, width=20, height=15)
        self.theme_listbox.pack(padx=10, pady=(0, 10))
        self.theme_listbox.bind('<<ListboxSelect>>', self._on_theme_select)
        
        # Theme management buttons
        button_frame = ctk.CTkFrame(left_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        new_button = ctk.CTkButton(button_frame, text="New", command=self._new_theme, width=80)
        new_button.pack(side="left", padx=(0, 5))
        
        copy_button = ctk.CTkButton(button_frame, text="Copy", command=self._copy_theme, width=80)
        copy_button.pack(side="left", padx=(0, 5))
        
        delete_button = ctk.CTkButton(button_frame, text="Delete", command=self._delete_theme, 
                                    fg_color="red", width=80)
        delete_button.pack(side="left")
    
    def _create_theme_editor(self, parent):
        """Create the theme editing panel."""
        middle_frame = ctk.CTkFrame(parent)
        middle_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Editor header
        editor_label = ctk.CTkLabel(middle_frame, text="Theme Editor", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        editor_label.pack(pady=(10, 5))
        
        # Scrollable editor content
        self.editor_scroll = ctk.CTkScrollableFrame(middle_frame)
        self.editor_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Theme name
        name_frame = ctk.CTkFrame(self.editor_scroll)
        name_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(name_frame, text="Theme Name:").pack(side="left", padx=(10, 5))
        self.theme_name_entry = ctk.CTkEntry(name_frame, width=200)
        self.theme_name_entry.pack(side="right", padx=(5, 10))
        
        # Colors section
        self._create_color_section(self.editor_scroll)
        
        # Visual effects section
        self._create_effects_section(self.editor_scroll)
        
        # Icon section
        self._create_icon_section(self.editor_scroll)
        
        # Border section
        self._create_border_section(self.editor_scroll)
    
    def _create_color_section(self, parent):
        """Create color configuration section."""
        color_frame = ctk.CTkFrame(parent)
        color_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(color_frame, text="Colors", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5, 5))
        
        # Color entries
        self.color_entries = {}
        colors = [
            ("Header Color", "header_color"),
            ("Body Color", "body_color"),
            ("Text Color", "text_color"),
            ("Subtitle Color", "subtitle_color"),
            ("Border Color", "border_color"),
            ("Shadow Color", "shadow_color")
        ]
        
        for i, (label, key) in enumerate(colors):
            row = i // 2
            col = i % 2
            
            color_row = ctk.CTkFrame(color_frame)
            color_row.pack(fill="x", padx=10, pady=2)
            
            ctk.CTkLabel(color_row, text=label, width=120).pack(side="left")
            
            entry = ctk.CTkEntry(color_row, width=100)
            entry.pack(side="left", padx=5)
            self.color_entries[key] = entry
            
            button = ctk.CTkButton(color_row, text="Pick", width=60,
                                 command=lambda k=key: self._pick_color(k))
            button.pack(side="left", padx=5)
    
    def _create_effects_section(self, parent):
        """Create visual effects section."""
        effects_frame = ctk.CTkFrame(parent)
        effects_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(effects_frame, text="Visual Effects", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5, 5))
        
        # Checkboxes for effects
        self.effect_vars = {}
        effects = [
            ("Shadow Enabled", "shadow_enabled"),
            ("Hover Glow", "hover_glow"),
            ("Pulse Effect", "pulse_enabled")
        ]
        
        for label, key in effects:
            var = tk.BooleanVar()
            checkbox = ctk.CTkCheckBox(effects_frame, text=label, variable=var)
            checkbox.pack(anchor="w", padx=10, pady=2)
            self.effect_vars[key] = var
        
        # Numeric settings
        numeric_frame = ctk.CTkFrame(effects_frame)
        numeric_frame.pack(fill="x", padx=10, pady=5)
        
        self.numeric_entries = {}
        numerics = [
            ("Corner Radius", "corner_radius"),
            ("Border Width", "border_width"),
            ("Hover Scale", "hover_scale")
        ]
        
        for label, key in numerics:
            row_frame = ctk.CTkFrame(numeric_frame)
            row_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row_frame, text=label, width=120).pack(side="left")
            entry = ctk.CTkEntry(row_frame, width=100)
            entry.pack(side="left", padx=5)
            self.numeric_entries[key] = entry
    
    def _create_icon_section(self, parent):
        """Create icon configuration section."""
        icon_frame = ctk.CTkFrame(parent)
        icon_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(icon_frame, text="Icon", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5, 5))
        
        icon_row = ctk.CTkFrame(icon_frame)
        icon_row.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(icon_row, text="Icon:", width=120).pack(side="left")
        self.icon_entry = ctk.CTkEntry(icon_row, width=100)
        self.icon_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(icon_row, text="Color:", width=60).pack(side="left", padx=(10, 0))
        self.icon_color_entry = ctk.CTkEntry(icon_row, width=100)
        self.icon_color_entry.pack(side="left", padx=5)
        
        icon_color_button = ctk.CTkButton(icon_row, text="Pick", width=60,
                                        command=lambda: self._pick_color("icon_color"))
        icon_color_button.pack(side="left", padx=5)
        
        # Icon size
        size_row = ctk.CTkFrame(icon_frame)
        size_row.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(size_row, text="Size:", width=120).pack(side="left")
        self.icon_size_entry = ctk.CTkEntry(size_row, width=100)
        self.icon_size_entry.pack(side="left", padx=5)
        
        # Common icons
        ctk.CTkLabel(icon_frame, text="Common Icons:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        
        icons_grid = ctk.CTkFrame(icon_frame)
        icons_grid.pack(fill="x", padx=10, pady=5)
        
        common_icons = ["💬", "⚔️", "🛒", "🎲", "❓", "⏰", "🎒", "📖", "⭐", "🔒"]
        
        for i, icon in enumerate(common_icons):
            row = i // 5
            col = i % 5
            
            if col == 0:
                icon_row = ctk.CTkFrame(icons_grid)
                icon_row.pack(fill="x", pady=2)
            
            icon_button = ctk.CTkButton(icon_row, text=icon, width=40,
                                      command=lambda ic=icon: self._set_icon(ic))
            icon_button.pack(side="left", padx=2)
    
    def _create_border_section(self, parent):
        """Create border configuration section."""
        border_frame = ctk.CTkFrame(parent)
        border_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(border_frame, text="Border", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5, 5))
        
        # Border style
        style_row = ctk.CTkFrame(border_frame)
        style_row.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(style_row, text="Style:", width=120).pack(side="left")
        self.border_style_var = ctk.StringVar(value="solid")
        style_menu = ctk.CTkOptionMenu(style_row, variable=self.border_style_var,
                                     values=["solid", "dashed", "dotted"])
        style_menu.pack(side="left", padx=5)
    
    def _create_preview_panel(self, parent):
        """Create the preview panel."""
        right_frame = ctk.CTkFrame(parent)
        right_frame.pack(side="right", fill="y")
        
        # Preview header
        preview_label = ctk.CTkLabel(right_frame, text="Preview", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        preview_label.pack(pady=(10, 5))
        
        # Preview canvas
        self.preview_canvas = tk.Canvas(right_frame, width=300, height=400, bg="#1E1E1E")
        self.preview_canvas.pack(padx=10, pady=(0, 10))
        
        # Preview controls
        control_frame = ctk.CTkFrame(right_frame)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(control_frame, text="Preview Node Type:").pack(pady=(5, 2))
        
        self.preview_type_var = ctk.StringVar(value="DialogueNode")
        type_menu = ctk.CTkOptionMenu(control_frame, variable=self.preview_type_var,
                                    values=["DialogueNode", "CombatNode", "ShopNode", 
                                           "DiceRollNode", "TimerNode"],
                                    command=self._update_preview)
        type_menu.pack(pady=2)
        
        update_button = ctk.CTkButton(control_frame, text="Update Preview",
                                    command=self._update_preview)
        update_button.pack(pady=5)
    
    def _create_buttons(self, parent):
        """Create dialog buttons."""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x")
        
        # Left side buttons
        left_buttons = ctk.CTkFrame(button_frame)
        left_buttons.pack(side="left")
        
        save_preset_button = ctk.CTkButton(left_buttons, text="Save as Preset",
                                         command=self._save_preset)
        save_preset_button.pack(side="left", padx=(0, 10))
        
        load_preset_button = ctk.CTkButton(left_buttons, text="Load Preset",
                                         command=self._load_preset)
        load_preset_button.pack(side="left")
        
        # Right side buttons
        right_buttons = ctk.CTkFrame(button_frame)
        right_buttons.pack(side="right")
        
        cancel_button = ctk.CTkButton(right_buttons, text="Cancel",
                                    command=self._cancel, fg_color="gray")
        cancel_button.pack(side="right", padx=(10, 0))
        
        apply_button = ctk.CTkButton(right_buttons, text="Apply All",
                                   command=self._apply_all)
        apply_button.pack(side="right", padx=(10, 0))
        
        ok_button = ctk.CTkButton(right_buttons, text="OK",
                                command=self._ok)
        ok_button.pack(side="right", padx=(10, 0))
    
    def _load_themes(self):
        """Load available themes into the list."""
        self.theme_listbox.delete(0, tk.END)
        
        themes = theme_manager.get_available_themes()
        for theme_name in sorted(themes):
            self.theme_listbox.insert(tk.END, theme_name)
        
        # Select first theme
        if themes:
            self.theme_listbox.selection_set(0)
            self._on_theme_select()
    
    def _on_theme_select(self, event=None):
        """Handle theme selection."""
        selection = self.theme_listbox.curselection()
        if not selection:
            return
        
        theme_name = self.theme_listbox.get(selection[0])
        self.current_theme = theme_manager.themes[theme_name]
        self._load_theme_into_editor(self.current_theme)
        self._update_preview()
    
    def _load_theme_into_editor(self, theme: NodeTheme):
        """Load theme properties into the editor."""
        # Load colors
        self.color_entries["header_color"].delete(0, tk.END)
        self.color_entries["header_color"].insert(0, theme.header_color)
        
        self.color_entries["body_color"].delete(0, tk.END)
        self.color_entries["body_color"].insert(0, theme.body_color)
        
        self.color_entries["text_color"].delete(0, tk.END)
        self.color_entries["text_color"].insert(0, theme.text_color)
        
        self.color_entries["subtitle_color"].delete(0, tk.END)
        self.color_entries["subtitle_color"].insert(0, theme.subtitle_color)
        
        self.color_entries["border_color"].delete(0, tk.END)
        self.color_entries["border_color"].insert(0, theme.border_color)
        
        self.color_entries["shadow_color"].delete(0, tk.END)
        self.color_entries["shadow_color"].insert(0, theme.shadow_color)
        
        # Load effects
        self.effect_vars["shadow_enabled"].set(theme.shadow_enabled)
        self.effect_vars["hover_glow"].set(theme.hover_glow)
        self.effect_vars["pulse_enabled"].set(theme.pulse_enabled)
        
        # Load numeric values
        self.numeric_entries["corner_radius"].delete(0, tk.END)
        self.numeric_entries["corner_radius"].insert(0, str(theme.corner_radius))
        
        self.numeric_entries["border_width"].delete(0, tk.END)
        self.numeric_entries["border_width"].insert(0, str(theme.border_width))
        
        self.numeric_entries["hover_scale"].delete(0, tk.END)
        self.numeric_entries["hover_scale"].insert(0, str(theme.hover_scale))
        
        # Load icon
        self.icon_entry.delete(0, tk.END)
        self.icon_entry.insert(0, theme.icon)
        
        self.icon_color_entry.delete(0, tk.END)
        self.icon_color_entry.insert(0, theme.icon_color)
        
        self.icon_size_entry.delete(0, tk.END)
        self.icon_size_entry.insert(0, str(theme.icon_size))
    
    def _pick_color(self, color_key: str):
        """Open color picker for a color entry."""
        if color_key == "icon_color":
            entry = self.icon_color_entry
        else:
            entry = self.color_entries[color_key]
        
        current_color = entry.get()
        color = colorchooser.askcolor(title=f"Choose {color_key}", color=current_color)
        
        if color[1]:  # If user didn't cancel
            entry.delete(0, tk.END)
            entry.insert(0, color[1])
            self._update_preview()
    
    def _set_icon(self, icon: str):
        """Set the icon from common icons."""
        self.icon_entry.delete(0, tk.END)
        self.icon_entry.insert(0, icon)
        self._update_preview()
    
    def _update_preview(self, *args):
        """Update the preview with current settings."""
        # Create a temporary theme from current settings
        temp_theme = self._create_theme_from_editor()
        
        # Clear canvas
        self.preview_canvas.delete("all")
        
        # Draw preview node
        self._draw_preview_node(temp_theme)
    
    def _draw_preview_node(self, theme: NodeTheme):
        """Draw a preview node with the given theme."""
        x, y = 50, 50
        width, height = 200, 150
        
        # Shadow
        if theme.shadow_enabled:
            shadow_x = x + theme.shadow_offset[0]
            shadow_y = y + theme.shadow_offset[1]
            self.preview_canvas.create_rectangle(
                shadow_x, shadow_y, shadow_x + width, shadow_y + height,
                fill=theme.shadow_color, outline=""
            )
        
        # Body
        self.preview_canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=theme.body_color, outline=""
        )
        
        # Header
        header_height = 40
        self.preview_canvas.create_rectangle(
            x, y, x + width, y + header_height,
            fill=theme.header_color, outline=""
        )
        
        # Border
        if theme.border_width > 0:
            self.preview_canvas.create_rectangle(
                x, y, x + width, y + height,
                fill="", outline=theme.border_color, width=theme.border_width
            )
        
        # Icon
        if theme.icon:
            self.preview_canvas.create_text(
                x + 10, y + 20, text=theme.icon, fill=theme.icon_color,
                font=("Arial", theme.icon_size), anchor="w"
            )
        
        # Text
        text_x = x + (30 if theme.icon else 10)
        self.preview_canvas.create_text(
            text_x, y + 20, text="Preview Node", fill=theme.text_color,
            font=("Arial", 12, "bold"), anchor="w"
        )
        
        self.preview_canvas.create_text(
            x + 10, y + 60, text="This is a preview of how\nyour theme will look.",
            fill=theme.subtitle_color, font=("Arial", 10), anchor="nw"
        )
    
    def _create_theme_from_editor(self) -> NodeTheme:
        """Create a NodeTheme from current editor values."""
        return NodeTheme(
            header_color=self.color_entries["header_color"].get() or "#455A64",
            body_color=self.color_entries["body_color"].get() or "#3A3A3A",
            text_color=self.color_entries["text_color"].get() or "#DCE4EE",
            subtitle_color=self.color_entries["subtitle_color"].get() or "#8A95A0",
            border_color=self.color_entries["border_color"].get() or "",
            shadow_color=self.color_entries["shadow_color"].get() or "#111111",
            shadow_enabled=self.effect_vars["shadow_enabled"].get(),
            hover_glow=self.effect_vars["hover_glow"].get(),
            pulse_enabled=self.effect_vars["pulse_enabled"].get(),
            corner_radius=int(self.numeric_entries["corner_radius"].get() or "8"),
            border_width=int(self.numeric_entries["border_width"].get() or "0"),
            hover_scale=float(self.numeric_entries["hover_scale"].get() or "1.0"),
            icon=self.icon_entry.get(),
            icon_color=self.icon_color_entry.get() or "#DCE4EE",
            icon_size=int(self.icon_size_entry.get() or "16")
        )
    
    def _new_theme(self):
        """Create a new theme."""
        name = tk.simpledialog.askstring("New Theme", "Enter theme name:")
        if name and name not in theme_manager.themes:
            theme_manager.register_theme(name, NodeTheme())
            self._load_themes()
    
    def _copy_theme(self):
        """Copy the current theme."""
        if not self.current_theme:
            return
        
        name = tk.simpledialog.askstring("Copy Theme", "Enter new theme name:")
        if name and name not in theme_manager.themes:
            new_theme = self._create_theme_from_editor()
            theme_manager.register_theme(name, new_theme)
            self._load_themes()
    
    def _delete_theme(self):
        """Delete the selected theme."""
        selection = self.theme_listbox.curselection()
        if not selection:
            return
        
        theme_name = self.theme_listbox.get(selection[0])
        if messagebox.askyesno("Delete Theme", f"Delete theme '{theme_name}'?"):
            if theme_name in theme_manager.themes:
                del theme_manager.themes[theme_name]
                self._load_themes()
    
    def _save_preset(self):
        """Save current themes as a preset."""
        # Implementation for saving theme presets
        pass
    
    def _load_preset(self):
        """Load a theme preset."""
        # Implementation for loading theme presets
        pass
    
    def _apply_all(self):
        """Apply changes to all nodes."""
        # Update the current theme
        if self.current_theme:
            updated_theme = self._create_theme_from_editor()
            # Apply to theme manager
            selection = self.theme_listbox.curselection()
            if selection:
                theme_name = self.theme_listbox.get(selection[0])
                theme_manager.register_theme(theme_name, updated_theme)
        
        self.result = "apply"
        
    def _ok(self):
        """Accept changes and close."""
        self._apply_all()
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancel changes and close."""
        self.result = None
        self.dialog.destroy()
    
    def show(self) -> Optional[str]:
        """Show the dialog and return result."""
        self.dialog.wait_window()
        return self.result