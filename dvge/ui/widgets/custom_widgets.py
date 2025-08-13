# dvge/ui/widgets/custom_widgets.py

"""Custom reusable UI widgets."""

import customtkinter as ctk
from ...constants import *


class ScrollableListFrame(ctk.CTkScrollableFrame):
    """A scrollable frame optimized for list-like content."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
    
    def clear_all(self):
        """Removes all child widgets."""
        for widget in self.winfo_children():
            widget.destroy()
    
    def add_item_frame(self, fg_color=COLOR_PRIMARY_FRAME):
        """Creates and returns a new item frame."""
        item_frame = ctk.CTkFrame(self, fg_color=fg_color)
        item_frame.pack(fill="x", pady=2, padx=2)
        return item_frame


class LabeledEntry(ctk.CTkFrame):
    """A frame containing a label and entry widget."""
    
    def __init__(self, parent, label_text, entry_kwargs=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        entry_kwargs = entry_kwargs or {}
        
        self.grid_columnconfigure(1, weight=1)
        
        self.label = ctk.CTkLabel(
            self, text=label_text, 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_TEXT_MUTED
        )
        self.label.grid(row=0, column=0, padx=(0, 5), sticky="w")
        
        self.entry = ctk.CTkEntry(
            self, font=FONT_PROPERTIES_ENTRY, **entry_kwargs
        )
        self.entry.grid(row=0, column=1, sticky="ew")
    
    def get(self):
        """Returns the entry value."""
        return self.entry.get()
    
    def set(self, value):
        """Sets the entry value."""
        self.entry.delete(0, 'end')
        self.entry.insert(0, str(value))
    
    def bind_change(self, callback):
        """Binds a callback to entry changes."""
        self.entry.bind("<KeyRelease>", lambda e: callback(self.get()))


class LabeledComboBox(ctk.CTkFrame):
    """A frame containing a label and combobox widget."""
    
    def __init__(self, parent, label_text, values, combo_kwargs=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        combo_kwargs = combo_kwargs or {}
        
        self.grid_columnconfigure(1, weight=1)
        
        self.label = ctk.CTkLabel(
            self, text=label_text, 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_TEXT_MUTED
        )
        self.label.grid(row=0, column=0, padx=(0, 5), sticky="w")
        
        self.combobox = ctk.CTkComboBox(
            self, values=values, font=FONT_PROPERTIES_ENTRY, **combo_kwargs
        )
        self.combobox.grid(row=0, column=1, sticky="ew")
    
    def get(self):
        """Returns the combobox value."""
        return self.combobox.get()
    
    def set(self, value):
        """Sets the combobox value."""
        self.combobox.set(value)
    
    def update_values(self, values):
        """Updates the combobox values."""
        self.combobox.configure(values=values)
    
    def bind_change(self, callback):
        """Binds a callback to combobox changes."""
        self.combobox.configure(command=callback)


class ItemListWidget(ctk.CTkFrame):
    """A widget for managing lists of items with add/remove functionality."""
    
    def __init__(self, parent, title, add_callback, remove_callback, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.add_callback = add_callback
        self.remove_callback = remove_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header_frame, text=title, font=FONT_PROPERTIES_LABEL
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkButton(
            header_frame, text=f"+ Add {title.rstrip('s')}", 
            command=self.add_callback, height=28
        ).grid(row=0, column=1, sticky="e")
        
        # Scrollable content area
        self.content_frame = ScrollableListFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
    
    def clear_items(self):
        """Clears all items from the list."""
        self.content_frame.clear_all()
    
    def add_item_widget(self, widget_creator):
        """Adds a new item widget using the provided creator function."""
        item_frame = self.content_frame.add_item_frame()
        return widget_creator(item_frame)


class CollapsibleFrame(ctk.CTkFrame):
    """A frame that can be collapsed/expanded."""
    
    def __init__(self, parent, title, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.is_expanded = True
        
        self.grid_columnconfigure(0, weight=1)
        
        # Header with toggle button
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        self.toggle_button = ctk.CTkButton(
            self.header_frame, text="▼", width=30, height=30,
            command=self.toggle_expansion
        )
        self.toggle_button.grid(row=0, column=0, padx=(0, 5))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, text=title, font=FONT_PROPERTIES_LABEL
        )
        self.title_label.grid(row=0, column=1, sticky="w")
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        self.content_frame.grid_columnconfigure(0, weight=1)
    
    def toggle_expansion(self):
        """Toggles the expanded/collapsed state."""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.content_frame.grid()
            self.toggle_button.configure(text="▼")
        else:
            self.content_frame.grid_remove()
            self.toggle_button.configure(text="▶")
    
    def expand(self):
        """Expands the frame."""
        if not self.is_expanded:
            self.toggle_expansion()
    
    def collapse(self):
        """Collapses the frame."""
        if self.is_expanded:
            self.toggle_expansion()


class StatusIndicator(ctk.CTkFrame):
    """A simple status indicator with color coding."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=20, height=20, **kwargs)
        
        self.indicator = ctk.CTkLabel(self, text="●", font=("Arial", 16))
        self.indicator.pack(expand=True)
        
        self.set_status("unknown")
    
    def set_status(self, status):
        """Sets the status and color."""
        color_map = {
            "success": COLOR_SUCCESS,
            "warning": COLOR_WARNING,
            "error": COLOR_ERROR,
            "active": COLOR_QUEST_ACTIVE,
            "completed": COLOR_QUEST_COMPLETED,
            "failed": COLOR_QUEST_FAILED,
            "unknown": COLOR_TEXT_MUTED
        }
        
        color = color_map.get(status, COLOR_TEXT_MUTED)
        self.indicator.configure(text_color=color)