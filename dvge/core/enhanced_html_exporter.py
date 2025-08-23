"""Enhanced HTML Exporter with mobile-responsive design and modern features."""

import json
import base64
import os
from tkinter import filedialog, messagebox
from .variable_system import VariableSystem


class EnhancedHTMLExporter:
    """Enhanced HTML exporter with mobile-responsive design and PWA capabilities."""
    
    def __init__(self, app):
        self.app = app
        self.style_settings = None
        self.mobile_settings = {
            'enable_touch_controls': True,
            'responsive_design': True,
            'pwa_support': True,
            'offline_mode': True,
            'dark_mode_toggle': True
        }
    
    def export_game(self, enhanced_options=None):
        """Export game with enhanced mobile-responsive features."""
        if enhanced_options:
            self.mobile_settings.update(enhanced_options)
            
        if not self.app.nodes:
            messagebox.showwarning("Export Error", "Cannot export an empty project.")
            return False
        
        # Validate project first
        errors, warnings = self.app.validator.validate_project()
        if errors:
            message = "Project validation found errors:\n\n" + "\n".join(errors)
            messagebox.showerror("Validation Errors", message)
            return False
            
        if warnings:
            message = "Project validation found warnings:\n\n" + "\n".join(warnings) + "\n\nContinue with export?"
            if not messagebox.askyesno("Validation Warnings", message):
                return False

        try:
            # Process all game data
            dialogue_data = self._process_dialogue_data()
            
            # Get save file path
            file_path = filedialog.asksaveasfilename(
                title="Export Enhanced HTML Game",
                defaultextension=".html",
                filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")]
            )
            
            if not file_path:
                return False
            
            # Generate enhanced HTML content
            html_content = self._generate_enhanced_html(dialogue_data)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Generate PWA manifest if enabled
            if self.mobile_settings.get('pwa_support'):
                self._generate_pwa_manifest(file_path)
            
            messagebox.showinfo(
                "Export Successful", 
                f"Enhanced HTML game exported successfully to:\n{file_path}\n\n"
                f"Features enabled:\n"
                f"• Mobile-responsive design\n"
                f"• Touch controls\n" 
                f"• Dark mode toggle\n"
                f"{'• PWA support' if self.mobile_settings.get('pwa_support') else ''}"
            )
            
            return True
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export HTML game:\n{str(e)}")
            return False
    
    def _process_dialogue_data(self):
        """Process dialogue data with enhanced features."""
        processed_data = {}
        
        for node_id, node in self.app.nodes.items():
            node_data = {
                'id': node.id,
                'npc': getattr(node, 'npc', 'Narrator'),
                'text': getattr(node, 'text', ''),
                'type': getattr(node, 'NODE_TYPE', 'dialogue'),
                'backgroundTheme': getattr(node, 'backgroundTheme', ''),
                'chapter': getattr(node, 'chapter', ''),
                'backgroundImage': getattr(node, 'backgroundImage', ''),
                'audio': getattr(node, 'audio', ''),
                'music': getattr(node, 'music', ''),
                'auto_advance': getattr(node, 'auto_advance', False),
                'auto_advance_delay': getattr(node, 'auto_advance_delay', 0),
                
                # Enhanced mobile features
                'touch_areas': self._generate_touch_areas(node),
                'swipe_actions': self._generate_swipe_actions(node),
                'mobile_optimized': True
            }
            
            # Process options/choices
            if hasattr(node, 'options'):
                node_data['options'] = []
                for option in node.options:
                    option_data = dict(option)  
                    # Add mobile-specific option data
                    option_data['touch_priority'] = len(node_data['options'])
                    option_data['swipe_direction'] = self._get_swipe_direction(len(node_data['options']))
                    node_data['options'].append(option_data)
            
            processed_data[node_id] = node_data
            
        return processed_data
    
    def _generate_touch_areas(self, node):
        """Generate touch-friendly interaction areas."""
        areas = []
        if hasattr(node, 'options') and node.options:
            for i, option in enumerate(node.options):
                areas.append({
                    'id': f"choice_{i}",
                    'type': 'choice',
                    'size': 'large',  # Mobile-friendly size
                    'position': f"bottom_{i}"
                })
        return areas
    
    def _generate_swipe_actions(self, node):
        """Generate swipe gesture mappings."""
        actions = {
            'swipe_up': 'show_inventory',
            'swipe_down': 'show_stats', 
            'swipe_left': 'previous_choice',
            'swipe_right': 'next_choice'
        }
        
        if hasattr(node, 'options') and len(node.options) == 1:
            actions['swipe_left'] = 'select_choice_0'
            
        return actions
    
    def _get_swipe_direction(self, choice_index):
        """Get swipe direction for choice selection."""
        directions = ['up', 'right', 'down', 'left']
        return directions[choice_index % len(directions)]
    
    def _generate_enhanced_html(self, dialogue_data):
        """Generate enhanced HTML with mobile-responsive features."""
        # Prepare all game data
        game_data = {
            'dialogue': dialogue_data,
            'player': {
                'stats': self.app.player_stats,
                'inventory': self.app.player_inventory
            },
            'flags': self.app.story_flags,
            'variables': getattr(self.app, 'variables', {}),
            'quests': {qid: q.to_dict() for qid, q in self.app.quests.items()},
            'settings': self.mobile_settings
        }
        
        font_name = self.app.project_settings.get("font", "Merriweather")
        title_font_name = self.app.project_settings.get("title_font", "Special Elite")
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, maximum-scale=1.0, minimum-scale=1.0">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#232526">
    <title>Enhanced DVG Adventure</title>
    
    <!-- PWA Manifest -->
    {self._generate_manifest_link() if self.mobile_settings.get('pwa_support') else ''}
    
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family={font_name.replace(' ', '+')}:ital,wght@0,400;0,700;1,400&family={title_font_name.replace(' ', '+')}:wght@400;700&display=swap" rel="stylesheet">
    
    <!-- Icons -->
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    
    <style>
        {self._generate_enhanced_css(font_name, title_font_name)}
    </style>
