"""Example plugin that adds JSON export functionality."""

import json
import os
from tkinter import messagebox
from dvge.core.plugin_system import ExporterPlugin, PluginMetadata, PluginType


class JSONExporterPlugin(ExporterPlugin):
    """Plugin that exports projects to JSON format."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Example Exporter Plugin",
            version="1.0.0", 
            description="Example plugin that adds JSON export functionality",
            author="DVGE Team",
            plugin_type=PluginType.EXPORTER,
            dependencies=[],
            min_dvge_version="1.0.0"
        )
    
    def initialize(self, app) -> bool:
        """Initialize the plugin."""
        self.app = app
        print("JSON Exporter Plugin initialized")
        return True
    
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        print("JSON Exporter Plugin cleaned up")
    
    def get_export_format_name(self) -> str:
        """Return the name of the export format."""
        return "JSON Data Export"
    
    def get_file_extension(self) -> str:
        """Return the file extension for exported files."""
        return ".json"
    
    def export(self, app, file_path: str, options: dict = None) -> bool:
        """Export the project to JSON format."""
        try:
            # Collect all project data
            export_data = {
                "project_info": {
                    "name": "DVGE Project Export",
                    "version": "1.0.0",
                    "exported_by": "JSON Exporter Plugin",
                    "settings": app.project_settings
                },
                "nodes": {},
                "player_data": {
                    "stats": app.player_stats,
                    "inventory": app.player_inventory
                },
                "story_flags": app.story_flags,
                "variables": getattr(app, 'variables', {}),
                "quests": {
                    qid: quest.to_dict() if hasattr(quest, 'to_dict') else str(quest)
                    for qid, quest in app.quests.items()
                },
                "enemies": {
                    eid: enemy.to_dict() if hasattr(enemy, 'to_dict') else str(enemy)
                    for eid, enemy in getattr(app, 'enemies', {}).items()
                }
            }
            
            # Process nodes
            for node_id, node in app.nodes.items():
                node_data = {
                    "id": node.id,
                    "type": getattr(node, 'NODE_TYPE', 'unknown'),
                    "position": {
                        "x": getattr(node, 'x', 0),
                        "y": getattr(node, 'y', 0)
                    },
                    "npc": getattr(node, 'npc', 'Narrator'),
                    "text": getattr(node, 'text', ''),
                    "background_theme": getattr(node, 'backgroundTheme', ''),
                    "chapter": getattr(node, 'chapter', ''),
                    "color": getattr(node, 'color', '#FFFFFF'),
                    "background_image": getattr(node, 'backgroundImage', ''),
                    "audio": getattr(node, 'audio', ''),
                    "music": getattr(node, 'music', ''),
                    "auto_advance": getattr(node, 'auto_advance', False),
                    "auto_advance_delay": getattr(node, 'auto_advance_delay', 0)
                }
                
                # Add options if they exist
                if hasattr(node, 'options'):
                    node_data["options"] = node.options
                
                export_data["nodes"][node_id] = node_data
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo(
                "Export Successful",
                f"Project exported to JSON format:\n{file_path}\n\n"
                f"Exported {len(export_data['nodes'])} nodes and all project data."
            )
            
            return True
            
        except Exception as e:
            messagebox.showerror(
                "Export Error", 
                f"Failed to export to JSON:\n{str(e)}"
            )
            return False
    
    def get_export_options_ui(self):
        """Return UI class for configuring export options."""
        # Could return a custom UI class for export options
        return None
    
    def get_config_schema(self):
        """Return configuration schema for this plugin."""
        return {
            "properties": {
                "include_positions": {
                    "type": "boolean",
                    "title": "Include Node Positions",
                    "description": "Include X,Y coordinates of nodes in export",
                    "default": True
                },
                "pretty_format": {
                    "type": "boolean", 
                    "title": "Pretty Format",
                    "description": "Format JSON with indentation for readability",
                    "default": True
                }
            }
        }
    
    def configure(self, config: dict) -> bool:
        """Configure the plugin with user settings."""
        self.config = config
        return True