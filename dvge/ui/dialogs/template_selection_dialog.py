import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
from typing import Optional, Dict, Any
from ...core.template_manager import TemplateManager, ProjectTemplate

class TemplateSelectionDialog:
    def __init__(self, parent):
        self.parent = parent
        self.template_manager = TemplateManager()
        self.selected_template = None
        
        self._create_dialog()
        self._load_templates()
        
    def _create_dialog(self):
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Choose Project Template")
        self.dialog.geometry("900x600")
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
            text="Choose a Project Template",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Content frame
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Left side - Category filter
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        
        category_label = ctk.CTkLabel(left_frame, text="Categories", font=ctk.CTkFont(size=16, weight="bold"))
        category_label.pack(pady=(10, 5))
        
        self.category_listbox = tk.Listbox(left_frame, width=15, height=10)
        self.category_listbox.pack(padx=10, pady=(0, 10))
        self.category_listbox.bind('<<ListboxSelect>>', self._on_category_select)
        
        # Right side - Template selection
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Templates scrollable frame
        self.templates_frame = ctk.CTkScrollableFrame(right_frame, label_text="Templates")
        self.templates_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Selected template info
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_label = ctk.CTkLabel(info_frame, text="Template Information", font=ctk.CTkFont(size=16, weight="bold"))
        info_label.pack(pady=(10, 5))
        
        self.info_text = ctk.CTkTextbox(info_frame, height=100)
        self.info_text.pack(fill="x", padx=10, pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")
        
        self.create_button = ctk.CTkButton(
            button_frame,
            text="Create Project",
            command=self._create_project,
            state="disabled"
        )
        self.create_button.pack(side="right", padx=(10, 0), pady=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._cancel,
            fg_color="gray"
        )
        cancel_button.pack(side="right", pady=10)
        
        blank_button = ctk.CTkButton(
            button_frame,
            text="Create Blank Project",
            command=self._create_blank,
            fg_color="transparent",
            border_width=2
        )
        blank_button.pack(side="left", pady=10)
        
    def _load_templates(self):
        templates = self.template_manager.get_all_templates()
        
        # Get unique categories
        categories = set()
        for template in templates:
            categories.add(template.category)
        
        # Populate category listbox
        categories = sorted(list(categories))
        categories.insert(0, "All")
        
        for category in categories:
            self.category_listbox.insert(tk.END, category)
        
        # Select "All" by default
        self.category_listbox.selection_set(0)
        self._display_templates(templates)
        
    def _on_category_select(self, event):
        selection = self.category_listbox.curselection()
        if not selection:
            return
            
        category = self.category_listbox.get(selection[0])
        
        if category == "All":
            templates = self.template_manager.get_all_templates()
        else:
            templates = self.template_manager.get_templates_by_category(category)
            
        self._display_templates(templates)
        
    def _display_templates(self, templates):
        # Clear existing template widgets
        for widget in self.templates_frame.winfo_children():
            widget.destroy()
            
        self.template_widgets = []
        
        for template in templates:
            template_frame = self._create_template_widget(template)
            template_frame.pack(fill="x", padx=5, pady=5)
            
    def _create_template_widget(self, template: ProjectTemplate):
        # Main template frame
        frame = ctk.CTkFrame(self.templates_frame)
        
        # Template info frame
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        # Title and difficulty
        title_frame = ctk.CTkFrame(info_frame)
        title_frame.pack(fill="x", pady=(0, 5))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=template.name,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(side="left")
        
        # Difficulty badge
        difficulty_color = {
            "Beginner": "green",
            "Intermediate": "orange",
            "Advanced": "red"
        }.get(template.difficulty, "gray")
        
        difficulty_label = ctk.CTkLabel(
            title_frame,
            text=template.difficulty,
            text_color=difficulty_color,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        difficulty_label.pack(side="right")
        
        # Description
        desc_label = ctk.CTkLabel(
            info_frame,
            text=template.description,
            wraplength=400,
            justify="left"
        )
        desc_label.pack(anchor="w", pady=(0, 5))
        
        # Tags
        if template.tags:
            tags_frame = ctk.CTkFrame(info_frame)
            tags_frame.pack(fill="x", pady=(0, 5))
            
            tags_label = ctk.CTkLabel(tags_frame, text="Tags:", font=ctk.CTkFont(weight="bold"))
            tags_label.pack(side="left")
            
            for tag in template.tags[:5]:  # Limit to 5 tags
                tag_label = ctk.CTkLabel(
                    tags_frame,
                    text=f"#{tag}",
                    text_color="gray",
                    font=ctk.CTkFont(size=10)
                )
                tag_label.pack(side="left", padx=(5, 0))
        
        # Select button
        select_button = ctk.CTkButton(
            info_frame,
            text="Select Template",
            command=lambda t=template: self._select_template(t),
            height=30
        )
        select_button.pack(pady=(5, 0))
        
        return frame
        
    def _select_template(self, template: ProjectTemplate):
        self.selected_template = template
        
        # Update info display
        info_text = f"Template: {template.name}\n"
        info_text += f"Category: {template.category}\n"
        info_text += f"Difficulty: {template.difficulty}\n"
        info_text += f"Author: {template.author}\n\n"
        info_text += f"Description:\n{template.description}\n\n"
        
        if template.help_text:
            info_text += f"Help:\n{template.help_text}\n\n"
            
        if template.tutorial_steps:
            info_text += "Tutorial Steps:\n"
            for i, step in enumerate(template.tutorial_steps, 1):
                info_text += f"{i}. {step}\n"
        
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", info_text)
        
        # Enable create button
        self.create_button.configure(state="normal")
        
    def _create_project(self):
        if not self.selected_template:
            messagebox.showerror("Error", "Please select a template first.")
            return
            
        self.result = {
            "action": "create_from_template",
            "template": self.selected_template
        }
        self.dialog.destroy()
        
    def _create_blank(self):
        self.result = {
            "action": "create_blank"
        }
        self.dialog.destroy()
        
    def _cancel(self):
        self.result = None
        self.dialog.destroy()
        
    def show(self) -> Optional[Dict[str, Any]]:
        self.result = None
        self.dialog.wait_window()
        return self.result