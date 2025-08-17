# dvge/ui/windows/portrait_manager.py

"""Character Portrait Manager Window."""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from PIL import Image, ImageTk
from ...constants import *
from ...models.character_portrait import CharacterPortrait, PortraitManager


class PortraitManagerWindow(ctk.CTkToplevel):
    """Window for managing character portraits."""
    
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.app = parent_app
        self.portrait_manager = getattr(parent_app, 'portrait_manager', PortraitManager())
        
        # Ensure the app has a portrait manager
        if not hasattr(parent_app, 'portrait_manager'):
            parent_app.portrait_manager = self.portrait_manager
        
        self.current_character = None
        self.preview_images = {}  # Cache for preview images
        
        self.title("Character Portrait Manager")
        self.geometry("1000x700")
        self.transient(parent_app)
        self.resizable(True, True)
        
        # Make window modal
        self.grab_set()
        
        self._setup_ui()
        self._refresh_character_list()
        
        # Center the window
        self.center_window()
    
    def center_window(self):
        """Center the window on the parent."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _setup_ui(self):
        """Set up the main UI layout."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_character_list()
        self._create_portrait_editor()
        self._create_button_bar()
    
    def _create_character_list(self):
        """Create the character list panel."""
        list_frame = ctk.CTkFrame(self, width=250)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        list_frame.grid_propagate(False)
        list_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Characters",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Add",
            width=60,
            command=self._add_character
        )
        add_btn.grid(row=0, column=1, padx=(5, 0))
        
        # Character list
        self.character_listbox = ctk.CTkScrollableFrame(list_frame)
        self.character_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        import_btn = ctk.CTkButton(
            btn_frame,
            text="Import Folder",
            command=self._import_character_folder
        )
        import_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            fg_color="red",
            hover_color="darkred",
            command=self._delete_character
        )
        delete_btn.grid(row=0, column=1, sticky="ew", padx=(2, 0))
    
    def _create_portrait_editor(self):
        """Create the portrait editing panel."""
        editor_frame = ctk.CTkFrame(self)
        editor_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        editor_frame.grid_columnconfigure(0, weight=1)
        editor_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(editor_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header.grid_columnconfigure(1, weight=1)
        
        self.editor_title = ctk.CTkLabel(
            header,
            text="Select a character to edit",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.editor_title.grid(row=0, column=0, sticky="w")
        
        # Main content
        self.editor_content = ctk.CTkScrollableFrame(editor_frame)
        self.editor_content.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        self._create_empty_editor()
    
    def _create_empty_editor(self):
        """Create empty state for editor."""
        # Clear existing content
        for widget in self.editor_content.winfo_children():
            widget.destroy()
        
        empty_label = ctk.CTkLabel(
            self.editor_content,
            text="Select a character from the list to edit portraits",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        empty_label.pack(pady=50)
    
    def _create_character_editor(self, character: CharacterPortrait):
        """Create editor interface for a specific character."""
        # Clear existing content
        for widget in self.editor_content.winfo_children():
            widget.destroy()
        
        # Character info section
        info_frame = ctk.CTkFrame(self.editor_content)
        info_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            info_frame,
            text="Character Information",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(padx=15, pady=(15, 5), anchor="w")
        
        # Name field
        name_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=15, pady=5)
        name_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(name_frame, text="Name:", width=80).grid(row=0, column=0, sticky="w")
        self.name_entry = ctk.CTkEntry(name_frame, placeholder_text="Character name")
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        self.name_entry.insert(0, character.name)
        self.name_entry.bind('<KeyRelease>', lambda e: self._update_character_name())
        
        # Character ID (read-only)
        id_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        id_frame.pack(fill="x", padx=15, pady=(5, 15))
        id_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(id_frame, text="ID:", width=80).grid(row=0, column=0, sticky="w")
        id_label = ctk.CTkLabel(id_frame, text=character.character_id, anchor="w")
        id_label.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        # Portraits section
        portraits_frame = ctk.CTkFrame(self.editor_content)
        portraits_frame.pack(fill="both", expand=True)
        
        # Portraits header
        portraits_header = ctk.CTkFrame(portraits_frame, fg_color="transparent")
        portraits_header.pack(fill="x", padx=15, pady=(15, 10))
        portraits_header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            portraits_header,
            text="Portrait Expressions",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        add_portrait_btn = ctk.CTkButton(
            portraits_header,
            text="+ Add Portrait",
            width=100,
            command=self._add_portrait
        )
        add_portrait_btn.grid(row=0, column=1)
        
        # Portraits grid
        self.portraits_grid = ctk.CTkFrame(portraits_frame)
        self.portraits_grid.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self._refresh_portraits_grid()
    
    def _refresh_portraits_grid(self):
        """Refresh the portraits display grid."""
        if not self.current_character:
            return
        
        # Clear existing grid
        for widget in self.portraits_grid.winfo_children():
            widget.destroy()
        
        portraits = self.current_character.portraits
        if not portraits:
            no_portraits_label = ctk.CTkLabel(
                self.portraits_grid,
                text="No portraits added yet. Click 'Add Portrait' to get started.",
                text_color="gray"
            )
            no_portraits_label.pack(pady=30)
            return
        
        # Create grid of portrait cards
        row = 0
        col = 0
        max_cols = 3
        
        for expression, image_path in portraits.items():
            portrait_card = self._create_portrait_card(expression, image_path)
            portrait_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(max_cols):
            self.portraits_grid.grid_columnconfigure(i, weight=1)
    
    def _create_portrait_card(self, expression: str, image_path: str):
        """Create a card widget for a portrait."""
        card = ctk.CTkFrame(self.portraits_grid)
        card.grid_columnconfigure(0, weight=1)
        
        # Load and display image
        try:
            img = Image.open(image_path)
            img.thumbnail((120, 120), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            img_label = ctk.CTkLabel(card, image=photo, text="")
            img_label.grid(row=0, column=0, padx=10, pady=(10, 5))
            img_label.image = photo  # Keep reference
            
        except Exception as e:
            # Fallback if image can't be loaded
            img_label = ctk.CTkLabel(
                card,
                text="❌\nImage Error",
                width=120,
                height=120,
                fg_color="gray"
            )
            img_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        # Expression name
        name_label = ctk.CTkLabel(
            card,
            text=expression.title(),
            font=ctk.CTkFont(weight="bold")
        )
        name_label.grid(row=1, column=0, padx=10, pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="Edit",
            width=50,
            height=25,
            command=lambda: self._edit_portrait(expression)
        )
        edit_btn.grid(row=0, column=0, padx=(0, 2), sticky="ew")
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            width=50,
            height=25,
            fg_color="red",
            hover_color="darkred",
            command=lambda: self._delete_portrait(expression)
        )
        delete_btn.grid(row=0, column=1, padx=(2, 0), sticky="ew")
        
        return card
    
    def _create_button_bar(self):
        """Create the bottom button bar."""
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
        button_frame.grid_columnconfigure(1, weight=1)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.destroy
        )
        close_btn.grid(row=0, column=2, padx=15, pady=15)
    
    def _refresh_character_list(self):
        """Refresh the character list display."""
        # Clear existing list
        for widget in self.character_listbox.winfo_children():
            widget.destroy()
        
        characters = self.portrait_manager.get_all_characters()
        
        if not characters:
            no_chars_label = ctk.CTkLabel(
                self.character_listbox,
                text="No characters yet.\nClick 'Add' to create one.",
                text_color="gray"
            )
            no_chars_label.pack(pady=20)
            return
        
        for character in characters:
            char_frame = ctk.CTkFrame(self.character_listbox)
            char_frame.pack(fill="x", pady=2)
            char_frame.grid_columnconfigure(0, weight=1)
            
            # Character button
            char_btn = ctk.CTkButton(
                char_frame,
                text=f"{character.name}\n({len(character.portraits)} portraits)",
                height=50,
                anchor="w",
                command=lambda c=character: self._select_character(c)
            )
            char_btn.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    
    def _select_character(self, character: CharacterPortrait):
        """Select a character for editing."""
        self.current_character = character
        self.editor_title.configure(text=f"Editing: {character.name}")
        self._create_character_editor(character)
    
    def _add_character(self):
        """Add a new character."""
        dialog = ctk.CTkInputDialog(
            text="Enter character name:",
            title="Add Character"
        )
        name = dialog.get_input()
        
        if name:
            char_id = name.lower().replace(' ', '_').replace('-', '_')
            # Ensure unique ID
            counter = 1
            original_id = char_id
            while self.portrait_manager.get_character(char_id):
                char_id = f"{original_id}_{counter}"
                counter += 1
            
            character = self.portrait_manager.add_character(char_id, name)
            self._refresh_character_list()
            self._select_character(character)
    
    def _delete_character(self):
        """Delete the selected character."""
        if not self.current_character:
            messagebox.showwarning("No Selection", "Please select a character to delete.")
            return
        
        result = messagebox.askyesno(
            "Delete Character",
            f"Are you sure you want to delete '{self.current_character.name}' and all their portraits?"
        )
        
        if result:
            self.portrait_manager.remove_character(self.current_character.character_id)
            self.current_character = None
            self._refresh_character_list()
            self._create_empty_editor()
            self.editor_title.configure(text="Select a character to edit")
    
    def _import_character_folder(self):
        """Import character portraits from a folder."""
        folder_path = filedialog.askdirectory(
            title="Select folder containing character portraits"
        )
        
        if folder_path:
            try:
                folder_name = os.path.basename(folder_path)
                char_id = folder_name.lower().replace(' ', '_')
                
                character = self.portrait_manager.import_character_batch(folder_path, char_id)
                character.name = folder_name.replace('_', ' ').title()
                
                self._refresh_character_list()
                self._select_character(character)
                
                messagebox.showinfo(
                    "Import Complete",
                    f"Imported {len(character.portraits)} portraits for '{character.name}'"
                )
                
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import portraits: {str(e)}")
    
    def _add_portrait(self):
        """Add a portrait to the current character."""
        if not self.current_character:
            return
        
        file_path = filedialog.askopenfilename(
            title="Select portrait image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # Ask for expression name
            dialog = ctk.CTkInputDialog(
                text="Enter expression name (e.g., happy, sad, angry):",
                title="Portrait Expression"
            )
            expression = dialog.get_input()
            
            if expression:
                try:
                    self.current_character.add_portrait(expression.lower(), file_path)
                    self._refresh_portraits_grid()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add portrait: {str(e)}")
    
    def _edit_portrait(self, expression: str):
        """Edit a portrait expression."""
        if not self.current_character:
            return
        
        # For now, just allow changing the image
        file_path = filedialog.askopenfilename(
            title=f"Select new image for '{expression}' expression",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_character.add_portrait(expression, file_path)
                self._refresh_portraits_grid()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update portrait: {str(e)}")
    
    def _delete_portrait(self, expression: str):
        """Delete a portrait expression."""
        if not self.current_character:
            return
        
        result = messagebox.askyesno(
            "Delete Portrait",
            f"Are you sure you want to delete the '{expression}' portrait?"
        )
        
        if result:
            self.current_character.remove_portrait(expression)
            self._refresh_portraits_grid()
    
    def _update_character_name(self):
        """Update the character name."""
        if self.current_character:
            new_name = self.name_entry.get()
            self.current_character.name = new_name
            self.editor_title.configure(text=f"Editing: {new_name}")
            self._refresh_character_list()