</head>
<body>
    <div id="game-container" class="game-container">
        <!-- Loading Screen -->
        <div id="loading-screen" class="loading-screen">
            <div class="loading-spinner"></div>
            <p>Loading your adventure...</p>
        </div>
        
        <!-- Game Interface -->
        <div id="game-interface" class="game-interface hidden">
            <!-- Header Bar -->
            <header class="header-bar">
                <div class="header-left">
                    <button id="menu-btn" class="icon-btn" aria-label="Menu">
                        <i class="ph ph-list"></i>
                    </button>
                    <h1 class="game-title">Adventure</h1>
                </div>
                <div class="header-right">
                    <button id="fullscreen-btn" class="icon-btn" aria-label="Fullscreen">
                        <i class="ph ph-arrows-out"></i>
                    </button>
                    <button id="theme-btn" class="icon-btn" aria-label="Toggle Theme">
                        <i class="ph ph-moon"></i>
                    </button>
                </div>
            </header>
            
            <!-- Main Game Area -->
            <main class="main-content">
                <div class="background-container" id="background-container"></div>
                
                <!-- Dialogue Area -->
                <div class="dialogue-container">
                    <div class="speaker-info">
                        <div class="speaker-avatar" id="speaker-avatar"></div>
                        <h2 class="speaker-name" id="speaker-name">Narrator</h2>
                    </div>
                    <div class="dialogue-text" id="dialogue-text">
                        Welcome to your enhanced mobile adventure!
                    </div>
                    <div class="text-indicator" id="text-indicator">
                        <i class="ph ph-caret-down"></i>
                    </div>
                </div>
                
                <!-- Choice Buttons -->
                <div class="choices-container" id="choices-container"></div>
                
                <!-- HUD Elements -->
                <div class="hud-elements">
                    <!-- Stats Panel -->
                    <div class="hud-panel stats-panel" id="stats-panel">
                        <h3>Stats</h3>
                        <div class="stats-grid" id="stats-grid"></div>
                    </div>
                    
                    <!-- Inventory Panel -->
                    <div class="hud-panel inventory-panel" id="inventory-panel">
                        <h3>Inventory</h3>
                        <div class="inventory-grid" id="inventory-grid"></div>
                    </div>
                </div>
            </main>
            
            <!-- Bottom Navigation -->
            <nav class="bottom-nav">
                <button class="nav-btn" id="stats-btn">
                    <i class="ph ph-user"></i>
                    <span>Stats</span>
                </button>
                <button class="nav-btn" id="inventory-btn">
                    <i class="ph ph-backpack"></i>
                    <span>Items</span>
                </button>
                <button class="nav-btn" id="quests-btn">
                    <i class="ph ph-scroll"></i>
                    <span>Quests</span>
                </button>
                <button class="nav-btn" id="save-btn">
                    <i class="ph ph-floppy-disk"></i>
                    <span>Save</span>
                </button>
            </nav>
        </div>
        
        <!-- Mobile Menu Overlay -->
        <div id="menu-overlay" class="menu-overlay hidden">
            <div class="menu-content">
                <button class="menu-close" id="menu-close">
                    <i class="ph ph-x"></i>
                </button>
                <div class="menu-items">
                    <button class="menu-item" id="save-game-btn">
                        <i class="ph ph-floppy-disk"></i>
                        Save Game
                    </button>
                    <button class="menu-item" id="load-game-btn">
                        <i class="ph ph-folder-open"></i>
                        Load Game
                    </button>
                    <button class="menu-item" id="settings-btn">
                        <i class="ph ph-gear"></i>
                        Settings
                    </button>
                    <button class="menu-item" id="about-btn">
                        <i class="ph ph-info"></i>
                        About
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        {self._generate_enhanced_javascript(game_data)}
    </script>
