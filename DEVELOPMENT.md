# DVGE Development Guide

This document provides guidance for developers working on the Dialogue Venture Game Engine (DVGE).

## Development Setup

### Prerequisites
- Python 3.8+
- Git

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd DVEngine

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements.txt  # Includes dev dependencies

# Set up pre-commit hooks
pre-commit install
```

### Development Commands
Use the provided scripts for common tasks:

**Windows:**
```batch
# Run all quality checks
dev.bat quality

# Run tests
dev.bat test

# Run tests with coverage
dev.bat test-cov

# Format code
dev.bat format

# Run linting
dev.bat lint

# Clean build artifacts
dev.bat clean
```

**Unix/Linux/Mac:**
```bash
# Use Makefile commands
make quality
make test
make test-cov
make format
make lint
make clean
```

## Code Quality Standards

### Code Style
- **Formatter**: Black (88 character line limit)
- **Import Sorting**: isort (black-compatible profile)
- **Linting**: flake8 with project-specific rules
- **Type Checking**: mypy (gradually adding type hints)

### Testing
- **Framework**: pytest
- **Coverage Target**: 70% minimum
- **Test Types**: Unit tests, integration tests, UI tests (marked)
- **Test Structure**: Mirror source structure in `tests/` directory

### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality:
- Trailing whitespace removal
- End-of-file fixing
- YAML/JSON validation
- Large file checking
- Merge conflict detection
- Black formatting
- flake8 linting
- isort import sorting

## Architecture Overview

### Core Systems
- **Application**: `dvge/core/application.py` - Main app class
- **State Management**: `dvge/core/state_manager.py` - Undo/redo system
- **Project Handling**: `dvge/core/project_handler.py` - Save/load functionality
- **Validation**: `dvge/core/validation.py` - Project integrity checking
- **HTML Export**: `dvge/core/html_exporter.py` - Game export to HTML
- **Enhanced Export**: `dvge/core/enhanced_html_exporter.py` - Mobile-responsive export
- **Batch Operations**: `dvge/core/batch_operations.py` - Bulk node editing
- **Plugin System**: `dvge/core/plugin_system.py` - Extensibility framework

### UI Architecture
- **Main Window**: `dvge/ui/main_window.py` - Layout setup
- **Menus**: `dvge/ui/menus.py` - Menu system
- **Canvas**: `dvge/ui/canvas/` - Node visualization
- **Panels**: `dvge/ui/panels/` - Property editors
- **Dialogs**: `dvge/ui/dialogs/` - Modal dialogs
- **Windows**: `dvge/ui/windows/` - Standalone windows

### Data Models
- **Base Node**: `dvge/models/base_node.py` - Common node functionality
- **Specialized Nodes**: Various node types (dialogue, combat, QTE, etc.)
- **Game Objects**: Quests, enemies, timers, etc.

### Plugin System
The engine supports extensible plugins for:
- **Node Types**: Custom node implementations
- **Exporters**: New export formats
- **Validators**: Custom validation rules
- **Features**: Additional game features
- **Batch Operations**: Custom bulk operations

## Development Workflow

### Adding New Features
1. **Plan**: Create GitHub issue describing the feature
2. **Branch**: Create feature branch (`feature/feature-name`)
3. **Implement**: Write code following style guidelines
4. **Test**: Add comprehensive tests
5. **Document**: Update relevant documentation
6. **Review**: Submit pull request for review

### Bug Fixes
1. **Reproduce**: Create test case that reproduces the bug
2. **Fix**: Implement minimal fix
3. **Test**: Ensure fix works and doesn't break other functionality
4. **Validate**: Run full test suite

### Code Review Process
- All changes require review before merging
- Automated checks must pass (tests, linting, formatting)
- Documentation must be updated for API changes
- Breaking changes require version bump and migration guide

## Testing Guidelines

### Test Organization
```
tests/
├── core/           # Core system tests
├── models/         # Data model tests
├── ui/            # UI component tests
├── features/      # Feature system tests
├── integration/   # Integration tests
└── fixtures/      # Test data and fixtures
```

### Test Naming
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`  
- Test methods: `test_<specific_behavior>`

