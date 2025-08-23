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
    file_menu.add_command(
        label="Export Enhanced Mobile Game", 
        command=lambda: _export_enhanced_mobile(app)
    )
    
    # Add custom exporters from plugins
    if hasattr(app, 'custom_exporters'):
        for name, exporter in app.custom_exporters.items():
            file_menu.add_command(
                label=f"Export as {name}",
                command=lambda e=exporter: app._export_with_plugin(e)
            )
    file_menu.add_command(
        label="HTML Export Styling...", 
        command=lambda: _open_style_customizer(app)
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
        command=lambda: _validate_project_menu(app)
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
    view_menu.add_separator()
    view_menu.add_command(
        label="Live Preview",
        command=lambda: _open_live_preview(app),
        accelerator="Ctrl+P"
    )
    view_menu.add_command(
        label="Quick Test Selected Node",
        command=lambda: _quick_test_node(app)
    )
    view_menu.add_separator()
    view_menu.add_command(
        label="Visual Style Configuration",
        command=lambda: _open_visual_style_dialog(app)
    )
    view_menu.add_command(
        label="Toggle Enhanced Rendering",
        command=lambda: _toggle_enhanced_rendering(app)
    )
    view_menu.add_command(
        label="Toggle Node Groups",
        command=lambda: _toggle_node_groups(app)
    )
    menu_bar.add_cascade(label="View", menu=view_menu)

    # Tools Menu
    tools_menu = tk.Menu(menu_bar, tearoff=0)
    tools_menu.add_command(
        label="Batch Operations...",
        command=lambda: _open_batch_operations(app)
    )
    tools_menu.add_separator()
    tools_menu.add_command(
        label="Plugin Manager...",
        command=lambda: _open_plugin_manager(app)
    )
    tools_menu.add_separator()
    tools_menu.add_command(
        label="Character Portraits...",
        command=lambda: _open_portrait_manager(app)
    )
    tools_menu.add_command(
        label="Dynamic Music Manager...",
        command=lambda: _open_music_manager(app)
    )
    menu_bar.add_cascade(label="Tools", menu=tools_menu)

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


def _open_live_preview(app):
    """Opens live preview from menu."""
    if hasattr(app, 'preview_toolbar'):
        app.preview_toolbar.preview_controls._open_preview()


def _quick_test_node(app):
    """Quick tests selected node from menu."""
    if hasattr(app, 'preview_toolbar'):
        app.preview_toolbar.preview_controls._quick_test()


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
        "Ctrl+P - Live Preview\n"
        "Delete - Delete Selected Nodes\n"
        "Right Click - Context Menu\n"
        "Middle Mouse - Pan Canvas\n"
        "Ctrl+Scroll - Zoom Canvas"
    )
    show_info("Keyboard Shortcuts", shortcuts_text)


def _open_visual_style_dialog(app):
    """Opens the visual style configuration dialog."""
    try:
        from .dialogs.visual_style_dialog import VisualStyleDialog
        dialog = VisualStyleDialog(app)
        result = dialog.show()
        
        if result == "apply":
            # Redraw nodes with new themes
            if hasattr(app, 'canvas_manager'):
                app.canvas_manager.redraw_all_nodes()
                
    except Exception as e:
        from ..core.utils import show_error
        show_error("Visual Style Error", f"Failed to open visual style dialog: {e}")


def _toggle_enhanced_rendering(app):
    """Toggle enhanced node rendering."""
    if hasattr(app, 'canvas_manager'):
        app.canvas_manager.toggle_enhanced_rendering()
        status = "enabled" if app.canvas_manager.use_enhanced_rendering else "disabled"
        from ..core.utils import show_info
        show_info("Enhanced Rendering", f"Enhanced rendering {status}")


def _toggle_node_groups(app):
    """Toggle node group background display."""
    if hasattr(app, 'canvas_manager'):
        app.canvas_manager.toggle_node_groups()
        status = "shown" if app.canvas_manager.show_node_groups else "hidden"
        from ..core.utils import show_info
        show_info("Node Groups", f"Node group backgrounds {status}")


