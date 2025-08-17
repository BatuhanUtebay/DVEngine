"""Project template management system for DVGE."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from ..models import create_node_from_dict


class ProjectTemplate:
    """Represents a single project template."""
    
    def __init__(self, template_data: Dict):
        self.id = template_data.get("id", "")
        self.name = template_data.get("name", "Untitled Template")
        self.description = template_data.get("description", "")
        self.category = template_data.get("category", "General")
        self.difficulty = template_data.get("difficulty", "Beginner")
        self.tags = template_data.get("tags", [])
        self.author = template_data.get("author", "DVGE Team")
        self.version = template_data.get("version", "1.0")
        self.preview_image = template_data.get("preview_image", "")
        
        # Project data
        self.project_data = template_data.get("project_data", {})
        
        # Tutorial/help information
        self.tutorial_steps = template_data.get("tutorial_steps", [])
        self.help_text = template_data.get("help_text", "")


class TemplateManager:
    """Manages project templates."""
    
    def __init__(self):
        self.templates: Dict[str, ProjectTemplate] = {}
        self.templates_path = Path(__file__).parent.parent / "templates"
        self._ensure_templates_directory()
        self._load_templates()
    
    def _ensure_templates_directory(self):
        """Ensure the templates directory exists."""
        self.templates_path.mkdir(exist_ok=True)
    
    def _load_templates(self):
        """Load all templates from the templates directory."""
        self.templates.clear()
        
        # Load built-in templates
        for template_file in self.templates_path.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    template = ProjectTemplate(template_data)
                    self.templates[template.id] = template
            except Exception as e:
                print(f"Failed to load template {template_file}: {e}")
    
    def get_template(self, template_id: str) -> Optional[ProjectTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)
    
    def get_all_templates(self) -> List[ProjectTemplate]:
        """Get all available templates."""
        return list(self.templates.values())
    
    def get_templates_by_category(self, category: str = None) -> List[ProjectTemplate]:
        """Get templates filtered by category."""
        if category is None:
            return list(self.templates.values())
        return [template for template in self.templates.values() 
                if template.category == category]
    
    def get_categories(self) -> List[str]:
        """Get all available template categories."""
        categories = set(template.category for template in self.templates.values())
        return sorted(list(categories))
    
    def search_templates(self, query: str) -> List[ProjectTemplate]:
        """Search templates by name, description, or tags."""
        query = query.lower()
        results = []
        
        for template in self.templates.values():
            if (query in template.name.lower() or 
                query in template.description.lower() or 
                any(query in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results
    
    def apply_template(self, template, app) -> bool:
        """Apply a template to the application."""
        if isinstance(template, str):
            template = self.get_template(template)
        if not template:
            return False
        
        try:
            # Clear current state (only if UI elements exist)
            if hasattr(app, 'canvas'):
                app.canvas.delete("all")
            app.nodes.clear()
            if hasattr(app, 'set_selection'):
                app.set_selection([])
            if hasattr(app, 'canvas_manager'):
                app.canvas_manager.draw_grid()
            
            # Reset to defaults first (only if method exists)
            if hasattr(app, '_initialize_project_state'):
                app._initialize_project_state()
            
            # Apply template data
            project_data = template.project_data
            
            # Load basic project settings
            app.node_id_counter = project_data.get("node_id_counter", 0)
            app.player_stats = project_data.get("player_stats", {})
            app.player_inventory = project_data.get("player_inventory", [])
            app.story_flags = project_data.get("story_flags", {})
            app.variables = project_data.get("variables", {})
            app.project_settings = project_data.get("project_settings", {
                "font": "Merriweather", 
                "title_font": "Special Elite", 
                "background": ""
            })
            
            # Load quests
            app.quests.clear()
            for quest_id, quest_data in project_data.get("quests", {}).items():
                from ..models import Quest
                quest = Quest.from_dict(quest_data)
                app.quests[quest_id] = quest
            
            # Load enemies
            app.enemies = {}
            for enemy_id, enemy_data in project_data.get("enemies", {}).items():
                from ..models import Enemy
                enemy = Enemy.from_dict(enemy_data)
                app.enemies[enemy_id] = enemy
            
            # Load timers
            app.timers = {}
            for timer_id, timer_data in project_data.get("timers", {}).items():
                from ..models import GameTimer
                timer = GameTimer.from_dict(timer_data)
                app.timers[timer_id] = timer
            
            # Load nodes
            for node_id, node_data in project_data.get("nodes", {}).items():
                node = create_node_from_dict(node_data)
                app.nodes[node_id] = node
            
            # Update variable system references (if available)
            if hasattr(app, 'variable_system'):
                app.variable_system.set_variables_ref(app.variables)
                app.variable_system.set_flags_ref(app.story_flags)
            
            # Redraw everything (only if UI elements exist)
            if hasattr(app, 'canvas_manager'):
                app.canvas_manager.redraw_all_nodes()
            if hasattr(app, 'properties_panel'):
                app.properties_panel.update_all_panels()
            if hasattr(app, 'state_manager'):
                app.state_manager.clear_history()
                app.state_manager.save_state(f"Applied template: {template.name}")
            
            return True
            
        except Exception as e:
            print(f"Failed to apply template {template.name}: {e}")
            return False
    
    def create_template_from_project(self, app, template_info: Dict) -> bool:
        """Create a new template from the current project."""
        try:
            # Create template data
            template_data = {
                "id": template_info["id"],
                "name": template_info["name"],
                "description": template_info["description"],
                "category": template_info["category"],
                "difficulty": template_info.get("difficulty", "Beginner"),
                "tags": template_info.get("tags", []),
                "author": template_info.get("author", "User"),
                "version": "1.0",
                "project_data": {
                    "version": "1.0.0",
                    "nodes": {node_id: node.to_dict() for node_id, node in app.nodes.items()},
                    "player_stats": app.player_stats,
                    "player_inventory": app.player_inventory,
                    "story_flags": app.story_flags,
                    "quests": {quest_id: quest.to_dict() for quest_id, quest in app.quests.items()},
                    "variables": getattr(app, 'variables', {}),
                    "enemies": {eid: e.to_dict() for eid, e in getattr(app, 'enemies', {}).items()},
                    "timers": {tid: t.to_dict() for tid, t in getattr(app, 'timers', {}).items()},
                    "node_id_counter": app.node_id_counter,
                    "project_settings": app.project_settings
                },
                "tutorial_steps": template_info.get("tutorial_steps", []),
                "help_text": template_info.get("help_text", "")
            }
            
            # Save template file
            template_file = self.templates_path / f"{template_info['id']}.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=4)
            
            # Reload templates
            self._load_templates()
            
            return True
            
        except Exception as e:
            print(f"Failed to create template: {e}")
            return False