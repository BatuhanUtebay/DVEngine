# dvge/core/project_handler.py
import json
from tkinter import filedialog, messagebox
from ..data_models import DialogueNode, Quest

def save_project(app):
    """Saves the current project state to a .dvgproj file."""
    filepath = filedialog.asksaveasfilename(defaultextension=".dvgproj", filetypes=[("DVG Project Files", "*.dvgproj")])
    if not filepath: return
    project_data = {
        "nodes": {node_id: node.to_dict() for node_id, node in app.nodes.items()},
        "player_stats": app.player_stats,
        "player_inventory": app.player_inventory,
        "story_flags": app.story_flags,
        "quests": {quest_id: quest.to_dict() for quest_id, quest in app.quests.items()},
        "node_id_counter": app.node_id_counter,
        "project_settings": app.project_settings
    }
    with open(filepath, 'w', encoding='utf-8') as f: json.dump(project_data, f, indent=4)
    messagebox.showinfo("Save Successful", f"Project saved to {filepath}")

def load_project(app):
    """Loads a project from a .dvgproj file."""
    filepath = filedialog.askopenfilename(filetypes=[("DVG Project Files", "*.dvgproj")])
    if not filepath: return

    app.canvas.delete("all")
    app.nodes.clear()
    app.set_selection([])
    app.canvas_manager.draw_grid()

    with open(filepath, 'r', encoding='utf-8') as f: project_data = json.load(f)

    app._initialize_project_state() # Reset to defaults first
    app.node_id_counter = project_data.get("node_id_counter", 0)
    app.player_stats = project_data.get("player_stats", {})
    app.player_inventory = project_data.get("player_inventory", [])
    app.story_flags = project_data.get("story_flags", {})
    app.project_settings = project_data.get("project_settings", { "font": "Merriweather", "title_font": "Special Elite", "background": ""})
    
    app.quests.clear()
    for quest_id, quest_data in project_data.get("quests", {}).items():
        app.quests[quest_id] = Quest.from_dict(quest_data)

    for node_id, node_data in project_data.get("nodes", {}).items():
        app.nodes[node_data['editor_data']['id']] = DialogueNode.from_dict(node_data)
    
    app.undo_stack.clear()
    app.redo_stack.clear()
    app._save_state_for_undo("Load Project")

    app.canvas_manager.redraw_all_nodes()
    app.properties_panel.update_all_panels()
    messagebox.showinfo("Load Successful", "Project loaded successfully.")