def _export_enhanced_mobile(app):
    """Export game with enhanced mobile-responsive features."""
    try:
        from ..core.enhanced_html_exporter import EnhancedHTMLExporter
        from ..core.utils import show_info, show_error, ask_yes_no
        
        # Show options dialog
        if ask_yes_no(
            "Enhanced Mobile Export",
            "Export with enhanced mobile features?\n\n"
            "This includes:\n"
            "• Mobile-responsive design\n"
            "• Touch controls and gestures\n" 
            "• Dark mode toggle\n"
            "• PWA support (offline capable)\n"
            "• Optimized performance\n\n"
            "Continue with enhanced export?"
        ):
            enhanced_exporter = EnhancedHTMLExporter(app)
            
            # Configure mobile options
            mobile_options = {
                'enable_touch_controls': True,
                'responsive_design': True,
                'pwa_support': True,
                'offline_mode': True,
                'dark_mode_toggle': True
            }
            
            success = enhanced_exporter.export_game(mobile_options)
            
            if success:
                show_info(
                    "Enhanced Export Complete",
                    "Your game has been exported with enhanced mobile features!\n\n"
                    "The exported game includes:\n"
                    "• Responsive design for all screen sizes\n"
                    "• Touch and swipe gesture support\n"
                    "• PWA capabilities for app-like experience\n"
                    "• Dark/light theme toggle\n"
                    "• Optimized mobile performance"
                )
        
    except Exception as e:
        show_error("Enhanced Export Error", f"Failed to export enhanced mobile game:\n{str(e)}")


def _open_batch_operations(app):
    """Open the batch operations dialog."""
    try:
        from .dialogs.batch_operations_dialog import BatchOperationsDialog
        dialog = BatchOperationsDialog(app, app)
        
    except Exception as e:
        from ..core.utils import show_error
        show_error("Batch Operations Error", f"Failed to open batch operations dialog:\n{str(e)}")


def _open_plugin_manager(app):
    """Open the plugin manager dialog."""
    try:
        from ..core.utils import show_info
        
        if not hasattr(app, 'plugin_manager') or app.plugin_manager is None:
            show_info("Plugin Manager", "Plugin system is not available.")
            return
        
        plugin_info = []
        for name, plugin in app.plugin_manager.plugins.items():
            status = "Enabled" if plugin.enabled else "Disabled"
            plugin_info.append(f"• {name} v{plugin.metadata.version} - {status}")
        
        if not plugin_info:
            plugin_info = ["No plugins loaded."]
        
        info_text = (
            f"Plugin Manager\n\n"
            f"Loaded Plugins ({len(app.plugin_manager.plugins)}):\n\n" +
            "\n".join(plugin_info) +
            f"\n\nPlugin directories:\n" +
            "\n".join(f"• {d}" for d in app.plugin_manager.plugin_directories)
        )
        
        show_info("Plugin Manager", info_text)
        
    except Exception as e:
        from ..core.utils import show_error
        show_error("Plugin Manager Error", f"Failed to open plugin manager:\n{str(e)}")


def _open_style_customizer(app):
    """Opens the HTML export style customizer."""
    try:
        from .windows.style_customizer import StyleCustomizer
        customizer = StyleCustomizer(app, app)
        customizer.focus()
    except Exception as e:
        from ..core.utils import show_error
        show_error("Style Customizer Error", f"Failed to open style customizer: {e}")


def _open_portrait_manager(app):
    """Opens the character portrait manager."""
    try:
        from .windows.portrait_manager import PortraitManagerWindow
        
        # Initialize portrait manager if not exists
        if not hasattr(app, 'portrait_manager'):
            from ..models.character_portrait import PortraitManager
            app.portrait_manager = PortraitManager()
        
        manager = PortraitManagerWindow(app)
        manager.focus()
    except Exception as e:
        from ..core.utils import show_error
        show_error("Portrait Manager Error", f"Failed to open portrait manager: {e}")


def _open_music_manager(app):
    """Opens the dynamic music manager."""
    try:
        from .windows.music_manager import MusicManagerWindow
        
        # Initialize music engine if not exists
        if not hasattr(app, 'music_engine'):
            from ..models.music_system import DynamicMusicEngine
            app.music_engine = DynamicMusicEngine()
        
        manager = MusicManagerWindow(app)
        manager.focus()
    except Exception as e:
        from ..core.utils import show_error
        show_error("Music Manager Error", f"Failed to open music manager: {e}")