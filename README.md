# Dialogue Venture Game Engine (DVGE) 🎮

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-113%20passing-brightgreen.svg)](#testing)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A **powerful, intuitive, node-based editor** for creating branching dialogue and narrative-driven experiences. Build interactive stories, visual novels, RPGs, and text adventures with a professional visual interface, then export to standalone HTML games that run anywhere.

## 🌟 Key Features

### 🎨 **Visual Node-Based Editor**
- **Intuitive drag-and-drop interface** for crafting complex narratives
- **Real-time connection system** - visually link dialogue choices to story branches
- **Advanced node types**: Dialogue, combat, dice rolls, QTE sequences, shops, and more
- **Smart canvas management** with zooming, panning, and node grouping
- **Customizable themes** and node styling for better organization

### 🎯 **Advanced Storytelling Systems**

**Character & Player Systems:**
- **Dynamic player stats** (Strength, Charisma, Health, etc.) that influence story paths
- **Comprehensive inventory system** with item effects and conditional availability
- **Quest tracking** with nested objectives and completion states
- **Relationship/reputation system** for complex character interactions

**Narrative Tools:**
- **Conditional branching** - choices appear based on stats, items, flags, or story progress
- **Story flags & variables** for tracking world states and player decisions
- **Timer systems** for time-sensitive events and story pacing
- **Random events** and dice-based outcomes for dynamic storytelling

**Combat & Game Mechanics:**
- **Advanced combat system** with tactical positioning and abilities
- **Skill check system** with difficulty scaling and stat-based outcomes
- **Quick-time events (QTE)** for interactive action sequences
- **Mini-games and puzzle mechanics** integration
- **Loot system** with random drops and treasure management

### 🤖 **AI-Powered Content Generation**
- **Smart dialogue generation** with context awareness and character consistency
- **Character profile creation** with backstory, personality, and voice analysis
- **Plot development assistance** including story structure and pacing analysis
- **Content improvement suggestions** and plot hole detection
- **Multiple AI provider support**: OpenAI, Anthropic, local AI (Ollama)

### 🔧 **Professional Development Tools**
- **Comprehensive testing suite** (113+ tests) with coverage reporting
- **Code quality tools**: Black formatting, flake8 linting, mypy type checking
- **Pre-commit hooks** for automated code quality assurance
- **Batch operations system** for bulk editing and project management
- **Plugin architecture** for extending functionality
- **Template system** with 7 pre-built project templates

### 📱 **Modern Export System**
- **Single-file HTML export** - complete games in one portable file
- **Mobile-responsive design** with touch controls and PWA support
- **Dark mode support** and accessibility features
- **Embedded media** - all images, audio, and assets bundled automatically
- **Advanced combat engine** with JavaScript-based tactical gameplay
- **Cross-platform compatibility** - runs in any modern web browser

## 🚀 Quick Start

### Option 1: Install via pip (Recommended)
```bash
# Install from PyPI
pip install dialogue-venture-game-engine

# Run the application
dvge
```

### Option 2: Development Setup
```bash
# Clone the repository
git clone https://github.com/BatuhanUtebay/DVEngine.git
cd DVEngine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 3: Download Executable
Visit the [Releases page](https://github.com/BatuhanUtebay/DVEngine/releases) and download the latest `DialogueVenture.exe` - no installation required!

## 📖 How to Use

### Basic Workflow
1. **Create nodes**: Right-click on the canvas to add dialogue, choice, or special nodes
2. **Edit properties**: Select nodes to modify text, conditions, and effects in the side panel
3. **Connect nodes**: Drag from choice handles to link story paths
4. **Set up systems**: Define player stats, inventory, and story flags
5. **Test your story**: Use the built-in preview system
6. **Export**: Generate a complete HTML game file

### Advanced Features
- **Templates**: Start with pre-built story structures (RPG, Mystery, Romance, etc.)
- **Media management**: Add images, audio, and character portraits
- **Batch operations**: Edit multiple nodes simultaneously
- **AI assistance**: Generate content and analyze your story structure
- **Plugin system**: Extend functionality with custom plugins

## 🎮 Project Templates

Choose from professionally designed templates:
- **Basic Story** - Simple branching narrative
- **RPG Adventure** - Full RPG with stats, combat, and inventory
- **Mystery Detective** - Investigation-based gameplay
- **Romance Story** - Character relationship focus
- **Sci-Fi Adventure** - Futuristic setting with technology themes
- **Advanced Combat RPG** - Tactical combat with positioning
- **Marketplace Demo** - Showcase of all engine features

## 🧪 Testing

DVGE includes a comprehensive test suite ensuring reliability:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dvge --cov-report=html

# Run specific test categories
pytest tests/core/          # Core functionality
pytest tests/ai/            # AI systems
pytest tests/models/        # Data models
```

Current test coverage: **113+ tests** across all major systems.

## 🛠️ Development Tools

Built with professional development practices:

```bash
# Code formatting
black .

# Linting
flake8

# Type checking
mypy dvge/

# Pre-commit hooks
pre-commit install
```

## 🏗️ Architecture

```
dvge/
├── core/           # Application core and state management
├── models/         # Node types and data structures  
├── ui/            # User interface components
├── features/      # Advanced game systems
├── ai/            # AI content generation
├── templates/     # Project templates
└── constants/     # Theme and styling constants
```

**Key Technologies:**
- **CustomTkinter** - Modern GUI framework
- **Pillow** - Image processing
- **ReportLab** - PDF export capabilities
- **Markdown** - Enhanced text processing

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Follow coding standards** (Black formatting, type hints, tests)
4. **Add tests** for new functionality
5. **Submit a pull request**

### Development Guidelines
- Follow PEP 8 style guidelines (enforced by Black)
- Add type hints to new functions
- Include docstrings for public APIs
- Write tests for new features
- Update documentation as needed

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/BatuhanUtebay/DVEngine/issues)
- **Feature Requests**: Use the "enhancement" tag
- **Documentation**: Check the [Wiki](https://github.com/BatuhanUtebay/DVEngine/wiki) (coming soon)

## 📈 Project Stats

- **115+ Python modules** with clean, maintainable architecture
- **7 pre-built templates** covering major game genres  
- **15+ node types** for complex storytelling
- **113+ automated tests** ensuring stability
- **Multiple AI providers** supported for content generation
- **Cross-platform** - Windows, macOS, Linux support

## 🎯 Roadmap

### Upcoming Features
- **Voice acting pipeline** with TTS integration
- **Visual novel mode** with sprite-based characters
- **Accessibility suite** with screen reader support
- **Community marketplace** for sharing templates and assets
- **Collaborative editing** for team projects
- **Advanced animation system** for dynamic scenes

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern UI
- Icons and assets from various open-source contributors
- Community feedback and testing from game developers worldwide

---

**Ready to create your interactive story?** 🚀

[Download Now](https://github.com/BatuhanUtebay/DVEngine/releases) | [View Examples](https://github.com/BatuhanUtebay/DVEngine/wiki/Examples) | [Join Community](https://github.com/BatuhanUtebay/DVEngine/discussions)