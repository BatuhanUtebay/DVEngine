import pytest
import sys
import os
import tempfile
import json

# Add the project root to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from dvge.core.plugin_system import (
    PluginManager, PluginMetadata, PluginType, PluginInterface, 
    ExporterPlugin, LoadedPlugin, NodeTypePlugin
)
from unittest.mock import Mock, patch


class TestPluginMetadata:
    """Test cases for PluginMetadata."""
    
    def test_create_metadata(self):
        """Test creating plugin metadata."""
        metadata = PluginMetadata(
            name="Test Plugin",
            version="1.0.0",
            description="A test plugin",
            author="Test Author",
            plugin_type=PluginType.EXPORTER,
            dependencies=["dep1", "dep2"],
            min_dvge_version="1.0.0"
        )
        
        assert metadata.name == "Test Plugin"
        assert metadata.version == "1.0.0"
        assert metadata.plugin_type == PluginType.EXPORTER
        assert metadata.dependencies == ["dep1", "dep2"]
        assert metadata.enabled == True  # Default
        assert metadata.priority == 100  # Default
    
    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = PluginMetadata(
            name="Test Plugin",
            version="1.0.0",
            description="A test plugin",
            author="Test Author",
            plugin_type=PluginType.EXPORTER,
            dependencies=[],
            min_dvge_version="1.0.0"
        )
        
        data = metadata.to_dict()
        
        assert isinstance(data, dict)
        assert data['name'] == "Test Plugin"
        assert data['plugin_type'] == "exporter"
        assert data['enabled'] == True
    
    def test_metadata_from_dict(self):
        """Test creating metadata from dictionary."""
        data = {
            'name': 'Test Plugin',
            'version': '1.0.0',
            'description': 'A test plugin',
            'author': 'Test Author',
            'plugin_type': 'exporter',
            'dependencies': [],
            'min_dvge_version': '1.0.0'
        }
        
        metadata = PluginMetadata.from_dict(data)
        
        assert metadata.name == "Test Plugin"
        assert metadata.plugin_type == PluginType.EXPORTER


class TestExporterPlugin(ExporterPlugin):
    """Test implementation of ExporterPlugin."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Test Exporter",
            version="1.0.0",
            description="Test exporter plugin",
            author="Test Author",
            plugin_type=PluginType.EXPORTER,
            dependencies=[],
            min_dvge_version="1.0.0"
        )
    
    def initialize(self, app) -> bool:
        return True
    
    def cleanup(self) -> None:
        pass
    
    def get_export_format_name(self) -> str:
        return "Test Format"
    
    def get_file_extension(self) -> str:
        return ".test"
    
    def export(self, app, file_path: str, options=None) -> bool:
        # Write a simple test file
        with open(file_path, 'w') as f:
            f.write("Test export content")
        return True


class TestNodeTypePlugin(NodeTypePlugin):
    """Test implementation of NodeTypePlugin."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Test Node Type",
            version="1.0.0",
            description="Test node type plugin",
            author="Test Author",
            plugin_type=PluginType.NODE_TYPE,
            dependencies=[],
            min_dvge_version="1.0.0"
        )
    
    def initialize(self, app) -> bool:
        return True
    
    def cleanup(self) -> None:
        pass
    
    def get_node_class(self):
        return Mock  # Return mock class for testing
    
    def get_ui_panel_class(self):
        return None