### Test Categories
Use pytest markers to categorize tests:
- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.ui` - Tests requiring UI components

### Running Tests
```bash
# All tests
pytest

# Specific category
pytest -m unit

# With coverage
pytest --cov=dvge --cov-report=html

# Parallel execution
pytest -n auto
```

## Plugin Development

### Creating a Plugin
1. **Create Plugin Directory**: `plugins/your_plugin/`
2. **Add Manifest**: `plugin.json` with metadata
3. **Implement Interface**: Extend appropriate plugin base class
4. **Add Module**: `__init__.py` with plugin class
5. **Test**: Create tests in `tests/plugins/`

### Plugin Structure
```
plugins/example_plugin/
├── plugin.json      # Plugin metadata
├── __init__.py      # Plugin implementation
├── ui.py           # Optional UI components
└── README.md       # Plugin documentation
```

### Example Plugin
```python
from dvge.core.plugin_system import ExporterPlugin, PluginMetadata, PluginType

class MyExporterPlugin(ExporterPlugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="My Exporter",
            version="1.0.0",
            description="Custom export format",
            author="Your Name",
            plugin_type=PluginType.EXPORTER,
            dependencies=[],
            min_dvge_version="1.0.0"
        )
    
    def initialize(self, app) -> bool:
        return True
    
    def cleanup(self) -> None:
        pass
    
    def get_export_format_name(self) -> str:
        return "My Format"
    
    def get_file_extension(self) -> str:
        return ".myformat"
    
    def export(self, app, file_path: str, options=None) -> bool:
        # Implementation here
        return True
```

## Performance Guidelines

### General Principles
- Profile before optimizing
- Optimize hot paths first
- Use appropriate data structures
- Cache expensive computations
- Minimize UI updates during bulk operations

### Canvas Performance
- Use canvas item recycling for large node counts
- Implement viewport culling
- Batch canvas updates
- Use efficient hit-testing algorithms

### Memory Management
- Clean up event handlers and references
- Use weak references where appropriate
- Implement proper cleanup in destructors
- Monitor memory usage with large projects

## Debugging

### Logging
The application uses Python's logging module:
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug information")
logger.info("General information") 
logger.warning("Warning message")
logger.error("Error occurred")
```

### Debug Mode
Enable debug mode for additional information:
```python
# In development
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues
- **Circular Imports**: Use lazy imports or restructure modules
- **Memory Leaks**: Check for uncleaned event handlers
- **Performance**: Profile with cProfile for bottlenecks
- **UI Freezing**: Move long operations to background threads

## Release Process

### Version Numbering
Follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

### Release Checklist
1. Update version numbers in `__init__.py` and `setup.py`
2. Update CHANGELOG.md with changes
3. Run full test suite
4. Build and test package
5. Create release tag
6. Publish to PyPI (if applicable)
7. Update documentation

### Building Distribution
```bash
# Clean previous builds
dev.bat clean

# Build source and wheel distributions
python -m build

# Check package
twine check dist/*
```

## Contributing Guidelines

### Before Contributing
- Read this development guide
- Set up development environment
- Run tests to ensure everything works
- Check existing issues and PRs

### Contribution Process
1. Fork the repository
2. Create feature branch
3. Make changes following guidelines
4. Add/update tests
5. Update documentation
6. Submit pull request

### Pull Request Guidelines
- Clear, descriptive title
- Detailed description of changes
- Reference related issues
- Include screenshots for UI changes
- Ensure all checks pass

### Code of Conduct
- Be respectful and constructive
- Help others learn and grow
- Focus on what's best for the project
- Welcome newcomers

## Resources

### Documentation
- [Python Style Guide](https://pep8.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)

### Tools
- [Black Code Formatter](https://black.readthedocs.io/)
- [flake8 Linter](https://flake8.pycqa.org/)
- [mypy Type Checker](https://mypy.readthedocs.io/)
- [pre-commit Hooks](https://pre-commit.com/)

### Getting Help
- Check existing documentation
- Search through GitHub issues
- Ask questions in discussions
- Contact maintainers for urgent issues