</body>
</html>'''
    
    def _generate_manifest_link(self):
        """Generate PWA manifest link."""
        return '<link rel="manifest" href="manifest.json">'
    
    def _generate_enhanced_css(self, font_name, title_font_name):
        """Generate enhanced mobile-responsive CSS."""
        return f'''
        :root {{
            /* Fonts */
            --primary-font: "{font_name}", serif;
            --title-font: "{title_font_name}", cursive;
            
            /* Colors - Light Theme */
            --bg-primary: #f5f5f5;
            --bg-secondary: #ffffff;
            --text-primary: #2c3e50;
            --text-secondary: #7f8c8d;
            --accent-color: #3498db;
            --accent-hover: #2980b9;
            --border-color: #e1e1e1;
            --shadow-color: rgba(0,0,0,0.1);
            
            /* Colors - Dark Theme */
            --bg-primary-dark: #1a1a1a;
            --bg-secondary-dark: #2d2d2d;
            --text-primary-dark: #ffffff;
            --text-secondary-dark: #b0b0b0;
            --accent-color-dark: #5dade2;
            --accent-hover-dark: #3498db;
            --border-color-dark: #404040;
            --shadow-color-dark: rgba(0,0,0,0.3);
            
            /* Layout */
            --header-height: 60px;
            --bottom-nav-height: 80px;
            --border-radius: 12px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        /* Dark theme styles */
        [data-theme="dark"] {{
            --bg-primary: var(--bg-primary-dark);
            --bg-secondary: var(--bg-secondary-dark);
            --text-primary: var(--text-primary-dark);
            --text-secondary: var(--text-secondary-dark);
            --accent-color: var(--accent-color-dark);
            --accent-hover: var(--accent-hover-dark);
            --border-color: var(--border-color-dark);
            --shadow-color: var(--shadow-color-dark);
        }}
        
        /* Reset and base styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html, body {{
            height: 100%;
            overflow: hidden;
            font-family: var(--primary-font);
            background: var(--bg-primary);
            color: var(--text-primary);
            transition: var(--transition);
        }}
        
        .game-container {{
            height: 100vh;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }}
        
        /* Loading Screen */
        .loading-screen {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--bg-primary);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }}
        
        .loading-spinner {{
            width: 50px;
            height: 50px;
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--accent-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        /* Header */
        .header-bar {{
            height: var(--header-height);
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            position: relative;
            z-index: 100;
            box-shadow: 0 2px 10px var(--shadow-color);
        }}
        
        .header-left, .header-right {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .game-title {{
            font-family: var(--title-font);
            font-size: 24px;
            font-weight: 700;
            color: var(--text-primary);
        }}
        
        .icon-btn {{
            background: none;
            border: none;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: var(--text-secondary);
            transition: var(--transition);
            font-size: 24px;
        }}
        
        .icon-btn:hover {{
            background: var(--border-color);
            color: var(--accent-color);
            transform: scale(1.05);
        }}
        
        .icon-btn:active {{
            transform: scale(0.95);
        }}
        
        /* Main Content */
        .main-content {{
            flex: 1;
            position: relative;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        
        .background-container {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            transition: var(--transition);
        }}
        
        /* Dialogue Container */
        .dialogue-container {{
            position: relative;
            z-index: 10;
            background: rgba(255,255,255,0.95);
            margin: 20px;
            border-radius: var(--border-radius);
            padding: 30px;
            box-shadow: 0 8px 32px var(--shadow-color);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-color);
            max-height: 60vh;
            overflow-y: auto;
        }}
        
        [data-theme="dark"] .dialogue-container {{
            background: rgba(45,45,45,0.95);
        }}
        
        .speaker-info {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .speaker-avatar {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: var(--accent-color);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 18px;
        }}
        
        .speaker-name {{
            font-family: var(--title-font);
            font-size: 20px;
            color: var(--text-primary);
        }}
        
        .dialogue-text {{
            font-size: 18px;
            line-height: 1.6;
            color: var(--text-primary);
            margin-bottom: 15px;
        }}
        
        .text-indicator {{
            text-align: center;
            color: var(--text-secondary);
            font-size: 20px;
            animation: bounce 2s infinite;
        }}
        
        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
            40% {{ transform: translateY(-10px); }}
            60% {{ transform: translateY(-5px); }}
        }}
        
        /* Choices */
        .choices-container {{
            position: relative;
            z-index: 10;
            padding: 0 20px 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        
        .choice-btn {{
            background: var(--bg-secondary);
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius);
            padding: 20px;
            font-size: 16px;
            font-family: var(--primary-font);
            color: var(--text-primary);
            cursor: pointer;
            transition: var(--transition);
            text-align: left;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 12px var(--shadow-color);
        }}
        
        .choice-btn:hover {{
            border-color: var(--accent-color);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px var(--shadow-color);
        }}
        
        .choice-btn:active {{
            transform: translateY(0);
        }}
        
        .choice-btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: var(--transition);
        }}
        
        .choice-btn:hover::before {{
            left: 100%;
        }}
        
        /* HUD Elements */
        .hud-elements {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 5;
        }}
        
        .hud-panel {{
            position: absolute;
            background: rgba(255,255,255,0.9);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            padding: 20px;
            box-shadow: 0 8px 32px var(--shadow-color);
            backdrop-filter: blur(10px);
            transform: translateY(-100%);
            transition: var(--transition);
            pointer-events: auto;
            max-width: 90vw;
        }}
        
        [data-theme="dark"] .hud-panel {{
            background: rgba(45,45,45,0.9);
        }}
        
        .hud-panel.visible {{
            transform: translateY(0);
        }}
        
        .stats-panel {{
            top: 20px;
            left: 20px;
            min-width: 200px;
        }}
        
        .inventory-panel {{
            top: 20px;
            right: 20px;
            min-width: 200px;
        }}
        
        .hud-panel h3 {{
            font-family: var(--title-font);
            margin-bottom: 15px;
            color: var(--text-primary);
        }}
        
        .stats-grid, .inventory-grid {{
            display: grid;
            gap: 10px;
        }}
        
        .stat-item, .inventory-item {{
            padding: 10px;
            background: var(--bg-primary);
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}
        
        /* Bottom Navigation */
        .bottom-nav {{
            height: var(--bottom-nav-height);
            background: var(--bg-secondary);
            border-top: 1px solid var(--border-color);
            display: flex;
            justify-content: space-around;
            align-items: center;
            padding: 10px 0;
            box-shadow: 0 -2px 10px var(--shadow-color);
        }}
        
        .nav-btn {{
            background: none;
            border: none;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
            cursor: pointer;
            color: var(--text-secondary);
            transition: var(--transition);
            padding: 8px 12px;
            border-radius: 8px;
            min-width: 60px;
        }}
        
        .nav-btn:hover, .nav-btn.active {{
            color: var(--accent-color);
            background: rgba(52, 152, 219, 0.1);
        }}
        
        .nav-btn i {{
            font-size: 24px;
        }}
        
        .nav-btn span {{
            font-size: 12px;
            font-weight: 500;
        }}
        
        /* Menu Overlay */
        .menu-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .menu-content {{
            background: var(--bg-secondary);
            border-radius: var(--border-radius);
            padding: 30px;
            max-width: 400px;
            width: 90%;
            box-shadow: 0 20px 60px var(--shadow-color);
            position: relative;
        }}
        
        .menu-close {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: var(--text-secondary);
            transition: var(--transition);
        }}
        
        .menu-close:hover {{
            color: var(--text-primary);
        }}
        
        .menu-items {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        .menu-item {{
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            display: flex;
            align-items: center;
            gap: 15px;
            cursor: pointer;
            transition: var(--transition);
            font-size: 16px;
            color: var(--text-primary);
        }}
        
        .menu-item:hover {{
            border-color: var(--accent-color);
            background: var(--accent-color);
            color: white;
        }}
        
        .menu-item i {{
            font-size: 20px;
        }}
        
        /* Utility Classes */
        .hidden {{
            display: none !important;
        }}
        
        .fade-in {{
            animation: fadeIn 0.5s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* Touch and Mobile Specific */
        .touch-target {{
            min-height: 44px;
            min-width: 44px;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .dialogue-container {{
                margin: 10px;
                padding: 20px;
            }}
            
            .choices-container {{
                padding: 0 10px 10px;
            }}
            
            .hud-panel {{
                max-width: calc(100vw - 20px);
                left: 10px !important;
                right: 10px !important;
            }}
        }}
        
        @media (max-width: 480px) {{
            .header-bar {{
                padding: 0 15px;
            }}
            
            .game-title {{
                font-size: 20px;
            }}
            
            .dialogue-text {{
                font-size: 16px;
            }}
            
            .choice-btn {{
                padding: 15px;
                font-size: 15px;
            }}
        }}
        '''
    
    def _generate_enhanced_javascript(self, game_data):
        """Generate enhanced JavaScript with mobile features."""
        return f'''
        // Enhanced DVGE Game Engine with Mobile Support
        class EnhancedDVGEngine {{
            constructor() {{
                this.gameData = {json.dumps(game_data, indent=2)};
                this.currentNodeId = 'intro';
                this.gameState = {{
                    player: this.gameData.player,
                    flags: this.gameData.flags,
                    variables: this.gameData.variables,
                    visited: new Set(),
                    darkMode: false,
                    fullscreen: false
                }};
                
                this.touchStartX = 0;
                this.touchStartY = 0;
                this.swipeThreshold = 50;
                this.isAnimating = false;
                
                this.init();
            }}
            
            init() {{
                this.setupEventListeners();
                this.setupTouchControls();
                this.loadGameState();
                this.hideLoadingScreen();
                this.displayNode(this.currentNodeId);
                this.updateHUD();
            }}
            
            setupEventListeners() {{
                // Header buttons
                document.getElementById('menu-btn').addEventListener('click', () => this.toggleMenu());
                document.getElementById('fullscreen-btn').addEventListener('click', () => this.toggleFullscreen());
                document.getElementById('theme-btn').addEventListener('click', () => this.toggleTheme());
                
                // Bottom navigation
                document.getElementById('stats-btn').addEventListener('click', () => this.togglePanel('stats'));
                document.getElementById('inventory-btn').addEventListener('click', () => this.togglePanel('inventory'));
                document.getElementById('quests-btn').addEventListener('click', () => this.showQuests());
                document.getElementById('save-btn').addEventListener('click', () => this.saveGame());
                
                // Menu overlay
                document.getElementById('menu-close').addEventListener('click', () => this.hideMenu());
                document.getElementById('menu-overlay').addEventListener('click', (e) => {{
                    if (e.target.id === 'menu-overlay') this.hideMenu();
                }});
                
                // Menu items
                document.getElementById('save-game-btn').addEventListener('click', () => this.saveGame());
                document.getElementById('load-game-btn').addEventListener('click', () => this.loadGame());
                document.getElementById('settings-btn').addEventListener('click', () => this.showSettings());
                document.getElementById('about-btn').addEventListener('click', () => this.showAbout());
                
                // Keyboard shortcuts
                document.addEventListener('keydown', (e) => this.handleKeyboard(e));
                
                // Prevent context menu on long press
                document.addEventListener('contextmenu', (e) => e.preventDefault());
                
                // Handle viewport changes
                window.addEventListener('resize', () => this.handleResize());
                window.addEventListener('orientationchange', () => {{
                    setTimeout(() => this.handleResize(), 100);
                }});
            }}
            
            setupTouchControls() {{
                const gameContainer = document.getElementById('game-container');
                
                gameContainer.addEventListener('touchstart', (e) => {{
                    this.touchStartX = e.touches[0].clientX;
                    this.touchStartY = e.touches[0].clientY;
                }}, {{ passive: true }});
                
                gameContainer.addEventListener('touchend', (e) => {{
                    if (!e.changedTouches[0]) return;
                    
                    const touchEndX = e.changedTouches[0].clientX;
                    const touchEndY = e.changedTouches[0].clientY;
                    const deltaX = touchEndX - this.touchStartX;
                    const deltaY = touchEndY - this.touchStartY;
                    
                    this.handleSwipeGesture(deltaX, deltaY);
                }}, {{ passive: true }});
                
                // Prevent pull-to-refresh
                document.addEventListener('touchmove', (e) => {{
                    if (e.touches.length > 1) {{
                        e.preventDefault();
                    }}
                }}, {{ passive: false }});
            }}
            
            handleSwipeGesture(deltaX, deltaY) {{
                const absX = Math.abs(deltaX);
                const absY = Math.abs(deltaY);
                
                if (absX < this.swipeThreshold && absY < this.swipeThreshold) return;
                
                if (absX > absY) {{
                    // Horizontal swipe
                    if (deltaX > 0) {{
                        this.handleSwipeRight();
                    }} else {{
                        this.handleSwipeLeft();
                    }}
                }} else {{
                    // Vertical swipe
                    if (deltaY > 0) {{
                        this.handleSwipeDown();
                    }} else {{
                        this.handleSwipeUp();
                    }}
                }}
            }}
            
            handleSwipeUp() {{
                this.togglePanel('inventory');
            }}
            
            handleSwipeDown() {{
                this.togglePanel('stats');
            }}
            
            handleSwipeLeft() {{
                const choices = document.querySelectorAll('.choice-btn');
                if (choices.length === 1) {{
                    choices[0].click();
                }}
            }}
            
            handleSwipeRight() {{
                // Could implement back navigation here
                console.log('Swipe right - could implement back navigation');
            }}
            
            hideLoadingScreen() {{
                setTimeout(() => {{
                    document.getElementById('loading-screen').classList.add('hidden');
                    document.getElementById('game-interface').classList.remove('hidden');
                    document.getElementById('game-interface').classList.add('fade-in');
                }}, 1000);
            }}
            
            displayNode(nodeId) {{
                const node = this.gameData.dialogue[nodeId];
                if (!node) {{
                    console.error('Node not found:', nodeId);
                    return;
                }}
                
                this.currentNodeId = nodeId;
                this.gameState.visited.add(nodeId);
                
                // Update speaker info
                const speakerName = document.getElementById('speaker-name');
                const speakerAvatar = document.getElementById('speaker-avatar');
                speakerName.textContent = node.npc || 'Narrator';
                speakerAvatar.textContent = (node.npc || 'N')[0].toUpperCase();
                
                // Update dialogue text with typewriter effect
                this.typewriterEffect(node.text || '');
                
                // Update background
                this.updateBackground(node);
                
                // Generate choices
                this.generateChoices(node);
                
                // Update HUD
                this.updateHUD();
            }}
            
            typewriterEffect(text) {{
                const dialogueElement = document.getElementById('dialogue-text');
                const indicator = document.getElementById('text-indicator');
                
                dialogueElement.textContent = '';
                indicator.style.opacity = '0';
                
                let i = 0;
                const speed = 30;
                
                const typeNext = () => {{
                    if (i < text.length) {{
                        dialogueElement.textContent += text.charAt(i);
                        i++;
                        setTimeout(typeNext, speed);
                    }} else {{
                        indicator.style.opacity = '1';
                    }}
                }};
                
                typeNext();
            }}
            
            updateBackground(node) {{
                const container = document.getElementById('background-container');
                
                if (node.backgroundImage) {{
                    container.style.backgroundImage = `url('${{node.backgroundImage}}')`;
                }} else if (node.backgroundTheme) {{
                    // Apply theme-based backgrounds
                    container.style.backgroundImage = this.getThemeBackground(node.backgroundTheme);
                }}
            }}
            
            getThemeBackground(theme) {{
                const themes = {{
                    'forest': 'linear-gradient(135deg, #2d5016 0%, #3e6b1f 100%)',
                    'dungeon': 'linear-gradient(135deg, #2c2c2c 0%, #1a1a1a 100%)',
                    'tavern': 'linear-gradient(135deg, #8b4513 0%, #a0522d 100%)',
                    'castle': 'linear-gradient(135deg, #4682b4 0%, #5f9ea0 100%)'
                }};
                return themes[theme] || themes['forest'];
            }}
            
            generateChoices(node) {{
                const container = document.getElementById('choices-container');
                container.innerHTML = '';
                
                if (node.options && node.options.length > 0) {{
                    node.options.forEach((option, index) => {{
                        if (this.shouldShowChoice(option)) {{
                            const button = this.createChoiceButton(option, index);
                            container.appendChild(button);
                        }}
                    }});
                }} else {{
                    // Auto-continue or end game
                    setTimeout(() => {{
                        // Could implement auto-continue logic here
                        console.log('No choices available');
                    }}, 2000);
                }}
            }}
            
            shouldShowChoice(option) {{
                // Implement condition checking logic
                return true; // Simplified for now
            }}
            
            createChoiceButton(option, index) {{
                const button = document.createElement('button');
                button.className = 'choice-btn touch-target';
                button.textContent = option.text || `Choice ${{index + 1}}`;
                
                button.addEventListener('click', () => {{
                    if (this.isAnimating) return;
                    this.selectChoice(option);
                }});
                
                return button;
            }}
            
            selectChoice(option) {{
                this.isAnimating = true;
                
                // Apply choice effects
                this.applyChoiceEffects(option);
                
                // Navigate to next node
                if (option.nextNode) {{
                    setTimeout(() => {{
                        this.displayNode(option.nextNode);
                        this.isAnimating = false;
                    }}, 300);
                }} else {{
                    console.log('No next node specified');
                    this.isAnimating = false;
                }}
            }}
            
            applyChoiceEffects(option) {{
                // Apply stat changes, flag updates, etc.
                if (option.effects) {{
                    // Implement effect system
                    console.log('Applying effects:', option.effects);
                }}
            }}
            
            updateHUD() {{
                this.updateStats();
                this.updateInventory();
            }}
            
            updateStats() {{
                const statsGrid = document.getElementById('stats-grid');
                statsGrid.innerHTML = '';
                
                Object.entries(this.gameState.player.stats).forEach(([key, value]) => {{
                    const statItem = document.createElement('div');
                    statItem.className = 'stat-item';
                    statItem.innerHTML = `
                        <strong>${{key.charAt(0).toUpperCase() + key.slice(1)}}</strong><br>
                        ${{value}}
                    `;
                    statsGrid.appendChild(statItem);
                }});
            }}
            
            updateInventory() {{
                const inventoryGrid = document.getElementById('inventory-grid');
                inventoryGrid.innerHTML = '';
                
                this.gameState.player.inventory.forEach(item => {{
                    const inventoryItem = document.createElement('div');
                    inventoryItem.className = 'inventory-item';
                    inventoryItem.innerHTML = `
                        <strong>${{item.name}}</strong><br>
                        <small>${{item.description}}</small>
                    `;
                    inventoryGrid.appendChild(inventoryItem);
                }});
            }}
            
            togglePanel(panelType) {{
                const panel = document.getElementById(`${{panelType}}-panel`);
                const navBtn = document.getElementById(`${{panelType}}-btn`);
                
                // Close other panels
                document.querySelectorAll('.hud-panel').forEach(p => {{
                    if (p !== panel) p.classList.remove('visible');
                }});
                
                document.querySelectorAll('.nav-btn').forEach(btn => {{
                    if (btn !== navBtn) btn.classList.remove('active');
                }});
                
                // Toggle current panel
                panel.classList.toggle('visible');
                navBtn.classList.toggle('active');
            }}
            
            toggleMenu() {{
                document.getElementById('menu-overlay').classList.toggle('hidden');
            }}
            
            hideMenu() {{
                document.getElementById('menu-overlay').classList.add('hidden');
            }}
            
            toggleFullscreen() {{
                if (!document.fullscreenElement) {{
                    document.documentElement.requestFullscreen();
                    this.gameState.fullscreen = true;
                }} else {{
                    document.exitFullscreen();
                    this.gameState.fullscreen = false;
                }}
            }}
            
            toggleTheme() {{
                const body = document.body;
                const themeBtn = document.getElementById('theme-btn');
                const icon = themeBtn.querySelector('i');
                
                if (body.getAttribute('data-theme') === 'dark') {{
                    body.removeAttribute('data-theme');
                    icon.className = 'ph ph-moon';
                    this.gameState.darkMode = false;
                }} else {{
                    body.setAttribute('data-theme', 'dark');
                    icon.className = 'ph ph-sun';
                    this.gameState.darkMode = true;
                }}
                
                this.saveGameState();
            }}
            
            saveGame() {{
                const saveData = {{
                    currentNodeId: this.currentNodeId,
                    gameState: this.gameState,
                    timestamp: new Date().toISOString()
                }};
                
                localStorage.setItem('dvge_save', JSON.stringify(saveData));
                this.showNotification('Game saved successfully!');
            }}
            
            loadGame() {{
                const savedData = localStorage.getItem('dvge_save');
                if (savedData) {{
                    try {{
                        const data = JSON.parse(savedData);
                        this.currentNodeId = data.currentNodeId;
                        this.gameState = data.gameState;
                        this.displayNode(this.currentNodeId);
                        this.showNotification('Game loaded successfully!');
                        this.hideMenu();
                    }} catch (e) {{
                        this.showNotification('Failed to load game!', 'error');
                    }}
                }} else {{
                    this.showNotification('No saved game found!', 'error');
                }}
            }}
            
            saveGameState() {{
                localStorage.setItem('dvge_settings', JSON.stringify({{
                    darkMode: this.gameState.darkMode,
                    fullscreen: this.gameState.fullscreen
                }}));
            }}
            
            loadGameState() {{
                const settings = localStorage.getItem('dvge_settings');
                if (settings) {{
                    try {{
                        const data = JSON.parse(settings);
                        if (data.darkMode) {{
                            document.body.setAttribute('data-theme', 'dark');
                            document.querySelector('#theme-btn i').className = 'ph ph-sun';
                            this.gameState.darkMode = true;
                        }}
                    }} catch (e) {{
                        console.error('Failed to load settings:', e);
                    }}
                }}
            }}
            
            showNotification(message, type = 'success') {{
                // Create notification element
                const notification = document.createElement('div');
                notification.className = `notification notification-${{type}}`;
                notification.textContent = message;
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: var(--${{type === 'success' ? 'accent-color' : 'error-color'}});
                    color: white;
                    padding: 15px 20px;
                    border-radius: 8px;
                    z-index: 10000;
                    box-shadow: 0 4px 12px var(--shadow-color);
                    animation: slideInRight 0.3s ease;
                `;
                
                document.body.appendChild(notification);
                
                setTimeout(() => {{
                    notification.style.animation = 'slideOutRight 0.3s ease';
                    setTimeout(() => notification.remove(), 300);
                }}, 3000);
            }}
            
            handleKeyboard(e) {{
                switch (e.key) {{
                    case 'Escape':
                        this.hideMenu();
                        break;
                    case 'F11':
                        e.preventDefault();
                        this.toggleFullscreen();
                        break;
                    case 'Tab':
                        e.preventDefault();
                        this.toggleTheme();
                        break;
                }}
            }}
            
            handleResize() {{
                // Handle responsive adjustments
                const vh = window.innerHeight * 0.01;
                document.documentElement.style.setProperty('--vh', `${{vh}}px`);
            }}
            
            showQuests() {{
                this.showNotification('Quests feature coming soon!');
            }}
            
            showSettings() {{
                this.showNotification('Settings feature coming soon!');
                this.hideMenu();
            }}
            
            showAbout() {{
                this.showNotification('Created with Enhanced DVGE');
                this.hideMenu();
            }}
        }}
        
        // Add notification animations CSS
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {{
                from {{
                    transform: translateX(100%);
                    opacity: 0;
                }}
                to {{
                    transform: translateX(0);
                    opacity: 1;
                }}
            }}
            
            @keyframes slideOutRight {{
                from {{
                    transform: translateX(0);
                    opacity: 1;
                }}
                to {{
                    transform: translateX(100%);
                    opacity: 0;
                }}
            }}
        `;
        document.head.appendChild(style);
        
        // Initialize the game when DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {{
            window.game = new EnhancedDVGEngine();
        }});
        '''
    
    def _generate_pwa_manifest(self, html_file_path):
        """Generate PWA manifest file."""
        manifest_path = html_file_path.replace('.html', '_manifest.json')
        
        manifest = {
            "name": "Enhanced DVG Adventure",
            "short_name": "DVG Adventure",
            "description": "An enhanced dialogue venture game with mobile support",
            "start_url": "./",
            "display": "standalone",
            "orientation": "portrait-primary",
            "theme_color": "#232526",
            "background_color": "#f5f5f5",
            "icons": [
                {
                    "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 192 192'%3E%3Cpath fill='%23232526' d='M0 0h192v192H0z'/%3E%3Ctext x='96' y='96' font-family='serif' font-size='64' text-anchor='middle' dy='0.35em' fill='white'%3EDVG%3C/text%3E%3C/svg%3E",
                    "sizes": "192x192",
                    "type": "image/svg+xml"
                }
            ],
            "categories": ["games", "entertainment"],
            "shortcuts": [
                {
                    "name": "New Game",
                    "short_name": "New",
                    "description": "Start a new adventure",
                    "url": "./?action=new"
                }
            ]
        }
        
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not create PWA manifest: {e}")