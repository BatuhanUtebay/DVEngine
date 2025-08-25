# dvge/ui/dialogs/responsive_dialog.py

"""Responsive dialog utilities for better sizing and layout."""

import customtkinter as ctk
from typing import Tuple, Optional


class ResponsiveDialog:
    """Utility class for creating responsive dialogs."""
    
    @staticmethod
    def calculate_optimal_size(parent, 
                             min_width: int = 400, 
                             min_height: int = 300,
                             max_width: int = 1400, 
                             max_height: int = 1000,
                             screen_ratio: float = 0.8) -> Tuple[int, int]:
        """
        Calculate optimal dialog size based on screen dimensions.
        
        Args:
            parent: Parent window
            min_width: Minimum dialog width
            min_height: Minimum dialog height  
            max_width: Maximum dialog width
            max_height: Maximum dialog height
            screen_ratio: Percentage of screen to use (0.0-1.0)
            
        Returns:
            Tuple of (width, height) for optimal dialog size
        """
        # Get screen dimensions
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        
        # Calculate optimal size as percentage of screen
        optimal_width = int(screen_width * screen_ratio)
        optimal_height = int(screen_height * screen_ratio)
        
        # Apply constraints
        width = max(min_width, min(optimal_width, max_width))
        height = max(min_height, min(optimal_height, max_height))
        
        return width, height
    
    @staticmethod
    def center_dialog(dialog, parent=None):
        """
        Center a dialog on screen or relative to parent.
        
        Args:
            dialog: The dialog window to center
            parent: Optional parent window to center relative to
        """
        dialog.update_idletasks()
        
        if parent:
            # Center relative to parent
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            
            dialog_width = dialog.winfo_width()
            dialog_height = dialog.winfo_height()
            
            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
        else:
            # Center on screen
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            dialog_width = dialog.winfo_width()
            dialog_height = dialog.winfo_height()
            
            x = (screen_width - dialog_width) // 2
            y = (screen_height - dialog_height) // 2
        
        # Ensure dialog stays on screen
        x = max(0, min(x, dialog.winfo_screenwidth() - dialog_width))
        y = max(0, min(y, dialog.winfo_screenheight() - dialog_height))
        
        dialog.geometry(f"+{x}+{y}")
    
    @staticmethod
    def setup_responsive_dialog(dialog, parent, 
                              title: str,
                              min_width: int = 400,
                              min_height: int = 300,
                              max_width: int = 1400,
                              max_height: int = 1000,
                              resizable: bool = True,
                              modal: bool = True):
        """
        Set up a dialog with responsive sizing and proper positioning.
        
        Args:
            dialog: The dialog window
            parent: Parent window
            title: Dialog title
            min_width: Minimum width
            min_height: Minimum height
            max_width: Maximum width  
            max_height: Maximum height
            resizable: Whether dialog should be resizable
            modal: Whether dialog should be modal
        """
        dialog.title(title)
        
        # Calculate optimal size
        width, height = ResponsiveDialog.calculate_optimal_size(
            parent, min_width, min_height, max_width, max_height
        )
        
        dialog.geometry(f"{width}x{height}")
        
        # Set minimum size
        dialog.minsize(min_width, min_height)
        
        # Set maximum size if specified
        if max_width < 9999 or max_height < 9999:
            dialog.maxsize(max_width, max_height)
        
        # Configure resizability
        dialog.resizable(resizable, resizable)
        
        # Set up modal behavior
        if modal:
            dialog.transient(parent)
            dialog.grab_set()
        
        # Center the dialog
        ResponsiveDialog.center_dialog(dialog, parent)
        
        # Ensure dialog appears on top
        dialog.attributes("-topmost", True)
        dialog.after(100, lambda: dialog.attributes("-topmost", False))


class ResponsiveToplevel(ctk.CTkToplevel):
    """Base class for responsive dialog windows."""
    
    def __init__(self, parent, title: str = "Dialog",
                 min_width: int = 400, min_height: int = 300,
                 max_width: int = 1400, max_height: int = 1000,
                 resizable: bool = True, modal: bool = True):
        super().__init__(parent)
        
        self.parent = parent
        
        # Set up responsive dialog
        ResponsiveDialog.setup_responsive_dialog(
            self, parent, title, min_width, min_height, 
            max_width, max_height, resizable, modal
        )