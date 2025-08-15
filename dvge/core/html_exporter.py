import json
import base64
import os
from tkinter import filedialog, messagebox
from .variable_system import VariableSystem


class HTMLExporter:
    """Handles HTML game export functionality."""
    
    def __init__(self, app):
        self.app = app
    
    def export_game(self):
        """Exports the current project to a single, playable HTML file."""
        if not self.app.nodes: 
            messagebox.showwarning("Export Error", "Cannot export an empty project.")
            return False
        
        # Validate project first
        errors, warnings = self.app.validator.validate_project()
        if errors or warnings:
            message = "Project validation found issues:\n\n"
            if errors: 
                message += "ERRORS (must be fixed):\n" + "\n".join(errors) + "\n\n"
            if warnings: 
                message += "WARNINGS (can be ignored):\n" + "\n".join(warnings) + "\n\n"
            if errors:
                messagebox.showerror("Validation Errors", message)
                return False
            if not messagebox.askyesno("Validation Warnings", message + "Continue with export anyway?"):
                return False

        try:
            # Process dialogue data
            dialogue_data = self._process_dialogue_data()
            
            # Create JSON strings
            dialogue_json_string = json.dumps(dialogue_data, indent=4)
            player_data = json.dumps({
                "stats": self.app.player_stats, 
                "inventory": self.app.player_inventory
            }, indent=4)
            flags_data = json.dumps(self.app.story_flags, indent=4)
            quests_data = json.dumps({
                qid: q.to_dict() for qid, q in self.app.quests.items()
            }, indent=4)
            variables_data = json.dumps(getattr(self.app, 'variables', {}), indent=4)
            enemies_data = json.dumps({
                eid: e.to_dict() for eid, e in getattr(self.app, 'enemies', {}).items()
            }, indent=4)
            timers_data = json.dumps({
                tid: t.to_dict() for tid, t in getattr(self.app, 'timers', {}).items()
            }, indent=4)
            
            # Feature systems data
            feature_data = json.dumps({
                'reputation': getattr(self.app, 'reputation_data', {}),
                'loot_tables': getattr(self.app, 'loot_tables', {}),
                'skill_modifiers': getattr(self.app, 'skill_modifiers', {}),
                'active_puzzles': getattr(self.app, 'active_puzzles', {}),
                'minigame_results': getattr(self.app, 'minigame_results', {})
            }, indent=4)

            # Update the _generate_html call:
            html_content = self._generate_html(
                dialogue_json_string, 
                player_data, 
                flags_data, 
                quests_data,
                variables_data,
                enemies_data,
                timers_data,
                feature_data
            )

            # Save file
            filepath = filedialog.asksaveasfilename(
                defaultextension=".html", 
                filetypes=[("HTML Game Files", "*.html")]
            )
            if filepath:
                with open(filepath, "w", encoding="utf-8") as f: 
                    f.write(html_content)
                messagebox.showinfo("Export Successful", f"Game successfully exported to {os.path.basename(filepath)}")
                return True
            
            return False
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export game: {e}")
            return False
    
    def _process_dialogue_data(self):
        """Process node data for export, including media encoding."""
        dialogue_data = {}
    
    # Initialize variable system for text substitution
        temp_var_system = VariableSystem()
        temp_var_system.set_variables_ref(getattr(self.app, 'variables', {}))
        temp_var_system.set_flags_ref(self.app.story_flags)
        
        for node_id, node in self.app.nodes.items():
            game_data = node.to_dict()['game_data']
            
            # Add node type to game data
            game_data['node_type'] = node.to_dict()['node_type']
            
            # Embed image as Base64 data URI if it exists
            if game_data.get('backgroundImage') and os.path.exists(game_data['backgroundImage']):
                try:
                    with open(game_data['backgroundImage'], "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                        # Detect file type
                        ext = os.path.splitext(game_data['backgroundImage'])[1].lower()
                        if ext in ['.jpg', '.jpeg']:
                            game_data['backgroundImage'] = f"data:image/jpeg;base64,{encoded_string}"
                        elif ext == '.png':
                            game_data['backgroundImage'] = f"data:image/png;base64,{encoded_string}"
                        elif ext == '.gif':
                            game_data['backgroundImage'] = f"data:image/gif;base64,{encoded_string}"
                        else:
                            game_data['backgroundImage'] = f"data:image/png;base64,{encoded_string}"
                except Exception as e:
                    print(f"Could not process image for node {node_id}: {e}")
                    game_data['backgroundImage'] = ""
            else:
                game_data['backgroundImage'] = ""
            
            # Embed audio as Base64 data URI if it exists
            if game_data.get('audio') and os.path.exists(game_data['audio']):
                try:
                    with open(game_data['audio'], "rb") as audio_file:
                        encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
                        # Detect file type
                        ext = os.path.splitext(game_data['audio'])[1].lower()
                        if ext == '.mp3':
                            game_data['audio'] = f"data:audio/mpeg;base64,{encoded_string}"
                        elif ext == '.wav':
                            game_data['audio'] = f"data:audio/wav;base64,{encoded_string}"
                        elif ext == '.ogg':
                            game_data['audio'] = f"data:audio/ogg;base64,{encoded_string}"
                        else:
                            game_data['audio'] = f"data:audio/mpeg;base64,{encoded_string}"
                except Exception as e:
                    print(f"Could not process audio for node {node_id}: {e}")
                    game_data['audio'] = ""
            else:
                game_data['audio'] = ""

            # Embed music as Base64 data URI if it exists
            if game_data.get('music') and os.path.exists(game_data['music']):
                try:
                    with open(game_data['music'], "rb") as music_file:
                        encoded_string = base64.b64encode(music_file.read()).decode('utf-8')
                        # Detect file type
                        ext = os.path.splitext(game_data['music'])[1].lower()
                        if ext == '.mp3':
                            game_data['music'] = f"data:audio/mpeg;base64,{encoded_string}"
                        elif ext == '.wav':
                            game_data['music'] = f"data:audio/wav;base64,{encoded_string}"
                        elif ext == '.ogg':
                            game_data['music'] = f"data:audio/ogg;base64,{encoded_string}"
                        else:
                            game_data['music'] = f"data:audio/mpeg;base64,{encoded_string}"
                except Exception as e:
                    print(f"Could not process music for node {node_id}: {e}")
                    game_data['music'] = ""
            else:
                game_data['music'] = ""
            
            # Apply variable substitution to text content
            if 'text' in game_data:
                game_data['text'] = temp_var_system.substitute_text(game_data['text'])
            
            # Apply variable substitution to option text
            for option in game_data.get('options', []):
                if 'text' in option:
                    option['text'] = temp_var_system.substitute_text(option['text'])
        
            dialogue_data[node_id] = game_data
    
        return dialogue_data
    
    def _generate_html(self, dialogue_data, player_data, flags_data, quests_data, variables_data, enemies_data=None, timers_data=None, feature_data=None):
        """Generate the complete HTML file content."""
        font_name = self.app.project_settings.get("font", "Merriweather")
        title_font_name = self.app.project_settings.get("title_font", "Special Elite")
        background_setting = self.app.project_settings.get("background", "").strip()

        font_url_name = font_name.replace(' ', '+')
        title_font_url_name = title_font_name.replace(' ', '+')
        font_link = f'<link href="https://fonts.googleapis.com/css2?family={font_url_name}:ital,wght@0,400;0,700;1,400&family={title_font_url_name}&display=swap" rel="stylesheet" />'

        font_css = f'--primary-font:"{font_name}",serif;'
        title_font_css = f'--title-font:"{title_font_name}",cursive;'

        background_css = self._generate_background_css(background_setting)
        
        html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>My DVG Adventure</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    {font_link}
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <style>
        :root {{
            {font_css}
            {title_font_css}
            --bg-grad-start-default: #232526; 
            --bg-grad-end-default: #414345;
            --text-light: #ECEFF1; 
            --text-dark: #263238; 
            --text-muted: #90A4AE;
            --accent-color: #80CBC4; 
            --accent-dark: #004D40;
            --dialogue-bg: rgba(38, 50, 56, 0.9);
            --hud-bg: rgba(38, 50, 56, 0.95);
            --button-bg: #455A64; 
            --button-hover-bg: #607D8B;
            --border-color: rgba(120, 144, 156, 0.3);
            --shadow-color: rgba(0,0,0,0.4);
            --success-color: #A5D6A7; 
            --error-color: #EF9A9A;
            --quest-active-color: #F1C40F; 
            --quest-completed-color: #2ECC71; 
            --quest-failed-color: #E74C3C;
        }}
        
        body {{
            {background_css}
            margin:0; padding:0; font-family:var(--primary-font); color:var(--text-light); 
            min-height:100vh; transition:background 0.8s ease-in-out; 
            background-size: cover; background-position: center; background-attachment: fixed;
            overflow: hidden;
        }}
        
        /* Theme variations */
        body.theme-dream {{ --accent-color: #CE93D8; --accent-dark: #4A148C; }}
        body.theme-ritual {{ --accent-color: #EF9A9A; --accent-dark: #B71C1C; }}

        #game-container {{ display:flex; flex-direction:column; min-height:100vh; position:relative; }}

        #dialogue-box {{
            position:fixed; bottom:2em; left:50%; transform:translateX(-50%);
            width:90%; max-width:800px; background:var(--dialogue-bg);
            border-radius:12px; padding:1.5em 2em; 
            box-shadow:0 10px 30px var(--shadow-color);
            border: 1px solid var(--border-color); backdrop-filter: blur(10px);
            animation: slideUp 0.5s ease-out forwards;
        }}
        
        @keyframes slideUp {{ from {{ opacity:0; transform: translate(-50%, 50px); }} to {{ opacity:1; transform: translate(-50%, 0); }} }}

        #npc-name {{
            font-family:var(--title-font); font-size:1.6em; margin-bottom:0.7em;
            color: var(--accent-color); text-shadow: 0 0 10px var(--accent-color);
        }}
        
        #dialogue-text {{
            font-size:1.15em; line-height:1.7; margin-bottom:1.5em;
            color:var(--text-light); min-height:60px; font-style: italic;
        }}
        
        #options {{ display:flex; flex-direction:column; gap:0.8em; }}
        
        #options button {{
            padding:0.9em 1.4em; border:1px solid transparent; background:var(--button-bg);
            color:var(--text-light); border-radius:8px; cursor:pointer;
            font-size:1em; transition: all 0.2s ease-out; text-align:left;
        }}
        
        #options button:hover {{ background:var(--button-hover-bg); border-color: var(--accent-color); transform: translateY(-2px); }}
        #options button:disabled {{ opacity:0.5; cursor:not-allowed; filter:grayscale(70%); }}

        /* Shop Interface */
        .shop-interface {{
            display: none; position: fixed; top: 50%; left: 50%;
            transform: translate(-50%, -50%); width: 90%; max-width: 600px;
            background: var(--hud-bg); border-radius: 12px; padding: 2em;
            box-shadow: 0 20px 40px var(--shadow-color); z-index: 1000;
        }}
        
        .shop-interface.active {{ display: block; }}

        .modal-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%;
             background: rgba(0,0,0,0.7); z-index: 999; display: none; }}
        .modal-overlay.active {{ display: block; }}

        .shop-item-info {{ flex: 1; }}
        .shop-item-name {{ font-weight: bold; color: var(--text-light); }}
        .shop-item-description {{ color: var(--text-muted); font-size: 0.9em; margin-top: 0.3em; }}

        .inventory-tabs {{ display: flex; margin-bottom: 1em; gap: 0.5em; }}
        .inventory-tab {{ padding: 0.5em 1em; background: var(--button-bg); 
                border: none; color: var(--text-light); cursor: pointer; border-radius: 6px; }}
        .inventory-tab.active {{ background: var(--accent-color); color: var(--text-dark); }}

        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} }}
        .timer-display {{ animation: pulse 2s infinite; }}
        
        .shop-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5em; }}
        .shop-title {{ font-family: var(--title-font); font-size: 1.8em; color: var(--accent-color); }}
        .shop-currency {{ font-size: 1.2em; color: var(--success-color); }}
        
        .shop-tabs {{ display: flex; margin-bottom: 1em; }}
        .shop-tab {{ padding: 0.5em 1em; margin-right: 0.5em; background: var(--button-bg); 
                   border: none; color: var(--text-light); cursor: pointer; border-radius: 6px; }}
        .shop-tab.active {{ background: var(--accent-color); color: var(--text-dark); }}
        
        .shop-items {{ max-height: 300px; overflow-y: auto; }}
        .shop-item {{ display: flex; justify-content: space-between; align-items: center;
                     padding: 1em; margin-bottom: 0.5em; background: var(--button-bg); border-radius: 8px; }}
        .shop-item-name {{ font-weight: bold; }}
        .shop-item-price {{ color: var(--success-color); margin: 0 1em; }}
        .shop-item button {{ padding: 0.5em 1em; background: var(--accent-color); 
                           color: var(--text-dark); border: none; border-radius: 4px; cursor: pointer; }}

        /* Random Event Interface */
        .random-event-interface {{
            text-align: center; padding: 2em 0;
        }}
        
        .random-outcome {{ 
            background: var(--button-bg); padding: 1.5em; border-radius: 12px;
            margin: 1em 0; border-left: 4px solid var(--accent-color);
        }}

        /* Timer Interface */
        .timer-interface {{
            text-align: center; padding: 2em 0;
        }}
        
        .timer-display {{
            font-size: 3em; font-family: monospace; color: var(--accent-color);
            margin: 1em 0; text-shadow: 0 0 20px var(--accent-color);
        }}
        
        .timer-progress {{
            width: 100%; height: 20px; background: var(--button-bg);
            border-radius: 10px; overflow: hidden; margin: 1em 0;
        }}
        
        .timer-progress-bar {{
            height: 100%; background: linear-gradient(90deg, var(--accent-color), var(--success-color));
            transition: width 1s linear;
        }}

        /* Inventory Interface */
        .inventory-interface {{
            display: none; position: fixed; top: 50%; left: 50%;
            transform: translate(-50%, -50%); width: 90%; max-width: 700px;
            background: var(--hud-bg); border-radius: 12px; padding: 2em;
            box-shadow: 0 20px 40px var(--shadow-color); z-index: 1000;
        }}
        
        .inventory-interface.active {{ display: block; }}
        
        .inventory-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); 
                          gap: 1em; margin: 1em 0; }}
        .inventory-item {{ background: var(--button-bg); padding: 1em; border-radius: 8px; text-align: center; }}
        
        .crafting-recipes {{ margin-top: 2em; }}
        .recipe {{ background: var(--button-bg); padding: 1em; border-radius: 8px; margin-bottom: 1em; }}
        .recipe-ingredients {{ color: var(--text-muted); font-size: 0.9em; }}

        /* HUD and other existing styles remain the same */
        #hud-toggle {{ position: fixed; top: 20px; left: 20px; z-index: 101;
            background: var(--hud-bg); color: var(--text-light);
            border: 1px solid var(--border-color); border-radius: 50%;
            width: 50px; height: 50px; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.8em; transition: all 0.3s ease; }}
        
        #hud-toggle:hover {{ background: var(--accent-dark); color: white; }}

        #hud-container {{ position: fixed; top: 0; left: -350px; width: 320px; height: 100%;
            background: var(--hud-bg); padding: 20px;
            box-shadow: 5px 0 25px var(--shadow-color);
            transition: left 0.4s ease-in-out; z-index: 100;
            overflow-y: auto; border-right: 1px solid var(--border-color); }}
        
        #hud-container.open {{ left: 0; }}
        
        .hud-section {{ margin-bottom: 1.5em; }}
        .hud-section h3 {{ font-family: var(--title-font); color: var(--accent-color);
            margin-top: 0; border-bottom: 1px solid var(--border-color); 
            padding-bottom: 0.5em; display: flex; align-items: center; 
            gap: 0.5em; font-size: 1.4em; }}
        
        .stat-line, .inventory-line, .quest-line {{ display: flex; justify-content: space-between; 
            align-items: center; margin: 0.6em 0; padding: 0.4em; 
            border-radius: 4px; transition: background-color 0.2s; }}
        
        .inventory-item, .quest-line {{ cursor: help; }}
        .inventory-item:hover, .quest-line:hover {{ background-color: rgba(255,255,255,0.05); }}
        
        .quest-line.active {{ border-left: 3px solid var(--quest-active-color); }}
        .quest-line.completed {{ border-left: 3px solid var(--quest-completed-color); 
            text-decoration: line-through; color: var(--text-muted); }}
        .quest-line.failed {{ border-left: 3px solid var(--quest-failed-color); 
            text-decoration: line-through; color: var(--text-muted); }}

        #save-load-buttons {{ position: fixed; top: 20px; right: 20px; z-index: 101; }}
        #save-load-buttons button {{ margin-left: 10px; padding: 10px 18px; font-size: 1em;
            background: var(--button-bg); color: var(--text-light);
            border: 1px solid var(--border-color); border-radius: 8px;
            cursor: pointer; transition: all 0.2s ease; }}
        #save-load-buttons button:hover {{ background: var(--button-hover-bg); }}

        .notification {{ position:fixed; bottom:2em; right:2em; background:var(--hud-bg);
            color:var(--text-light); padding:1em 1.5em; border-radius:8px;
            z-index:200; animation:fadeInOut 4s ease-in-out forwards;
            border-left:4px solid var(--accent-color); }}
        
        @keyframes fadeInOut {{ 0%,100% {{ opacity:0; transform:translateY(20px); }} 
            10%,90% {{ opacity:1; transform:translateY(0); }} }}

        .chapter-transition {{ position:fixed; top:0; left:0; width:100%; height:100%;
            background:rgba(5,5,10,0.99); color:var(--text-light);
            display:flex; justify-content:center; align-items:center; 
            flex-direction: column; z-index:1000; font-size:2.5em; 
            text-align:center; font-family:var(--title-font);
            opacity:0; animation:chapterFade 4s ease-in-out forwards; }}
        
        .chapter-transition small {{ font-size: 0.5em; margin-top: 1em; 
            font-family: var(--primary-font); font-style: italic; opacity: 0.8; }}
        
        @keyframes chapterFade {{ 0%,100% {{ opacity:0; }} 20%,80% {{ opacity:1; }} }}

        #start-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85); color: white;
            display: flex; flex-direction: column; justify-content: center; 
            align-items: center; z-index: 2000; cursor: pointer; 
            backdrop-filter: blur(5px); }}
        
        #start-overlay h1 {{ font-size: 4em; font-family: var(--title-font); margin-bottom: 0.2em; }}
        #start-overlay p {{ font-size: 1.2em; }}
    </style>
