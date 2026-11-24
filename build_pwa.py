"""Generate the self-contained Framing Factory Planner PWA (docs/index.html) embedding the exported project data."""
import json
import os
import framing_engine as fe

ROOT = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(ROOT, "docs", "project_data.json")
HTML_PATH = os.path.join(ROOT, "docs", "index.html")


def build_html():
    data = fe.export_project_json(JSON_PATH)
    data_js = json.dumps(data)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0f172a">
<title>Framing Factory Planner — Doyle's Contracting System</title>
<link rel="manifest" href="manifest.json">
<style>
  :root {{
    --bg: #0f172a; --card: #1e293b; --border: #334155; --text: #f8fafc;
    --muted: #94a3b8; --accent: #ea580c; --green: #16a34a; --blue: #2563eb;
    --purple: #7c3aed; --red: #dc2626; --amber: #d97706;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.45;
  }}
  header {{
    background: #020617; border-bottom: 2px solid var(--accent);
    padding: 16px 20px; position: sticky; top: 0; z-index: 20;
  }}
  .hdr-top {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px; max-width: 1200px; margin: 0 auto; }}
  h1 {{ margin: 0; font-size: 20px; letter-spacing: 0.3px; }}
  .sub {{ color: var(--muted); font-size: 13px; margin-top: 2px; }}
  .btn {{
    background: var(--accent); color: #fff; border: none; padding: 9px 15px;
    border-radius: 7px; font-weight: 700; font-size: 13px; cursor: pointer;
  }}
  .btn.sec {{ background: #334155; }}
  .btn.grn {{ background: var(--green); }}
  .wrap {{ max-width: 1200px; margin: 0 auto; padding: 18px 16px 60px; }}
  .goal-banner {{
    background: linear-gradient(90deg, #1e293b, #0f172a);
    border-left: 5px solid var(--accent); border: 1px solid var(--border);
    border-left-width: 6px; border-left-color: var(--accent);
    padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; font-size: 14px;
  }}
  .legend-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 10px; margin-bottom: 18px;
  }}
  .leg-card {{
    background: var(--card); border: 1px solid var(--border); border-radius: 8px;
    padding: 10px 12px; border-top: 4px solid #fff; font-size: 12.5px;
  }}
  .leg-title {{ font-weight: 700; font-size: 13.5px; margin-bottom: 3px; }}
  .tabs {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }}
  .tab {{
    background: var(--card); color: var(--text); border: 1px solid var(--border);
    padding: 9px 16px; border-radius: 7px; font-weight: 700; cursor: pointer; font-size: 13.5px;
  }}
  .tab.active {{ background: var(--accent); border-color: var(--accent); color: #fff; }}
  .wall-selector {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }}
  .w-pill {{
    padding: 8px 13px; border-radius: 7px; border: 2px solid var(--border);
    background: var(--card); color: var(--text); cursor: pointer; font-weight: 700; font-size: 13px;
  }}
  .w-pill.active {{ outline: 2px solid #fff; }}
  .card {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 16px; margin-bottom: 16px;
  }}
  .callout-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px; margin: 12px 0 16px;
  }}
  .stat {{
    background: #020617; border: 1px solid var(--border); border-radius: 8px;
    padding: 10px 14px;
  }}
  .stat .lbl {{ color: var(--muted); font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.6px; }}
  .stat .val {{ font-size: 21px; font-weight: 800; margin-top: 3px; color: #38bdf8; }}
  .stat .val.go {{ color: #4ade80; }}
  .goofy {{
    background: rgba(220, 38, 38, 0.16); border: 2px solid #ef4444;
    color: #fecaca; padding: 12px 15px; border-radius: 8px; margin: 12px 0;
    font-weight: 600; font-size: 13.5px;
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }}
  th, td {{ border: 1px solid var(--border); padding: 8px 10px; text-align: left; }}
  th {{ background: #020617; color: #cbd5e1; font-size: 12px; text-transform: uppercase; }}
  .badge {{
    display: inline-block; padding: 2px 8px; border-radius: 5px; font-weight: 700; font-size: 11.5px;
  }}
  .b-ver {{ background: rgba(22, 163, 74, 0.25); color: #86efac; border: 1px solid #16a34a; }}
  .b-old {{ background: rgba(148, 163, 184, 0.15); color: #94a3b8; text-decoration: line-through; margin-left: 6px; }}
  .tape-strip {{
    display: flex; flex-wrap: wrap; gap: 6px; background: #020617;
    padding: 12px; border-radius: 8px; border: 1px solid var(--border);
  }}
  .tick {{
    background: #1e293b; border: 1px solid #475569; padding: 4px 8px;
    border-radius: 5px; font-family: monospace; font-size: 12.5px;
  }}
  .tick.first {{ background: #14532d; border-color: #22c55e; color: #bbf7d0; font-weight: 700; }}
  .form-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; margin-bottom: 12px; }}
  input, select {{
    width: 100%; padding: 8px 10px; border-radius: 6px; border: 1px solid var(--border);
    background: #020617; color: var(--text); font-size: 13.5px;
  }}
  label {{ font-size: 12px; color: var(--muted); display: block; margin-bottom: 4px; font-weight: 600; }}
  @media print {{
    body {{ background: #fff; color: #000; }}
    header, .tabs, .wall-selector, .no-print {{ display: none !important; }}
    .card, .stat {{ background: #fff; border: 1px solid #000; color: #000; }}
    .goofy {{ background: #fee2e2; color: #7f1d1d; border: 2px solid #dc2626; }}
    th {{ background: #e2e8f0; color: #000; }}
    th, td {{ border: 1px solid #000; color: #000; }}
  }}
</style>
</head>
<body>
<header>
  <div class="hdr-top">
    <div>
      <h1>FRAMING FACTORY PLANNER — DOYLE'S CONTRACTING SYSTEM</h1>
      <div class="sub">Left-End "X &amp; Go" Plate Layout &middot; Order-Packet Verified Openings &middot; Pre-Made Header/Shoulder Batches &middot; Crew Work Cards</div>
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap">
      <button class="btn grn" id="installBtn" style="display:none" onclick="installApp()">Install Crew App</button>
      <button class="btn sec" onclick="window.print()">Print Active Crew Sheet</button>
    </div>
  </div>
</header>

<div class="wrap">
  <div class="goal-banner" id="goalBanner"></div>

  <div class="legend-grid" id="legendGrid"></div>

  <div class="tabs">
    <button class="tab active" onclick="showTab('walls', this)">1. Crew Wall Pull Sheets (Left-End Tape)</button>
    <button class="tab" onclick="showTab('batches', this)">2. Cut Bench: Grouped Headers &amp; Pre-Made Shoulders</button>
    <button class="tab" onclick="showTab('windows', this)">3. Window &amp; Door Order Verification Schedule</button>
    <button class="tab" onclick="showTab('custom', this)">4. Custom Wall / "X &amp; Go" Calculator</button>
    <button class="tab" onclick="showTab('qc', this)">5. Municipal Framing Pre-Inspection Checklist</button>
  </div>

  <div id="tab-walls">
    <div class="wall-selector" id="wallPills"></div>
    <div id="activeWallCard"></div>
  </div>

  <div id="tab-batches" style="display:none"></div>
  <div id="tab-windows" style="display:none"></div>
  <div id="tab-custom" style="display:none"></div>
  <div id="tab-qc" style="display:none"></div>
</div>

<script>
const DATA = {data_js};
let currentWallIdx = 0;
let deferredPrompt = null;

window.addEventListener('beforeinstallprompt', (e) => {{
  e.preventDefault();
  deferredPrompt = e;
  document.getElementById('installBtn').style.display = 'inline-block';
}});

function installApp() {{
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
}}

if ('serviceWorker' in navigator) {{
  navigator.serviceWorker.register('./sw.js').catch(() => {{}});
}}

function init() {{
  document.getElementById('goalBanner').innerHTML =
    `<strong>PROJECT:</strong> ${{DATA.project_name}}<br><strong>TODAY'S CREW GOAL:</strong> ${{DATA.daily_goal}}`;

  const leg = document.getElementById('legendGrid');
  leg.innerHTML = Object.values(DATA.color_legend).map(c => `
    <div class="leg-card" style="border-top-color:${{c.hex}}">
      <div class="leg-title" style="color:${{c.hex}}">${{c.color}} Highlight — ${{c.wall_height_label}}</div>
      <div>${{c.meaning}}</div>
    </div>
  `).join('');

  renderWallPills();
  renderActiveWall();
  renderBatches();
  renderWindowSchedule();
  renderCustomCalculator();
  renderChecklist();
}}

function showTab(name, btn) {{
  ['walls','batches','windows','custom','qc'].forEach(t => {{
    document.getElementById('tab-' + t).style.display = (t === name) ? 'block' : 'none';
  }});
  document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}}

function renderWallPills() {{
  const box = document.getElementById('wallPills');
  box.innerHTML = DATA.walls.map((w, idx) => `
    <button class="w-pill ${{idx === currentWallIdx ? 'active' : ''}}"
            style="border-color:${{w.color_info.hex}}"
            onclick="selectWall(${{idx}})">
      <span style="color:${{w.color_info.hex}}">&#9632;</span> ${{w.wall_id}}: ${{w.name}}
    </button>
  `).join('');
}}

function selectWall(idx) {{
  currentWallIdx = idx;
  renderWallPills();
  renderActiveWall();
}}

function renderActiveWall() {{
  const w = DATA.walls[currentWallIdx];
  const box = document.getElementById('activeWallCard');

  const goofyHtml = w.goofy_alert
    ? `<div class="goofy">&#9888; FIELD HEADS-UP / GOOFY AREA: ${{w.goofy_alert}}</div>`
    : '';

  const openingsRows = w.openings.map(op => `
    <tr>
      <td>
        <strong style="font-size:15px;color:#38bdf8">${{op.label}}</strong>
        <span class="badge b-old">Plan: ${{op.plan_old_code}}</span><br>
        <span style="color:var(--muted);font-size:12px">${{op.room_and_type}}</span>
      </td>
      <td><strong>${{op.ro_size_label}}</strong><br><span class="badge b-ver">&#10003; Order Packet Verified</span></td>
      <td>
        <strong>King (L):</strong> ${{op.left_king_label}}<br>
        <strong>Shoulders (L):</strong> ${{op.left_shoulder_label}}<br>
        <strong style="color:#4ade80">R.O. Pull: ${{op.left_ro_start_label}} to ${{op.right_ro_end_label}}</strong><br>
        <strong>Shoulders (R End):</strong> ${{op.right_shoulder_end_label}} | <strong>King (R End):</strong> ${{op.right_king_end_label}}
      </td>
      <td>
        <strong>Header:</strong> ${{op.header_stock}} @ <strong>${{op.header_length_label}}</strong><br>
        <strong>Pre-Made Supporting Shoulders:</strong> ${{op.shoulders_per_side}}x each side @ <strong>${{op.shoulder_length_label}}</strong><br>
        <strong>Sill:</strong> ${{op.sill_length_label}}
      </td>
    </tr>
  `).join('') || `<tr><td colspan="4">No openings in this wall.</td></tr>`;

  const ixRows = w.intersections.map(ix => `
    <tr>
      <td><strong style="color:#fbbf24;font-size:15px">${{ix.intersecting_wall_id}} Channel</strong><br><span style="color:var(--muted);font-size:12px">${{ix.description}}</span></td>
      <td>
        <strong>Left Channel Stud (1-1/2"):</strong> ${{ix.left_backer_label}}<br>
        <strong style="color:#4ade80">Partition Wall Face-to-Face (${{ix.thickness_label}}): ${{ix.left_edge_label}} to ${{ix.right_edge_label}}</strong><br>
        <strong>Right Channel Stud End:</strong> ${{ix.right_backer_end_label}}
      </td>
      <td>
        <strong>Build In Wall On Deck:</strong> Nail 2 channel studs + flat drywall backer blocks while framing wall.<br>
        <strong style="color:#38bdf8">Double Top-Plate Tie-In:</strong> ${{ix.top_plate_lap_gap_label}}
      </td>
    </tr>
  `).join('') || `<tr><td colspan="3">No intersecting partition channels on this plate.</td></tr>`;

  const ticks = w.oc_marks_short.map((m, i) =>
    `<span class="tick ${{i===0 ? 'first' : ''}}">${{i===0 ? 'START ' + m + ' & GO' : m + ' X'}}</span>`
  ).join('');

  box.innerHTML = `
    <div class="card" style="border-top: 6px solid ${{w.color_info.hex}}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px">
        <div>
          <div style="font-size:12.5px;font-weight:700;color:${{w.color_info.hex}};text-transform:uppercase">
            ${{w.color_info.color}} Highlight Zone &middot; ${{w.color_info.wall_height_label}} &middot; ${{w.lumber_size}} Wall
          </div>
          <h2 style="margin:4px 0 4px;font-size:22px">${{w.wall_id}} — ${{w.name}}</h2>
          <div style="color:var(--muted);font-size:13.5px">${{w.crew_note}}</div>
        </div>
      </div>

      ${{goofyHtml}}

      <div class="callout-grid">
        <div class="stat">
          <div class="lbl">1. Hook Left End &amp; Pull Studs</div>
          <div class="val go">${{w.x_and_go_callout}}</div>
          <div style="font-size:12px;color:var(--muted)">Then 16" O.C. straight down plate</div>
        </div>
        <div class="stat">
          <div class="lbl">2. Full Plate Length</div>
          <div class="val">${{w.length_label}}</div>
          <div style="font-size:12px;color:var(--muted)">${{w.lumber_size}} Bottom + Double Top Plate</div>
        </div>
        <div class="stat">
          <div class="lbl">3. Factory Pre-Cut Studs</div>
          <div class="val">${{w.precut_stud_count}} pcs @ ${{w.color_info.precut_stud_label}}</div>
          <div style="font-size:12px;color:var(--muted)">${{w.color_info.wall_height_label}}</div>
        </div>
      </div>

      <h3 style="margin:16px 0 6px;font-size:15px">A. Door &amp; Window Openings (Pulled from LEFT End of Plate — Verified Order Sizes)</h3>
      <table>
        <tr>
          <th>Doyle Label (Replaces Plan Code)</th>
          <th>Verified R.O. Size</th>
          <th>Left-End Tape Pulls (King / Shoulders / R.O.)</th>
          <th>Pre-Staged Header &amp; Supporting Shoulders</th>
        </tr>
        ${{openingsRows}}
      </table>

      <h3 style="margin:18px 0 6px;font-size:15px">B. Intersecting Partition Channels Built Into Wall on Deck (Pulled from LEFT End of Plate)</h3>
      <table>
        <tr><th>Intersecting Wall Tag</th><th>Left-End Tape Pulls (Channel Studs &amp; Partition Pocket)</th><th>On-Deck Assembly &amp; Double Top-Plate Lap Cutout</th></tr>
        ${{ixRows}}
      </table>

      <h3 style="margin:18px 0 6px;font-size:15px">C. 16" O.C. Stud Layout Tape Marks (Pulled from LEFT End: ${{w.x_and_go_callout}})</h3>
      <div class="tape-strip">${{ticks}}</div>
    </div>
  `;
}}

function renderBatches() {{
  const hRows = DATA.batches.headers.map(h => `
    <tr>
      <td><strong style="font-size:15px;color:#4ade80">${{h.count}}x</strong></td>
      <td><strong>${{h.stock}}</strong></td>
      <td><strong style="font-size:15px">${{h.length_label}}</strong></td>
      <td>${{h.labels.join(', ')}}</td>
    </tr>
  `).join('');

  const sRows = DATA.batches.shoulders.map(s => `
    <tr>
      <td><strong style="font-size:15px;color:#38bdf8">${{s.total_assemblies}} assemblies</strong> (${{s.total_pieces}} pcs)</td>
      <td><strong>${{s.lumber}} (${{s.plies_per_side}}-ply Pre-Made Supporting Shoulder)</strong></td>
      <td><strong style="font-size:15px">${{s.length_label}}</strong></td>
      <td>${{s.labels.join(', ')}}</td>
    </tr>
  `).join('');

  const slRows = DATA.batches.sills.map(s => `
    <tr>
      <td><strong>${{s.count}}x</strong></td>
      <td>${{s.lumber}} Rough Sill</td>
      <td><strong>${{s.length_label}}</strong></td>
      <td>${{s.labels.join(', ')}}</td>
    </tr>
  `).join('');

  document.getElementById('tab-batches').innerHTML = `
    <div class="card">
      <h2 style="margin-top:0">Chop-Saw &amp; Pre-Assembly Bench — Grouped Header &amp; Supporting Shoulder Batches</h2>
      <p style="color:var(--muted);font-size:13.5px">
        Cut, nail together, and keel-label every header and supporting shoulder in batches before framing the walls. Stage each labeled bundle at its wall with the SkyTrak.
      </p>
      <h3>1. Grouped Header Cut List</h3>
      <table>
        <tr><th>Batch Qty</th><th>Header Stock</th><th>Exact Cut Length</th><th>Keel Labels to Write on Header</th></tr>
        ${{hRows}}
      </table>
      <h3 style="margin-top:20px">2. Grouped Pre-Made Supporting Shoulders (Jacks)</h3>
      <table>
        <tr><th>Batch Qty</th><th>Shoulder Assembly</th><th>Exact Cut Length</th><th>Openings Served</th></tr>
        ${{sRows}}
      </table>
      <h3 style="margin-top:20px">3. Grouped Window Rough Sills</h3>
      <table>
        <tr><th>Batch Qty</th><th>Lumber</th><th>Exact Cut Length</th><th>Window Labels</th></tr>
        ${{slRows}}
      </table>
    </div>
  `;
}}

function renderWindowSchedule() {{
  const allOps = [];
  DATA.walls.forEach(w => w.openings.forEach(op => allOps.push({{wall_id: w.wall_id, wall_name: w.name, ...op}})));
  const rows = allOps.map(op => `
    <tr>
      <td><strong style="color:#38bdf8;font-size:15px">${{op.label}}</strong></td>
      <td><span class="badge b-old">${{op.plan_old_code}}</span></td>
      <td><strong>${{op.wall_id}}</strong> — ${{op.room_and_type}}</td>
      <td><strong>${{op.ro_size_label}}</strong></td>
      <td>${{op.left_ro_start_label}} to ${{op.right_ro_end_label}}</td>
      <td><span class="badge b-ver">&#10003; VERIFIED VS. ORDER PACKET</span></td>
    </tr>
  `).join('');

  document.getElementById('tab-windows').innerHTML = `
    <div class="card">
      <h2 style="margin-top:0">Window &amp; Door Order Packet Verification Gate</h2>
      <p style="color:var(--muted);font-size:13.5px">
        Every rough opening is cross-checked against the manufacturer window/door order packet in pre-planning and assigned a Doyle label (<strong>Room/Type + # + Width</strong>) so framers never build off a wrong blueprint callout like "TZ172".
      </p>
      <table>
        <tr>
          <th>Doyle Label</th>
          <th>Ignored Plan Code</th>
          <th>Wall &amp; Location</th>
          <th>Order-Verified R.O.</th>
          <th>Left-End Plate Location</th>
          <th>Pre-Plan Gate</th>
        </tr>
        ${{rows}}
      </table>
    </div>
  `;
}}

function renderCustomCalculator() {{
  document.getElementById('tab-custom').innerHTML = `
    <div class="card">
      <h2 style="margin-top:0">Custom Wall Left-End "X &amp; Go" + Opening Calculator</h2>
      <p style="color:var(--muted);font-size:13.5px">
        Add a wall on the fly from your architectural scale notes: enter the plate length, the left-end first stud pull ("X and Go"), and an optional door/window opening to generate an instant crew pull card.
      </p>
      <div class="form-grid">
        <div><label>Wall Tag &amp; Name</label><input id="c_name" value="W-9 — Basement Bedroom #3 Partition"></div>
        <div><label>Wall Length (Inches)</label><input id="c_len" type="number" step="0.25" value="192"></div>
        <div><label>Left-End First Stud Pull (Inches)</label><input id="c_pull" type="number" step="0.25" value="8.25"></div>
        <div><label>Wall Height / Color Zone</label>
          <select id="c_zone">
            <option value="92-5/8&quot; Studs (Blue 8' Wall)">Blue — 8'1-1/8" (92-5/8" Pre-Cuts)</option>
            <option value="104-5/8&quot; Studs (Green 9' Wall)" selected>Green — 9'1-1/8" (104-5/8" Pre-Cuts)</option>
            <option value="116-5/8&quot; Studs (Orange 10' Wall)">Orange — 10'1-1/8" (116-5/8" Pre-Cuts)</option>
          </select>
        </div>
      </div>
      <div class="form-grid">
        <div><label>Doyle Opening Label</label><input id="c_oplabel" value="BR3W2-48"></div>
        <div><label>Left-End to R.O. Start (Inches)</label><input id="c_rostart" type="number" step="0.25" value="60"></div>
        <div><label>Verified R.O. Width (Inches)</label><input id="c_rowidth" type="number" step="0.25" value="48"></div>
        <div><label>Shoulders Per Side (1 or 2)</label><input id="c_sh" type="number" min="1" max="3" value="2"></div>
      </div>
      <button class="btn" onclick="calcCustomWall()">Generate Left-End Crew Pull Sheet</button>
      <div id="customOut" style="margin-top:16px"></div>
    </div>
  `;
  calcCustomWall();
}}

function fmtInJS(v) {{
  const whole = Math.floor(v);
  const rem = Math.round((v - whole) * 4) / 4;
  const fracMap = {{0.25: '1/4', 0.5: '1/2', 0.75: '3/4'}};
  if (rem === 0) return whole + '"';
  return whole + '-' + (fracMap[rem] || rem.toFixed(2)) + '"';
}}

function calcCustomWall() {{
  const name = document.getElementById('c_name').value;
  const len = parseFloat(document.getElementById('c_len').value) || 192;
  const pull = parseFloat(document.getElementById('c_pull').value) || 8.25;
  const zone = document.getElementById('c_zone').value;
  const opLabel = document.getElementById('c_oplabel').value;
  const roStart = parseFloat(document.getElementById('c_rostart').value) || 60;
  const roWidth = parseFloat(document.getElementById('c_rowidth').value) || 48;
  const sh = parseInt(document.getElementById('c_sh').value) || 2;

  const shSpan = 1.5 * sh;
  const hdrLen = roWidth + 2 * shSpan;
  const leftSh = roStart - shSpan;
  const leftKing = leftSh - 1.5;
  const rightRo = roStart + roWidth;
  const rightSh = rightRo + shSpan;
  const rightKing = rightSh + 1.5;

  const marks = [];
  for (let p = pull; p < len - 1.5; p += 16) marks.push(fmtInJS(p));

  document.getElementById('customOut').innerHTML = `
    <div class="card" style="background:#020617">
      <h3 style="margin-top:0">${{name}} — ${{zone}}</h3>
      <p><strong>Left-End Stud Pull:</strong> <span style="color:#4ade80;font-weight:800">${{fmtInJS(pull)}} &amp; GO</span> &nbsp;|&nbsp; <strong>Plate Length:</strong> ${{fmtInJS(len)}}</p>
      <p><strong>Opening ${{opLabel}}:</strong> King(L) <code>${{fmtInJS(leftKing)}}</code> &middot; Shoulders(L) <code>${{fmtInJS(leftSh)}}</code> &middot; <strong style="color:#38bdf8">R.O. <code>${{fmtInJS(roStart)}}</code> to <code>${{fmtInJS(rightRo)}}</code></strong> &middot; Shoulders(R) <code>${{fmtInJS(rightSh)}}</code> &middot; King(R) <code>${{fmtInJS(rightKing)}}</code></p>
      <p><strong>Pre-Staged Header Length:</strong> <code>${{fmtInJS(hdrLen)}}</code> &nbsp;|&nbsp; <strong>Pre-Made Supporting Shoulders:</strong> <code>${{sh}}x each side @ 81"</code></p>
      <div class="tape-strip">${{marks.map((m,i) => `<span class="tick ${{i===0?'first':''}}">${{i===0 ? 'START '+m+' & GO' : m+' X'}}</span>`).join('')}}</div>
    </div>
  `;
}}

function renderChecklist() {{
  const items = [
    "Window & Door R.O. Verification: Every rough opening measured with tape against the Order-Packet Verified schedule (PD1-82, LLPD1-82, GRW1-60, MS1-60, BR2W1-48, BR3W1-48, GD1-194).",
    "Pre-Made Supporting Shoulders & Header Bearing: Double supporting shoulders installed tightly under all spans >= 48\"; zero gaps between bottom plate, shoulder, and header.",
    "Double Top-Plate Laps & Partition Tie-Ins: Minimum 48\" lap across all top-plate joints; intersecting interior partition walls (W-6 through W-12) lapped and nailed into exterior top plates.",
    "Walkout Lower-Level Exposure Wall (W-1): Treated bottom plate bolted every 48\" max and within 12\" of plate breaks; step-frost wall anchor bolts washered and tightened.",
    "Garage Portal Wall Hold-Downs (W-6 / GD1-194): Simpson portal hold-down brackets fastened to embedded foundation anchor bolts at both king posts before sheathing.",
    "Tray Ceiling & Fireplace Blocking (W-2, W-3, W-8): 9'0\" perimeter tray ceiling soffit ledgers snapped and nailed; 2x12 TV/mantle backing installed above FP1-50; fireblocking installed at all soffit/chase drops.",
    "Plumb, Line & String-Plane Check: All tall 9' and 10' walls plumbed, string-lined top plate to top plate, and braced prior to setting roof trusses."
  ];
  document.getElementById('tab-qc').innerHTML = `
    <div class="card">
      <h2 style="margin-top:0">Standardized Municipal Framing Pre-Inspection Checklist</h2>
      <p style="color:var(--muted);font-size:13.5px">
        Co-developed with the municipal building inspector at Doyle's Contracting to guarantee first-time framing inspection pass rates across 100+ builds.
      </p>
      ${{items.map((txt, i) => `
        <label style="display:flex;align-items:flex-start;gap:10px;padding:10px;border-bottom:1px solid var(--border);color:var(--text);font-size:14px;cursor:pointer">
          <input type="checkbox" style="width:18px;height:18px;margin-top:2px">
          <span><strong>#${{i+1}}.</strong> ${{txt}}</span>
        </label>
      `).join('')}}
    </div>
  `;
}}

init();
</script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(HTML_PATH), exist_ok=True)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", HTML_PATH, "bytes:", len(html))


if __name__ == "__main__":
    build_html()
