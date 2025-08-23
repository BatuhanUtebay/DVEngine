# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Recent Major Improvements

The engine has been significantly enhanced with professional development tools and advanced features:

### ✅ Completed Enhancements (Latest Session)
- **Testing Framework**: Comprehensive pytest setup with 113 passing tests, coverage reporting
- **Code Quality**: Black formatter, flake8 linting, pre-commit hooks, isort import sorting
- **Professional Packaging**: setup.py, pyproject.toml, pip-installable with console scripts
- **Mobile-Responsive Export**: Enhanced HTML export with touch controls, PWA support, dark mode
- **Batch Operations**: Powerful system for bulk node editing with filtering and validation
- **Plugin System**: Extensible architecture for custom exporters, node types, features
- **AI-Powered Content Generation**: Intelligent writing assistant with OpenAI/Anthropic/local AI support
- **Development Tools**: Makefile/batch scripts, pre-commit hooks, comprehensive documentation

### 🚀 Next-Generation UX Enhancements (Planned)
- **Voice Acting Pipeline**: Professional TTS integration, voice asset management, character voice matching
- **Visual Novel Mode**: Sprite-based character system, background management, scene transitions
- **Accessibility Suite**: Screen reader support, colorblind-friendly themes, keyboard navigation
- **Community Marketplace**: Share templates, assets, and complete games with the community

## Project Overview

Dialogue Venture Game Engine (DVGE) is a Python-based, node-based editor for creating branching dialogue and narrative-driven experiences. It uses CustomTkinter for the GUI and exports games to standalone HTML files.

