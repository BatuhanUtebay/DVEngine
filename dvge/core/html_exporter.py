# dvge/core/html_exporter.py
import json
import base64
import os
from tkinter import filedialog, messagebox

def validate_project(app):
    """Checks the project for common errors before exporting."""
    errors, warnings = [], []
    if "intro" not in app.nodes:
        errors.append("Project must contain a node with the ID 'intro' to start.")
        return errors, warnings # Fatal error, no point in checking more

    reachable_nodes = set(["intro"])
    node_queue = ["intro"]
    
    # Breadth-first search to find all reachable nodes
    head = 0
    while head < len(node_queue):
        current_id = node_queue[head]
        head += 1
        node = app.nodes.get(current_id)
        if not node: continue
        
        for option in node.options:
            target_id = option.get("nextNode")
            if target_id and target_id in app.nodes and target_id not in reachable_nodes:
                reachable_nodes.add(target_id)
                node_queue.append(target_id)

    all_node_ids = set(app.nodes.keys())
    unreachable = all_node_ids - reachable_nodes
    if unreachable: warnings.append(f"Unreachable nodes found: {', '.join(unreachable)}")

    # Check for broken links
    for node_id, node in app.nodes.items():
        for i, option in enumerate(node.options):
            target_id = option.get('nextNode')
            if target_id and target_id not in all_node_ids and target_id != "[End Game]":
                errors.append(f"Node '{node_id}', Choice #{i+1}: Links to non-existent node '{target_id}'.")
    
    return errors, warnings

