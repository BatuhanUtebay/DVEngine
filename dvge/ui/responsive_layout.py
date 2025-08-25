# dvge/ui/responsive_layout.py

"""Responsive layout utilities for the DVGEngine editor."""

import tkinter as tk
import customtkinter as ctk
from typing import Tuple, Optional, Dict, Any


class ResponsiveLayout:
    """Utilities for creating responsive layouts in CustomTkinter."""
    
    @staticmethod
    def setup_responsive_grid(widget, columns: Dict[int, dict], rows: Dict[int, dict] = None):
        """
        Set up responsive grid configuration for a widget.
        
        Args:
            widget: The widget to configure
            columns: Dict of {column_index: {'weight': int, 'minsize': int, 'pad': int}}
            rows: Dict of {row_index: {'weight': int, 'minsize': int, 'pad': int}}
        """
        for col_index, config in columns.items():
            widget.grid_columnconfigure(
                col_index, 
                weight=config.get('weight', 1),
                minsize=config.get('minsize', 0),
                pad=config.get('pad', 0)
            )
        
        if rows:
            for row_index, config in rows.items():
                widget.grid_rowconfigure(
                    row_index, 
                    weight=config.get('weight', 1),
                    minsize=config.get('minsize', 0),
                    pad=config.get('pad', 0)
                )
    
    @staticmethod
    def create_scrollable_frame(parent, **kwargs) -> Tuple[ctk.CTkScrollableFrame, ctk.CTkFrame]:
        """
        Create a scrollable frame for content that might overflow.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments for CTkScrollableFrame
            
        Returns:
            Tuple of (scrollable_frame, content_frame)
        """
        # Default configuration for scrollable frame
        scroll_config = {
            'fg_color': 'transparent',
            'scrollbar_fg_color': 'transparent',
            'scrollbar_button_color': '#3B3B3B',
            'scrollbar_button_hover_color': '#4B4B4B'
        }
        scroll_config.update(kwargs)
        
        scrollable_frame = ctk.CTkScrollableFrame(parent, **scroll_config)
        
        # Content frame inside the scrollable frame
        content_frame = ctk.CTkFrame(scrollable_frame, fg_color='transparent')
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        return scrollable_frame, content_frame
    
    @staticmethod
    def adapt_font_size(base_size: int, scale_factor: float = 1.0, min_size: int = 8, max_size: int = 24) -> int:
        """
        Adapt font size based on scale factor with reasonable limits.
        
        Args:
            base_size: Base font size
            scale_factor: Scale factor (1.0 = no change)
            min_size: Minimum font size
            max_size: Maximum font size
            
        Returns:
            Adapted font size
        """
        new_size = int(base_size * scale_factor)
        return max(min_size, min(new_size, max_size))
    
    @staticmethod
    def setup_resizable_paned_window(parent, orientation='horizontal', 
                                   sash_relief='flat', sashwidth=4) -> tk.PanedWindow:
        """
        Create a resizable paned window for splitting layouts.
        
        Args:
            parent: Parent widget
            orientation: 'horizontal' or 'vertical'
            sash_relief: Relief style for the sash
            sashwidth: Width of the sash
            
        Returns:
            PanedWindow widget
        """
        paned_window = tk.PanedWindow(
            parent,
            orient=orientation,
            sashrelief=sash_relief,
            sashwidth=sashwidth,
            bg='#2B2B2B',
            bd=0,
            highlightthickness=0
        )
        
        return paned_window
    
    @staticmethod
    def make_widget_responsive_text(widget, text: str, max_width: int = None):
        """
        Make a widget's text responsive by truncating with ellipsis if needed.
        
        Args:
            widget: The widget to update
            text: Original text
            max_width: Maximum width in characters (None = no limit)
        """
        if max_width and len(text) > max_width:
            truncated = text[:max_width-3] + "..."
            widget.configure(text=truncated)
            
            # Add tooltip for full text if truncated
            try:
                # Try to create tooltip (if tooltip system is available)
                ResponsiveLayout._create_tooltip(widget, text)
            except:
                pass  # Tooltip system not available
        else:
            widget.configure(text=text)
    
    @staticmethod
    def _create_tooltip(widget, text):
        """Create a simple tooltip for a widget."""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip, 
                text=text, 
                background="#3B3B3B", 
                foreground="white",
                font=("Arial", 10),
                padx=5,
                pady=2,
                relief="solid",
                borderwidth=1
            )
            label.pack()
            widget._tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, '_tooltip'):
                widget._tooltip.destroy()
                del widget._tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    @staticmethod
    def setup_auto_sizing_frame(parent, content_widgets: list, min_height: int = 100, 
                               max_height: int = None) -> ctk.CTkFrame:
        """
        Create a frame that automatically sizes based on its content.
        
        Args:
            parent: Parent widget
            content_widgets: List of widgets that will be added to the frame
            min_height: Minimum height of the frame
            max_height: Maximum height of the frame (None = no limit)
            
        Returns:
            Auto-sizing frame
        """
        frame = ctk.CTkFrame(parent)
        
        def update_frame_size():
            # Calculate required height based on content
            total_height = sum(w.winfo_reqheight() for w in content_widgets if w.winfo_exists())
            
            # Apply constraints
            height = max(min_height, total_height)
            if max_height:
                height = min(height, max_height)
            
            frame.configure(height=height)
        
        # Bind to configure events to auto-update size
        for widget in content_widgets:
            widget.bind('<Configure>', lambda e: parent.after_idle(update_frame_size))
        
        return frame


class ResponsiveWindow:
    """Utilities for making windows more responsive."""
    
    @staticmethod
    def setup_window_resize_handling(window, min_width: int = 800, min_height: int = 600):
        """
        Set up proper window resize handling with constraints.
        
        Args:
            window: The window to configure
            min_width: Minimum window width
            min_height: Minimum window height
        """
        window.minsize(min_width, min_height)
        
        # Store original configure method
        original_configure = window.configure
        
        def smart_configure(*args, **kwargs):
            """Enhanced configure method with responsive handling."""
            result = original_configure(*args, **kwargs)
            
            # Trigger responsive updates after configuration
            window.after_idle(ResponsiveWindow._update_responsive_elements, window)
            
            return result
        
        # Replace configure method
        window.configure = smart_configure
    
    @staticmethod
    def _update_responsive_elements(window):
        """Update responsive elements after window resize."""
        try:
            # Update any responsive elements
            if hasattr(window, 'properties_panel'):
                # Ensure properties panel maintains minimum width
                current_width = window.properties_panel.winfo_width()
                if current_width < 350:  # Minimum comfortable width
                    window.properties_panel.configure(width=350)
                    
        except:
            pass  # Ignore errors during responsive updates