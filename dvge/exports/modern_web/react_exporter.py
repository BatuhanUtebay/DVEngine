"""React-based Modern Web Exporter for DVGE."""

import json
import os
import base64
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Dict, Any, Optional, List

from ...core.variable_system import VariableSystem


class ReactExporter:
    """Exports DVGE projects as modern React-based Progressive Web Apps."""
    
    def __init__(self, app):
        """Initialize the React exporter."""
        self.app = app
        self.style_settings = None
        
        # Get the template directory
        self.template_dir = Path(__file__).parent / "templates"
        
    def export_game(self, export_type: str = "pwa") -> bool:
        """Export the current project as a modern web app.
        
        Args:
            export_type: Type of export ('pwa', 'spa', 'static')
        """
        if not self.app.nodes:
            messagebox.showwarning("Export Error", "Cannot export an empty project.")
            return False
            
        # Apply any saved style settings
        if hasattr(self.app, 'html_export_settings') and self.app.html_export_settings:
            self.style_settings = self.app.html_export_settings
            
        # Validate project
        if not self._validate_project():
            return False
            
        try:
            # Process all game data
            game_data = self._process_game_data()
            
            # Choose output directory
            output_dir = filedialog.askdirectory(title="Choose Export Directory")
            if not output_dir:
                return False
                
            project_name = self.app.project_settings.get("title", "DVGE Game").replace(" ", "_")
            export_path = Path(output_dir) / f"{project_name}_modern"
            
            # Create export structure
            self._create_export_structure(export_path, game_data, export_type)
            
            messagebox.showinfo(
                "Export Successful", 
                f"Modern web game exported to: {export_path}\\n\\n"
                f"Open index.html in your browser to play!"
            )
            return True
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export game: {e}")
            return False
            
    def _validate_project(self) -> bool:
        """Validate the project before export."""
        errors, warnings = self.app.validator.validate_project()
        
        if errors or warnings:
            message = "Project validation found issues:\\n\\n"
            if errors:
                message += "ERRORS (must be fixed):\\n" + "\\n".join(errors) + "\\n\\n"
            if warnings:
                message += "WARNINGS (can be ignored):\\n" + "\\n".join(warnings) + "\\n\\n"
                
            if errors:
                messagebox.showerror("Validation Errors", message)
                return False
                
            if not messagebox.askyesno("Validation Warnings", message + "Continue with export anyway?"):
                return False
                
        return True
        
    def _process_game_data(self) -> Dict[str, Any]:
        """Process all game data for React export."""
        # Initialize variable system
        temp_var_system = VariableSystem()
        temp_var_system.set_variables_ref(getattr(self.app, 'variables', {}))
        temp_var_system.set_flags_ref(self.app.story_flags)
        
        # Process nodes with media embedding
        nodes_data = {}
        media_assets = {}
        
        for node_id, node in self.app.nodes.items():
            node_dict = node.to_dict()
            game_data = node_dict['game_data']
            game_data['node_type'] = node_dict['node_type']
            
            # Process and extract media assets
            game_data, node_assets = self._process_node_media(game_data, node_id)
            media_assets.update(node_assets)
            
            nodes_data[node_id] = game_data
            
        # Compile complete game data
        return {
            "metadata": {
                "title": self.app.project_settings.get("title", "Untitled Game"),
                "description": self.app.project_settings.get("description", "A DVGE interactive story"),
                "author": self.app.project_settings.get("author", "Unknown"),
                "version": "1.0.0",
                "created_with": "Dialogue Venture Game Engine",
                "export_timestamp": self._get_timestamp(),
                "starting_node": self._find_starting_node()
            },
            "theme": {
                "primary_font": self.app.project_settings.get("font", "Inter"),
                "title_font": self.app.project_settings.get("title_font", "Inter"),
                "background": self.app.project_settings.get("background", ""),
                "color_scheme": self._get_color_scheme()
            },
            "nodes": nodes_data,
            "game_state": {
                "player_stats": self.app.player_stats,
                "player_inventory": self.app.player_inventory,
                "story_flags": self.app.story_flags,
                "variables": getattr(self.app, 'variables', {}),
                "quests": {qid: q.to_dict() for qid, q in self.app.quests.items()},
                "enemies": {eid: e.to_dict() for eid, e in getattr(self.app, 'enemies', {}).items()},
                "timers": {tid: t.to_dict() for tid, t in getattr(self.app, 'timers', {}).items()}
            },
            "features": {
                "reputation": getattr(self.app, 'reputation_data', {}),
                "loot_tables": getattr(self.app, 'loot_tables', {}),
                "skill_modifiers": getattr(self.app, 'skill_modifiers', {}),
                "active_puzzles": getattr(self.app, 'active_puzzles', {}),
                "minigame_results": getattr(self.app, 'minigame_results', {})
            },
            "media_assets": media_assets,
            "systems": self._get_system_configs()
        }
        
    def _process_node_media(self, game_data: Dict[str, Any], node_id: str) -> tuple[Dict[str, Any], Dict[str, str]]:
        """Process media assets for a node, returning processed data and asset references."""
        assets = {}
        
        # Process background image
        if game_data.get('backgroundImage') and os.path.exists(game_data['backgroundImage']):
            asset_id = f"bg_{node_id}_{hash(game_data['backgroundImage']) % 10000}"
            assets[asset_id] = self._encode_asset(game_data['backgroundImage'])
            game_data['backgroundImage'] = asset_id
            
        # Process audio
        if game_data.get('audio') and os.path.exists(game_data['audio']):
            asset_id = f"audio_{node_id}_{hash(game_data['audio']) % 10000}"
            assets[asset_id] = self._encode_asset(game_data['audio'])
            game_data['audio'] = asset_id
            
        # Process music
        if game_data.get('music') and os.path.exists(game_data['music']):
            asset_id = f"music_{node_id}_{hash(game_data['music']) % 10000}"
            assets[asset_id] = self._encode_asset(game_data['music'])
            game_data['music'] = asset_id
            
        return game_data, assets
        
    def _encode_asset(self, file_path: str) -> str:
        """Encode a media asset as base64 data URI."""
        try:
            with open(file_path, "rb") as f:
                encoded_string = base64.b64encode(f.read()).decode('utf-8')
                
            ext = os.path.splitext(file_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                '.png': 'image/png', '.gif': 'image/gif',
                '.mp3': 'audio/mpeg', '.wav': 'audio/wav',
                '.ogg': 'audio/ogg', '.m4a': 'audio/mp4'
            }
            
            mime_type = mime_types.get(ext, 'application/octet-stream')
            return f"data:{mime_type};base64,{encoded_string}"
            
        except Exception as e:
            print(f"Could not encode asset {file_path}: {e}")
            return ""
            
    def _find_starting_node(self) -> str:
        """Find the starting node ID."""
        # Look for node with no incoming connections or explicit start marker
        for node_id, node in self.app.nodes.items():
            node_dict = node.to_dict()
            if node_dict.get('game_data', {}).get('starting_node', False):
                return node_id
                
        # Fallback to first node
        return list(self.app.nodes.keys())[0] if self.app.nodes else ""
        
    def _get_color_scheme(self) -> Dict[str, str]:
        """Get color scheme from style settings or defaults."""
        if self.style_settings:
            return {
                "primary": self.style_settings.get("primary_color", "#2563eb"),
                "secondary": self.style_settings.get("secondary_color", "#64748b"),
                "background": self.style_settings.get("background_color", "#ffffff"),
                "text": self.style_settings.get("text_color", "#1f2937"),
                "accent": self.style_settings.get("accent_color", "#f59e0b")
            }
        return {
            "primary": "#2563eb",
            "secondary": "#64748b", 
            "background": "#ffffff",
            "text": "#1f2937",
            "accent": "#f59e0b"
        }
        
    def _get_system_configs(self) -> Dict[str, Any]:
        """Get configuration for various game systems."""
        return {
            "portrait_system": getattr(self.app, 'portrait_manager', None).to_dict() if hasattr(self.app, 'portrait_manager') and self.app.portrait_manager else {},
            "music_system": getattr(self.app, 'music_engine', None).to_dict() if hasattr(self.app, 'music_engine') and self.app.music_engine else {},
            "media_library": getattr(self.app, 'media_library', None).to_dict() if hasattr(self.app, 'media_library') and self.app.media_library else {},
            "voice_system": getattr(self.app, 'voice_manager', None).export_voice_data_for_html() if hasattr(self.app, 'voice_manager') and self.app.voice_manager else {}
        }
        
    def _get_timestamp(self) -> str:
        """Get current timestamp for export metadata."""
        from datetime import datetime
        return datetime.now().isoformat()
        
    def _create_export_structure(self, export_path: Path, game_data: Dict[str, Any], export_type: str):
        """Create the complete export directory structure."""
        export_path.mkdir(exist_ok=True)
        
        # Create directory structure
        (export_path / "src").mkdir(exist_ok=True)
        (export_path / "src" / "components").mkdir(exist_ok=True)
        (export_path / "src" / "hooks").mkdir(exist_ok=True)
        (export_path / "src" / "utils").mkdir(exist_ok=True)
        (export_path / "public").mkdir(exist_ok=True)
        
        # Write game data
        with open(export_path / "src" / "gameData.json", "w", encoding="utf-8") as f:
            json.dump(game_data, f, indent=2)
            
        # Generate all template files
        self._generate_package_json(export_path, game_data)
        self._generate_index_html(export_path, game_data)
        self._generate_react_app(export_path, game_data)
        self._generate_pwa_files(export_path, game_data) if export_type == "pwa" else None
        self._generate_build_config(export_path, export_type)
        
    def _generate_package_json(self, export_path: Path, game_data: Dict[str, Any]):
        """Generate package.json for the React app."""
        package_json = {
            "name": game_data["metadata"]["title"].lower().replace(" ", "-"),
            "version": "1.0.0",
            "description": game_data["metadata"]["description"],
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "eslintConfig": {
                "extends": ["react-app", "react-app/jest"]
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        }
        
        with open(export_path / "package.json", "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2)
            
    def _generate_index_html(self, export_path: Path, game_data: Dict[str, Any]):
        """Generate the main HTML file."""
        metadata = game_data["metadata"]
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="{game_data["theme"]["color_scheme"]["primary"]}" />
    <meta name="description" content="{metadata["description"]}" />
    <meta name="author" content="{metadata["author"]}" />
    
    <title>{metadata["title"]}</title>
    
    <!-- PWA manifest -->
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    
    <!-- Apple PWA support -->
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-status-bar-style" content="default" />
    <meta name="apple-mobile-web-app-title" content="{metadata["title"]}" />
    
    <!-- Favicon -->
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        body {{
            margin: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            background-color: {game_data["theme"]["color_scheme"]["background"]};
            color: {game_data["theme"]["color_scheme"]["text"]};
        }}
        
        #root {{
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        .loading {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-size: 1.2rem;
            color: {game_data["theme"]["color_scheme"]["secondary"]};
        }}
    </style>
</head>
<body>
    <noscript>You need to enable JavaScript to play this interactive story.</noscript>
    <div id="root">
        <div class="loading">Loading your interactive story...</div>
    </div>
    
    <!-- Service Worker Registration -->
    <script>
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => console.log('SW registered'))
                    .catch(error => console.log('SW registration failed'));
            }});
        }}
    </script>