def export_game(app):
    """Exports the current project to a single, playable HTML file."""
    if not app.nodes: return messagebox.showwarning("Export Error", "Cannot export an empty project.")
    
    errors, warnings = validate_project(app)
    if errors or warnings:
        message = "Project validation found issues:\n\n"
        if errors: message += "ERRORS (must be fixed):\n" + "\n".join(errors) + "\n\n"
        if warnings: message += "WARNINGS (can be ignored):\n" + "\n".join(warnings) + "\n\n"
        if errors:
            messagebox.showerror("Validation Errors", message)
            return
        if not messagebox.askyesno("Validation Warnings", message + "Continue with export anyway?"):
            return

    dialogue_data = {}
    for node_id, node in app.nodes.items():
        game_data = node.to_dict()['game_data']
        # Embed image as Base64 data URI if it exists
        if game_data['backgroundImage'] and os.path.exists(game_data['backgroundImage']):
            try:
                with open(game_data['backgroundImage'], "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    game_data['backgroundImage'] = f"data:image/png;base64,{encoded_string}"
            except Exception as e:
                print(f"Could not process image for node {node_id}: {e}")
                game_data['backgroundImage'] = "" # Clear if there's an error
        else:
             game_data['backgroundImage'] = "" # Clear if path is invalid
        
        # Embed audio as Base64 data URI if it exists
        if game_data['audio'] and os.path.exists(game_data['audio']):
            try:
                with open(game_data['audio'], "rb") as audio_file:
                    encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
                    game_data['audio'] = f"data:audio/mpeg;base64,{encoded_string}"
            except Exception as e:
                print(f"Could not process audio for node {node_id}: {e}")
                game_data['audio'] = "" # Clear if there's an error
        else:
            game_data['audio'] = "" # Clear if path is invalid

        # Embed music as Base64 data URI if it exists
        if game_data['music'] and os.path.exists(game_data['music']):
            try:
                with open(game_data['music'], "rb") as music_file:
                    encoded_string = base64.b64encode(music_file.read()).decode('utf-8')
                    game_data['music'] = f"data:audio/mpeg;base64,{encoded_string}"
            except Exception as e:
                print(f"Could not process music for node {node_id}: {e}")
                game_data['music'] = "" # Clear if there's an error
        else:
            game_data['music'] = "" # Clear if path is invalid
        
        dialogue_data[node_id] = game_data

    dialogue_json_string = json.dumps(dialogue_data, indent=4)
    
    player_data = json.dumps({"stats": app.player_stats, "inventory": app.player_inventory}, indent=4)
    flags_data = json.dumps(app.story_flags, indent=4)
    quests_data = json.dumps({qid: q.to_dict() for qid, q in app.quests.items()}, indent=4)


    font_name = app.project_settings.get("font", "Merriweather")
    title_font_name = app.project_settings.get("title_font", "Special Elite")
    background_setting = app.project_settings.get("background", "").strip()

    font_url_name = font_name.replace(' ', '+')
    title_font_url_name = title_font_name.replace(' ', '+')
    font_link = f'<link href="https://fonts.googleapis.com/css2?family={font_url_name}:ital,wght@0,400;0,700;1,400&family={title_font_url_name}&display=swap" rel="stylesheet" />'

    font_css = f'--primary-font:"{font_name}",serif;'
    title_font_css = f'--title-font:"{title_font_name}",cursive;'

    background_css = ""
    if background_setting:
        if background_setting.startswith("url(") or background_setting.startswith("linear-gradient("):
            background_css = f"background: {background_setting}; background-size: cover; background-position: center;"
        else:
            background_css = f"background: {background_setting};"
    else:
        background_css = "background:linear-gradient(135deg,var(--bg-grad-start-default) 0%,var(--bg-grad-end-default) 100%);"
    
    html_template = """
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>My DVG Adventure</title><link rel="preconnect" href="https://fonts.googleapis.com" /><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />{font_link}
<script src="https://unpkg.com/@phosphor-icons/web"></script>
<style>
:root {{
    {font_css}{title_font_css}
    --bg-grad-start-default: #232526; --bg-grad-end-default: #414345;
    --text-light: #ECEFF1; --text-dark: #263238; --text-muted: #90A4AE;
    --accent-color: #80CBC4; --accent-dark: #004D40;
    --dialogue-bg: rgba(38, 50, 56, 0.9);
    --hud-bg: rgba(38, 50, 56, 0.95);
    --button-bg: #455A64; --button-hover-bg: #607D8B;
    --border-color: rgba(120, 144, 156, 0.3);
    --shadow-color: rgba(0,0,0,0.4);
    --success-color: #A5D6A7; --error-color: #EF9A9A;
    --quest-active-color: #F1C40F; --quest-completed-color: #2ECC71; --quest-failed-color: #E74C3C;
}}
body {{
    {background_css}
    margin:0; padding:0; font-family:var(--primary-font); color:var(--text-light); 
    min-height:100vh; transition:background 0.8s ease-in-out; 
    background-size: cover; background-position: center; background-attachment: fixed;
    overflow: hidden;
}}
body.theme-dream {{ --accent-color: #CE93D8; --accent-dark: #4A148C; }}
body.theme-ritual {{ --accent-color: #EF9A9A; --accent-dark: #B71C1C; }}

#game-container {{ display:flex; flex-direction:column; min-height:100vh; position:relative; }}

#dialogue-box {{
    position:fixed; bottom:2em; left:50%; transform:translateX(-50%);
    width:90%; max-width:800px; background:var(--dialogue-bg);
    border-radius:12px; padding:1.5em 2em; box-shadow:0 10px 30px var(--shadow-color);
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

#hud-toggle {{
    position: fixed; top: 20px; left: 20px; z-index: 101;
    background: var(--hud-bg); color: var(--text-light);
    border: 1px solid var(--border-color); border-radius: 50%;
    width: 50px; height: 50px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8em; transition: all 0.3s ease;
}}
#hud-toggle:hover {{ background: var(--accent-dark); color: white; }}

#hud-container {{
    position: fixed; top: 0; left: -350px; width: 320px; height: 100%;
    background: var(--hud-bg); padding: 20px;
    box-shadow: 5px 0 25px var(--shadow-color);
    transition: left 0.4s ease-in-out; z-index: 100;
    overflow-y: auto; border-right: 1px solid var(--border-color);
}}
#hud-container.open {{ left: 0; }}
.hud-section {{ margin-bottom: 1.5em; }}
.hud-section h3 {{
    font-family: var(--title-font); color: var(--accent-color);
    margin-top: 0; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5em;
    display: flex; align-items: center; gap: 0.5em; font-size: 1.4em;
}}
.stat-line, .inventory-line, .quest-line {{
    display: flex; justify-content: space-between; align-items: center;
    margin: 0.6em 0; padding: 0.4em; border-radius: 4px;
    transition: background-color 0.2s;
}}
.inventory-item, .quest-line {{ cursor: help; }}
.inventory-item:hover, .quest-line:hover {{ background-color: rgba(255,255,255,0.05); }}
.quest-line.active {{ border-left: 3px solid var(--quest-active-color); }}
.quest-line.completed {{ border-left: 3px solid var(--quest-completed-color); text-decoration: line-through; color: var(--text-muted);}}
.quest-line.failed {{ border-left: 3px solid var(--quest-failed-color); text-decoration: line-through; color: var(--text-muted);}}


#save-load-buttons {{ position: fixed; top: 20px; right: 20px; z-index: 101; }}
#save-load-buttons button {{
    margin-left: 10px; padding: 10px 18px; font-size: 1em;
    background: var(--button-bg); color: var(--text-light);
    border: 1px solid var(--border-color); border-radius: 8px;
    cursor: pointer; transition: all 0.2s ease;
}}
#save-load-buttons button:hover {{ background: var(--button-hover-bg); }}

.notification {{
    position:fixed; bottom:2em; right:2em; background:var(--hud-bg);
    color:var(--text-light); padding:1em 1.5em; border-radius:8px;
    z-index:200; animation:fadeInOut 4s ease-in-out forwards;
    border-left:4px solid var(--accent-color);
}}
@keyframes fadeInOut {{ 0%,100% {{ opacity:0; transform:translateY(20px); }} 10%,90% {{ opacity:1; transform:translateY(0); }} }}

.chapter-transition {{
    position:fixed; top:0; left:0; width:100%; height:100%;
    background:rgba(5,5,10,0.99); color:var(--text-light);
    display:flex; justify-content:center; align-items:center; flex-direction: column;
    z-index:1000; font-size:2.5em; text-align:center; font-family:var(--title-font);
    opacity:0; animation:chapterFade 4s ease-in-out forwards;
}}
.chapter-transition small {{ font-size: 0.5em; margin-top: 1em; font-family: var(--primary-font); font-style: italic; opacity: 0.8; }}
@keyframes chapterFade {{ 0%,100% {{ opacity:0; }} 20%,80% {{ opacity:1; }} }}

#start-overlay {{
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.85); color: white;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    z-index: 2000; cursor: pointer; backdrop-filter: blur(5px);
}}
#start-overlay h1 {{ font-size: 4em; font-family: var(--title-font); margin-bottom: 0.2em; }}
#start-overlay p {{ font-size: 1.2em; }}
</style></head><body>
<div id="game-container">
    <div id="hud-toggle"><i class="ph-fill ph-backpack"></i></div>
    <div id="hud-container"></div>
    <div id="save-load-buttons">
        <button id="save-button" title="Save Progress"><i class="ph-fill ph-floppy-disk"></i></button>
        <button id="load-button" title="Load Progress"><i class="ph-fill ph-folder-open"></i></button>
    </div>
    <div id="dialogue-box">
        <div id="npc-name"></div>
        <div id="dialogue-text"></div>
        <div id="options"></div>
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
let currentNode = "intro", previousBackgroundTheme = "theme-default", gameState = {{ currentChapter:"", flags:{flags_data}, quests:{quests_data} }};
let autoAdvanceTimer = null;

function updateHud() {{
    const hud = document.getElementById('hud-container');
    let statsHTML = `<div class="hud-section"><h3><i class="ph-fill ph-heartbeat"></i> Stats</h3>`;
    for(const stat in player.stats){{
        statsHTML+=`<div class="stat-line"><span>${{stat.charAt(0).toUpperCase()+stat.slice(1)}}:</span> <span>${{player.stats[stat]}}</span></div>`;
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

function showNotification(message,duration=3000){{
    const n=document.createElement("div");
    n.className="notification";
    n.textContent=message;
    document.body.appendChild(n);
    setTimeout(()=>{{if(n.parentNode)n.remove()}},duration);
}}

function showChapterTransition(name){{
    const t=document.createElement("div");
    t.className="chapter-transition";
    t.innerHTML=`<div>${{name}}</div><small>A New Chapter Begins</small>`;
    document.body.appendChild(t);
    setTimeout(()=>{{if(t.parentNode)t.remove()}},4000);
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
        document.body.style.backgroundImage = ''; // Clear if no image
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
        }}
    }});
    updateHud();
}}

function renderNode(key){{ 
    if (autoAdvanceTimer) clearTimeout(autoAdvanceTimer);
    if (key === '[End Game]') {{
        document.getElementById('dialogue-text').textContent = 'The story ends here.';
        document.getElementById('options').innerHTML = '';
        document.getElementById('npc-name').textContent = 'Game Over';
        return;
    }}
    const nodeData=dialogueData[key];
    if(!nodeData){{console.error("Node not found:",key);return;}}
    currentNode=key;
    setBackground(nodeData);
    updateHud();

    const audioPlayer = document.getElementById('audio-player');
    if (nodeData.audio) {{
        audioPlayer.src = nodeData.audio;
        audioPlayer.play().catch(e => {{
            console.log("Autoplay was prevented. Audio will start on first interaction.");
        }});
    }} else {{
        audioPlayer.src = "";
    }}

    const musicPlayer = document.getElementById('music-player');
    if (nodeData.music && musicPlayer.src !== nodeData.music) {{
        musicPlayer.src = nodeData.music;
        musicPlayer.play().catch(e => {{
            console.log("Autoplay was prevented. Music will start on first interaction.");
        }});
    }} else if (!nodeData.music) {{
        musicPlayer.src = "";
        musicPlayer.pause();
    }}


    if(nodeData.chapter&&nodeData.chapter!==gameState.currentChapter){{
        gameState.currentChapter=nodeData.chapter;
        showChapterTransition(nodeData.chapter);
    }}
    document.getElementById("npc-name").textContent=nodeData.npc;
    document.getElementById("dialogue-text").textContent=nodeData.text;
    const o=document.getElementById("options");
    o.innerHTML="";

    if (nodeData.auto_advance && nodeData.options && nodeData.options.length > 0) {{
        const nextNode = nodeData.options[0].nextNode;
        const delay = nodeData.auto_advance_delay * 1000;
        if (delay > 0) {{
            autoAdvanceTimer = setTimeout(() => renderNode(nextNode), delay);
        }} else if (nodeData.audio) {{
            audioPlayer.onended = () => renderNode(nextNode);
        }}
    }} else if (nodeData.node_type === "DiceRoll") {{
        const b=document.createElement("button");
        b.textContent=`Roll ${{{nodeData.num_dice}}}d${{{nodeData.num_sides}}}`;
        b.onclick=()=>{{
            let total = 0;
            for(let i=0; i < nodeData.num_dice; i++){{
                total += Math.floor(Math.random() * nodeData.num_sides) + 1;
            }}
            showNotification(`You rolled a ${{total}}`);
            if(total >= nodeData.success_threshold){{
                renderNode(nodeData.success_node);
            }} else {{
                renderNode(nodeData.failure_node);
            }}
        }};
        o.appendChild(b);
    }} else {{
        (nodeData.options||[]).forEach(opt=>{{
            if(!checkConditions(opt.conditions)) return;
            const b=document.createElement("button");
            b.textContent=opt.text;
            b.onclick=()=>{{
                applyEffects(opt.effects);
                renderNode(opt.nextNode);
            }};
            o.appendChild(b);
        }});
    }}
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

document.addEventListener('DOMContentLoaded',()=>{{
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
</script></body></html>
"""
    final_html = html_template.format(
        dialogue_data=dialogue_json_string, 
        player_data=player_data,
        flags_data=flags_data,
        quests_data=quests_data,
        font_link=font_link,
        font_css=font_css,
        title_font_css=title_font_css,
        background_css=background_css
    )

    filepath = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Game Files", "*.html")])
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f: f.write(final_html)
        messagebox.showinfo("Export Successful", f"Game successfully exported to {os.path.basename(filepath)}")
