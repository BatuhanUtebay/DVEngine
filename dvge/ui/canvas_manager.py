# dvge/ui/canvas_manager.py
import tkinter as tk
from tkinter import messagebox
from ..constants import *
from ..data_models import DialogueNode, DiceRollNode

class CanvasManager:
    def __init__(self, app):
        self.app = app
        self.canvas = app.canvas
        
        self.is_connecting = False
        self.connection_start_info = {}
        self.temp_connection_line = None
        self.right_click_pos = (0, 0)
        self.selection_rectangle = None
        self.drag_mode = None
        self.drag_start_pos = {}
        self.placeholder_id = None
        
        self.context_menu = tk.Menu(self.app, tearoff=0, bg=COLOR_PRIMARY_FRAME, fg=COLOR_TEXT, relief="flat",
                                    activebackground=COLOR_ACCENT, activeforeground=COLOR_TEXT)
        self.context_menu.add_command(label="Add New Node Here", command=self.add_node_from_menu)
        self.context_menu.add_command(label="Add Dice Roll Node", command=self.add_dice_roll_node_from_menu)
        self.context_menu.add_command(label="Delete Selected Node(s)", command=self.delete_selected_nodes)

        self.bind_events()

    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<ButtonPress-2>", self.on_pan_start) # Middle mouse for pan
        self.canvas.bind("<B2-Motion>", self.on_pan_move)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Control-MouseWheel>", self.on_zoom)

    def draw_grid(self):
        """Draws the background grid on the canvas."""
        self.canvas.delete("grid_line")
        for i in range(0, 10000, GRID_SIZE):
            self.canvas.create_line([(i, 0), (i, 10000)], tag="grid_line", fill=COLOR_GRID_LINES, width=1)
            self.canvas.create_line([(0, i), (10000, i)], tag="grid_line", fill=COLOR_GRID_LINES, width=1)
        self.canvas.tag_lower("grid_line")

    def draw_placeholder_if_empty(self):
        """Draws a placeholder message if the canvas is empty."""
        if self.placeholder_id:
            self.canvas.delete(self.placeholder_id)
            self.placeholder_id = None
        if not self.app.nodes:
            self.app.after(50, self._create_placeholder_text)

    def _create_placeholder_text(self):
        """Helper to create the placeholder text widget."""
        if not self.app.nodes:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            self.placeholder_id = self.canvas.create_text(
                canvas_width / 2, canvas_height / 2,
                text="Right-click to add a new node",
                font=(FONT_FAMILY, 16, "italic"),
                fill=COLOR_TEXT_MUTED,
                tags="placeholder"
            )

    def _create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        """Helper function to draw a rounded rectangle on the canvas."""
        points = [x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1,
                  x2, y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius, x2, y2 - radius,
                  x2, y2, x2 - radius, y2, x2 - radius, y2, x1 + radius, y2, x1 + radius, y2,
                  x1, y2, x1, y2 - radius, x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def redraw_all_nodes(self):
        """Clears and redraws the entire canvas, including grid, nodes, and connections."""
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_placeholder_if_empty()
        for node in self.app.nodes.values():
            self.create_node_visual(node)
        self.update_selection_visuals()
        self.draw_connections()

    def redraw_node(self, node_id):
        """Redraws a single node, which is more efficient than redrawing everything."""
        node = self.app.nodes.get(node_id)
        if not node: return
        for item_id in node.canvas_item_ids.values():
            if self.canvas.find_withtag(item_id):
                self.canvas.delete(item_id)
        node.canvas_item_ids.clear()
        
        self.create_node_visual(node)
        self.update_selection_visuals()
        self.draw_connections()

    def create_node_visual(self, node):
        """Creates all the visual components for a single node on the canvas."""
        x, y = node.x, node.y
        tags = ("node", node.id)
        
        temp_text = self.canvas.create_text(0, 0, text=node.text, font=FONT_DIALOGUE, anchor="nw", width=NODE_WIDTH - 40, state='hidden')
        bbox = self.canvas.bbox(temp_text)
        node.calculated_text_height = bbox[3] - bbox[1] if bbox else 0
        self.canvas.delete(temp_text)

        height = node.get_height()
        is_start_node = node.id == "intro"
        header_color = NODE_INTRO_COLOR if is_start_node else node.color if node.color != NODE_DEFAULT_COLOR else "#455A64"

        node.canvas_item_ids['shadow'] = self._create_rounded_rectangle(x+3, y+3, x + NODE_WIDTH+3, y + height+3, NODE_BORDER_RADIUS, fill="#111111", outline="", tags=tags)
        node.canvas_item_ids['body'] = self._create_rounded_rectangle(x, y, x + NODE_WIDTH, y + height, NODE_BORDER_RADIUS, fill=NODE_DEFAULT_COLOR, outline="", tags=tags)
        node.canvas_item_ids['header'] = self._create_rounded_rectangle(x, y, x + NODE_WIDTH, y + NODE_HEADER_HEIGHT, NODE_BORDER_RADIUS, fill=header_color, outline="", tags=tags)
        
        header_text = f"{'★' if is_start_node else ''} {node.id} | {node.npc}"
        node.canvas_item_ids['npc_text'] = self.canvas.create_text(x + 20, y + 20, text=header_text, fill=COLOR_TEXT, anchor="w", font=FONT_NPC, tags=tags)
        node.canvas_item_ids['dialogue_text'] = self.canvas.create_text(x + 20, y + 60, text=node.text, fill=COLOR_TEXT_MUTED, anchor="nw", width=NODE_WIDTH - 40, font=FONT_DIALOGUE, tags=tags)

        body_height = max(NODE_BASE_BODY_HEIGHT, node.calculated_text_height + 20)
        
        if isinstance(node, DiceRollNode):
            dice_text = f"Roll {node.num_dice}d{node.num_sides} vs {node.success_threshold}"
            node.canvas_item_ids['dice_text'] = self.canvas.create_text(x + 20, y + 100, text=dice_text, fill=COLOR_TEXT, anchor="nw", font=FONT_OPTION, tags=tags)
            node.canvas_item_ids['success_text'] = self.canvas.create_text(x + 20, y + 130, text=f"Success: {node.success_node}", fill=COLOR_SUCCESS, anchor="nw", font=FONT_OPTION, tags=tags)
            node.canvas_item_ids['failure_text'] = self.canvas.create_text(x + 20, y + 150, text=f"Failure: {node.failure_node}", fill=COLOR_ERROR, anchor="nw", font=FONT_OPTION, tags=tags)
        else:
            for i, option in enumerate(node.options):
                y_pos = y + NODE_HEADER_HEIGHT + body_height + (i * OPTION_LINE_HEIGHT) + 15
                option_text = f"{i+1}. {self.wrap_text(option.get('text', '...'), 35)}"
                
                indicator_text = ""
                if option.get('conditions'): indicator_text += " [C]"
                if option.get('effects'): indicator_text += " [E]"
                
                node.canvas_item_ids[f'option_text_{i}'] = self.canvas.create_text(x + 20, y_pos, text=option_text, fill=COLOR_TEXT, anchor="w", font=FONT_OPTION, tags=tags)
                if indicator_text:
                    node.canvas_item_ids[f'option_indicator_{i}'] = self.canvas.create_text(x + NODE_WIDTH - 45, y_pos, text=indicator_text, fill=COLOR_ACCENT, anchor="e", font=FONT_OPTION, tags=tags)

                node.canvas_item_ids[f'option_handle_{i}'] = self.canvas.create_oval(x + NODE_WIDTH - 20, y_pos - 8, x + NODE_WIDTH-4, y_pos + 8, fill=COLOR_ACCENT, outline="", tags=("handle", node.id, f"opt_{i}", "node"))

        footer_y = y + height - NODE_FOOTER_HEIGHT
        footer_tags = ("node", node.id, "add_option_button")
        # The footer is now just a clickable area, not visually distinct unless hovered
        if not isinstance(node, DiceRollNode):
            node.canvas_item_ids['add_button_text'] = self.canvas.create_text(x + NODE_WIDTH/2, footer_y + 18, text="+ Add Choice", fill=COLOR_TEXT_MUTED, font=FONT_ADD_BUTTON, tags=footer_tags, activefill=COLOR_ACCENT)

    def wrap_text(self, text, max_chars):
        """Truncates text to a maximum length for display on the node."""
        return text[:max_chars].strip() + "..." if len(text) > max_chars else text

    def add_node(self, x, y, node_type="dialogue"):
        """Creates a new node in the data model and on the canvas."""
        self.app._save_state_for_undo("Add Node")
        if self.placeholder_id:
            self.canvas.delete(self.placeholder_id)
            self.placeholder_id = None
        while f"node_{self.app.node_id_counter}" in self.app.nodes:
            self.app.node_id_counter += 1
        node_id_str = f"node_{self.app.node_id_counter}"
        self.app.node_id_counter += 1
        
        if node_type == "dice_roll":
            new_node = DiceRollNode(x=x, y=y, node_id=node_id_str)
        else:
            new_node = DialogueNode(x=x, y=y, node_id=node_id_str)
            
        self.app.nodes[node_id_str] = new_node
        self.create_node_visual(new_node)
        self.app.set_selection([node_id_str], node_id_str)

    def update_selection_visuals(self):
        """Updates the highlight state of all nodes based on the current selection."""
        for node_id, node in self.app.nodes.items():
            if node.canvas_item_ids.get('body'):
                is_selected = node_id in self.app.selected_node_ids
                outline_color = NODE_SELECTED_OUTLINE_COLOR if is_selected else ""
                outline_width = 3 if is_selected else 0
                self.canvas.itemconfig(node.canvas_item_ids['body'], outline=outline_color, width=outline_width)

    def on_canvas_press(self, event):
        """Handles the initial left-click event on the canvas."""
        self.context_menu.unpost()
        
        canvas_x, canvas_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(canvas_x, canvas_y)
        tags = self.canvas.gettags(item[0]) if item else []
        node_id = next((tag for tag in tags if tag in self.app.nodes), None)

        if "handle" in tags:
            opt_tag = next((t for t in tags if t.startswith("opt_")), None)
            if not opt_tag: return
            opt_index = int(opt_tag.split('_')[1])
            self.is_connecting = True
            self.connection_start_info = {'node_id': node_id, 'option_index': opt_index}
            x1, y1 = self.app.nodes[node_id].get_connection_point_out(opt_index)
            self.temp_connection_line = self.canvas.create_line(x1, y1, canvas_x, canvas_y, fill=COLOR_ACCENT, width=2.5, dash=(5, 5))
            return
        
        if "add_option_button" in tags:
            self.app.set_selection([node_id], node_id)
            if self.app.properties_panel.add_option_to_node(node_id):
                self.redraw_node(node_id)
                self.app.properties_panel.update_properties_panel()
            return

        if node_id:
            self.drag_mode = 'drag_nodes'
            if not event.state & 0x0001: # If not holding shift for multi-select
                if node_id not in self.app.selected_node_ids:
                    self.app.set_selection([node_id], node_id)
            else: # Holding shift
                if node_id in self.app.selected_node_ids:
                    self.app.selected_node_ids.remove(node_id)
                else:
                    self.app.selected_node_ids.append(node_id)
                self.app.set_selection(self.app.selected_node_ids, node_id)
            
            self.drag_start_pos['mouse'] = (canvas_x, canvas_y)
            self.drag_start_pos['nodes'] = {nid: (self.app.nodes[nid].x, self.app.nodes[nid].y) for nid in self.app.selected_node_ids}
        
        else:
            self.drag_mode = 'select_rect'
            if not event.state & 0x0001: self.app.set_selection([])
            self.drag_start_pos['mouse'] = (canvas_x, canvas_y)
            self.selection_rectangle = self.canvas.create_rectangle(canvas_x, canvas_y, canvas_x, canvas_y, outline=COLOR_ACCENT, dash=(4, 4), width=1.5)

    def on_canvas_drag(self, event):
        """Handles mouse movement while the left button is held down."""
        canvas_x, canvas_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        if self.is_connecting and self.temp_connection_line:
            x1, y1 = self.app.nodes[self.connection_start_info['node_id']].get_connection_point_out(self.connection_start_info['option_index'])
            self.canvas.coords(self.temp_connection_line, x1, y1, canvas_x, canvas_y)
        
        elif self.drag_mode == 'select_rect' and self.selection_rectangle:
            start_x, start_y = self.drag_start_pos['mouse']
            self.canvas.coords(self.selection_rectangle, start_x, start_y, canvas_x, canvas_y)
        
        elif self.drag_mode == 'drag_nodes' and self.app.selected_node_ids:
            mouse_start_x, mouse_start_y = self.drag_start_pos['mouse']
            dx = canvas_x - mouse_start_x
            dy = canvas_y - mouse_start_y
            
            for node_id in self.app.selected_node_ids:
                node = self.app.nodes[node_id]
                node_start_x, node_start_y = self.drag_start_pos['nodes'][node_id]
                
                new_x, new_y = node_start_x + dx, node_start_y + dy
                move_dx, move_dy = new_x - node.x, new_y - node.y
                
                if move_dx != 0 or move_dy != 0:
                    for item_id in node.canvas_item_ids.values():
                        self.canvas.move(item_id, move_dx, move_dy)
                    node.x, node.y = new_x, new_y
            
            self.draw_connections()

    def on_canvas_release(self, event):
        """Handles the release of the left mouse button."""
        if self.drag_mode == 'drag_nodes' and self.drag_start_pos.get('mouse') != (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)):
            self.app._save_state_for_undo("Drag Nodes")

        if self.is_connecting:
            if self.temp_connection_line: self.canvas.delete(self.temp_connection_line)
            target_item = self.canvas.find_closest(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
            if target_item:
                target_tags = self.canvas.gettags(target_item[0])
                target_node_id = next((tag for tag in target_tags if tag in self.app.nodes), None)
                if target_node_id:
                    self.app._save_state_for_undo("Create Connection")
                    source_node_id = self.connection_start_info['node_id']
                    opt_index = self.connection_start_info['option_index']
                    self.app.nodes[source_node_id].options[opt_index]['nextNode'] = target_node_id
                    self.draw_connections()
                    if self.app.active_node_id == source_node_id: self.app.properties_panel.update_properties_panel()
        
        elif self.drag_mode == 'select_rect' and self.selection_rectangle:
            x1, y1, x2, y2 = self.canvas.bbox(self.selection_rectangle)
            enclosed_items = self.canvas.find_enclosed(x1, y1, x2, y2)
            
            newly_selected_ids = self.app.selected_node_ids.copy()
            for item in enclosed_items:
                tags = self.canvas.gettags(item)
                node_id = next((tag for tag in tags if tag in self.app.nodes), None)
                if node_id and node_id not in newly_selected_ids:
                    newly_selected_ids.append(node_id)
            
            self.app.set_selection(newly_selected_ids)
            self.canvas.delete(self.selection_rectangle)

        elif self.drag_mode == 'drag_nodes':
            for node_id in self.app.selected_node_ids:
                node = self.app.nodes[node_id]
                snapped_x = round(node.x / GRID_SIZE) * GRID_SIZE
                snapped_y = round(node.y / GRID_SIZE) * GRID_SIZE
                move_dx, move_dy = snapped_x - node.x, snapped_y - node.y
                if move_dx != 0 or move_dy != 0:
                    for item_id in node.canvas_item_ids.values():
                        self.canvas.move(item_id, move_dx, move_dy)
                node.x, node.y = snapped_x, snapped_y
            
            self.draw_connections()

        self.is_connecting, self.temp_connection_line, self.drag_mode, self.drag_start_pos, self.selection_rectangle = False, None, None, {}, None

    def on_canvas_right_click(self, event):
        """Handles right-click events to show the context menu."""
        self.right_click_pos = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        item = self.canvas.find_closest(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        tags = self.canvas.gettags(item[0]) if item else []
        node_id = next((tag for tag in tags if tag in self.app.nodes), None)
        
        is_node_selected = bool(self.app.selected_node_ids)
        self.context_menu.entryconfig("Delete Selected Node(s)", state="normal" if is_node_selected else "disabled")
        
        if node_id and node_id not in self.app.selected_node_ids:
            self.app.set_selection([node_id], node_id)
            
        self.context_menu.post(event.x_root, event.y_root)

    def add_node_from_menu(self):
        """Adds a new node at the position of the right-click."""
        self.add_node(*self.right_click_pos)
        
    def add_dice_roll_node_from_menu(self):
        """Adds a new dice roll node at the position of the right-click."""
        self.add_node(*self.right_click_pos, node_type="dice_roll")
        
    def delete_selected_nodes(self, event=None):
        """Deletes all currently selected nodes."""
        if not self.app.selected_node_ids: return
        
        confirm = messagebox.askyesno("Delete Nodes", f"Are you sure you want to delete {len(self.app.selected_node_ids)} selected node(s)?")
        if not confirm: return

        self.app._save_state_for_undo("Delete Nodes")
        nodes_to_delete = list(self.app.selected_node_ids)
        for node_to_delete_id in nodes_to_delete:
            if node_to_delete_id == "intro": 
                messagebox.showwarning("Cannot Delete", "The 'intro' node cannot be deleted.")
                continue

            for node in self.app.nodes.values():
                for option in node.options:
                    if option.get('nextNode') == node_to_delete_id: option['nextNode'] = ""
                    
            if node_to_delete_id in self.app.nodes:
                node_to_delete = self.app.nodes[node_to_delete_id]
                for item_id in node_to_delete.canvas_item_ids.values():
                    self.canvas.delete(item_id)
                self.app.nodes.pop(node_to_delete_id, None)
        
        self.app.set_selection([])
        self.draw_connections()
        self.draw_placeholder_if_empty()

    def draw_connections(self):
        """Draws all the connection arrows between nodes."""
        self.canvas.delete("connection")
        for node in self.app.nodes.values():
            if isinstance(node, DiceRollNode):
                if node.success_node and node.success_node in self.app.nodes:
                    self.draw_arrow(node, self.app.nodes[node.success_node], 0, COLOR_SUCCESS)
                if node.failure_node and node.failure_node in self.app.nodes:
                    self.draw_arrow(node, self.app.nodes[node.failure_node], 1, COLOR_ERROR)
            else:
                for i, option in enumerate(node.options):
                    target_id = option.get("nextNode")
                    if target_id and target_id in self.app.nodes:
                        self.draw_arrow(node, self.app.nodes[target_id], i, NODE_CONNECTION_COLOR)
        self.canvas.tag_raise("node")

    def draw_arrow(self, source, target, opt_idx, color):
        """Draws a single Bezier curve arrow between two points."""
        x1, y1 = source.get_connection_point_out(opt_idx)
        x2, y2 = target.get_connection_point_in()
        ctrlx1, ctrly1 = x1 + 70, y1
        ctrlx2, ctrly2 = x2 - 70, y2
        line_id = self.canvas.create_line(x1, y1, ctrlx1, ctrly1, ctrlx2, ctrly2, x2, y2, smooth=True, arrow=tk.LAST, fill=color, width=2.5, tags="connection")
        self.canvas.tag_lower(line_id)

    def on_pan_start(self, event): self.canvas.scan_mark(event.x, event.y)
    def on_pan_move(self, event): self.canvas.scan_dragto(event.x, event.y, gain=1)
    def on_zoom(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.canvas.scale("all", self.canvas.canvasx(event.x), self.canvas.canvasy(event.y), factor, factor)

    def pan_to_node(self, node_id):
        """Pans the main canvas to center on a specific node."""
        node = self.app.nodes.get(node_id)
        if not node: return
        self.app.set_selection([node_id], node_id)
        x, y = node.x, node.y
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        target_x = x - canvas_width / 2 + NODE_WIDTH / 2
        target_y = y - canvas_height / 2 + node.get_height() / 2
        
        self.canvas.xview_moveto(target_x / 10000)
        self.canvas.yview_moveto(target_y / 10000)
