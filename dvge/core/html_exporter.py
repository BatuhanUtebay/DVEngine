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
        
        dialogue_data[node_id] = game_data

    dialogue_json_string = json.dumps(dialogue_data, indent=4)
    
    player_data = json.dumps({"stats": app.player_stats, "inventory": app.player_inventory}, indent=4)
    flags_data = json.dumps(app.story_flags, indent=4)

    font_name = app.project_settings.get("font", "Merriweather")
    title_font_name = app.project_settings.get("title_font", "Special Elite")
    background_setting = app.project_settings.get("background", "").strip()

    font_url_name = font_name.replace(' ', '+')
    title_font_url_name = title_font_name.replace(' ', '+')
    font_link = f'<link href="https://fonts.googleapis.com/css2?family={font_url_name}:ital,wght@0,400;0,700&family={title_font_url_name}&display=swap" rel="stylesheet" />'

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
<style>
:root {{
    {font_css}{title_font_css}
    --text-dark:#b0bec5;--text-light:#263238;--text-hud:#90a4ae;--text-accent:#ffcdd2;--bg-grad-start-default:#263238;--bg-grad-end-default:#102027;--current-bg-grad-start:var(--bg-grad-start-default);--current-bg-grad-end:var(--bg-grad-end-default);--hud-bg:rgba(0,10,15,0.88);--dialogue-box-bg:rgba(207,216,220,0.97);--npc-name-bg-default:linear-gradient(135deg,#455a64,#37474f);--dialogue-text-bg-default:rgba(176,190,197,0.9);--button-bg-default:linear-gradient(135deg,#546e7a,#455a64);--button-bg-hover-default:linear-gradient(135deg,#607d8b,#546e7a);--button-skill-bg-default:linear-gradient(135deg,#6d4c41,#5d4037);--border-light:rgba(120,144,156,0.4);--shadow-color:rgba(0,0,0,0.6);--highlight-color-default:#80cbc4;--current-npc-name-bg:var(--npc-name-bg-default);--current-dialogue-text-bg:var(--dialogue-text-bg-default);--current-button-bg:var(--button-bg-default);--current-button-hover-bg:var(--button-bg-hover-default);--current-button-skill-bg:var(--button-skill-bg-default);--current-highlight-color:var(--highlight-color-default);
}}
body {{
    {background_css}
    margin:0;padding:0;font-family:var(--primary-font);color:var(--text-dark);min-height:100vh;transition:background 1s ease-in-out; background-size: cover; background-position: center; background-attachment: fixed;
}}
body.theme-dream {{
    --current-bg-grad-start:#300032;--current-bg-grad-end:#000010;--current-npc-name-bg:linear-gradient(135deg,#5c004b,#4a003b);--current-highlight-color:#e1bee7;--current-dialogue-text-bg:rgba(50,30,60,0.9);
}}
body.theme-ritual {{
    --current-bg-grad-start:#5f0000;--current-bg-grad-end:#200000;--current-npc-name-bg:linear-gradient(135deg,#8f0000,#7f0000);--current-highlight-color:#ff8a80;--current-dialogue-text-bg:rgba(70,20,20,0.9);
}}
#game-container {{ display:flex;flex-direction:column;min-height:100vh;position:relative; }}
#story-header {{ text-align:center;padding:1.5em 1em;background:rgba(0,0,0,0.25);border-bottom:1px solid var(--border-light); }}
#story-title {{ font-family:var(--title-font);font-size:2.5em;margin:0; }}
#hud {{ position:fixed;top:1.5em;left:1.5em;background:var(--hud-bg);color:var(--text-hud);padding:1em 1.2em;border-radius:8px;box-shadow:0 4px 15px var(--shadow-color);min-width:270px;z-index:100;border:1px solid var(--border-light); }}
.stat-line {{ display:flex;justify-content:space-between;margin:0.4em 0; }}
#inventory {{ margin-top:0.8em;padding-top:0.7em;border-top:1px solid var(--border-light); }}
#dialogue-box {{ position:fixed;bottom:1.5em;left:50%;transform:translateX(-50%);width:90%;max-width:720px;background:var(--dialogue-box-bg);border-radius:10px;padding:1.2em 1.5em;box-shadow:0 8px 25px var(--shadow-color); z-index: 50;}}
#npc-name {{ font-family:var(--title-font);font-size:1.35em;margin-bottom:0.8em;color:var(--text-dark);text-align:center;padding:0.5em;background:var(--current-npc-name-bg);border-radius:6px; }}
#dialogue-text {{ font-size:1.1em;line-height:1.65;margin-bottom:1.2em;background:var(--current-dialogue-text-bg);padding:1em;border-radius:6px;border-left:4px solid var(--current-highlight-color);color:var(--text-light);min-height:60px; }}
#options {{ display:flex;flex-direction:column;gap:0.8em; }}
#options button {{ padding:0.8em 1.2em;border:none;background:var(--current-button-bg);color:var(--text-dark);border-radius:6px;cursor:pointer;font-size:0.95em;transition:all 0.2s ease-out;text-align:left; }}
#options button:hover {{ background:var(--current-button-hover-bg);transform:translateY(-2px); }}
#options button:disabled {{ opacity:0.5;cursor:not-allowed;filter:grayscale(70%); }}
.notification {{ position:fixed;top:1.5em;right:1.5em;background:var(--hud-bg);color:var(--text-hud);padding:0.8em 1.2em;border-radius:6px;z-index:200;animation:fadeInOut 3s ease-in-out forwards;border-left:3px solid var(--current-highlight-color); }}
@keyframes fadeInOut {{ 0%,100% {{ opacity:0;transform:translateX(100%); }} 10%,90% {{ opacity:1;transform:translateX(0); }} }}
.chapter-transition {{ position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(5,5,10,0.99);color:#b0bec5;display:flex;justify-content:center;align-items:center;z-index:1000;font-size:2em;text-align:center;font-family:var(--title-font);opacity:0;animation:chapterFade 3s ease-in-out forwards; }}
@keyframes chapterFade {{ 0%,100% {{ opacity:0; }} 25%,75% {{ opacity:1; }} }}
</style></head><body><div id="game-container"><div id="story-header"><h1 id="story-title">My DVG Adventure</h1></div><div id="hud"></div><div id="dialogue-box"><div id="npc-name"></div><div id="dialogue-text"></div><div id="options"></div></div></div>
<script>
const dialogueData = {dialogue_data};
const player = {player_data};
let currentNode = "intro", previousBackgroundTheme = "theme-default", gameState = {{ currentChapter:"", flags:{flags_data} }};

function updatePlayerStats() {{
    const hud=document.getElementById('hud');
    let statsHTML=`<h3>Player</h3>`;
    for(const stat in player.stats){{
        statsHTML+=`<div class="stat-line"><span>${{stat.charAt(0).toUpperCase()+stat.slice(1)}}:</span> <span>${{player.stats[stat]}}</span></div>`;
    }}
    statsHTML+=`<div id="inventory"><strong>Inventory:</strong><div>${{player.inventory.join(", ")||"Empty"}}</div></div>`;
    hud.innerHTML=statsHTML;
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
    t.innerHTML=`<div>${{name}}</div>`;
    document.body.appendChild(t);
    setTimeout(()=>{{if(t.parentNode)t.remove()}},3000);
}}

function setBackground(nodeData) {{
    if (nodeData.backgroundImage) {{
        document.body.className = '';
        document.body.style.background = `url(${{nodeData.backgroundImage}})`;
        document.body.style.backgroundSize = 'cover';
        document.body.style.backgroundPosition = 'center';
        document.body.style.backgroundAttachment = 'fixed';
    }} else {{
        document.body.style.background = '';
        let themeName = nodeData.backgroundTheme || 'theme-default';
        if (!document.body.classList.contains(themeName)) {{
            document.body.className = '';
            document.body.classList.add(themeName);
        }}
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
                const hasItem = player.inventory.includes(subject);
                return operator === 'has' ? hasItem : !hasItem;
            case 'flag':
                const flagValue = gameState.flags[subject];
                if (flagValue === undefined) return false;
                const comparisonValue = (value === true || String(value).toLowerCase() === 'true');
                return operator === 'is' ? (flagValue === comparisonValue) : (flagValue !== comparisonValue);
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
                if (operator === 'add' && !player.inventory.includes(subject)) {{
                    player.inventory.push(subject);
                    showNotification(`Added '${{subject}}' to inventory.`);
                }} else if (operator === 'remove') {{
                    const index = player.inventory.indexOf(subject);
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
        }}
    }});
    updatePlayerStats();
}}

function renderNode(key){{ 
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
    updatePlayerStats();
    if(nodeData.chapter&&nodeData.chapter!==gameState.currentChapter){{
        gameState.currentChapter=nodeData.chapter;
        showChapterTransition(nodeData.chapter);
    }}
    document.getElementById("npc-name").textContent=nodeData.npc;
    document.getElementById("dialogue-text").textContent=nodeData.text;
    const o=document.getElementById("options");
    o.innerHTML="";
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

document.addEventListener('DOMContentLoaded',()=>{{
    updatePlayerStats();
    renderNode('intro');
}});
</script></body></html>
"""
    final_html = html_template.format(
        dialogue_data=dialogue_json_string, 
        player_data=player_data,
        flags_data=flags_data,
        font_link=font_link,
        font_css=font_css,
        title_font_css=title_font_css,
        background_css=background_css
    )

    filepath = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Game Files", "*.html")])
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f: f.write(final_html)
        messagebox.showinfo("Export Successful", f"Game successfully exported to {os.path.basename(filepath)}")