</body>
</html>'''
        
        with open(export_path / "public" / "index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
    def _generate_react_app(self, export_path: Path, game_data: Dict[str, Any]):
        """Generate the main React application files."""
        # Generate App.js
        self._generate_app_component(export_path, game_data)
        
        # Generate core components
        self._generate_story_player(export_path, game_data)
        self._generate_ui_components(export_path, game_data)
        
        # Generate hooks and utilities
        self._generate_game_hooks(export_path)
        self._generate_utilities(export_path)
        
        # Generate index.js
        self._generate_index_js(export_path)
        
    def _generate_app_component(self, export_path: Path, game_data: Dict[str, Any]):
        """Generate the main App component."""
        app_js = '''import React from 'react';
import StoryPlayer from './components/StoryPlayer';
import gameData from './gameData.json';
import './App.css';

function App() {
  return (
    <div className="App">
      <StoryPlayer gameData={gameData} />
    </div>
  );
}

export default App;'''

        with open(export_path / "src" / "App.js", "w", encoding="utf-8") as f:
            f.write(app_js)
            
        # Generate App.css
        theme = game_data["theme"]
        colors = theme["color_scheme"]
        
        app_css = f''':root {{
  --primary-color: {colors["primary"]};
  --secondary-color: {colors["secondary"]};
  --background-color: {colors["background"]};
  --text-color: {colors["text"]};
  --accent-color: {colors["accent"]};
  --primary-font: '{theme["primary_font"]}', -apple-system, BlinkMacSystemFont, sans-serif;
  --title-font: '{theme["title_font"]}', serif;
}}

