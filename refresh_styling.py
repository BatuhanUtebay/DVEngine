#!/usr/bin/env python3
"""Script to refresh enhanced styling for existing projects."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def refresh_enhanced_styling():
    """Refresh all nodes with enhanced styling."""
    print("Refreshing Enhanced Styling...")
    
    try:
        # Import main app
        from dvge.core.application import DVGApp
        import tkinter as tk
        
        # Create app instance
        root = tk.Tk()
        app = DVGApp()
        
        # Ensure enhanced rendering is enabled
        if hasattr(app, 'canvas_manager'):
            app.canvas_manager.use_enhanced_rendering = True
            
            # Get node count before
            node_count = len(app.nodes)
            print(f"Found {node_count} nodes to refresh")
            
            if node_count > 0:
                # Force redraw all nodes with enhanced styling
                print("Applying enhanced themes and styling...")
                app.canvas_manager.redraw_all_nodes()
                
                # Check themes applied
                from dvge.ui.canvas.node_themes import theme_manager
                themed_nodes = 0
                for node in app.nodes.values():
                    theme = theme_manager.get_theme_for_node(node)
                    if theme.header_color != "#455A64":  # Not default
                        themed_nodes += 1
                
                print(f"Enhanced styling applied to all nodes!")
                print(f"- Enhanced rendering: ENABLED")
                print(f"- Node groups: {'ENABLED' if app.canvas_manager.show_node_groups else 'DISABLED'}")
                print(f"- Themed elements: Icons, colors, shadows, borders")
                print(f"- Special themes: {themed_nodes} nodes have non-default themes")
                
                print("\nEnhanced styling features available:")
                print("- View → Toggle Enhanced Rendering (to switch back to basic)")
                print("- View → Visual Style Configuration (to customize themes)")
                print("- View → Toggle Node Groups (for chapter organization)")
                
            else:
                print("No nodes found. Create some nodes to see enhanced styling!")
                
        else:
            print("Canvas manager not found!")
            
        # Keep window open for user to see results
        print("\nDVGE is now running with enhanced styling!")
        print("Close this window when done testing.")
        
        root.mainloop()
        
    except Exception as e:
        print(f"Error refreshing styling: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    refresh_enhanced_styling()