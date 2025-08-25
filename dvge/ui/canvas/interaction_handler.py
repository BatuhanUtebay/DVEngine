# dvge/ui/canvas/interaction_handler.py

"""Interaction handling for canvas events."""

import tkinter as tk
from ...constants import *


class InteractionHandler:
    """Handles user interactions with the canvas."""
    
    def __init__(self, app, canvas):
        self.app = app
        self.canvas = canvas
        
        # Interaction state
        self.is_connecting = False
        self.connection_start_info = {}
        self.temp_connection_line = None
        self.selection_rectangle = None
        self.drag_mode = None
        self.drag_start_pos = {}
        self.is_dragging = False
        
        self._setup_context_menu()
        self._bind_events()

    def _setup_context_menu(self):
        """Sets up the right-click context menu."""
        self.context_menu = tk.Menu(
            self.app, tearoff=0, bg=COLOR_PRIMARY_FRAME, 
            fg=COLOR_TEXT, relief="flat",
            activebackground=COLOR_ACCENT, activeforeground=COLOR_TEXT
        )
    
        # Node creation submenu
        node_menu = tk.Menu(self.context_menu, tearoff=0, bg=COLOR_PRIMARY_FRAME, fg=COLOR_TEXT)
        node_menu.add_command(label="Dialogue Node", command=lambda: self._add_node_type("dialogue"))
        node_menu.add_command(label="Dice Roll Node", command=lambda: self._add_node_type("dice_roll"))
        node_menu.add_command(label="Combat Node", command=lambda: self._add_node_type("combat"))
        node_menu.add_command(label="Advanced Combat Node", command=lambda: self._add_node_type("advanced_combat"))
        node_menu.add_separator()
        node_menu.add_command(label="Shop Node", command=lambda: self._add_node_type("shop"))
        node_menu.add_command(label="Random Event Node", command=lambda: self._add_node_type("random_event"))
        node_menu.add_command(label="Timer Node", command=lambda: self._add_node_type("timer"))
        node_menu.add_command(label="Inventory Node", command=lambda: self._add_node_type("inventory"))
    
        self.context_menu.add_cascade(label="Add Node", menu=node_menu)
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Delete Selected Node(s)", 
            command=self._delete_selected_nodes
        )

    def _bind_events(self):
        """Binds mouse and keyboard events to the canvas."""
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<ButtonPress-2>", self.on_pan_start)
        self.canvas.bind("<B2-Motion>", self.on_pan_move)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Control-MouseWheel>", self.on_zoom)

    def on_canvas_press(self, event):
        """Handles the initial left-click event on the canvas."""
        self.context_menu.unpost()
        
        canvas_x, canvas_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(canvas_x, canvas_y)
        tags = self.canvas.gettags(item[0]) if item else []
        
        # Find the node ID from tags
        node_id = None
        for tag in tags:
            if tag in self.app.nodes:
                node_id = tag
                break

        # Check for handle click first (highest priority)
        if "handle" in tags and node_id:
            self._handle_connection_start(tags, node_id, canvas_x, canvas_y)
        elif "add_option_button" in tags and node_id:
            self._handle_add_option_click(node_id)
        elif node_id:
            self._handle_node_selection(node_id, event, canvas_x, canvas_y)
        else:
            self._handle_empty_canvas_click(event, canvas_x, canvas_y)

    def _handle_connection_start(self, tags, node_id, canvas_x, canvas_y):
        """Handles starting a connection from an option handle."""
        # Find the option index from the tags
        opt_tag = None
        for tag in tags:
            if tag.startswith("opt_"):
                opt_tag = tag
                break
                
        if not opt_tag:
            return
        
        try:
            opt_index = int(opt_tag.split('_')[1])
        except (IndexError, ValueError):
            return
        
        # Check if the node has enough options
        node = self.app.nodes.get(node_id)
        if not node or not hasattr(node, 'options') or opt_index >= len(node.options):
            return
        
        self.is_connecting = True
        self.connection_start_info = {'node_id': node_id, 'option_index': opt_index}
        
        # Get the connection start point
        x1, y1 = node.get_connection_point_out(opt_index)
        self.temp_connection_line = self.canvas.create_line(
            x1, y1, canvas_x, canvas_y, fill=COLOR_ACCENT, 
            width=2.5, dash=(5, 5), tags="temp_connection"
        )

    def _handle_add_option_click(self, node_id):
        """Handles clicking the add option button."""
        self.app.set_selection([node_id], node_id)
        if self.app.properties_panel.add_option_to_node(node_id):
            self.app.canvas_manager.redraw_node(node_id)
            self.app.properties_panel.update_properties_panel()

    def _handle_node_selection(self, node_id, event, canvas_x, canvas_y):
        """Handles node selection and drag preparation."""
        self.drag_mode = 'drag_nodes'
        self.is_dragging = False
        
        # Handle multi-select with Shift
        if not event.state & 0x0001:  # If not holding shift
            if node_id not in self.app.selected_node_ids:
                self.app.set_selection([node_id], node_id)
        else:  # Holding shift
            if node_id in self.app.selected_node_ids:
                self.app.selected_node_ids.remove(node_id)
            else:
                self.app.selected_node_ids.append(node_id)
            self.app.set_selection(self.app.selected_node_ids, node_id)
        
        self.drag_start_pos['mouse'] = (canvas_x, canvas_y)
        self.drag_start_pos['nodes'] = {
            nid: (self.app.nodes[nid].x, self.app.nodes[nid].y) 
            for nid in self.app.selected_node_ids
        }

    def _handle_empty_canvas_click(self, event, canvas_x, canvas_y):
        """Handles clicking on empty canvas for selection rectangle."""
        self.drag_mode = 'select_rect'
        if not event.state & 0x0001:
            self.app.set_selection([])
        
        self.drag_start_pos['mouse'] = (canvas_x, canvas_y)
        self.selection_rectangle = self.canvas.create_rectangle(
            canvas_x, canvas_y, canvas_x, canvas_y, 
            outline=COLOR_ACCENT, dash=(4, 4), width=1.5
        )

    def on_canvas_drag(self, event):
        """Handles mouse movement while the left button is held down."""
        canvas_x, canvas_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        if self.is_connecting and self.temp_connection_line:
            self._update_temp_connection(canvas_x, canvas_y)
        elif self.drag_mode == 'select_rect' and self.selection_rectangle:
            self._update_selection_rectangle(canvas_x, canvas_y)
        elif self.drag_mode == 'drag_nodes' and self.app.selected_node_ids:
            self._handle_node_dragging(canvas_x, canvas_y)

    def _update_temp_connection(self, canvas_x, canvas_y):
        """Updates the temporary connection line during dragging."""
        node_id = self.connection_start_info['node_id']
        opt_index = self.connection_start_info['option_index']
        
        if node_id in self.app.nodes:
            x1, y1 = self.app.nodes[node_id].get_connection_point_out(opt_index)
            self.canvas.coords(self.temp_connection_line, x1, y1, canvas_x, canvas_y)

    def _update_selection_rectangle(self, canvas_x, canvas_y):
        """Updates the selection rectangle during dragging."""
        start_x, start_y = self.drag_start_pos['mouse']
        self.canvas.coords(self.selection_rectangle, start_x, start_y, canvas_x, canvas_y)

    def _handle_node_dragging(self, canvas_x, canvas_y):
        """Handles dragging of selected nodes."""
        if not self.is_dragging:
            self.is_dragging = True
        
        mouse_start_x, mouse_start_y = self.drag_start_pos['mouse']
        dx = canvas_x - mouse_start_x
        dy = canvas_y - mouse_start_y
        
        # Update node positions and move visual elements
        for node_id in self.app.selected_node_ids:
            if node_id not in self.app.nodes:
                continue
                
            node = self.app.nodes[node_id]
            node_start_x, node_start_y = self.drag_start_pos['nodes'][node_id]
            
            new_x, new_y = node_start_x + dx, node_start_y + dy
            move_dx, move_dy = new_x - node.x, new_y - node.y
            
            if move_dx != 0 or move_dy != 0:
                # Move all visual elements for this node
                for item_id in node.canvas_item_ids.values():
                    if self.canvas.find_withtag(item_id):
                        self.canvas.move(item_id, move_dx, move_dy)
                # Update node position in data model
                node.x, node.y = new_x, new_y
        
        # Redraw connections during drag to show live updates
        self.app.canvas_manager.draw_connections()

    def on_canvas_release(self, event):
        """Handles the release of the left mouse button."""
        # Save state for undo if nodes were actually dragged
        if self.drag_mode == 'drag_nodes' and self.is_dragging:
            self.app._save_state_for_undo("Drag Nodes")
        
        if self.is_connecting:
            self._handle_connection_completion(event)
        elif self.drag_mode == 'select_rect' and self.selection_rectangle:
            self._handle_selection_completion()
        elif self.drag_mode == 'drag_nodes' and self.is_dragging:
            self._handle_drag_completion()

        # Reset drag state
        self._reset_interaction_state()

    def _handle_connection_completion(self, event):
        """Handles completion of a connection."""
        if self.temp_connection_line:
            self.canvas.delete(self.temp_connection_line)
        
        canvas_x, canvas_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        target_item = self.canvas.find_closest(canvas_x, canvas_y)
        
        if target_item:
            target_tags = self.canvas.gettags(target_item[0])
            
            # Find target node ID from tags
            target_node_id = None
            for tag in target_tags:
                if tag in self.app.nodes:
                    target_node_id = tag
                    break
            
            if target_node_id and target_node_id != self.connection_start_info['node_id']:
                self.app._save_state_for_undo("Create Connection")
                source_node_id = self.connection_start_info['node_id']
                opt_index = self.connection_start_info['option_index']
                
                # Ensure the source node and option still exist
                source_node = self.app.nodes.get(source_node_id)
                if (source_node and hasattr(source_node, 'options') and 
                    opt_index < len(source_node.options)):
                    source_node.options[opt_index]['nextNode'] = target_node_id
                    self.app.canvas_manager.draw_connections()
                    
                    if self.app.active_node_id == source_node_id:
                        self.app.properties_panel.update_properties_panel()

    def _handle_selection_completion(self):
        """Handles completion of rectangle selection."""
        if not self.selection_rectangle:
            return
            
        bbox = self.canvas.bbox(self.selection_rectangle)
        if bbox:
            x1, y1, x2, y2 = bbox
            enclosed_items = self.canvas.find_enclosed(x1, y1, x2, y2)
            
            newly_selected_ids = self.app.selected_node_ids.copy()
            for item in enclosed_items:
                tags = self.canvas.gettags(item)
                node_id = None
                for tag in tags:
                    if tag in self.app.nodes:
                        node_id = tag
                        break
                if node_id and node_id not in newly_selected_ids:
                    newly_selected_ids.append(node_id)
            
            self.app.set_selection(newly_selected_ids)
        
        self.canvas.delete(self.selection_rectangle)

    def _handle_drag_completion(self):
        """Handles completion of node dragging with grid snapping."""
        for node_id in self.app.selected_node_ids:
            if node_id not in self.app.nodes:
                continue
                
            node = self.app.nodes[node_id]
            snapped_x = round(node.x / GRID_SIZE) * GRID_SIZE
            snapped_y = round(node.y / GRID_SIZE) * GRID_SIZE
            move_dx, move_dy = snapped_x - node.x, snapped_y - node.y
            
            if move_dx != 0 or move_dy != 0:
                # Move visual elements to snapped position
                for item_id in node.canvas_item_ids.values():
                    if self.canvas.find_withtag(item_id):
                        self.canvas.move(item_id, move_dx, move_dy)
                # Update node position to snapped coordinates
                node.x, node.y = snapped_x, snapped_y
        
        # Final redraw of connections with correct positions
        self.app.canvas_manager.draw_connections()

    def _reset_interaction_state(self):
        """Resets all interaction state variables."""
        self.is_connecting = False
        self.temp_connection_line = None
        self.drag_mode = None
        self.drag_start_pos = {}
        self.selection_rectangle = None
        self.is_dragging = False

    def on_canvas_right_click(self, event):
        """Handles right-click events to show the context menu."""
        self.right_click_pos = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        
        canvas_x, canvas_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(canvas_x, canvas_y)
        tags = self.canvas.gettags(item[0]) if item else []
        
        # Find node ID from tags
        node_id = None
        for tag in tags:
            if tag in self.app.nodes:
                node_id = tag
                break
        
        is_node_selected = bool(self.app.selected_node_ids)
        self.context_menu.entryconfig(
            "Delete Selected Node(s)", 
            state="normal" if is_node_selected else "disabled"
        )
        
        if node_id and node_id not in self.app.selected_node_ids:
            self.app.set_selection([node_id], node_id)
            
        self.context_menu.post(event.x_root, event.y_root)

    def _add_node_from_menu(self):
        """Adds a new node at the position of the right-click."""
        self.app.canvas_manager.add_node(*self.right_click_pos)
        
    def _add_dice_roll_node_from_menu(self):
        """Adds a new dice roll node at the position of the right-click."""
        self.app.canvas_manager.add_node(*self.right_click_pos, node_type="dice_roll")
        
    def _delete_selected_nodes(self):
        """Deletes all currently selected nodes."""
        self.app.canvas_manager.delete_selected_nodes()
    
    def _add_node_type(self, node_type):
        """Adds a specific node type at the right-click position."""
        if node_type == "advanced_combat":
            # Open the advanced combat editor for new nodes
            from ...ui.windows import AdvancedCombatEditor
            # Pass the right-click position to the editor
            editor = AdvancedCombatEditor(self.app, position=self.right_click_pos)
        else:
            self.app.canvas_manager.add_node(*self.right_click_pos, node_type=node_type)

    def on_pan_start(self, event):
        """Handles the start of canvas panning."""
        self.canvas.scan_mark(event.x, event.y)
        
    def on_pan_move(self, event):
        """Handles canvas panning movement."""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        
    def on_zoom(self, event):
        """Handles canvas zooming with mouse wheel and maintains text readability."""
        factor = 1.1 if event.delta > 0 else 0.9
        
        # Get current zoom level (stored in canvas if available)
        if not hasattr(self.canvas, 'zoom_level'):
            self.canvas.zoom_level = 1.0
            
        new_zoom = self.canvas.zoom_level * factor
        
        # Limit zoom range for usability
        if new_zoom < 0.3 or new_zoom > 3.0:
            return
            
        # Update zoom level
        self.canvas.zoom_level = new_zoom
        
        # Standard scaling for most elements
        self.canvas.scale("all", self.canvas.canvasx(event.x), self.canvas.canvasy(event.y), factor, factor)
        
        # For very small zoom levels, trigger node text optimization
        if new_zoom < 0.6:
            self._optimize_nodes_for_small_zoom()
        elif hasattr(self, '_zoom_optimized') and self._zoom_optimized:
            # Restore normal view when zooming back in
            self._restore_normal_node_view()
    
    def _optimize_nodes_for_small_zoom(self):
        """Optimizes node display for small zoom levels."""
        if hasattr(self, '_zoom_optimized') and self._zoom_optimized:
            return
            
        # Hide detailed text and show only essential info
        for node in self.app.nodes.values():
            if 'dialogue_text' in node.canvas_item_ids:
                # Hide dialogue text when zoomed out
                self.canvas.itemconfig(node.canvas_item_ids['dialogue_text'], state='hidden')
            
        self._zoom_optimized = True
    
    def _restore_normal_node_view(self):
        """Restores normal node view when zooming back in."""
        for node in self.app.nodes.values():
            if 'dialogue_text' in node.canvas_item_ids:
                # Show dialogue text when zoomed in
                self.canvas.itemconfig(node.canvas_item_ids['dialogue_text'], state='normal')
                
        self._zoom_optimized = False