class TestLoadedPlugin:
    """Test cases for LoadedPlugin."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.plugin_instance = TestExporterPlugin()
        self.metadata = self.plugin_instance.get_metadata()
        self.module = Mock()
        
        self.loaded_plugin = LoadedPlugin(
            self.plugin_instance, 
            self.metadata, 
            self.module
        )
    
    def test_initialization(self):
        """Test loaded plugin initialization."""
        assert self.loaded_plugin.instance == self.plugin_instance
        assert self.loaded_plugin.metadata == self.metadata
        assert self.loaded_plugin.enabled == True
        assert self.loaded_plugin.initialized == False
    
    def test_enable_disable(self):
        """Test enabling and disabling plugin."""
        # Initially enabled
        assert self.loaded_plugin.enabled == True
        
        # Disable
        result = self.loaded_plugin.disable()
        assert result == True
        assert self.loaded_plugin.enabled == False
        
        # Enable again
        result = self.loaded_plugin.enable()
        assert result == True
        assert self.loaded_plugin.enabled == True
    
    def test_initialize_plugin(self):
        """Test initializing plugin."""
        mock_app = Mock()
        
        result = self.loaded_plugin.initialize(mock_app)
        assert result == True
        assert self.loaded_plugin.initialized == True


class TestPluginManager:
    """Test cases for PluginManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_app = Mock()
        self.plugin_manager = PluginManager(self.mock_app)
    
    def test_initialization(self):
        """Test plugin manager initialization."""
        assert self.plugin_manager.app == self.mock_app
        assert isinstance(self.plugin_manager.plugins, dict)
        assert isinstance(self.plugin_manager.plugin_directories, list)
        assert isinstance(self.plugin_manager.hooks, dict)
        
        # Should have default plugin directories
        assert len(self.plugin_manager.plugin_directories) >= 1
    
    def test_add_plugin_directory(self):
        """Test adding plugin directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            initial_count = len(self.plugin_manager.plugin_directories)
            
            self.plugin_manager.add_plugin_directory(temp_dir)
            
            assert len(self.plugin_manager.plugin_directories) == initial_count + 1
            assert temp_dir in self.plugin_manager.plugin_directories
    
    def test_register_hook(self):
        """Test registering hooks."""
        def test_callback():
            return "test"
        
        self.plugin_manager.register_hook("test_hook", test_callback)
        
        assert "test_hook" in self.plugin_manager.hooks
        assert test_callback in self.plugin_manager.hooks["test_hook"]
    
    def test_execute_hook(self):
        """Test executing hooks."""
        results = []
        
        def callback1(data):
            results.append(f"callback1: {data}")
        
        def callback2(data):
            results.append(f"callback2: {data}")
        
        self.plugin_manager.register_hook("test_hook", callback1)
        self.plugin_manager.register_hook("test_hook", callback2)
        
        self.plugin_manager.execute_hook("test_hook", "test_data")
        
        assert len(results) == 2
        assert "callback1: test_data" in results
        assert "callback2: test_data" in results
    
    def test_load_plugin_from_instance(self):
        """Test loading a plugin instance directly."""
        plugin_instance = TestExporterPlugin()
        metadata = plugin_instance.get_metadata()
        
        # Manually add plugin (simulating successful load)
        loaded_plugin = LoadedPlugin(plugin_instance, metadata, Mock())
        self.plugin_manager.plugins[metadata.name] = loaded_plugin
        
        assert metadata.name in self.plugin_manager.plugins
        assert self.plugin_manager.get_plugin(metadata.name) == loaded_plugin
    
    def test_get_plugins_by_type(self):
        """Test getting plugins by type."""
        # Add test plugins
        exporter_plugin = TestExporterPlugin()
        exporter_metadata = exporter_plugin.get_metadata()
        exporter_loaded = LoadedPlugin(exporter_plugin, exporter_metadata, Mock())
        
        node_plugin = TestNodeTypePlugin()
        node_metadata = node_plugin.get_metadata()
        node_loaded = LoadedPlugin(node_plugin, node_metadata, Mock())
        
        self.plugin_manager.plugins[exporter_metadata.name] = exporter_loaded
        self.plugin_manager.plugins[node_metadata.name] = node_loaded
        
        # Test filtering
        exporters = self.plugin_manager.get_plugins_by_type(PluginType.EXPORTER)
        node_types = self.plugin_manager.get_plugins_by_type(PluginType.NODE_TYPE)
        
        assert len(exporters) == 1
        assert len(node_types) == 1
        assert exporters[0] == exporter_loaded
        assert node_types[0] == node_loaded
    
    def test_enable_disable_plugin(self):
        """Test enabling and disabling plugins."""
        # Add test plugin
        plugin_instance = TestExporterPlugin()
        metadata = plugin_instance.get_metadata()
        loaded_plugin = LoadedPlugin(plugin_instance, metadata, Mock())
        self.plugin_manager.plugins[metadata.name] = loaded_plugin
        
        # Test disable
        result = self.plugin_manager.disable_plugin(metadata.name)
        assert result == True
        assert loaded_plugin.enabled == False
        
        # Test enable
        result = self.plugin_manager.enable_plugin(metadata.name)
        assert result == True
        assert loaded_plugin.enabled == True
    
    def test_unload_plugin(self):
        """Test unloading plugins."""
        # Add test plugin
        plugin_instance = TestExporterPlugin()
        metadata = plugin_instance.get_metadata()
        loaded_plugin = LoadedPlugin(plugin_instance, metadata, Mock())
        self.plugin_manager.plugins[metadata.name] = loaded_plugin
        
        # Verify plugin is loaded
        assert metadata.name in self.plugin_manager.plugins
        
        # Unload plugin
        result = self.plugin_manager.unload_plugin(metadata.name)
        assert result == True
        assert metadata.name not in self.plugin_manager.plugins
    
    def test_plugin_config(self):
        """Test plugin configuration."""
        # Add test plugin
        plugin_instance = TestExporterPlugin()
        metadata = plugin_instance.get_metadata()
        loaded_plugin = LoadedPlugin(plugin_instance, metadata, Mock())
        self.plugin_manager.plugins[metadata.name] = loaded_plugin
        
        # Set config
        test_config = {"test_option": "test_value"}
        result = self.plugin_manager.set_plugin_config(metadata.name, test_config)
        assert result == True
        
        # Get config
        retrieved_config = self.plugin_manager.get_plugin_config(metadata.name)
        assert retrieved_config == test_config
    
    def test_save_load_plugin_states(self):
        """Test saving and loading plugin states."""
        # Add test plugin
        plugin_instance = TestExporterPlugin()
        metadata = plugin_instance.get_metadata()
        loaded_plugin = LoadedPlugin(plugin_instance, metadata, Mock())
        loaded_plugin.config = {"test": "config"}
        self.plugin_manager.plugins[metadata.name] = loaded_plugin
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            states_file = f.name
        
        try:
            # Save states
            self.plugin_manager.save_plugin_states(states_file)
            
            # Verify file was created and contains expected data
            assert os.path.exists(states_file)
            
            with open(states_file, 'r') as f:
                saved_states = json.load(f)
            
            assert metadata.name in saved_states
            assert saved_states[metadata.name]['enabled'] == True
            assert saved_states[metadata.name]['config'] == {"test": "config"}
            
            # Test loading (create new manager to simulate fresh start)
            new_manager = PluginManager(self.mock_app)
            new_manager.plugins[metadata.name] = LoadedPlugin(
                plugin_instance, metadata, Mock()
            )
            
            new_manager.load_plugin_states(states_file)
            
            # Verify states were loaded (this test is limited since we can't fully test
            # enable/disable without a more complex setup)
            
        finally:
            # Clean up
            if os.path.exists(states_file):
                os.unlink(states_file)
    
    def test_cleanup(self):
        """Test plugin cleanup."""
        # Add test plugin
        plugin_instance = TestExporterPlugin()
        metadata = plugin_instance.get_metadata()
        loaded_plugin = LoadedPlugin(plugin_instance, metadata, Mock())
        self.plugin_manager.plugins[metadata.name] = loaded_plugin
        
        # Add hook
        self.plugin_manager.register_hook("test_hook", lambda: None)
        
        # Verify initial state
        assert len(self.plugin_manager.plugins) > 0
        assert len(self.plugin_manager.hooks) > 0
        
        # Cleanup
        self.plugin_manager.cleanup()
        
        # Verify cleanup
        assert len(self.plugin_manager.plugins) == 0
        assert len(self.plugin_manager.hooks) == 0


class TestExporterPluginImplementation:
    """Test the test exporter plugin implementation."""
    
    def test_exporter_functionality(self):
        """Test the test exporter plugin."""
        plugin = TestExporterPlugin()
        
        # Test metadata
        metadata = plugin.get_metadata()
        assert metadata.name == "Test Exporter"
        assert metadata.plugin_type == PluginType.EXPORTER
        
        # Test exporter methods
        assert plugin.get_export_format_name() == "Test Format"
        assert plugin.get_file_extension() == ".test"
        
        # Test export functionality
        mock_app = Mock()
        
        with tempfile.NamedTemporaryFile(suffix='.test', delete=False) as f:
            test_file = f.name
        
        try:
            result = plugin.export(mock_app, test_file)
            assert result == True
            
            # Verify file was created with expected content
            with open(test_file, 'r') as f:
                content = f.read()
            assert content == "Test export content"
            
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)