# dvge/ui/main_menu.py
import tkinter as tk
from .search_dialog import SearchDialog

def create_menu(app):
    """Creates the main application menu bar (File, Edit, etc.)."""
    menu_bar = tk.Menu(app)
    
    # File Menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Save Project", command=app.save_project_handler, accelerator="Ctrl+S")
    file_menu.add_command(label="Load Project", command=app.load_project_handler, accelerator="Ctrl+O")
    file_menu.add_separator()
    file_menu.add_command(label="Find Node", command=lambda: SearchDialog(app), accelerator="Ctrl+F")
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=app.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)

    # Edit Menu
    edit_menu = tk.Menu(menu_bar, tearoff=0)
    edit_menu.add_command(label="Undo", command=app.undo, accelerator="Ctrl+Z")
    edit_menu.add_command(label="Redo", command=app.redo, accelerator="Ctrl+Y")
    menu_bar.add_cascade(label="Edit", menu=edit_menu)

    app.config(menu=menu_bar)
