import os
import re
import json

# --- CONFIGURATION ---
# Path to the main ruleset file from the Dioxine_XPiratez folder
RUL_FILE = 'user/mods/Piratez/Ruleset/Piratez.rul'

# Paths to the language files from the Dioxine_XPiratez folder
LANG_FILES = {
    'en-US': 'user/mods/Piratez/Language/en-US.yml',
    'ru': 'user/mods/Piratez/Language/ru.yml'
}

HTML_OUTPUT = 'pirate_viewer_v35.html'
START_TECH = "STR_SCHOOLING_2" 
# ---------------------

def clean_ufo_text(text):
    if not text: return ""
    text = text.replace('{NEWLINE}', '\n').replace('\\n', '\n')
    text = re.sub(r'\{.*?\}', '', text)
    text = re.sub(r'<.*?>', '', text)
    return text.strip()

def parse_lang_file(filepath):
    lang, ufo = {}, {}
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8-sig', errors='replace') as f:
                content = f.read()
                matches = re.findall(r'^\s*(STR_[A-Z0-9_]+):\s*"(.*?)"', content, re.MULTILINE)
                for k, v in matches:
                    if k.endswith('_UFOPEDIA'):
                        ufo[k.replace('_UFOPEDIA', '')] = clean_ufo_text(v)
                    else:
                        lang[k] = v.replace('"', "'")
        except: pass
    return lang, ufo

