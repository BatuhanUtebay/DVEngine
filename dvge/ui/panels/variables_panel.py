# dvge/ui/panels/variables_panel.py

"""Variables panel for managing numeric variables with advanced operations."""

from tkinter import messagebox
import customtkinter as ctk
from ...constants import *
from ..widgets.custom_widgets import ScrollableListFrame


class VariablesPanel:
    """Handles the Variables tab in the properties panel."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self._setup_layout()
        self._create_widgets()

    def _setup_layout(self):
        """Sets up the tab layout."""
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

    def _create_widgets(self):
        """Creates all widgets for the variables panel."""
        # Main container
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Scrollable variables frame
        self.variables_frame = ScrollableListFrame(
            main_frame, 
            label_text="Numeric Variables", 
            label_font=FONT_PROPERTIES_LABEL
        )
        self.variables_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add variable button
        ctk.CTkButton(
            main_frame, text="+ Add Variable", command=self._add_variable
        ).grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    def update_panel(self):
        """Updates the panel with current data."""
        self.variables_frame.clear_all()
        
        # Ensure variables dict exists
        if not hasattr(self.app, 'variables'):
            self.app.variables = {"gold": 50}
        
        for var_name, value in self.app.variables.items():
            item_frame = self.variables_frame.add_item_frame()
            item_frame.grid_columnconfigure(0, weight=1)
            
            # Variable name entry
            name_entry = ctk.CTkEntry(item_frame, placeholder_text="Variable name")
            name_entry.insert(0, var_name)
            name_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            name_entry.bind(
                "<KeyRelease>", 
                lambda e, old_name=var_name, w=name_entry: self._rename_variable(old_name, w.get())
            )
            
            # Variable value entry
            val_entry = ctk.CTkEntry(item_frame, width=80, placeholder_text="0")
            val_entry.insert(0, str(value))
            val_entry.grid(row=0, column=1, padx=5, pady=5)
            val_entry.bind(
                "<KeyRelease>", 
                lambda e, name=var_name, w=val_entry: self._change_variable_value(name, w.get())
            )
            
            # Delete button
            ctk.CTkButton(
                item_frame, text="✕", width=28, height=28, 
                fg_color="transparent", hover_color=COLOR_ERROR,
                command=lambda v=var_name: self._delete_variable(v)
            ).grid(row=0, column=2, padx=5, pady=5)

    def _add_variable(self):
        """Adds a new numeric variable."""
        self.app._save_state_for_undo("Add Variable")
        
        # Ensure variables dict exists
        if not hasattr(self.app, 'variables'):
            self.app.variables = {}
        
        var_name = f"new_var_{len(self.app.variables)}"
        self.app.variables[var_name] = 0
        self.update_panel()
        
    def _rename_variable(self, old_name, new_name):
        """Renames a variable."""
        if not new_name or new_name == old_name:
            return
        if new_name in self.app.variables:
            return
        
        self.app._save_state_for_undo("Rename Variable")
        self.app.variables[new_name] = self.app.variables.pop(old_name)
        
    def _change_variable_value(self, var_name, value_str):
        """Changes the value of a variable."""
        try:
            value = float(value_str) if '.' in value_str else int(value_str)
        except (ValueError, TypeError):
            return
        
        if var_name in self.app.variables and self.app.variables[var_name] != value:
            self.app._save_state_for_undo("Change Variable Value")
            self.app.variables[var_name] = value
        
    def _delete_variable(self, var_name):
        """Deletes a variable."""
        if messagebox.askyesno("Delete Variable", f"Delete '{var_name}'?"):
            self.app._save_state_for_undo("Delete Variable")
            self.app.variables.pop(var_name, None)
            self.update_panel()