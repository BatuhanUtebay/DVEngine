"""Plugin system architecture for DVGE."""

import os
import sys
import json
import importlib
import inspect
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Type, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class PluginType(Enum):
    """Types of plugins supported by DVGE."""
    NODE_TYPE = "node_type"          # Custom node types
    EXPORTER = "exporter"            # Custom export formats
    IMPORTER = "importer"            # Custom import formats
    VALIDATOR = "validator"          # Custom validation rules
    FEATURE = "feature"              # New game features
    UI_COMPONENT = "ui_component"    # UI enhancements
    BATCH_OPERATION = "batch_operation"  # Custom batch operations
    THEME = "theme"                  # Visual themes
    TEMPLATE = "template"            # Project templates


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str]
    min_dvge_version: str
    max_dvge_version: Optional[str] = None
    enabled: bool = True
    priority: int = 100  # Lower numbers load first
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'plugin_type': self.plugin_type.value,
            'dependencies': self.dependencies,
            'min_dvge_version': self.min_dvge_version,
            'max_dvge_version': self.max_dvge_version,
            'enabled': self.enabled,
            'priority': self.priority
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginMetadata':
        """Create from dictionary."""
        return cls(
            name=data['name'],
            version=data['version'],
            description=data['description'],
            author=data['author'],
            plugin_type=PluginType(data['plugin_type']),
            dependencies=data.get('dependencies', []),
            min_dvge_version=data['min_dvge_version'],
            max_dvge_version=data.get('max_dvge_version'),
            enabled=data.get('enabled', True),
            priority=data.get('priority', 100)
        )


class PluginInterface(ABC):
    """Base interface that all plugins must implement."""
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    def initialize(self, app) -> bool:
        """Initialize the plugin with the main application.
        
        Args:
            app: The main DVGE application instance
            
        Returns:
            bool: True if initialization was successful
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass
    
    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """Return configuration schema for this plugin."""
        return None
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """Configure the plugin with user settings.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            bool: True if configuration was successful
        """
        return True


class NodeTypePlugin(PluginInterface):
    """Base class for plugins that add new node types."""
    
    @abstractmethod
    def get_node_class(self) -> Type:
        """Return the node class this plugin provides."""
        pass
    
    @abstractmethod
    def get_ui_panel_class(self) -> Optional[Type]:
        """Return the UI panel class for configuring this node type."""
        pass
    
    def get_canvas_renderer_class(self) -> Optional[Type]:
        """Return custom canvas renderer for this node type."""
        return None


class ExporterPlugin(PluginInterface):
    """Base class for plugins that add new export formats."""
    
    @abstractmethod
    def get_export_format_name(self) -> str:
        """Return the name of the export format (e.g., 'PDF', 'EPUB')."""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Return the file extension for exported files (e.g., '.pdf')."""
        pass
    
    @abstractmethod
    def export(self, app, file_path: str, options: Dict[str, Any] = None) -> bool:
        """Export the project to the specified format.
        
        Args:
            app: Main application instance
            file_path: Path to save the exported file
            options: Export options
            
        Returns:
            bool: True if export was successful
        """
        pass
    
    def get_export_options_ui(self) -> Optional[Type]:
        """Return UI class for configuring export options."""
        return None


class ValidatorPlugin(PluginInterface):
    """Base class for plugins that add custom validation rules."""
    
    @abstractmethod
    def validate_project(self, app) -> tuple[List[str], List[str]]:
        """Validate the project and return errors and warnings.
        
        Args:
            app: Main application instance
            
        Returns:
            tuple: (errors, warnings) - lists of error and warning messages
        """
        pass
    
    def get_validation_name(self) -> str:
        """Return a name for this validation check."""
        return self.__class__.__name__