</head>
<body>
    <div id="game-container">
        <div id="hud-toggle"><i class="ph-fill ph-backpack"></i></div>
        <div id="hud-container"></div>
        <div id="save-load-buttons">
            <button id="save-button" title="Save Progress"><i class="ph-fill ph-floppy-disk"></i></button>
            <button id="load-button" title="Load Progress"><i class="ph-fill ph-folder-open"></i></button>
        </div>
        
        <!-- Main dialogue interface -->
        <div id="dialogue-box">
            <div id="npc-name"></div>
            <div id="dialogue-text"></div>
            <div id="options"></div>
        </div>
        
        <!-- Shop Interface -->
        <div id="shop-interface" class="shop-interface">
            <div class="shop-header">
                <h2 class="shop-title">🏪 Shop</h2>
                <div class="shop-currency">Gold: <span id="shop-currency-amount">0</span></div>
                <button onclick="closeShop()" style="background: var(--error-color); border: none; color: white; padding: 0.5em 1em; border-radius: 6px; cursor: pointer;">Close</button>
            </div>
            <div class="shop-tabs">
                <button class="shop-tab active" onclick="showShopTab('buy')">Buy</button>
                <button class="shop-tab" onclick="showShopTab('sell')">Sell</button>
            </div>
            <div id="shop-items" class="shop-items"></div>
        </div>
        
        <!-- Inventory Interface -->
        <div id="inventory-interface" class="inventory-interface">
            <div class="shop-header">
                <h2 class="shop-title">🎒 Inventory</h2>
                <button onclick="closeInventory()" style="background: var(--error-color); border: none; color: white; padding: 0.5em 1em; border-radius: 6px; cursor: pointer;">Close</button>
            </div>
            <div id="inventory-grid" class="inventory-grid"></div>
            <div class="crafting-recipes">
                <h3>Crafting Recipes</h3>
                <div id="crafting-recipes-list"></div>
            </div>
        </div>
        
        <audio id="audio-player" src=""></audio>
        <audio id="music-player" src="" loop></audio>
        <div id="start-overlay">
            <h1 id="story-title-overlay">My DVG Adventure</h1>
            <p>Click to Start</p>
        </div>
    </div>
    
    <script>
        const dialogueData = {dialogue_data};
        let player = {player_data};
        let currentNode = "intro";
        let gameState = {{ currentChapter:"", flags:{flags_data}, quests:{quests_data}, variables:{variables_data} }};
        let enemiesData = {enemies_data};
        let timersData = {timers_data};
        let featureData = {feature_data};
        let autoAdvanceTimer = null;
        let currentShopData = null;
        let currentInventoryData = null;
        let timerInterval = null;

        function updateHud() {{
            const hud = document.getElementById('hud-container');
            let statsHTML = `<div class="hud-section"><h3><i class="ph-fill ph-heartbeat"></i> Stats</h3>`;
            for(const stat in player.stats){{
                statsHTML+=`<div class="stat-line"><span>${{stat.charAt(0).toUpperCase()+stat.slice(1)}}:</span> <span>${{player.stats[stat]}}</span></div>`;
            }}
            
            // Add variables to stats display
            for(const varName in gameState.variables) {{
                const varValue = gameState.variables[varName];
                statsHTML += `<div class="stat-line"><span>${{varName.charAt(0).toUpperCase() + varName.slice(1)}}:</span> <span>${{varValue}}</span></div>`;
            }}
            statsHTML += `</div>`;
            
            let inventoryHTML = `<div class="hud-section"><h3><i class="ph-fill ph-treasure-chest"></i> Inventory</h3>`;
            if (player.inventory.length > 0) {{
                player.inventory.forEach(item => {{
                    inventoryHTML += `<div class="inventory-line"><span class="inventory-item" title="${{item.description || ''}}">${{item.name}}</span></div>`;
                }});
            }} else {{
                inventoryHTML += `<div>Empty</div>`;
            }}
            inventoryHTML += `</div>`;

            let journalHTML = `<div class="hud-section"><h3><i class="ph-fill ph-scroll"></i> Journal</h3>`;
            const quests = Object.values(gameState.quests);
            const activeQuests = quests.filter(q => q.state === 'active');
            const completedQuests = quests.filter(q => q.state === 'completed');
            const failedQuests = quests.filter(q => q.state === 'failed');

            if (activeQuests.length > 0) {{
                journalHTML += `<h4>Active</h4>`;
                 activeQuests.forEach(quest => {{
                    journalHTML += `<div class="quest-line active" title="${{quest.description || ''}}"><span>${{quest.name}}</span></div>`;
                }});
            }}
            
            if (completedQuests.length > 0) {{
                journalHTML += `<h4>Completed</h4>`;
                 completedQuests.forEach(quest => {{
                    journalHTML += `<div class="quest-line completed" title="${{quest.description || ''}}"><span>${{quest.name}}</span></div>`;
                }});
            }}

            if (failedQuests.length > 0) {{
                journalHTML += `<h4>Failed</h4>`;
                 failedQuests.forEach(quest => {{
                    journalHTML += `<div class="quest-line failed" title="${{quest.description || ''}}"><span>${{quest.name}}</span></div>`;
                }});
            }}

            if (activeQuests.length === 0 && completedQuests.length === 0 && failedQuests.length === 0) {{
                journalHTML += `<div>No quests.</div>`;
            }}
            journalHTML += `</div>`;

            hud.innerHTML = statsHTML + inventoryHTML + journalHTML;
        }}

        function showNotification(message, duration=3000) {{
            const n = document.createElement("div");
            n.className = "notification";
            n.textContent = message;
            document.body.appendChild(n);
            setTimeout(() => {{ if(n.parentNode) n.remove() }}, duration);
        }}

        function showChapterTransition(name) {{
            const t = document.createElement("div");
            t.className = "chapter-transition";
            t.innerHTML = `<div>${{name}}</div><small>A New Chapter Begins</small>`;
            document.body.appendChild(t);
            setTimeout(() => {{ if(t.parentNode) t.remove() }}, 4000);
        }}

        function setBackground(nodeData) {{
            let themeName = nodeData.backgroundTheme || 'theme-default';
            if (!document.body.classList.contains(themeName)) {{
                document.body.className = '';
                document.body.classList.add(themeName);
            }}
            if (nodeData.backgroundImage) {{
                document.body.style.backgroundImage = `url(${{nodeData.backgroundImage}})`;
            }} else {{
                document.body.style.backgroundImage = '';
            }}
        }}

        function checkConditions(conditions) {{
            if (!conditions || conditions.length === 0) return true;
            return conditions.every(cond => {{
                const {{ type, subject, operator, value }} = cond;
                switch (type) {{
                    case 'stat':
                        const playerStat = player.stats[subject];
                        if (playerStat === undefined) return false;
                        switch (operator) {{
                            case '==': return playerStat == value;
                            case '!=': return playerStat != value;
                            case '>':  return playerStat > value;
                            case '<':  return playerStat < value;
                            case '>=': return playerStat >= value;
                            case '<=': return playerStat <= value;
                            default: return false;
                        }}
                    case 'item':
                        const hasItem = player.inventory.some(item => item.name === subject);
                        return operator === 'has' ? hasItem : !hasItem;
                    case 'flag':
                        const flagValue = gameState.flags[subject];
                        if (flagValue === undefined) return false;
                        const comparisonValue = (value === true || String(value).toLowerCase() === 'true');
                        return operator === 'is' ? (flagValue === comparisonValue) : (flagValue !== comparisonValue);
                    case 'quest':
                        const quest = gameState.quests[subject];
                        if (!quest) return false;
                        return operator === 'is' ? (quest.state === value) : (quest.state !== value);
                    case 'variable':
                        const playerVar = gameState.variables[subject];
                        if (playerVar === undefined) return false;
                        const varValue = parseFloat(value) || 0;
                        switch (operator) {{
                            case '==': return playerVar == varValue;
                            case '!=': return playerVar != varValue;
                            case '>':  return playerVar > varValue;
                            case '<':  return playerVar < varValue;
                            case '>=': return playerVar >= varValue;
                            case '<=': return playerVar <= varValue;
                            default: return false;
                        }}
                    default: return true;
                }}
            }});
        }}

        function applyEffects(effects) {{
            if (!effects || effects.length === 0) return;
            effects.forEach(effect => {{
                const {{ type, subject, operator, value }} = effect;
                switch (type) {{
                    case 'stat':
                        let numericValue;
                        try {{ numericValue = parseFloat(value); }} catch(e) {{ numericValue = 0; }}
                        if (isNaN(numericValue)) numericValue = 0;
                        if (player.stats[subject] === undefined) player.stats[subject] = 0;

                        switch (operator) {{
                            case '=':  player.stats[subject] = numericValue; break;
                            case '+=': player.stats[subject] += numericValue; break;
                            case '-=': player.stats[subject] -= numericValue; break;
                        }}
                        showNotification(`'${{subject}}' changed by ${{operator}}${{numericValue}}`);
                        break;
                    case 'item':
                        if (operator === 'add' && !player.inventory.some(item => item.name === subject)) {{
                            player.inventory.push({{name: subject, description: ""}});
                            showNotification(`Added '${{subject}}' to inventory.`);
                        }} else if (operator === 'remove') {{
                            const index = player.inventory.findIndex(item => item.name === subject);
                            if (index > -1) {{
                                player.inventory.splice(index, 1);
                                showNotification(`Removed '${{subject}}' from inventory.`);
                            }}
                        }}
                        break;
                    case 'flag':
                        const boolValue = (value === true || String(value).toLowerCase() === 'true');
                        gameState.flags[subject] = boolValue;
                        showNotification(`Flag '${{subject}}' set to ${{boolValue}}.`);
                        break;
                    case 'quest':
                        const quest = gameState.quests[subject];
                        if (quest) {{
                            quest.state = value;
                            showNotification(`Quest '${{quest.name}}' updated to '${{value}}'.`);
                        }}
                        break;
                    case 'variable':
                        let variableValue;
                        try {{ 
                            let valueStr = String(value);
                            for (const [varName, varValue] of Object.entries(gameState.variables)) {{
                                valueStr = valueStr.replace(new RegExp(`\\{{${{varName}}\\}}`, 'g'), varValue);
                            }}
                            variableValue = eval(valueStr) || 0;
                        }} catch(e) {{ 
                            variableValue = parseFloat(value) || 0; 
                        }}
                        
                        if (gameState.variables[subject] === undefined) gameState.variables[subject] = 0;
                        const currentVar = gameState.variables[subject];

                        switch (operator) {{
                            case '=':  gameState.variables[subject] = variableValue; break;
                            case '+=': gameState.variables[subject] = currentVar + variableValue; break;
                            case '-=': gameState.variables[subject] = currentVar - variableValue; break;
                            case '*=': gameState.variables[subject] = currentVar * variableValue; break;
                            case '/=': if (variableValue !== 0) gameState.variables[subject] = currentVar / variableValue; break;
                            case '%=': if (variableValue !== 0) gameState.variables[subject] = currentVar % variableValue; break;
                            case 'min': gameState.variables[subject] = Math.min(currentVar, variableValue); break;
                            case 'max': gameState.variables[subject] = Math.max(currentVar, variableValue); break;
                        }}
                        showNotification(`${{subject}} ${{operator}} ${{variableValue}} (now: ${{gameState.variables[subject]}})`);
                        break;
                }}
            }});
            updateHud();
        }}

        function renderNode(key) { 
            if (autoAdvanceTimer) clearTimeout(autoAdvanceTimer);
            if (timerInterval) clearInterval(timerInterval);
    
            if (key === '[End Game]') {
                document.getElementById('dialogue-text').textContent = 'The story ends here.';
                document.getElementById('options').innerHTML = '';
                document.getElementById('npc-name').textContent = 'Game Over';
                return;
            }
    
            const nodeData = dialogueData[key];
            if (!nodeData) {
                console.error("Node not found:", key);
                return;
            }
    
            currentNode = key;
            setBackground(nodeData);
            updateHud();

            // Handle audio/music
            const audioPlayer = document.getElementById('audio-player');
            if (nodeData.audio) {{
                audioPlayer.src = nodeData.audio;
                audioPlayer.play().catch(e => console.log("Audio autoplay prevented"));
            }} else {{
                audioPlayer.src = "";
            }}

            const musicPlayer = document.getElementById('music-player');
            if (nodeData.music && musicPlayer.src !== nodeData.music) {{
                musicPlayer.src = nodeData.music;
                musicPlayer.play().catch(e => console.log("Music autoplay prevented"));
            }} else if (!nodeData.music) {{
                musicPlayer.src = "";
                musicPlayer.pause();
            }}

            // Handle chapter transitions
            if (nodeData.chapter && nodeData.chapter !== gameState.currentChapter) {{
                gameState.currentChapter = nodeData.chapter;
                showChapterTransition(nodeData.chapter);
            }}

            // Update dialogue display
            document.getElementById("npc-name").textContent = nodeData.npc || "Narrator";
            document.getElementById("dialogue-text").textContent = nodeData.text || "";
            const optionsContainer = document.getElementById("options");
            optionsContainer.innerHTML = "";

            // Handle different node types with switch statement
            switch (nodeData.node_type) {
                case "Shop":
                    handleShopNode(nodeData);
                    break;
                case "RandomEvent":
                    handleRandomEventNode(nodeData);
                    break;
                case "Timer":
                    handleTimerNode(nodeData);
                    break;
                case "Inventory":
                    handleInventoryNode(nodeData);
                    break;
                case "DiceRoll":
                    handleDiceRollNode(nodeData);
                    break;
                case "Combat":
                    handleCombatNode(nodeData);
                    break;
                default:
                    handleDialogueNode(nodeData);
                    break;
            }
        }

        function handleShopNode(nodeData) {{
            currentShopData = nodeData;
            const optionsContainer = document.getElementById("options");
            
            const shopButton = document.createElement("button");
            shopButton.textContent = "🏪 Enter Shop";
            shopButton.onclick = () => openShop(nodeData);
            optionsContainer.appendChild(shopButton);
            
            if (nodeData.continue_node) {{
                const continueButton = document.createElement("button");
                continueButton.textContent = "Continue on your way";
                continueButton.onclick = () => renderNode(nodeData.continue_node);
                optionsContainer.appendChild(continueButton);
            }}
        }}

        function openShop(shopData) {{
            currentShopData = shopData;
            document.getElementById('shop-interface').classList.add('active');
            document.getElementById('shop-currency-amount').textContent = gameState.variables[shopData.currency_variable] || 0;
            showShopTab('buy');
        }}

        function showShopTab(tabType) {{
            // Update tab appearance
            document.querySelectorAll('.shop-tab').forEach(tab => tab.classList.remove('active'));
            document.querySelector(`[onclick="showShopTab('${{tabType}}')"]`).classList.add('active');
            
            const shopItems = document.getElementById('shop-items');
            shopItems.innerHTML = '';
            
            if (tabType === 'buy') {{
                currentShopData.items_for_sale.forEach(item => {{
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'shop-item';
                    itemDiv.innerHTML = `
                        <div>
                            <div class="shop-item-name">${{item.name}}</div>
                            <div class="shop-item-description">${{item.description || ''}}</div>
                        </div>
                        <div class="shop-item-price">${{item.price}} ${{currentShopData.currency_variable}}</div>
                        <button onclick="buyItem('${{item.name}}', ${{item.price}})">Buy</button>
                    `;
                    shopItems.appendChild(itemDiv);
                }});
            }} else {{
                currentShopData.items_to_buy.forEach(buyItem => {{
                    const hasItem = player.inventory.some(item => item.name === buyItem.name);
                    if (hasItem) {{
                        const itemDiv = document.createElement('div');
                        itemDiv.className = 'shop-item';
                        itemDiv.innerHTML = `
                            <div>
                                <div class="shop-item-name">${{buyItem.name}}</div>
                                <div class="shop-item-description">${{buyItem.description || ''}}</div>
                            </div>
                            <div class="shop-item-price">${{buyItem.price}} ${{currentShopData.currency_variable}}</div>
                            <button onclick="sellItem('${{buyItem.name}}', ${{buyItem.price}})">Sell</button>
                        `;
                        shopItems.appendChild(itemDiv);
                    }}
                }});
                
                if (shopItems.children.length === 0) {{
                    shopItems.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 2em;">You have no items to sell</div>';
                }}
            }}
        }}

        function buyItem(itemName, price) {{
            const currency = gameState.variables[currentShopData.currency_variable] || 0;
            if (currency >= price) {{
                gameState.variables[currentShopData.currency_variable] = currency - price;
                player.inventory.push({{ name: itemName, description: "" }});
                showNotification(`Bought ${{itemName}} for ${{price}} ${{currentShopData.currency_variable}}!`);
                document.getElementById('shop-currency-amount').textContent = gameState.variables[currentShopData.currency_variable];
                updateHud();
                showShopTab('buy'); // Refresh display
            }} else {{
                showNotification(`Not enough ${{currentShopData.currency_variable}}! Need ${{price}}, have ${{currency}}`);
            }}
        }}

        function sellItem(itemName, price) {{
            const itemIndex = player.inventory.findIndex(item => item.name === itemName);
            if (itemIndex >= 0) {{
                player.inventory.splice(itemIndex, 1);
                gameState.variables[currentShopData.currency_variable] = (gameState.variables[currentShopData.currency_variable] || 0) + price;
                showNotification(`Sold ${{itemName}} for ${{price}} ${{currentShopData.currency_variable}}!`);
                document.getElementById('shop-currency-amount').textContent = gameState.variables[currentShopData.currency_variable];
                updateHud();
                showShopTab('sell'); // Refresh display
            }}
        }}

        function closeShop() {{
            document.getElementById('shop-interface').classList.remove('active');
            if (currentShopData && currentShopData.continue_node) {{
                renderNode(currentShopData.continue_node);
            }}
        }}

        function handleRandomEventNode(nodeData) {{
            const optionsContainer = document.getElementById("options");
            
            if (nodeData.auto_trigger) {{
                // Auto-trigger random event
                triggerRandomEvent(nodeData);
            }} else {{
                // Show manual trigger button
                const triggerButton = document.createElement("button");
                triggerButton.textContent = "🎲 Trigger Random Event";
                triggerButton.onclick = () => triggerRandomEvent(nodeData);
                optionsContainer.appendChild(triggerButton);
            }}
        }}

        function triggerRandomEvent(nodeData) {{
            if (!nodeData.random_outcomes || nodeData.random_outcomes.length === 0) return;
            
            // Calculate weighted random selection
            const totalWeight = nodeData.random_outcomes.reduce((sum, outcome) => sum + (outcome.weight || 1), 0);
            const randomValue = Math.random() * totalWeight;
            
            let currentWeight = 0;
            let selectedOutcome = null;
            
            for (const outcome of nodeData.random_outcomes) {{
                currentWeight += outcome.weight || 1;
                if (randomValue <= currentWeight) {{
                    selectedOutcome = outcome;
                    break;
                }}
            }}
            
            if (selectedOutcome) {{
                // Show outcome
                const outcomeDiv = document.createElement('div');
                outcomeDiv.className = 'random-outcome';
                outcomeDiv.innerHTML = `
                    <h3>Random Event Result</h3>
                    <p>${{selectedOutcome.description}}</p>
                `;
                document.getElementById('options').innerHTML = '';
                document.getElementById('options').appendChild(outcomeDiv);
                
                showNotification(`Random Event: ${{selectedOutcome.description}}`);
                
                // Navigate after delay
                setTimeout(() => {{
                    if (selectedOutcome.next_node) {{
                        renderNode(selectedOutcome.next_node);
                    }}
                }}, 2000);
            }}
        }}

        function handleTimerNode(nodeData) {{
            const optionsContainer = document.getElementById("options");
            
            // Create timer interface
            const timerDiv = document.createElement('div');
            timerDiv.className = 'timer-interface';
            
            const totalSeconds = nodeData.total_seconds || 5;
            let remainingSeconds = totalSeconds;
            
            timerDiv.innerHTML = `
                <div class="timer-display" id="timer-display">${{formatTime(remainingSeconds)}}</div>
                ${{nodeData.show_countdown ? `
                    <div class="timer-progress">
                        <div class="timer-progress-bar" id="timer-progress" style="width: 100%"></div>
                    </div>
                ` : ''}}
                ${{nodeData.allow_skip ? '<button onclick="skipTimer()">Skip Wait</button>' : ''}}
            `;
            
            optionsContainer.appendChild(timerDiv);
            
            // Start timer
            timerInterval = setInterval(() => {{
                remainingSeconds--;
                document.getElementById('timer-display').textContent = formatTime(remainingSeconds);
                
                if (nodeData.show_countdown) {{
                    const progress = (remainingSeconds / totalSeconds) * 100;
                    document.getElementById('timer-progress').style.width = progress + '%';
                }}
                
                if (remainingSeconds <= 0) {{
                    clearInterval(timerInterval);
                    if (nodeData.next_node) {{
                        renderNode(nodeData.next_node);
                    }}
                }}
            }}, 1000);
        }}

        function skipTimer() {{
            if (timerInterval) {{
                clearInterval(timerInterval);
                const nodeData = dialogueData[currentNode];
                if (nodeData && nodeData.next_node) {{
                    renderNode(nodeData.next_node);
                }}
            }}
        }}

        function formatTime(seconds) {{
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return mins > 0 ? `${{mins}}:${{secs.toString().padStart(2, '0')}}` : secs.toString();
        }}

        function handleInventoryNode(nodeData) {{
            currentInventoryData = nodeData;
            const optionsContainer = document.getElementById("options");
            
            if (nodeData.auto_open) {{
                openInventory(nodeData);
            }} else {{
                const inventoryButton = document.createElement("button");
                inventoryButton.textContent = "🎒 Open Inventory";
                inventoryButton.onclick = () => openInventory(nodeData);
                optionsContainer.appendChild(inventoryButton);
            }}
            
            if (nodeData.continue_node) {{
                const continueButton = document.createElement("button");
                continueButton.textContent = "Continue";
                continueButton.onclick = () => renderNode(nodeData.continue_node);
                optionsContainer.appendChild(continueButton);
            }}
        }}

        function openInventory(inventoryData) {{
            currentInventoryData = inventoryData;
            document.getElementById('inventory-interface').classList.add('active');
            
            // Display inventory items
            const inventoryGrid = document.getElementById('inventory-grid');
            inventoryGrid.innerHTML = '';
            
            player.inventory.forEach(item => {{
                const itemDiv = document.createElement('div');
                itemDiv.className = 'inventory-item';
                itemDiv.innerHTML = `
                    <div><strong>${{item.name}}</strong></div>
                    <div style="font-size: 0.8em; color: var(--text-muted)">${{item.description || ''}}</div>
                `;
                inventoryGrid.appendChild(itemDiv);
            }});
            
            // Display crafting recipes
            const recipesContainer = document.getElementById('crafting-recipes-list');
            recipesContainer.innerHTML = '';
            
            inventoryData.crafting_recipes.forEach(recipe => {{
                const canCraft = recipe.ingredients.every(ingredient => 
                    player.inventory.some(item => item.name === ingredient)
                );
                
                const recipeDiv = document.createElement('div');
                recipeDiv.className = 'recipe';
                recipeDiv.innerHTML = `
                    <div><strong>${{recipe.name}}</strong></div>
                    <div class="recipe-ingredients">Requires: ${{recipe.ingredients.join(', ')}}</div>
                    <div>Creates: ${{recipe.result}}</div>
                    <button onclick="craftItem('${{recipe.name}}')" ${{!canCraft ? 'disabled' : ''}}>
                        ${{canCraft ? 'Craft' : 'Missing Items'}}
                    </button>
                `;
                recipesContainer.appendChild(recipeDiv);
            }});
        }}

        function craftItem(recipeName) {{
            const recipe = currentInventoryData.crafting_recipes.find(r => r.name === recipeName);
            if (!recipe) return;
            
            // Check ingredients
            const hasAllIngredients = recipe.ingredients.every(ingredient => 
                player.inventory.some(item => item.name === ingredient)
            );
            
            if (hasAllIngredients) {{
                // Remove ingredients
                recipe.ingredients.forEach(ingredient => {{
                    const itemIndex = player.inventory.findIndex(item => item.name === ingredient);
                    if (itemIndex >= 0) {{
                        player.inventory.splice(itemIndex, 1);
                    }}
                }});
                
                // Add result
                player.inventory.push({{ name: recipe.result, description: "" }});
                showNotification(`Crafted ${{recipe.result}}!`);
                updateHud();
                openInventory(currentInventoryData); // Refresh display
            }}
        }}

        function closeInventory() {{
            document.getElementById('inventory-interface').classList.remove('active');
            if (currentInventoryData && currentInventoryData.continue_node) {{
                renderNode(currentInventoryData.continue_node);
            }}
        }}

        function handleDiceRollNode(nodeData) {{
            const optionsContainer = document.getElementById("options");
            const rollButton = document.createElement("button");
            rollButton.textContent = `🎲 Roll ${{nodeData.num_dice || 1}}d${{nodeData.num_sides || 6}} (Need ${{nodeData.success_threshold || 4}}+)`;
            rollButton.onclick = () => performDiceRoll(nodeData);
            optionsContainer.appendChild(rollButton);
        }}

        function performDiceRoll(nodeData) {{
            const numDice = nodeData.num_dice || 1;
            const numSides = nodeData.num_sides || 6;
            const threshold = nodeData.success_threshold || 4;
            
            let total = 0;
            let rolls = [];
            for (let i = 0; i < numDice; i++) {{
                const roll = Math.floor(Math.random() * numSides) + 1;
                rolls.push(roll);
                total += roll;
            }}
            
            const success = total >= threshold;
            const rollText = rolls.length > 1 ? ` (${{rolls.join(' + ')}})` : '';
            showNotification(`Rolled: ${{total}}${{rollText}} - ${{success ? 'Success!' : 'Failed!'}}`);
            
            setTimeout(() => {{
                const nextNode = success ? nodeData.success_node : nodeData.failure_node;
                if (nextNode) {{
                    renderNode(nextNode);
                }}
            }}, 1500);
        }}

        function handleCombatNode(nodeData) {{
            const optionsContainer = document.getElementById("options");
            const combatButton = document.createElement("button");
            combatButton.textContent = "⚔️ Begin Combat";
            combatButton.onclick = () => performCombat(nodeData);
            optionsContainer.appendChild(combatButton);
        }}

        function performCombat(nodeData) {{
            const playerPower = (player.stats.strength || 10) + (player.stats.defense || 5) + ((player.stats.health || 100) / 10);
            const randomFactor = Math.random() * 20 + 90; // 90-110%
            const finalPower = playerPower * (randomFactor / 100);
            const victory = finalPower > 50;
            
            showNotification(`Combat Power: ${{finalPower.toFixed(1)}} - ${{victory ? 'Victory!' : 'Defeat!'}}`);
            
            setTimeout(() => {{
                const nextNode = victory ? nodeData.successNode : nodeData.failNode;
                if (nextNode) {{
                    renderNode(nextNode);
                }}
            }}, 1500);
        }}

        function handleDialogueNode(nodeData) {{
            const optionsContainer = document.getElementById("options");
            
            // Handle auto-advance
            if (nodeData.auto_advance && nodeData.options && nodeData.options.length > 0) {{
                const nextNode = nodeData.options[0].nextNode;
                const delay = (nodeData.auto_advance_delay || 0) * 1000;
                if (delay > 0) {{
                    autoAdvanceTimer = setTimeout(() => renderNode(nextNode), delay);
                }} else if (nodeData.audio) {{
                    document.getElementById('audio-player').onended = () => renderNode(nextNode);
                }}
            }} else {{
                // Show dialogue options
                (nodeData.options || []).forEach(opt => {{
                    if (!checkConditions(opt.conditions)) return;
                    const button = document.createElement("button");
                    button.textContent = opt.text;
                    button.onclick = () => {{
                        applyEffects(opt.effects);
                        renderNode(opt.nextNode);
                    }};
                    optionsContainer.appendChild(button);
                }});
            }}
        }}

        function openShop(shopData) {{
            currentShopData = shopData;
            document.getElementById('shop-interface').classList.add('active');
            document.getElementById('modal-overlay').classList.add('active');
            document.getElementById('shop-currency-amount').textContent = gameState.variables[shopData.currency_variable] || 0;
            showShopTab('buy');
        }}

        function showShopTab(tabType) {{
            // Update tab appearance
            document.querySelectorAll('.shop-tab').forEach(tab => tab.classList.remove('active'));
            document.querySelector(`[onclick="showShopTab('${{tabType}}')"]`).classList.add('active');
            
            const shopItems = document.getElementById('shop-items');
            shopItems.innerHTML = '';
            
            if (tabType === 'buy') {{
                (currentShopData.items_for_sale || []).forEach(item => {{
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'shop-item';
                    itemDiv.innerHTML = `
                        <div class="shop-item-info">
                            <div class="shop-item-name">${{item.name}}</div>
                            <div class="shop-item-description">${{item.description || ''}}</div>
                        </div>
                        <div class="shop-item-price">${{item.price}} ${{currentShopData.currency_variable}}</div>
                        <button onclick="buyItem('${{item.name}}', ${{item.price}})">Buy</button>
                    `;
                    shopItems.appendChild(itemDiv);
                }});
            }} else {{
                (currentShopData.items_to_buy || []).forEach(buyItem => {{
                    const hasItem = player.inventory.some(item => item.name === buyItem.name);
                    if (hasItem) {{
                        const itemDiv = document.createElement('div');
                        itemDiv.className = 'shop-item';
                        itemDiv.innerHTML = `
                            <div class="shop-item-info">
                                <div class="shop-item-name">${{buyItem.name}}</div>
                                <div class="shop-item-description">${{buyItem.description || ''}}</div>
                            </div>
                            <div class="shop-item-price">${{buyItem.price}} ${{currentShopData.currency_variable}}</div>
                            <button onclick="sellItem('${{buyItem.name}}', ${{buyItem.price}})">Sell</button>
                        `;
                        shopItems.appendChild(itemDiv);
                    }}
                }});
                
                if (shopItems.children.length === 0) {{
                    shopItems.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 2em;">You have no items to sell</div>';
                }}
            }}
        }}

        function buyItem(itemName, price) {{
            const currency = gameState.variables[currentShopData.currency_variable] || 0;
            if (currency >= price) {{
                gameState.variables[currentShopData.currency_variable] = currency - price;
                player.inventory.push({{ name: itemName, description: "" }});
                showNotification(`Bought ${{itemName}} for ${{price}} ${{currentShopData.currency_variable}}!`);
                document.getElementById('shop-currency-amount').textContent = gameState.variables[currentShopData.currency_variable];
                updateHud();
                showShopTab('buy'); // Refresh display
            }} else {{
                showNotification(`Not enough ${{currentShopData.currency_variable}}! Need ${{price}}, have ${{currency}}`);
            }}
        }}

        function sellItem(itemName, price) {{
            const itemIndex = player.inventory.findIndex(item => item.name === itemName);
            if (itemIndex >= 0) {{
                player.inventory.splice(itemIndex, 1);
                gameState.variables[currentShopData.currency_variable] = (gameState.variables[currentShopData.currency_variable] || 0) + price;
                showNotification(`Sold ${{itemName}} for ${{price}} ${{currentShopData.currency_variable}}!`);
                document.getElementById('shop-currency-amount').textContent = gameState.variables[currentShopData.currency_variable];
                updateHud();
                showShopTab('sell'); // Refresh display
            }}
        }}

        function closeShop() {{
            document.getElementById('shop-interface').classList.remove('active');
            document.getElementById('modal-overlay').classList.remove('active');
            if (currentShopData && currentShopData.continue_node) {{
                renderNode(currentShopData.continue_node);
            }}
        }}

        function openInventory(inventoryData) {{
            currentInventoryData = inventoryData;
            document.getElementById('inventory-interface').classList.add('active');
            document.getElementById('modal-overlay').classList.add('active');
            showInventoryTab('items');
        }}

        function showInventoryTab(tabType) {{
            // Update tab appearance
            document.querySelectorAll('.inventory-tab').forEach(tab => tab.classList.remove('active'));
            document.querySelector(`[onclick="showInventoryTab('${{tabType}}')"]`).classList.add('active');
            
            if (tabType === 'items') {{
                document.getElementById('inventory-grid').style.display = 'grid';
                document.getElementById('crafting-recipes').style.display = 'none';
                showInventoryItems();
            }} else {{
                document.getElementById('inventory-grid').style.display = 'none';
                document.getElementById('crafting-recipes').style.display = 'block';
                showCraftingRecipes();
            }}
        }}

        function showInventoryItems() {{
            const inventoryGrid = document.getElementById('inventory-grid');
            inventoryGrid.innerHTML = '';
            
            if (player.inventory.length === 0) {{
                inventoryGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 2em;">Your inventory is empty</div>';
                return;
            }}
            
            player.inventory.forEach(item => {{
                const itemDiv = document.createElement('div');
                itemDiv.className = 'inventory-item';
                itemDiv.innerHTML = `
                    <div class="inventory-item-name">${{item.name}}</div>
                    <div class="inventory-item-description">${{item.description || ''}}</div>
                `;
                inventoryGrid.appendChild(itemDiv);
            }});
        }}

        function showCraftingRecipes() {{
            const recipesContainer = document.getElementById('crafting-recipes-list');
            recipesContainer.innerHTML = '';
            
            if (!currentInventoryData.crafting_recipes || currentInventoryData.crafting_recipes.length === 0) {{
                recipesContainer.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 2em;">No crafting recipes available</div>';
                return;
            }}
            
            currentInventoryData.crafting_recipes.forEach(recipe => {{
                const canCraft = recipe.ingredients.every(ingredient => 
                    player.inventory.some(item => item.name === ingredient)
                );
                
                const recipeDiv = document.createElement('div');
                recipeDiv.className = 'recipe';
                recipeDiv.innerHTML = `
                    <div class="recipe-name">${{recipe.name}}</div>
                    <div class="recipe-ingredients">Requires: ${{recipe.ingredients.join(', ')}}</div>
                    <div class="recipe-result">Creates: ${{recipe.result}}</div>
                    <button onclick="craftItem('${{recipe.name}}')" ${{!canCraft ? 'disabled' : ''}}>
                        ${{canCraft ? 'Craft' : 'Missing Items'}}
                    </button>
                `;
                recipesContainer.appendChild(recipeDiv);
            }});
        }}

        function craftItem(recipeName) {{
            const recipe = currentInventoryData.crafting_recipes.find(r => r.name === recipeName);
            if (!recipe) return;
            
            // Check ingredients
            const hasAllIngredients = recipe.ingredients.every(ingredient => 
                player.inventory.some(item => item.name === ingredient)
            );
            
            if (hasAllIngredients) {{
                // Remove ingredients
                recipe.ingredients.forEach(ingredient => {{
                    const itemIndex = player.inventory.findIndex(item => item.name === ingredient);
                    if (itemIndex >= 0) {{
                        player.inventory.splice(itemIndex, 1);
                    }}
                }});
                
                // Add result
                player.inventory.push({{ name: recipe.result, description: "" }});
                showNotification(`Crafted ${{recipe.result}}!`);
                updateHud();
                showCraftingRecipes(); // Refresh display
            }}
        }}

        function closeInventory() {{
            document.getElementById('inventory-interface').classList.remove('active');
            document.getElementById('modal-overlay').classList.remove('active');
            if (currentInventoryData && currentInventoryData.continue_node) {{
                renderNode(currentInventoryData.continue_node);
            }}
        }}

        function triggerRandomEvent(nodeData) {{
            if (!nodeData.random_outcomes || nodeData.random_outcomes.length === 0) return;
            
            // Calculate weighted random selection
            const totalWeight = nodeData.random_outcomes.reduce((sum, outcome) => sum + (outcome.weight || 1), 0);
            const randomValue = Math.random() * totalWeight;
            
            let currentWeight = 0;
            let selectedOutcome = null;
            
            for (const outcome of nodeData.random_outcomes) {{
                currentWeight += outcome.weight || 1;
                if (randomValue <= currentWeight) {{
                    selectedOutcome = outcome;
                    break;
                }}
            }}
            
            if (selectedOutcome) {{
                // Show outcome
                const outcomeDiv = document.createElement('div');
                outcomeDiv.className = 'random-outcome';
                outcomeDiv.innerHTML = `
                    <h3>Random Event Result</h3>
                    <p>${{selectedOutcome.description}}</p>
                `;
                document.getElementById('options').innerHTML = '';
                document.getElementById('options').appendChild(outcomeDiv);
                
                showNotification(`Random Event: ${{selectedOutcome.description}}`);
                
                // Navigate after delay
                setTimeout(() => {{
                    if (selectedOutcome.next_node) {{
                        renderNode(selectedOutcome.next_node);
                    }}
                }}, 2000);
            }}
        }}

        function skipTimer() {{
            if (timerInterval) {{
                clearInterval(timerInterval);
                const nodeData = dialogueData[currentNode];
                if (nodeData && nodeData.next_node) {{
                    renderNode(nodeData.next_node);
                }}
            }}
        }}

        function formatTime(seconds) {{
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return mins > 0 ? `${{mins}}:${{secs.toString().padStart(2, '0')}}` : secs.toString();
        }}

        function performDiceRoll(nodeData) {{
            const numDice = nodeData.num_dice || 1;
            const numSides = nodeData.num_sides || 6;
            const threshold = nodeData.success_threshold || 4;
            
            let total = 0;
            let rolls = [];
            for (let i = 0; i < numDice; i++) {{
                const roll = Math.floor(Math.random() * numSides) + 1;
                rolls.push(roll);
                total += roll;
            }}
            
            const success = total >= threshold;
            const rollText = rolls.length > 1 ? ` (${{rolls.join(' + ')}})` : '';
            showNotification(`Rolled: ${{total}}${{rollText}} - ${{success ? 'Success!' : 'Failed!'}}`);
            
            setTimeout(() => {{
                const nextNode = success ? nodeData.success_node : nodeData.failure_node;
                if (nextNode) {{
                    renderNode(nextNode);
                }}
            }}, 1500);
        }}

        function performCombat(nodeData) {{
            const playerPower = (player.stats.strength || 10) + (player.stats.defense || 5) + ((player.stats.health || 100) / 10);
            const randomFactor = Math.random() * 20 + 90; // 90-110%
            const finalPower = playerPower * (randomFactor / 100);
            const victory = finalPower > 50;
            
            showNotification(`Combat Power: ${{finalPower.toFixed(1)}} - ${{victory ? 'Victory!' : 'Defeat!'}}`);
            
            setTimeout(() => {{
                const nextNode = victory ? nodeData.successNode : nodeData.failNode;
                if (nextNode) {{
                    renderNode(nextNode);
                }}
            }}, 1500);
        }}
        function saveGame() {{
            try {{
                const saveData = {{
                    player: player,
                    gameState: gameState,
                    currentNode: currentNode
                }};
                localStorage.setItem('dvgSaveData', JSON.stringify(saveData));
                showNotification("Game Saved!");
            }} catch (e) {{
                console.error("Failed to save game:", e);
                showNotification("Error: Could not save game.");
            }}
        }}

        function loadGame() {{
            try {{
                const savedJSON = localStorage.getItem('dvgSaveData');
                if (savedJSON) {{
                    const saveData = JSON.parse(savedJSON);
                    player = saveData.player;
                    gameState = saveData.gameState;
                    currentNode = saveData.currentNode;
                    
                    if (!gameState.variables) gameState.variables = {{}};
                    
                    renderNode(currentNode);
                    showNotification("Game Loaded!");
                }} else {{
                    showNotification("No save data found.");
                }}
            }} catch (e) {{
                console.error("Failed to load game:", e);
                showNotification("Error: Could not load save data.");
            }}
        }}
        function handleShopNode(nodeData) {
            currentShopData = nodeData;
            const optionsContainer = document.getElementById("options");
    
            const shopButton = document.createElement("button");
            shopButton.textContent = "🏪 Enter Shop";
            shopButton.onclick = () => openShop(nodeData);
            optionsContainer.appendChild(shopButton);
    
            if (nodeData.continue_node) {
                const continueButton = document.createElement("button");
                continueButton.textContent = "Continue on your way";
                continueButton.onclick = () => renderNode(nodeData.continue_node);
                optionsContainer.appendChild(continueButton);
            }
        }

        function handleTimerNode(nodeData) {
            const optionsContainer = document.getElementById("options");
            const totalSeconds = nodeData.total_seconds || nodeData.wait_time || 5;
            let remainingSeconds = totalSeconds;
    
            const timerDiv = document.createElement('div');
            timerDiv.className = 'timer-interface';
    
            let timerHTML = `<div class="timer-display" id="timer-display">${formatTime     (remainingSeconds)}</div>`;
    
            if (nodeData.show_countdown !== false) {
                timerHTML += `<div class="timer-progress">
                    <div class="timer-progress-bar" id="timer-progress" style="width: 100%"></div>
                </div>`;
            }
    
            if (nodeData.allow_skip) {
                timerHTML += `<button onclick="skipTimer()">Skip Wait</button>`;
            }
    
            timerDiv.innerHTML = timerHTML;
            optionsContainer.appendChild(timerDiv);
    
            // Start countdown
            timerInterval = setInterval(() => {
                remainingSeconds--;
                document.getElementById('timer-display').textContent = formatTime       (remainingSeconds);
        
                const progressBar = document.getElementById('timer-progress');
                if (progressBar) {
                    const progress = (remainingSeconds / totalSeconds) * 100;
                    progressBar.style.width = Math.max(0, progress) + '%';
                }
        
                if (remainingSeconds <= 0) {
                    clearInterval(timerInterval);
                    if (nodeData.next_node) {
                        renderNode(nodeData.next_node);
                    }
                }
            }, 1000);
        }

        function handleInventoryNode(nodeData) {
            currentInventoryData = nodeData;
            const optionsContainer = document.getElementById("options");
    
            if (nodeData.auto_open) {
                openInventory(nodeData);
            } else {
                const inventoryButton = document.createElement("button");
                inventoryButton.textContent = "🎒 Open Inventory";
                inventoryButton.onclick = () => openInventory(nodeData);
                optionsContainer.appendChild(inventoryButton);
            }
    
            if (nodeData.continue_node) {
                const continueButton = document.createElement("button");
                continueButton.textContent = "Continue";
                continueButton.onclick = () => renderNode(nodeData.continue_node);
                optionsContainer.appendChild(continueButton);
            }
        }

        document.addEventListener('DOMContentLoaded', () => {{
            updateHud();
            renderNode('intro');

            const startOverlay = document.getElementById('start-overlay');
            startOverlay.addEventListener('click', () => {{
                startOverlay.style.display = 'none';
                const audioPlayer = document.getElementById('audio-player');
                if (audioPlayer.src && audioPlayer.paused) {{
                    audioPlayer.play().catch(e => console.error("Audio play failed:", e));
                }}
                const musicPlayer = document.getElementById('music-player');
                if (musicPlayer.src && musicPlayer.paused) {{
                    musicPlayer.play().catch(e => console.error("Music play failed:", e));
                }}
            }}, {{ once: true }});

            document.getElementById('save-button').addEventListener('click', saveGame);
            document.getElementById('load-button').addEventListener('click', loadGame);
            
            const hudToggle = document.getElementById('hud-toggle');
            const hudContainer = document.getElementById('hud-container');
            hudToggle.addEventListener('click', () => {{
                hudContainer.classList.toggle('open');
            }});
        }});

        // ========== FEATURE SYSTEMS IMPLEMENTATIONS ==========
        
        // Skill Check System
        class SkillCheckSystem {{
            constructor() {{
                this.activeModifiers = {{}};
                this.advantageSources = [];
                this.disadvantageSources = [];
            }}
            
            performSkillCheck(skillValue, difficulty, skillType = "general") {{
                let roll = Math.floor(Math.random() * 20) + 1;
                
                // Handle advantage/disadvantage
                if (this.advantageSources.length > 0 && this.disadvantageSources.length === 0) {{
                    const secondRoll = Math.floor(Math.random() * 20) + 1;
                    roll = Math.max(roll, secondRoll);
                }} else if (this.disadvantageSources.length > 0 && this.advantageSources.length === 0) {{
                    const secondRoll = Math.floor(Math.random() * 20) + 1;
                    roll = Math.min(roll, secondRoll);
                }}
                
                // Apply modifiers
                let totalModifier = skillValue;
                for (const [modType, modValue] of Object.entries(this.activeModifiers)) {{
                    if (modType === skillType || modType === "all") {{
                        totalModifier += modValue;
                    }}
                }}
                
                const finalValue = roll + totalModifier;
                const success = roll === 20 || finalValue >= difficulty;
                const criticalSuccess = roll === 20;
                const criticalFailure = roll === 1;
                
                return {{
                    success,
                    roll,
                    finalValue,
                    criticalSuccess,
                    criticalFailure,
                    margin: finalValue - difficulty
                }};
            }}
        }}
        
        // Reputation System
        class ReputationSystem {{
            constructor() {{
                this.reputations = featureData.reputation || {{}};
            }}
            
            modifyReputation(factionId, amount) {{
                if (!this.reputations[factionId]) {{
                    this.reputations[factionId] = 0;
                }}
                this.reputations[factionId] = Math.max(-100, Math.min(100, 
                    this.reputations[factionId] + amount));
            }}
            
            getReputationLevel(factionId) {{
                const value = this.reputations[factionId] || 0;
                if (value <= -51) return "Hostile";
                if (value <= -11) return "Unfriendly";
                if (value <= 10) return "Neutral";
                if (value <= 50) return "Friendly";
                return "Allied";
            }}
        }}
        
        // Loot System
        class LootSystem {{
            constructor() {{
                this.lootTables = featureData.loot_tables || {{}};
            }}
            
            rollLoot(tableId, luckModifier = 1.0) {{
                const table = this.lootTables[tableId];
                if (!table) return {{ items: [], gold: 0 }};
                
                const drops = {{ items: [], gold: 0 }};
                
                // Roll for items
                if (table.items && Math.random() < 0.7) {{
                    const item = this.selectWeightedItem(table.items, luckModifier);
                    if (item) drops.items.push(item);
                }}
                
                // Roll for gold
                if (table.goldRange) {{
                    const [min, max] = table.goldRange;
                    drops.gold = Math.floor((Math.random() * (max - min + 1) + min) * luckModifier);
                }}
                
                return drops;
            }}
            
            selectWeightedItem(items, luckModifier) {{
                const totalWeight = items.reduce((sum, item) => sum + (item.weight || 1) * 
                    (item.rarity === 'rare' || item.rarity === 'epic' || item.rarity === 'legendary' ? luckModifier : 1), 0);
                
                let rand = Math.random() * totalWeight;
                for (const item of items) {{
                    const weight = (item.weight || 1) * 
                        (item.rarity === 'rare' || item.rarity === 'epic' || item.rarity === 'legendary' ? luckModifier : 1);
                    if (rand <= weight) return item;
                    rand -= weight;
                }}
                return null;
            }}
        }}
        
        // Initialize feature systems
        const skillCheckSystem = new SkillCheckSystem();
        const reputationSystem = new ReputationSystem();
        const lootSystem = new LootSystem();
        
    </script>