def get_data():
    all_game_data = {}
    for code, path in LANG_FILES.items():
        l, u = parse_lang_file(path)
        if l: all_game_data[code] = [l, u]
    if not all_game_data: all_game_data['en-US'] = [{}, {}]
    
    # Check if the RUL file exists at the specified path
    if not os.path.exists(RUL_FILE):
        print(f"Error: File not found at {RUL_FILE}")
        return None, None
        
    try:
        with open(RUL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            c = f.read()
        # Parse technology entries
        entries = re.finditer(r'^\s*-\s+name:\s*(STR_[A-Z0-9_]+)(.*?)(?=^\s*-\s+name:|\Z)', c, re.DOTALL | re.MULTILINE)
        raw = {}
        for m in entries:
            t_id, b = m.group(1), m.group(2)
            if 'delete:' in b[:20]: continue
            def gl(k):
                f = re.search(rf'{k}:(.*?)(?=\n\s*[a-z]|$)', b, re.DOTALL)
                return re.findall(r'(STR_[A-Z0-9_]+)', f.group(1)) if f else []
            raw[t_id] = {"deps": list(set(gl("dependencies"))), "unlocks": list(set(gl("unlocks")))}
        return raw, all_game_data
    except Exception as e:
        print(f"Error: {e}"); return None, None

def generate_html(raw_data, game_langs_data):
    data_json = json.dumps(raw_data, ensure_ascii=False)
    langs_json = json.dumps(game_langs_data, ensure_ascii=False)
    opts = "".join([f'<option value="{c}" {"selected" if c=="en-US" else ""}>{c}</option>' for c in game_langs_data.keys()])

    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>X-Piratez Tech Viewer v35</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body { background: #f8f9fa; color: #212529; font-family: sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        #sidebar { width: 420px; background: #fff; border-right: 2px solid #343a40; padding: 20px; overflow-y: auto; z-index: 10; box-shadow: 2px 0 5px rgba(0,0,0,0.1); }
        #mynetwork { flex-grow: 1; background: #eaebed; }
        .ctrl-group { display: flex; align-items: center; justify-content: space-between; margin: 5px 0; background: #f1f3f5; padding: 5px; border-radius: 4px; }
        .step-btn { width: 30px; height: 30px; cursor: pointer; border: 1px solid #ccc; background: #fff; font-weight: bold; }
        input, select, button { width: 100%; padding: 10px; margin: 5px 0; box-sizing: border-box; border-radius: 4px; border: 1px solid #ccc; }
        .card { border: 1px solid #dee2e6; padding: 12px; margin-top: 12px; background: #fff; border-radius: 4px; }
        .ufo-desc { background: #fffbe6; padding: 10px; border-left: 4px solid #f1c40f; font-size: 0.85rem; white-space: pre-wrap; margin: 10px 0; }
        .tech-link { color: #007bff; text-decoration: underline; cursor: pointer; display: block; margin: 3px 0; font-size: 0.9rem; }
        #suggestions { position: absolute; background: white; border: 1px solid #ccc; width: 380px; z-index: 100; display: none; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .suggest-item { padding: 8px; cursor: pointer; border-bottom: 1px solid #eee; font-size: 0.85rem; }
        .suggest-item:hover { background: #f1f3f5; }
        .and-label { color: #007bff; font-weight: bold; }
        .or-label { color: #6f42c1; font-weight: bold; }
    </style>
</head>
<body>
    <div id="sidebar">
        <h2 id="ui-main-title">X-Piratez Viewer</h2>
        <div style="display:flex; gap:5px;">
            <select id="appLang" onchange="updateUI()"><option value="en">App: EN</option><option value="ru">App: RU</option></select>
            <select id="gameLang" onchange="syncAndDraw()">__OPTIONS__</select>
        </div>
        <button id="backBtn" style="display:none; background:#e74c3c; color:white; font-weight:bold;" onclick="goBack()">← BACK</button>
        <div style="position:relative;"><input type="text" id="search" placeholder="Search..." autocomplete="off"><div id="suggestions"></div></div>
        
        <label id="ui-label-depth">Depth: <span id="dv">3</span></label>
        <div class="ctrl-group">
            <button class="step-btn" onclick="adj('depthRange',-1)">-</button>
            <input type="range" id="depthRange" min="1" max="25" value="3" oninput="dv.innerText=this.value" onchange="updateUI()" style="flex-grow:1; margin:0 10px;">
            <button class="step-btn" onclick="adj('depthRange',1)">+</button>
        </div>

        <label id="ui-label-hub">Max List size: <span id="hv">5</span></label>
        <div class="ctrl-group">
            <button class="step-btn" onclick="adj('hubRange',-1)">-</button>
            <input type="range" id="hubRange" min="2" max="150" value="5" oninput="hv.innerText=this.value" onchange="updateUI()" style="flex-grow:1; margin:0 10px;">
            <button class="step-btn" onclick="adj('hubRange',1)">+</button>
        </div>

        <button id="ui-btn-rebuild" onclick="updateUI()" style="background:#343a40; color:white; font-weight:bold;">REBUILD GRAPH</button>
        <div id="info"></div>
    </div>
    <div id="mynetwork"></div>

    <script>
        const rawData = __DATA__;
        const gameLangs = __LANGS__;
        let network, history = [], currentTID = "__START_TID__";

        const ui_lexicon = {
            en: { title: "X-Piratez Viewer", depth: "Depth: ", hub: "Max List: ", rebuild: "REBUILD GRAPH", req: "Requires ALL (AND)", unl: "Unlocked by Any (OR)", back: "← BACK" },
            ru: { title: "X-Piratez Навигатор", depth: "Глубина: ", hub: "Макс. список: ", rebuild: "ПЕРЕСТРОИТЬ ГРАФ", req: "Требует ВСЕ (AND)", unl: "Открывается через (OR)", back: "← НАЗАД" }
        };

        function getTechLabel(id) {
            const langData = gameLangs[document.getElementById('gameLang').value] || [{},{}];
            return langData[0][id] || id;
        }

        function adj(id, v) {
            const el = document.getElementById(id);
            el.value = parseInt(el.value) + v;
            el.dispatchEvent(new Event('input'));
            updateUI();
        }

        function syncAndDraw() {
            document.getElementById('search').value = getTechLabel(currentTID) + " (" + currentTID + ")";
            updateUI();
        }

        function updateUI() {
            const lex = ui_lexicon[document.getElementById('appLang').value];
            document.getElementById('ui-main-title').innerText = lex.title;
            document.getElementById('ui-label-depth').firstChild.textContent = lex.depth;
            document.getElementById('ui-label-hub').firstChild.textContent = lex.hub;
            document.getElementById('ui-btn-rebuild').innerText = lex.rebuild;
            document.getElementById('backBtn').innerText = lex.back;
            draw();
        }

        function goToTech(id, saveHistory = true) {
            if(saveHistory && currentTID !== id) {
                history.push(getTechLabel(currentTID) + " (" + currentTID + ")");
                document.getElementById('backBtn').style.display = 'block';
            }
            currentTID = id;
            syncAndDraw();
        }

        function goBack() {
            if(!history.length) return;
            const prev = history.pop();
            const match = prev.match(/\\((STR_[A-Z0-9_]+)\\)/);
            if(match) currentTID = match[1];
            document.getElementById('search').value = prev;
            if(!history.length) document.getElementById('backBtn').style.display = 'none';
            updateUI();
        }

        function draw() {
            const val = document.getElementById('search').value;
            const match = val.match(/\\((STR_[A-Z0-9_]+)\\)/);
            const tid = match ? match[1] : Object.keys(rawData).find(id => id === val || getTechLabel(id) === val) || currentTID;
            
            currentTID = tid;
            const depth = parseInt(document.getElementById('depthRange').value);
            const hubLimit = parseInt(document.getElementById('hubRange').value);
            const nodes = [], edges = [], queue = [[tid, 0]], seen = new Set();

            while(queue.length > 0) {
                const [id, step] = queue.shift();
                if(seen.has(id)) continue;
                seen.add(id);

                nodes.push({ id: id, label: getTechLabel(id), shape: 'box', color: (id===tid?'#dc3545':'#fff'), font: {color:(id===tid?'#fff':'#000'), size:14} });
                
                if(step < depth && rawData[id]) {
                    const ds = rawData[id].deps;
                    const unlockers = [];
                    for(let k in rawData) if(rawData[k].unlocks.includes(id)) unlockers.push(k);

                    if (unlockers.length > 0) {
                        if(unlockers.length < hubLimit) unlockers.forEach(s => {
                            edges.push({from:s, to:id, color: '#6f42c1'});
                            queue.push([s, step+1]);
                        });
                    } else {
                        if(ds.length < hubLimit) ds.forEach(d => { 
                            edges.push({from:d, to:id, color: '#007bff'}); 
                            queue.push([d, step+1]); 
                        });
                    }
                }
            }
            if(network) network.destroy();
            network = new vis.Network(document.getElementById('mynetwork'), {nodes, edges}, {
                layout: { hierarchical: { direction:'DU', nodeSpacing: 350, levelSeparation: 200, sortMethod:'directed' } },
                physics: false,
                edges: { arrows:'to', smooth: { type:'cubicBezier', forceDirection:'vertical', roundness:0.4 } }
            });
            network.on("click", p => p.nodes[0] && showDetail(p.nodes[0]));
            network.on("doubleClick", p => p.nodes[0] && goToTech(p.nodes[0]));
            showDetail(tid);
        }

        function showDetail(id) {
            if(!rawData[id]) return;
            const lang = gameLangs[document.getElementById('gameLang').value] || [{},{}];
            const lex = ui_lexicon[document.getElementById('appLang').value];
            
            let h = "<h4>"+getTechLabel(id)+"</h4><p style='font-size:0.8em;color:#666'>"+id+"</p>";
            if(lang[1][id]) h += "<div class='ufo-desc'>"+lang[1][id]+"</div>";
            
            const unlockers = [];
            for(let key in rawData) if(rawData[key].unlocks.includes(id)) unlockers.push(key);
            
            const fmt = (list) => list.map(x => "<span class='tech-link' onclick='goToTech(\""+x+"\")'>"+getTechLabel(x)+"</span>").join('');
            
            if(unlockers.length > 0) {
                h += "<div class='card'><b class='or-label'>"+lex.unl+" ("+unlockers.length+"):</b>"+fmt(unlockers)+"</div>";
            } else {
                const deps = rawData[id].deps;
                if(deps && deps.length > 0) {
                    h += "<div class='card'><b class='and-label'>"+lex.req+" ("+deps.length+"):</b>"+fmt(deps)+"</div>";
                }
            }
            
            document.getElementById('info').innerHTML = h;
        }

        const sInput = document.getElementById('search'), sDiv = document.getElementById('suggestions');
        sInput.oninput = () => {
            const v = sInput.value.toLowerCase();
            if(v.length < 2) { sDiv.style.display='none'; return; }
            const matches = Object.keys(rawData).filter(id => id.toLowerCase().includes(v) || getTechLabel(id).toLowerCase().includes(v)).slice(0,10);
            sDiv.innerHTML = matches.map(m => "<div class='suggest-item' onclick='goToTech(\""+m+"\"); sDiv.style.display=\"none\";'>"+getTechLabel(m)+" ("+m+")</div>").join('');
            sDiv.style.display='block';
        };

        window.onload = syncAndDraw;
    </script>
</body>
</html>"""
        # Inject data and parameters into the HTML template
        html = html.replace('__OPTIONS__', opts).replace('__DATA__', data_json).replace('__LANGS__', langs_json).replace('__START_TID__', START_TECH)
        f.write(html)

if __name__ == "__main__":
    raw, langs = get_data()
    if raw:
        generate_html(raw, langs)
        print(f"v35 ready. Running from Dioxine_XPiratez folder.")
