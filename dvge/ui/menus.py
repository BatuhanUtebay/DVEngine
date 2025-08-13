# dvge/ui/menus.py

"""Menu creation and handling for the DVGE application."""

import tkinter as tk


def create_menu(app):
    """Creates the main application menu bar (File, Edit, etc.)."""
    menu_bar = tk.Menu(app)
    
    # File Menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(
        label="New Project", 
        command=app.new_project_handler, 
        accelerator="Ctrl+N"
    )
    file_menu.add_separator()
    file_menu.add_command(
        label="Save Project", 
        command=app.save_project_handler, 
        accelerator="Ctrl+S"
    )
    file_menu.add_command(
        label="Load Project", 
        command=app.load_project_handler, 
        accelerator="Ctrl+O"
    )
    file_menu.add_separator()
    file_menu.add_command(
        label="Export Game", 
        command=app.export_game_handler
    )
    file_menu.add_separator()
    file_menu.add_command(
        label="Find Node", 
        command=lambda: _open_search_dialog(app), 
        accelerator="Ctrl+F"
    )
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=app.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)

    # Edit Menu
    edit_menu = tk.Menu(menu_bar, tearoff=0)
    edit_menu.add_command(
        label="Undo", 
        command=app.undo, 
        accelerator="Ctrl+Z"
    )
    edit_menu.add_command(
        label="Redo", 
        command=app.redo, 
        accelerator="Ctrl+Y"
    )
    edit_menu.add_separator()
    edit_menu.add_command(
        label="Validate Project",
        command=_validate_project_menu
    )
    menu_bar.add_cascade(label="Edit", menu=edit_menu)

    # View Menu
    view_menu = tk.Menu(menu_bar, tearoff=0)
    view_menu.add_command(
        label="Zoom to Fit",
        command=lambda: _zoom_to_fit(app)
    )
    view_menu.add_command(
        label="Center View",
        command=lambda: _center_view(app)
    )
    menu_bar.add_cascade(label="View", menu=view_menu)

    # Help Menu
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(
        label="About",
        command=lambda: _show_about_dialog(app)
    )
    help_menu.add_command(
        label="Keyboard Shortcuts",
        command=lambda: _show_shortcuts_dialog(app)
    )
    menu_bar.add_cascade(label="Help", menu=help_menu)

    app.config(menu=menu_bar)


def _open_search_dialog(app):
    """Opens the search dialog."""
    from .dialogs.search_dialog import SearchDialog
    SearchDialog(app)


def _validate_project_menu(app):
    """Validates the project and shows results."""
    errors, warnings = app.validate_project()
    
    if not errors and not warnings:
        from ..core.utils import show_info
        show_info("Validation", "Project validation passed! No issues found.")
    else:
        message = "Project validation results:\n\n"
        if errors:
            message += "ERRORS:\n" + "\n".join(errors) + "\n\n"
        if warnings:
            message += "WARNINGS:\n" + "\n".join(warnings)
        
        from ..core.utils import show_warning
        show_warning("Validation Results", message)


def _zoom_to_fit(app):
    """Zooms the canvas to fit all nodes."""
    if hasattr(app, 'canvas_manager'):
        app.canvas_manager.zoom_to_fit()


def _center_view(app):
    """Centers the canvas view."""
    if hasattr(app, 'canvas_manager'):
        app.canvas_manager.center_view()


def _show_about_dialog(app):
    """Shows the about dialog."""
    from ..core.utils import show_info
    about_text = (
        "Dialogue Venture Game Engine (DVGE)\n"
        "Version 1.0.0\n\n"
        "A powerful, intuitive, node-based editor for creating\n"
        "branching dialogue and narrative-driven experiences.\n\n"
        "Created by Dice Verce\n"
        "Licensed under MIT License"
    )
    show_info("About DVGE", about_text)


def _show_shortcuts_dialog(app):
    """Shows the keyboard shortcuts dialog."""
    from ..core.utils import show_info
    shortcuts_text = (
        "Keyboard Shortcuts:\n\n"
        "Ctrl+N - New Project\n"
        "Ctrl+S - Save Project\n"
        "Ctrl+O - Load Project\n"
        "Ctrl+Z - Undo\n"
        "Ctrl+Y - Redo\n"
        "Ctrl+F - Find Node\n"
        "Delete - Delete Selected Nodes\n"
        "Right Click - Context Menu\n"
        "Middle Mouse - Pan Canvas\n"
        "Ctrl+Scroll - Zoom Canvas"
    )
    show_info("Keyboard Shortcuts", shortcuts_text)