class FeaturePlugin(PluginInterface):
    """Base class for plugins that add new game features."""
    
    @abstractmethod
    def get_feature_name(self) -> str:
        """Return the name of the feature."""
        pass
    
    def get_menu_items(self) -> List[Dict[str, Any]]:
        """Return menu items to add to the application.
        
        Returns:
            List of menu item dictionaries with keys:
            - 'label': Menu item text
            - 'command': Callable to execute
            - 'menu': Menu to add to ('file', 'edit', 'tools', etc.)
        """
        return []
    
    def get_ui_panels(self) -> List[Type]:
        """Return UI panel classes to add to the application."""
        return []


class BatchOperationPlugin(PluginInterface):
    """Base class for plugins that add custom batch operations."""
    
    @abstractmethod
    def get_operations(self) -> Dict[str, Callable]:
        """Return dictionary of operation name -> operation function."""
        pass
    
    def get_operation_descriptions(self) -> Dict[str, str]:
        """Return dictionary of operation name -> description."""
        return {}


class LoadedPlugin:
    """Represents a loaded plugin instance."""
    
    def __init__(self, plugin_instance: PluginInterface, metadata: PluginMetadata, module):
        self.instance = plugin_instance
        self.metadata = metadata
        self.module = module
        self.enabled = metadata.enabled
        self.initialized = False
        self.config = {}
    
    def enable(self) -> bool:
        """Enable the plugin."""
        if not self.enabled:
            self.enabled = True
            return True
        return False
    
    def disable(self) -> bool:
        """Disable the plugin."""
        if self.enabled:
            self.enabled = False
            if self.initialized:
                self.instance.cleanup()
                self.initialized = False
            return True
        return False
    
    def initialize(self, app) -> bool:
        """Initialize the plugin."""
        if self.enabled and not self.initialized:
            try:
                self.initialized = self.instance.initialize(app)
                return self.initialized
            except Exception as e:
                print(f"Failed to initialize plugin {self.metadata.name}: {e}")
                return False
        return False


