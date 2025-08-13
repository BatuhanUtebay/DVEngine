# dvge/ui/main_window.py

"""Main window setup and layout for the DVGE application."""

import tkinter as tk
import customtkinter as ctk
from ..constants import *


def setup_main_window(app):
    """Sets up the main window layout and components."""
    # --- UI Structure ---
    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(2, weight=1)  # Changed from 1 to 2 for preview toolbar
    
    _create_menu(app)
    _create_header(app)
    _create_main_content(app)


def _create_menu(app):
    """Creates the main application menu bar."""
    from .menus import create_menu
    create_menu(app)


def _create_header(app):
    """Creates the header with title, preview toolbar, and export button."""
    header_frame = ctk.CTkFrame(app, fg_color="transparent", height=50)
    header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10,0))
    header_frame.grid_columnconfigure(0, weight=1)
    
    # Title and export on left/right
    title_export_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    title_export_frame.grid(row=0, column=0, sticky="ew")
    title_export_frame.grid_columnconfigure(0, weight=1)
    
    ctk.CTkLabel(
        title_export_frame, 
        text="Dialogue Venture", 
        font=FONT_TITLE
    ).grid(row=0, column=0, sticky="w")
    
    ctk.CTkButton(
        title_export_frame, 
        text="Export Game", 
        command=app.export_game_handler, 
        fg_color=COLOR_SUCCESS, 
        hover_color="#27AE60"
    ).grid(row=0, column=1, sticky="e")
    
    # Preview toolbar
    from .widgets.preview_controls import PreviewToolbar
    app.preview_toolbar = PreviewToolbar(header_frame, app)
    app.preview_toolbar.grid(row=1, column=0, sticky="ew", pady=(10,0))


def _create_main_content(app):
    """Creates the main content area with canvas and properties panel."""
    # Main content area
    app.main_frame = ctk.CTkFrame(app, fg_color="transparent")
    app.main_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)  # Changed from row=1 to row=2
    app.main_frame.grid_columnconfigure(0, weight=3)
    app.main_frame.grid_columnconfigure(1, weight=1)
    app.main_frame.grid_rowconfigure(0, weight=1)

    _create_canvas(app)
    _create_properties_panel(app)


def _create_canvas(app):
    """Creates the main canvas for node editing."""
    # Canvas
    app.canvas = tk.Canvas(
        app.main_frame, 
        bg=COLOR_CANVAS_BACKGROUND, 
        highlightthickness=0, 
        borderwidth=0
    )
    app.canvas.grid(row=0, column=0, sticky="nsew", padx=(10,5))
    
    # Canvas manager
    from .canvas.canvas_manager import CanvasManager
    app.canvas_manager = CanvasManager(app)

    # Initial draw
    app.canvas_manager.draw_grid()
    app.canvas_manager.draw_placeholder_if_empty()


def _create_properties_panel(app):
    """Creates the properties panel."""
    from .panels.properties_panel import PropertiesPanel
    app.properties_panel = PropertiesPanel(app.main_frame, app)
    app.properties_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10))
    
    # Initial update
    app.properties_panel.update_all_panels()