.App {{
  min-height: 100vh;
  background-color: var(--background-color);
  color: var(--text-color);
  font-family: var(--primary-font);
}}

/* Mobile-first responsive design */
@media (max-width: 768px) {{
  .App {{
    padding: 0;
  }}
}}

/* Dark mode support */
@media (prefers-color-scheme: dark) {{
  :root {{
    --background-color: #0f172a;
    --text-color: #f8fafc;
    --secondary-color: #64748b;
  }}
}}'''

        with open(export_path / "src" / "App.css", "w", encoding="utf-8") as f:
            f.write(app_css)
            
    def _generate_story_player(self, export_path: Path, game_data: Dict[str, Any]):
        """Generate the main StoryPlayer component."""
        story_player_js = '''import React, { useState, useEffect } from 'react';
import { useGameState } from '../hooks/useGameState';
import { useAudioSystem } from '../hooks/useAudioSystem';
import StoryNode from './StoryNode';
import GameHUD from './GameHUD';
import SaveSystem from './SaveSystem';
import './StoryPlayer.css';

const StoryPlayer = ({ gameData }) => {
  const {
    gameState,
    currentNode,
    updateGameState,
    goToNode,
    canGoToNode
  } = useGameState(gameData);
  
  const { playAudio, playMusic, stopMusic } = useAudioSystem();
  
  const [isLoading, setIsLoading] = useState(true);
  const [showSaveMenu, setShowSaveMenu] = useState(false);
  
  useEffect(() => {
    // Initialize game
    const startingNode = gameData.metadata.starting_node;
    if (startingNode && gameData.nodes[startingNode]) {
      goToNode(startingNode);
    }
    setIsLoading(false);
  }, [gameData, goToNode]);
  
  const handleChoice = (choiceId, targetNodeId) => {
    const choice = currentNode?.choices?.find(c => c.id === choiceId);
    if (!choice) return;
    
    // Process choice effects
    if (choice.effects) {
      updateGameState(choice.effects);
    }
    
    // Play choice audio if available
    if (choice.audio) {
      playAudio(choice.audio);
    }
    
    // Navigate to target node
    if (canGoToNode(targetNodeId)) {
      goToNode(targetNodeId);
    }
  };
  
  if (isLoading) {
    return (
      <div className="story-player loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading your story...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="story-player">
      <GameHUD 
        gameState={gameState}
        onSaveClick={() => setShowSaveMenu(true)}
      />
      
      <main className="story-content">
        {currentNode && (
          <StoryNode
            node={currentNode}
            gameState={gameState}
            onChoice={handleChoice}
            mediaAssets={gameData.media_assets}
          />
        )}
      </main>
      
      {showSaveMenu && (
        <SaveSystem
          gameState={gameState}
          currentNodeId={currentNode?.id}
          onClose={() => setShowSaveMenu(false)}
        />
      )}
    </div>
  );
};

export default StoryPlayer;'''

        with open(export_path / "src" / "components" / "StoryPlayer.js", "w", encoding="utf-8") as f:
            f.write(story_player_js)
            
        # Generate StoryPlayer.css
        story_player_css = '''.story-player {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
}

.story-player.loading {
  justify-content: center;
  align-items: center;
}

.loading-spinner {
  text-align: center;
  padding: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--secondary-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.story-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
  width: 100%;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .story-content {
    padding: 0.5rem;
  }
}

/* Touch-friendly interactions */
@media (max-width: 768px) {
  .story-player {
    -webkit-overflow-scrolling: touch;
  }
}'''

        with open(export_path / "src" / "components" / "StoryPlayer.css", "w", encoding="utf-8") as f:
            f.write(story_player_css)
            
    def _generate_ui_components(self, export_path: Path, game_data: Dict[str, Any]):
        """Generate UI components."""
        components_to_generate = [
            ("StoryNode", self._get_story_node_component()),
            ("GameHUD", self._get_game_hud_component()),
            ("SaveSystem", self._get_save_system_component()),
            ("ChoiceButton", self._get_choice_button_component())
        ]
        
        for component_name, component_code in components_to_generate:
            with open(export_path / "src" / "components" / f"{component_name}.js", "w", encoding="utf-8") as f:
                f.write(component_code)
                
    def _generate_game_hooks(self, export_path: Path):
        """Generate React hooks for game logic."""
        hooks_to_generate = [
            ("useGameState", self._get_game_state_hook()),
            ("useAudioSystem", self._get_audio_system_hook()),
            ("useLocalStorage", self._get_local_storage_hook())
        ]
        
        for hook_name, hook_code in hooks_to_generate:
            with open(export_path / "src" / "hooks" / f"{hook_name}.js", "w", encoding="utf-8") as f:
                f.write(hook_code)
                
    def _generate_utilities(self, export_path: Path):
        """Generate utility functions."""
        utilities = [
            ("gameEngine", self._get_game_engine_utils()),
            ("mediaUtils", self._get_media_utils()),
            ("saveUtils", self._get_save_utils())
        ]
        
        for util_name, util_code in utilities:
            with open(export_path / "src" / "utils" / f"{util_name}.js", "w", encoding="utf-8") as f:
                f.write(util_code)
                
    def _generate_index_js(self, export_path: Path):
        """Generate the main index.js file."""
        index_js = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);'''

        with open(export_path / "src" / "index.js", "w", encoding="utf-8") as f:
            f.write(index_js)
            
        # Generate index.css
        index_css = '''* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: var(--primary-font);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--background-color);
  color: var(--text-color);
  line-height: 1.6;
}

html {
  scroll-behavior: smooth;
}

/* Reset and base styles */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--title-font);
  margin: 0 0 1rem 0;
  font-weight: 600;
}

p {
  margin: 0 0 1rem 0;
}

button {
  font-family: inherit;
  cursor: pointer;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  padding: 0.75rem 1.5rem;
  transition: all 0.2s ease;
}

button:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  :root {
    --primary-color: #0000ff;
    --text-color: #000000;
    --background-color: #ffffff;
  }
}'''

        with open(export_path / "src" / "index.css", "w", encoding="utf-8") as f:
            f.write(index_css)
            
    def _generate_pwa_files(self, export_path: Path, game_data: Dict[str, Any]):
        """Generate PWA manifest and service worker."""
        metadata = game_data["metadata"]
        
        # Generate manifest.json
        manifest = {
            "name": metadata["title"],
            "short_name": metadata["title"][:12],
            "description": metadata["description"],
            "start_url": "./",
            "display": "standalone",
            "theme_color": game_data["theme"]["color_scheme"]["primary"],
            "background_color": game_data["theme"]["color_scheme"]["background"],
            "orientation": "portrait-primary",
            "icons": [
                {
                    "src": "favicon.ico",
                    "sizes": "64x64 32x32 24x24 16x16",
                    "type": "image/x-icon"
                },
                {
                    "src": "logo192.png",
                    "type": "image/png",
                    "sizes": "192x192"
                },
                {
                    "src": "logo512.png",
                    "type": "image/png", 
                    "sizes": "512x512"
                }
            ]
        }
        
        with open(export_path / "public" / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
            
        # Generate service worker
        service_worker = '''const CACHE_NAME = 'dvge-game-v1';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json'
];

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

// Fetch event
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      })
  );
});'''

        with open(export_path / "public" / "sw.js", "w", encoding="utf-8") as f:
            f.write(service_worker)
            
    def _generate_build_config(self, export_path: Path, export_type: str):
        """Generate build configuration files."""
        # Generate README.md
        readme = f'''# DVGE Game Export

This is a modern web export of a game created with Dialogue Venture Game Engine.

## Development

To run the development server:

```bash
npm install
npm start
```

## Building for Production

To create a production build:

```bash
npm run build
```

## Deployment

The built files will be in the `build` directory. You can deploy these to any web server.

### PWA Features

This game includes Progressive Web App features:
- Offline support
- Install as app on mobile devices
- Responsive design
- Touch-friendly controls

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Generated by DVGE

This game was exported using the Dialogue Venture Game Engine modern web exporter.
'''

        with open(export_path / "README.md", "w", encoding="utf-8") as f:
            f.write(readme)
            
        # Generate .gitignore
        gitignore = '''# Dependencies
node_modules/
/.pnp
.pnp.js

# Testing
/coverage

# Production
/build

# Environment
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime
.DS_Store
Thumbs.db
'''

        with open(export_path / ".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore)
            
    # Component and hook templates (simplified for brevity)
    def _get_story_node_component(self) -> str:
        return '''import React, { useState, useEffect } from 'react';
import ChoiceButton from './ChoiceButton';
import './StoryNode.css';

const StoryNode = ({ node, gameState, onChoice, mediaAssets }) => {
  const [displayText, setDisplayText] = useState('');
  const [showChoices, setShowChoices] = useState(false);
  
  useEffect(() => {
    // Typewriter effect
    let index = 0;
    const text = node.text || '';
    setDisplayText('');
    setShowChoices(false);
    
    const timer = setInterval(() => {
      if (index < text.length) {
        setDisplayText(text.slice(0, index + 1));
        index++;
      } else {
        clearInterval(timer);
        setTimeout(() => setShowChoices(true), 500);
      }
    }, 30);
    
    return () => clearInterval(timer);
  }, [node]);
  
  const backgroundImage = node.backgroundImage && mediaAssets[node.backgroundImage];
  
  return (
    <div className="story-node" style={{
      backgroundImage: backgroundImage ? `url(${backgroundImage})` : 'none'
    }}>
      <div className="story-content">
        <div className="text-container">
          <p className="story-text">{displayText}</p>
        </div>
        
        {showChoices && node.choices && (
          <div className="choices-container">
            {node.choices.map((choice) => (
              <ChoiceButton
                key={choice.id}
                choice={choice}
                onClick={() => onChoice(choice.id, choice.target)}
                disabled={!choice.enabled}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StoryNode;'''

    def _get_game_hud_component(self) -> str:
        return '''import React from 'react';
import './GameHUD.css';

const GameHUD = ({ gameState, onSaveClick }) => {
  return (
    <header className="game-hud">
      <div className="hud-left">
        <div className="player-stats">
          {Object.entries(gameState.player_stats).map(([stat, value]) => (
            <div key={stat} className="stat">
              <span className="stat-name">{stat}:</span>
              <span className="stat-value">{value}</span>
            </div>
          ))}
        </div>
      </div>
      
      <div className="hud-right">
        <button className="save-button" onClick={onSaveClick}>
          Save
        </button>
      </div>
    </header>
  );
};

export default GameHUD;'''

    def _get_save_system_component(self) -> str:
        return '''import React, { useState } from 'react';
import { saveGame, loadGame, getSavedGames } from '../utils/saveUtils';
import './SaveSystem.css';

const SaveSystem = ({ gameState, currentNodeId, onClose }) => {
  const [saves] = useState(() => getSavedGames());
  const [newSaveName, setNewSaveName] = useState('');
  
  const handleSave = () => {
    if (newSaveName.trim()) {
      saveGame(newSaveName, { gameState, currentNodeId });
      onClose();
    }
  };
  
  const handleLoad = (saveData) => {
    loadGame(saveData);
    onClose();
  };
  
  return (
    <div className="save-system-overlay">
      <div className="save-system">
        <h2>Save & Load</h2>
        
        <div className="save-section">
          <h3>Save Game</h3>
          <input
            type="text"
            placeholder="Enter save name..."
            value={newSaveName}
            onChange={(e) => setNewSaveName(e.target.value)}
          />
          <button onClick={handleSave}>Save</button>
        </div>
        
        <div className="load-section">
          <h3>Load Game</h3>
          {saves.length === 0 ? (
            <p>No saved games found.</p>
          ) : (
            saves.map((save) => (
              <div key={save.id} className="save-slot">
                <span>{save.name}</span>
                <span>{save.date}</span>
                <button onClick={() => handleLoad(save)}>Load</button>
              </div>
            ))
          )}
        </div>
        
        <button className="close-button" onClick={onClose}>Close</button>
      </div>
    </div>
  );
};

export default SaveSystem;'''

    def _get_choice_button_component(self) -> str:
        return '''import React from 'react';
import './ChoiceButton.css';

const ChoiceButton = ({ choice, onClick, disabled }) => {
  return (
    <button
      className={`choice-button ${disabled ? 'disabled' : ''}`}
      onClick={onClick}
      disabled={disabled}
    >
      {choice.text}
    </button>
  );
};

export default ChoiceButton;'''

    def _get_game_state_hook(self) -> str:
        return '''import { useState, useCallback } from 'react';

export const useGameState = (gameData) => {
  const [gameState, setGameState] = useState(gameData.game_state);
  const [currentNodeId, setCurrentNodeId] = useState(null);
  
  const currentNode = currentNodeId ? gameData.nodes[currentNodeId] : null;
  
  const updateGameState = useCallback((effects) => {
    setGameState(prevState => {
      const newState = { ...prevState };
      
      // Process effects
      if (effects.stats) {
        Object.assign(newState.player_stats, effects.stats);
      }
      
      if (effects.inventory) {
        newState.player_inventory = [...newState.player_inventory, ...effects.inventory];
      }
      
      if (effects.flags) {
        Object.assign(newState.story_flags, effects.flags);
      }
      
      return newState;
    });
  }, []);
  
  const goToNode = useCallback((nodeId) => {
    if (gameData.nodes[nodeId]) {
      setCurrentNodeId(nodeId);
    }
  }, [gameData.nodes]);
  
  const canGoToNode = useCallback((nodeId) => {
    // Add conditions checking logic here
    return gameData.nodes[nodeId] != null;
  }, [gameData.nodes]);
  
  return {
    gameState,
    currentNode,
    updateGameState,
    goToNode,
    canGoToNode
  };
};'''

    def _get_audio_system_hook(self) -> str:
        return '''import { useCallback } from 'react';

export const useAudioSystem = () => {
  const playAudio = useCallback((audioSrc) => {
    if (audioSrc) {
      const audio = new Audio(audioSrc);
      audio.play().catch(e => console.log('Audio play failed:', e));
    }
  }, []);
  
  const playMusic = useCallback((musicSrc) => {
    if (musicSrc) {
      const music = new Audio(musicSrc);
      music.loop = true;
      music.play().catch(e => console.log('Music play failed:', e));
      return music;
    }
  }, []);
  
  const stopMusic = useCallback((musicElement) => {
    if (musicElement) {
      musicElement.pause();
      musicElement.currentTime = 0;
    }
  }, []);
  
  return { playAudio, playMusic, stopMusic };
};'''

    def _get_local_storage_hook(self) -> str:
        return '''import { useState, useEffect } from 'react';

export const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.log(error);
      return initialValue;
    }
  });
  
  const setValue = (value) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.log(error);
    }
  };
  
  return [storedValue, setValue];
};'''

    def _get_game_engine_utils(self) -> str:
        return '''export const processText = (text, gameState) => {
  // Process variable substitution
  return text.replace(/\\{\\{([^}]+)\\}\\}/g, (match, variable) => {
    return gameState.variables[variable] || match;
  });
};

export const evaluateCondition = (condition, gameState) => {
  // Simple condition evaluation
  if (!condition) return true;
  
  // Add your condition evaluation logic here
  return true;
};

export const calculateChoiceVisibility = (choice, gameState) => {
  return evaluateCondition(choice.condition, gameState);
};'''

    def _get_media_utils(self) -> str:
        return '''export const preloadAssets = async (assets) => {
  const promises = Object.values(assets).map(assetUrl => {
    return new Promise((resolve, reject) => {
      if (assetUrl.startsWith('data:image')) {
        const img = new Image();
        img.onload = resolve;
        img.onerror = reject;
        img.src = assetUrl;
      } else if (assetUrl.startsWith('data:audio')) {
        const audio = new Audio();
        audio.oncanplaythrough = resolve;
        audio.onerror = reject;
        audio.src = assetUrl;
      } else {
        resolve();
      }
    });
  });
  
  try {
    await Promise.all(promises);
  } catch (error) {
    console.warn('Some assets failed to preload:', error);
  }
};

export const getAssetUrl = (assetId, mediaAssets) => {
  return mediaAssets[assetId] || '';
};'''

    def _get_save_utils(self) -> str:
        return '''const SAVE_KEY = 'dvge-saves';

export const saveGame = (name, gameData) => {
  const saves = getSavedGames();
  const newSave = {
    id: Date.now(),
    name,
    date: new Date().toISOString(),
    data: gameData
  };
  
  saves.push(newSave);
  localStorage.setItem(SAVE_KEY, JSON.stringify(saves));
  return newSave;
};

export const loadGame = (saveData) => {
  // This would need to be connected to your game state management
  console.log('Loading game:', saveData);
  return saveData.data;
};

export const getSavedGames = () => {
  try {
    const saves = localStorage.getItem(SAVE_KEY);
    return saves ? JSON.parse(saves) : [];
  } catch (error) {
    console.error('Error loading saves:', error);
    return [];
  }
};

export const deleteSave = (saveId) => {
  const saves = getSavedGames().filter(save => save.id !== saveId);
  localStorage.setItem(SAVE_KEY, JSON.stringify(saves));
};'''