</body>
</html>'''

        # Replace placeholders manually to avoid brace conflicts
        html_result = html_template.replace('{dialogue_data}', dialogue_data)
        html_result = html_result.replace('{player_data}', player_data)
        html_result = html_result.replace('{flags_data}', flags_data)
        html_result = html_result.replace('{quests_data}', quests_data)
        html_result = html_result.replace('{variables_data}', variables_data)
        html_result = html_result.replace('{enemies_data}', enemies_data or '{}')
        html_result = html_result.replace('{timers_data}', timers_data or '{}')
        html_result = html_result.replace('{feature_data}', feature_data or '{}')
        html_result = html_result.replace('{font_link}', font_link)
        html_result = html_result.replace('{font_css}', font_css)
        html_result = html_result.replace('{title_font_css}', title_font_css)
        html_result = html_result.replace('{background_css}', background_css)
        
        # Convert double braces back to single braces for CSS/JS (but be careful about order)
        # First handle spacing issues, then convert double braces
        html_result = html_result.replace('{ {', '{{')  # Fix spaced double braces
        html_result = html_result.replace('} }', '}}')  # Fix spaced double braces
        html_result = html_result.replace('{{', '{')
        html_result = html_result.replace('}}', '}')
        
        return html_result
    
    def _generate_background_css(self, background_setting):
        """Generate CSS for the background setting."""
        if background_setting:
            if background_setting.startswith("url(") or background_setting.startswith("linear-gradient("):
                return f"background: {background_setting}; background-size: cover; background-position: center;"
            else:
                return f"background: {background_setting};"
        else:
            return "background:linear-gradient(135deg,var(--bg-grad-start-default) 0%,var(--bg-grad-end-default) 100%);"