class PluginManager:
    """Manages plugin loading, initialization, and lifecycle."""
    
    def __init__(self, app):
        self.app = app
        self.plugins: Dict[str, LoadedPlugin] = {}
        self.plugin_directories = []
        self.hooks: Dict[str, List[Callable]] = {}
        
        # Set up default plugin directories
        self._setup_plugin_directories()
    
    def _setup_plugin_directories(self):
        """Set up default plugin directories."""
        # Application plugins directory
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        app_plugins_dir = os.path.join(app_dir, 'plugins')
        if not os.path.exists(app_plugins_dir):
            os.makedirs(app_plugins_dir)
        self.plugin_directories.append(app_plugins_dir)
        
        # User plugins directory
        user_home = os.path.expanduser('~')
        user_plugins_dir = os.path.join(user_home, '.dvge', 'plugins')
        if not os.path.exists(user_plugins_dir):
            os.makedirs(user_plugins_dir, exist_ok=True)
        self.plugin_directories.append(user_plugins_dir)
    
    def add_plugin_directory(self, directory: str):
        """Add a directory to search for plugins."""
        if os.path.exists(directory) and directory not in self.plugin_directories:
            self.plugin_directories.append(directory)
    
    def discover_plugins(self) -> List[str]:
        """Discover all available plugins."""
        discovered = []
        
        for directory in self.plugin_directories:
            if not os.path.exists(directory):
                continue
                
            for item in os.listdir(directory):
                plugin_path = os.path.join(directory, item)
                
                # Check for Python package (directory with __init__.py)
                if os.path.isdir(plugin_path):
                    init_file = os.path.join(plugin_path, '__init__.py')
                    manifest_file = os.path.join(plugin_path, 'plugin.json')
                    
                    if os.path.exists(init_file) and os.path.exists(manifest_file):
                        discovered.append(plugin_path)
                
                # Check for single Python file
                elif item.endswith('.py') and not item.startswith('_'):
                    # Look for corresponding JSON manifest
                    json_file = plugin_path.replace('.py', '.json')
                    if os.path.exists(json_file):
                        discovered.append(plugin_path)
        
        return discovered
    
    def load_plugin(self, plugin_path: str) -> bool:
        """Load a single plugin from path."""
        try:
            # Determine if it's a package or single file
            if os.path.isdir(plugin_path):
                manifest_path = os.path.join(plugin_path, 'plugin.json')
                module_name = os.path.basename(plugin_path)
                
                # Add plugin directory to path
                parent_dir = os.path.dirname(plugin_path)
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                
            else:
                manifest_path = plugin_path.replace('.py', '.json')
                module_name = os.path.splitext(os.path.basename(plugin_path))[0]
                
                # Add plugin file directory to path
                parent_dir = os.path.dirname(plugin_path)
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
            
            # Load manifest
            if not os.path.exists(manifest_path):
                print(f"Plugin manifest not found: {manifest_path}")
                return False
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            metadata = PluginMetadata.from_dict(manifest_data)
            
            # Check if plugin is already loaded
            if metadata.name in self.plugins:
                print(f"Plugin {metadata.name} is already loaded")
                return False
            
            # Import the module
            module = importlib.import_module(module_name)
            
            # Find the plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, PluginInterface) and 
                    obj != PluginInterface and 
                    not inspect.isabstract(obj)):
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                print(f"No plugin class found in {module_name}")
                return False
            
            # Create plugin instance
            plugin_instance = plugin_class()
            
            # Verify metadata matches
            plugin_metadata = plugin_instance.get_metadata()
            if plugin_metadata.name != metadata.name:
                print(f"Plugin metadata mismatch: {plugin_metadata.name} vs {metadata.name}")
                return False
            
            # Create loaded plugin
            loaded_plugin = LoadedPlugin(plugin_instance, metadata, module)
            self.plugins[metadata.name] = loaded_plugin
            
            print(f"Successfully loaded plugin: {metadata.name} v{metadata.version}")
            return True
            
        except Exception as e:
            print(f"Failed to load plugin from {plugin_path}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_all_plugins(self):
        """Discover and load all available plugins."""
        discovered = self.discover_plugins()
        
        loaded_count = 0
        for plugin_path in discovered:
            if self.load_plugin(plugin_path):
                loaded_count += 1
        
        print(f"Loaded {loaded_count} plugins from {len(discovered)} discovered")
        
        # Initialize plugins in priority order
        self.initialize_all_plugins()
    
    def initialize_all_plugins(self):
        """Initialize all loaded plugins in priority order."""
        # Sort by priority (lower numbers first)
        sorted_plugins = sorted(
            self.plugins.values(),
            key=lambda p: p.metadata.priority
        )
        
        initialized_count = 0
        for plugin in sorted_plugins:
            if plugin.initialize(self.app):
                initialized_count += 1
                self._register_plugin_features(plugin)
        
        print(f"Initialized {initialized_count} plugins")
    
    def _register_plugin_features(self, plugin: LoadedPlugin):
        """Register plugin features with the application."""
        instance = plugin.instance
        
        # Register node types
        if isinstance(instance, NodeTypePlugin):
            node_class = instance.get_node_class()
            if hasattr(self.app, 'register_node_type'):
                self.app.register_node_type(node_class)
        
        # Register exporters
        elif isinstance(instance, ExporterPlugin):
            if hasattr(self.app, 'register_exporter'):
                self.app.register_exporter(instance)
        
        # Register validators
        elif isinstance(instance, ValidatorPlugin):
            if hasattr(self.app, 'register_validator'):
                self.app.register_validator(instance)
        
        # Register features
        elif isinstance(instance, FeaturePlugin):
            # Add menu items
            menu_items = instance.get_menu_items()
            for item in menu_items:
                if hasattr(self.app, 'add_menu_item'):
                    self.app.add_menu_item(item)
            
            # Register UI panels
            ui_panels = instance.get_ui_panels()
            for panel_class in ui_panels:
                if hasattr(self.app, 'register_ui_panel'):
                    self.app.register_ui_panel(panel_class)
        
        # Register batch operations
        elif isinstance(instance, BatchOperationPlugin):
            operations = instance.get_operations()
            descriptions = instance.get_operation_descriptions()
            
            if hasattr(self.app, 'batch_operation_manager'):
                for op_name, op_func in operations.items():
                    description = descriptions.get(op_name, f"Custom operation: {op_name}")
                    self.app.batch_operation_manager.register_operation(
                        op_name, op_func, description
                    )
    
    def get_plugin(self, name: str) -> Optional[LoadedPlugin]:
        """Get a loaded plugin by name."""
        return self.plugins.get(name)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[LoadedPlugin]:
        """Get all loaded plugins of a specific type."""
        return [
            plugin for plugin in self.plugins.values()
            if plugin.metadata.plugin_type == plugin_type
        ]
    
    def enable_plugin(self, name: str) -> bool:
        """Enable a plugin."""
        plugin = self.plugins.get(name)
        if plugin:
            if plugin.enable():
                plugin.initialize(self.app)
                self._register_plugin_features(plugin)
                return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """Disable a plugin."""
        plugin = self.plugins.get(name)
        if plugin:
            return plugin.disable()
        return False
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin completely."""
        plugin = self.plugins.get(name)
        if plugin:
            plugin.disable()
            del self.plugins[name]
            return True
        return False
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Register a callback for a specific hook."""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    def execute_hook(self, hook_name: str, *args, **kwargs):
        """Execute all callbacks registered for a hook."""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Hook {hook_name} callback failed: {e}")
    
    def get_plugin_config(self, name: str) -> Dict[str, Any]:
        """Get configuration for a plugin."""
        plugin = self.plugins.get(name)
        if plugin:
            return plugin.config.copy()
        return {}
    
    def set_plugin_config(self, name: str, config: Dict[str, Any]) -> bool:
        """Set configuration for a plugin."""
        plugin = self.plugins.get(name)
        if plugin:
            if plugin.instance.configure(config):
                plugin.config = config.copy()
                return True
        return False
    
    def save_plugin_states(self, file_path: str):
        """Save plugin states to a file."""
        states = {}
        for name, plugin in self.plugins.items():
            states[name] = {
                'enabled': plugin.enabled,
                'config': plugin.config
            }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(states, f, indent=2)
    
    def load_plugin_states(self, file_path: str):
        """Load plugin states from a file."""
        if not os.path.exists(file_path):
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                states = json.load(f)
            
            for name, state in states.items():
                plugin = self.plugins.get(name)
                if plugin:
                    if state['enabled']:
                        self.enable_plugin(name)
                    else:
                        self.disable_plugin(name)
                    
                    if state.get('config'):
                        self.set_plugin_config(name, state['config'])
        
        except Exception as e:
            print(f"Failed to load plugin states: {e}")
    
    def cleanup(self):
        """Clean up all plugins."""
        for plugin in self.plugins.values():
            try:
                plugin.instance.cleanup()
            except Exception as e:
                print(f"Failed to cleanup plugin {plugin.metadata.name}: {e}")
        
        self.plugins.clear()
        self.hooks.clear()


# Example plugin implementations
class ExampleNodeTypePlugin(NodeTypePlugin):
    """Example plugin that adds a custom node type."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Example Node Type",
            version="1.0.0",
            description="Adds an example custom node type",
            author="DVGE Team",
            plugin_type=PluginType.NODE_TYPE,
            dependencies=[],
            min_dvge_version="1.0.0"
        )
    
    def initialize(self, app) -> bool:
        print("Example node type plugin initialized")
        return True
    
    def cleanup(self) -> None:
        print("Example node type plugin cleaned up")
    
    def get_node_class(self) -> Type:
        # Would return custom node class
        from ..models.base_node import BaseNode
        return BaseNode
    
    def get_ui_panel_class(self) -> Optional[Type]:
        return None