## Development Commands

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Virtual Environment Setup (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Unix/MacOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Architecture Overview

### Core Application Structure
- **Entry Point**: `main.py` → `dvge/core/application.py` (DVGApp class)
- **Main Window**: `dvge/ui/main_window.py` - Sets up the UI layout and components
- **State Management**: `dvge/core/state_manager.py` - Handles undo/redo and project state
- **Project Handling**: `dvge/core/project_handler.py` - Save/load project files
- **HTML Export**: `dvge/core/html_exporter.py` - Exports projects to playable HTML games

### Key System Components

#### Node System
- **Base Node**: `dvge/models/base_node.py` - Common functionality for all node types
- **Specialized Nodes**: Located in `dvge/models/` for dialogue, combat, dice rolls, QTE, etc.
- **Node Rendering**: `dvge/ui/canvas/` handles visual representation and interactions

#### Feature Systems
- **Variable System**: `dvge/core/variable_system.py` - Manages game variables and flags
- **Batch Operations**: `dvge/core/batch_operations.py` - Bulk editing and validation system
- **Plugin System**: `dvge/core/plugin_system.py` - Extensible plugin architecture
- **Feature Systems**: `dvge/features/` contains specialized systems (loot, reputation, skill checks, etc.)
- **Templates**: `dvge/templates/` contains pre-built project templates


#### AI-Powered Content Generation System
- **AI Service**: `dvge/ai/ai_service.py` - Core service with provider management, caching, rate limiting
- **AI Providers**: `dvge/ai/providers.py` - Support for OpenAI, Anthropic, local AI (Ollama), mock testing
- **Content Generators**: `dvge/ai/generators.py` - Specialized generators for different content types
  - **Dialogue Generator**: Context-aware dialogue creation, improvement, conversation generation
  - **Character Generator**: Character profiles, backstories, voice analysis, relationship suggestions
  - **Story Generator**: Plot outlines, scene descriptions, plot development suggestions
  - **Content Analyzer**: Story pacing analysis, plot hole detection, improvement recommendations
- **AI Assistant Panel**: `dvge/ui/panels/ai_assistant_panel.py` - Comprehensive UI with 6 tabs
  - **Chat Tab**: Interactive AI conversation with project context awareness
  - **Dialogue Tab**: Generate and improve dialogue lines, player options, conversations
  - **Character Tab**: Create character profiles, analyze voice consistency, generate backstories
  - **Story Tab**: Plot development, scene descriptions, story structure assistance
  - **Analysis Tab**: Content analysis, improvement suggestions, quality assessment
  - **Settings Tab**: Provider configuration, API key management, usage statistics
- **Features**: Async operations, response caching, request history, rate limiting, error handling

#### Next-Generation UX Enhancement Systems

##### 🎤 Voice Acting Pipeline
- **VoiceManager**: `dvge/features/voice_system.py` - Central voice asset management with TTS integration
- **TTSProviders**: `dvge/ai/tts_providers.py` - Multiple TTS services (Azure, AWS, Google, OpenAI)
- **VoiceAssetLibrary**: `dvge/models/voice_asset.py` - Organize voices by character/emotion with metadata
- **VoicePanel**: `dvge/ui/panels/voice_panel.py` - UI for voice management, preview, and batch generation
- **Integration**: Extends existing media system, connects to AI service for intelligent voice matching

##### 🎨 Visual Novel Mode
- **VisualNovelRenderer**: `dvge/core/visual_novel_exporter.py` - New export mode creating VN-style games
- **SpriteManager**: `dvge/features/sprite_system.py` - Character positioning, expressions, animations
- **BackgroundManager**: `dvge/features/background_system.py` - Scene backgrounds with transition effects
- **TransitionEngine**: `dvge/models/transitions.py` - Fade, slide, wipe transitions with timing control
- **VNConfigPanel**: `dvge/ui/panels/visual_novel_panel.py` - Visual novel settings and real-time preview
- **Integration**: Builds on character portrait system, integrates with media library

##### ♿ Accessibility Suite
- **AccessibilityManager**: `dvge/features/accessibility_system.py` - Central accessibility coordinator
- **ScreenReaderSupport**: `dvge/core/accessibility_exporter.py` - ARIA labels, semantic HTML structure
- **ColorblindSupport**: `dvge/ui/accessibility_themes.py` - Palette validation, pattern alternatives
- **FontScalingSystem**: `dvge/ui/accessibility_widgets.py` - Dynamic text sizing, contrast adjustment
- **KeyboardNavigation**: `dvge/features/keyboard_nav.py` - Full keyboard navigation for exported games
- **AccessibilityPanel**: `dvge/ui/panels/accessibility_panel.py` - A11y configuration and testing UI
- **Integration**: Enhances HTML export with WCAG compliance, extends theme system

##### 🏪 Community Marketplace
- **MarketplaceManager**: `dvge/features/marketplace_system.py` - Central marketplace coordinator with API
- **AssetStore**: `dvge/models/marketplace_content.py` - Repository for templates, assets, complete games
- **UserAuthentication**: `dvge/features/user_system.py` - Profile management, upload permissions
- **ContentBrowser**: `dvge/ui/windows/marketplace_window.py` - Search, filter, download community content
- **UploadManager**: `dvge/features/content_upload.py` - Content validation, metadata, publishing workflow
- **MarketplacePanel**: `dvge/ui/panels/marketplace_panel.py` - Browse, manage, and upload content
- **Integration**: Extends template manager, integrates with media system and plugin architecture

#### UI Architecture
- **Panels**: `dvge/ui/panels/` - Property editors and feature-specific UI panels
- **Dialogs**: `dvge/ui/dialogs/` - Modal dialogs (search, template selection, etc.)
- **Windows**: `dvge/ui/windows/` - Standalone windows (media manager, preview, etc.)
- **Canvas**: `dvge/ui/canvas/` - Node visualization and interaction system

### Key Data Structures

The main application (`DVGApp`) manages these core data structures:
- `nodes`: Dictionary of all story nodes by ID
- `player_stats`: Character attributes (health, strength, etc.)
- `player_inventory`: List of items the player possesses
- `story_flags`: Boolean flags for tracking story states
- `variables`: Numeric variables (gold, counters, etc.)
- `quests`: Quest tracking system
- `enemies`: Combat system enemies
- `timers`: Game timer objects

### Template System
- Templates are JSON files in `dvge/templates/` that define pre-configured projects
- Applied via `dvge/core/template_manager.py`
- Templates can set up nodes, variables, stats, and other project data

### Export System
- Games export to single HTML files with embedded JavaScript
- All media assets are base64 encoded into the HTML
- Uses validation system to check for errors before export

## UX Enhancement Implementation Strategy

### Phase 1: Voice Acting Pipeline (Priority: High)
1. **Core Voice System** (`dvge/features/voice_system.py`)
   - VoiceManager class with TTS provider abstraction
   - Voice asset metadata and storage management
   - Character voice profiling and consistency checking

2. **TTS Provider Integration** (`dvge/ai/tts_providers.py`)
   - Abstract base class for TTS providers
   - Azure Cognitive Services, AWS Polly, Google Cloud TTS, OpenAI TTS
   - Voice caching and batch generation capabilities

3. **UI Integration** (`dvge/ui/panels/voice_panel.py`)
   - Voice library browser with preview functionality
   - Character-to-voice assignment interface
   - Batch voice generation and export tools

4. **Export Enhancement**
   - Extend `html_exporter.py` to embed voice assets
   - HTML5 audio controls with dialogue synchronization
   - Fallback text display for accessibility

### Phase 2: Visual Novel Mode (Priority: High)
1. **Sprite Management** (`dvge/features/sprite_system.py`)
   - Character sprite library with expression/pose variants
   - Layer-based composition system for complex characters
   - Animation support (simple transitions, breathing effects)

2. **Scene Composition** (`dvge/features/background_system.py`)
   - Background library with parallax support
   - Scene transition effects (fade, slide, wipe, custom)
   - Environmental audio integration

3. **Visual Novel Exporter** (`dvge/core/visual_novel_exporter.py`)
   - Alternative HTML export mode for VN-style presentation
   - CSS-based character positioning and transitions
   - Touch/mobile-optimized controls

### Phase 3: Accessibility Suite (Priority: Medium)
1. **Accessibility Core** (`dvge/features/accessibility_system.py`)
   - WCAG compliance validation and reporting
   - Automated accessibility testing for exported games
   - Theme system extension for high contrast and colorblind support

2. **Enhanced Export** (`dvge/core/accessibility_exporter.py`)
   - Semantic HTML with proper ARIA labels
   - Keyboard navigation implementation
   - Screen reader optimizations

### Phase 4: Community Marketplace (Priority: Medium)
1. **Backend Integration** (`dvge/features/marketplace_system.py`)
   - RESTful API client for content repository
   - Authentication and user profile management
   - Content validation and metadata handling

2. **Content Management** (`dvge/features/content_upload.py`)
   - Upload wizard for templates, assets, and complete projects
   - Content categorization and tagging system
   - Community rating and review system

## Important Patterns

1. **Circular Import Prevention**: Many imports are done within functions to avoid circular dependencies
2. **State Management**: All significant actions should call `state_manager.save_state()` for undo support  
3. **Node References**: Nodes reference each other by ID strings, not direct object references
4. **Feature Integration**: Advanced features are optional and gracefully degrade if unavailable
5. **Canvas System**: UI elements store `canvas_item_ids` for tracking visual components
6. **UX Enhancement Integration**: New UX features extend existing systems without breaking compatibility
7. **Progressive Enhancement**: Features degrade gracefully when dependencies are unavailable

## Key Keyboard Shortcuts
- Ctrl+Z: Undo
- Ctrl+Y: Redo  
- Ctrl+F: Search nodes
- Ctrl+S: Save project
- Ctrl+O: Load project
- Ctrl+N: New project
- Ctrl+P: Live preview
- Delete: Delete selected nodes