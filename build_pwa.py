"""Generate the clean, numbers-only Framing Factory Planner PWA (docs/index.html).

No carpentry lectures on screen — strictly the pre-figured measurements, labels, cut batches,
blocking locations, stair plan-vs-field numbers, yard map, and daily goal hours a crew needs.
"""
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
<title>Framing Factory — Crew Layout &amp; Cut Sheet</title>
<link rel="manifest" href="manifest.json">
<style>
  :root {{
    --bg: #0f172a; --card: #1e293b; --border: #334155; --text: #f8fafc;
    --muted: #94a3b8; --accent: #ea580c; --green: #16a34a; --blue: #2563eb;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); }}
  header {{ background: #020617; border-bottom: 2px solid var(--accent); padding: 12px 16px; position: sticky; top: 0; z-index: 20; }}
  .hdr {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; max-width: 1180px; margin: 0 auto; }}
  h1 {{ margin: 0; font-size: 18px; }}
  .btn {{ background: var(--accent); color: #fff; border: none; padding: 7px 13px; border-radius: 6px; font-weight: 700; font-size: 12.5px; cursor: pointer; }}
  .btn.sec {{ background: #334155; }}
  .btn.blu {{ background: var(--blue); }}
  .wrap {{ max-width: 1180px; margin: 0 auto; padding: 14px 14px 50px; }}
  .goal {{ background: #1e293b; border-left: 5px solid var(--accent); padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; font-size: 13.5px; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }}
  .leg {{ background: var(--card); border: 1px solid var(--border); border-left: 5px solid #fff; padding: 5px 10px; border-radius: 5px; font-size: 12px; font-weight: 700; }}
  .tabs {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
  .tab {{ background: var(--card); color: var(--text); border: 1px solid var(--border); padding: 7px 13px; border-radius: 6px; font-weight: 700; cursor: pointer; font-size: 12.5px; }}
  .tab.active {{ background: var(--accent); border-color: var(--accent); }}
  .pills {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }}
  .pill {{ padding: 6px 11px; border-radius: 6px; border: 2px solid var(--border); background: var(--card); color: var(--text); cursor: pointer; font-weight: 700; font-size: 12.5px; }}
  .pill.active {{ outline: 2px solid #fff; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 14px; margin-bottom: 14px; }}
  .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px; margin: 10px 0 14px; }}
  .stat {{ background: #020617; border: 1px solid var(--border); border-radius: 6px; padding: 8px 12px; }}
  .stat .l {{ color: var(--muted); font-size: 11px; text-transform: uppercase; }}
  .stat .v {{ font-size: 20px; font-weight: 800; color: #38bdf8; margin-top: 2px; }}
  .stat .v.go {{ color: #4ade80; }}
  .alert {{ background: rgba(220,38,38,0.18); border: 1.5px solid #ef4444; color: #fecaca; padding: 9px 12px; border-radius: 6px; margin: 8px 0; font-weight: 600; font-size: 13px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; margin-top: 6px; }}
  th, td {{ border: 1px solid var(--border); padding: 6px 8px; text-align: left; vertical-align: top; }}
  th {{ background: #020617; color: #cbd5e1; font-size: 11px; text-transform: uppercase; }}
  .badge {{ display: inline-block; padding: 1px 6px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
  .b-ver {{ background: rgba(22,163,74,0.25); color: #86efac; border: 1px solid #16a34a; }}
  .b-lock {{ background: rgba(220,38,38,0.25); color: #fca5a5; border: 1px solid #ef4444; }}
  .b-flex {{ background: rgba(56,189,248,0.18); color: #bae6fd; }}
  .b-old {{ color: #94a3b8; text-decoration: line-through; margin-left: 5px; }}
  .tape {{ display: flex; flex-wrap: wrap; gap: 5px; background: #020617; padding: 9px; border-radius: 6px; border: 1px solid var(--border); }}
  .tk {{ background: #1e293b; border: 1px solid #475569; padding: 3px 7px; border-radius: 4px; font-family: monospace; font-size: 12px; }}
  .tk.st {{ background: #14532d; border-color: #22c55e; color: #bbf7d0; font-weight: 700; }}
  .fgrid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(165px, 1fr)); gap: 8px; margin-bottom: 10px; }}
  input, select {{ width: 100%; padding: 7px 9px; border-radius: 5px; border: 1px solid var(--border); background: #020617; color: var(--text); font-size: 13px; }}
  label {{ font-size: 11px; color: var(--muted); display: block; margin-bottom: 3px; font-weight: 600; }}
  .mbg {{ display: none; position: fixed; inset: 0; background: rgba(2,6,23,0.82); z-index: 50; align-items: center; justify-content: center; padding: 14px; }}
  .mdl {{ background: var(--card); border: 2px solid var(--accent); border-radius: 8px; max-width: 600px; width: 100%; padding: 16px; }}
  @media print {{
    body {{ background: #fff; color: #000; }}
    header, .tabs, .pills {{ display: none !important; }}
    .card, .stat {{ background: #fff; border: 1px solid #000; color: #000; }}
    th, td {{ border: 1px solid #000; color: #000; }}
  }}
</style>
</head>
<body>
<header>
  <div class="hdr">
    <h1>FRAMING FACTORY — CREW LAYOUT &amp; CUT SHEET</h1>
    <div style="display:flex;gap:8px">
      <button class="btn" id="installBtn" style="display:none" onclick="if(deferredPrompt)deferredPrompt.prompt()">Install App</button>
      <button class="btn sec" onclick="window.print()">Print Active Sheet</button>
    </div>
  </div>
</header>

<div class="wrap">
  <div class="goal" id="goalBanner"></div>
  <div class="legend" id="legendBar"></div>

  <div class="tabs">
    <button class="tab active" onclick="showTab('walls', this)">1. Wall Pull Sheets</button>
    <button class="tab" onclick="showTab('batches', this)">2. Cut Bench (Headers &amp; Shoulders)</button>
    <button class="tab" onclick="showTab('stairs', this)">3. Stairs (Plan vs. Field)</button>
    <button class="tab" onclick="showTab('yard', this)">4. Yard &amp; Deck Staging Map</button>
    <button class="tab" onclick="showTab('bidding', this)">5. Daily Goal &amp; Crew Hours</button>
  </div>

  <div id="tab-walls">
    <div class="pills" id="wallPills"></div>
    <div id="activeWallCard"></div>
  </div>
  <div id="tab-batches" style="display:none"></div>
  <div id="tab-stairs" style="display:none"></div>
  <div id="tab-yard" style="display:none"></div>
  <div id="tab-bidding" style="display:none"></div>
</div>

<div class="mbg" id="modalBg" onclick="closeModal()">
  <div class="mdl" onclick="event.stopPropagation()">
    <div id="modalContent"></div>
    <div style="margin-top:12px;text-align:right"><button class="btn" onclick="closeModal()">Close</button></div>
  </div>
</div>

<script>
const DATA = {data_js};
let currentWallIdx = 0, deferredPrompt = null;
window.addEventListener('beforeinstallprompt', e => {{ e.preventDefault(); deferredPrompt = e; document.getElementById('installBtn').style.display = 'inline-block'; }});
if ('serviceWorker' in navigator) navigator.serviceWorker.register('./sw.js').catch(() => {{}});
function openModal(h) {{ document.getElementById('modalContent').innerHTML = h; document.getElementById('modalBg').style.display = 'flex'; }}
function closeModal() {{ document.getElementById('modalBg').style.display = 'none'; }}

function showTab(name, btn) {{
  ['walls','batches','stairs','yard','bidding'].forEach(t => document.getElementById('tab-' + t).style.display = (t === name) ? 'block' : 'none');
  document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}}

function init() {{
  document.getElementById('goalBanner').innerHTML = `<strong>${{DATA.project_name}}</strong><br><strong>TODAY'S GOAL:</strong> ${{DATA.daily_goal}}`;
  document.getElementById('legendBar').innerHTML = Object.values(DATA.color_legend).map(c =>
    `<div class="leg" style="border-left-color:${{c.hex}}"><span style="color:${{c.hex}}">${{c.color}}:</span> ${{c.wall_height_label}} (${{c.precut_stud_label}} studs)</div>`
  ).join('');
  renderWallPills(); renderActiveWall(); renderBatches(); renderStairs(); renderYard(); renderBidding();
}}

function renderWallPills() {{
  document.getElementById('wallPills').innerHTML = DATA.walls.map((w, i) => `
    <button class="pill ${{i === currentWallIdx ? 'active' : ''}}" style="border-color:${{w.color_info.hex}}" onclick="currentWallIdx=${{i}};renderWallPills();renderActiveWall()">
      <span style="color:${{w.color_info.hex}}">&#9632;</span> ${{w.wall_id}}: ${{w.name}}
    </button>
  `).join('');
}}

function showCab(wIdx, cIdx) {{
  const c = DATA.walls[wIdx].cabinet_checks[cIdx];
  openModal(`
    <h3 style="margin:0 0 8px">${{c.title}}</h3>
    <table>
      <tr><th>Plan Drywall-to-Drywall</th><td><strong style="color:#38bdf8">${{c.finished_label}}</strong></td></tr>
      <tr><th>Drywall Allowance</th><td>+ ${{c.drywall_allowance_label}}</td></tr>
      <tr><th>Rough Stud-to-Stud</th><td><strong style="color:#4ade80;font-size:17px">${{c.required_rough_label}} (+/- ${{c.max_tolerance_label}})</strong></td></tr>
    </table>
    <p style="font-size:13px;margin-top:8px">${{c.detail_note}}</p>
  `);
}}

function renderActiveWall() {{
  const w = DATA.walls[currentWallIdx];
  const cabBtns = (w.cabinet_checks || []).map((c, ci) =>
    `<button class="btn blu" style="margin:6px 6px 0 0" onclick="showCab(${{currentWallIdx}},${{ci}})">${{c.title}} (${{c.finished_label}} DW -> ${{c.required_rough_label}} Rough)</button>`
  ).join('');

  const opRows = w.openings.map(op => `
    <tr>
      <td><strong style="color:#38bdf8;font-size:14.5px">${{op.label}}</strong><span class="badge b-old">${{op.plan_old_code}}</span><br><span style="color:var(--muted);font-size:11.5px">${{op.room_and_type}}</span></td>
      <td><strong>${{op.ro_size_label}}</strong> <span class="badge b-ver">&#10003; Order Verified</span></td>
      <td>King(L): <strong>${{op.left_king_label}}</strong> &middot; Sh(L): <strong>${{op.left_shoulder_label}}</strong><br><strong style="color:#4ade80">R.O.: ${{op.left_ro_start_label}} to ${{op.right_ro_end_label}}</strong><br>Sh(R): <strong>${{op.right_shoulder_end_label}}</strong> &middot; King(R): <strong>${{op.right_king_end_label}}</strong></td>
      <td>Hdr: <strong>${{op.header_stock}} @ ${{op.header_length_label}}</strong><br>Shoulders: <strong>${{op.shoulders_per_side}}x/side @ ${{op.shoulder_length_label}}</strong> &middot; Sill: <strong>${{op.sill_length_label}}</strong></td>
    </tr>
  `).join('') || `<tr><td colspan="4">None</td></tr>`;

  const ixRows = w.intersections.map(ix => `
    <tr>
      <td><strong style="color:#fbbf24">${{ix.intersecting_wall_id}}</strong> — ${{ix.description}} <span class="badge ${{ix.tolerance_rule.indexOf('LOCKED')!==-1?'b-lock':'b-flex'}}">${{ix.tolerance_rule}}</span></td>
      <td>Backer(L): <strong>${{ix.left_backer_label}}</strong> &middot; <strong style="color:#4ade80">Pocket (${{ix.thickness_label}}): ${{ix.left_edge_label}} to ${{ix.right_edge_label}}</strong> &middot; Backer(R): <strong>${{ix.right_backer_end_label}}</strong></td>
      <td>${{ix.top_plate_lap_gap_label}}</td>
    </tr>
  `).join('') || `<tr><td colspan="3">None</td></tr>`;

  const blkRows = (w.blocking || []).map(b => `
    <tr><td><strong style="color:#f472b6">${{b.kind}}</strong> — ${{b.label}}</td><td><strong>${{b.lumber}}</strong></td><td><strong style="color:#4ade80">${{b.height_aff_label}}</strong></td><td>${{b.location_note}}</td></tr>
  `).join('') || `<tr><td colspan="4">None</td></tr>`;

  document.getElementById('activeWallCard').innerHTML = `
    <div class="card" style="border-top:5px solid ${{w.color_info.hex}}">
      <div style="font-size:12px;font-weight:700;color:${{w.color_info.hex}}">${{w.color_info.color}} Zone &middot; ${{w.color_info.wall_height_label}} &middot; ${{w.lumber_size}} &middot; ${{w.labor_tier}} (${{w.baseline_man_hours}} hrs)</div>
      <h2 style="margin:3px 0;font-size:20px">${{w.wall_id}} — ${{w.name}}</h2>
      ${{cabBtns}}
      ${{w.goofy_alert ? `<div class="alert">&#9888; ${{w.goofy_alert}}</div>` : ''}}
      <div class="stats">
        <div class="stat"><div class="l">Left-End Stud Pull</div><div class="v go">${{w.x_and_go_callout}}</div></div>
        <div class="stat"><div class="l">Plate Length</div><div class="v">${{w.length_label}}</div></div>
        <div class="stat"><div class="l">Pre-Cut Studs</div><div class="v">${{w.precut_stud_count}} pcs @ ${{w.color_info.precut_stud_label}}</div></div>
      </div>
      <h3 style="margin:12px 0 4px;font-size:13.5px">Openings (From Left End)</h3>
      <table><tr><th>Label</th><th>Verified R.O.</th><th>Left-End Tape Pulls</th><th>Header &amp; Pre-Made Shoulders</th></tr>${{opRows}}</table>
      <h3 style="margin:12px 0 4px;font-size:13.5px">Partition Channels Built On Deck (From Left End)</h3>
      <table><tr><th>Wall Tag</th><th>Left-End Tape Pulls (Backers &amp; Pocket)</th><th>2nd Top-Plate Lap Cutout</th></tr>${{ixRows}}</table>
      <h3 style="margin:12px 0 4px;font-size:13.5px">Blocking &amp; Mechanical Locations</h3>
      <table><tr><th>Blocking</th><th>Stock</th><th>Height AFF</th><th>Location</th></tr>${{blkRows}}</table>
      <h3 style="margin:12px 0 4px;font-size:13.5px">16" O.C. Stud Marks (${{w.x_and_go_callout}})</h3>
      <div class="tape">${{w.oc_marks_short.map((m,i)=>`<span class="tk ${{i===0?'st':''}}">${{i===0?m+' & GO':m+' X'}}</span>`).join('')}}</div>
    </div>
  `;
}}

function renderBatches() {{
  document.getElementById('tab-batches').innerHTML = `
    <div class="card">
      <h2 style="margin-top:0">Cut Bench — Grouped Headers &amp; Pre-Made Shoulders</h2>
      <h3>Headers</h3>
      <table><tr><th>Qty</th><th>Stock</th><th>Cut Length</th><th>Labels</th></tr>
        ${{DATA.batches.headers.map(h=>`<tr><td><strong style="color:#4ade80">${{h.count}}x</strong></td><td><strong>${{h.stock}}</strong></td><td><strong>${{h.length_label}}</strong></td><td>${{h.labels.join(', ')}}</td></tr>`).join('')}}
      </table>
      <h3 style="margin-top:14px">Pre-Made Supporting Shoulders</h3>
      <table><tr><th>Qty</th><th>Stock</th><th>Cut Length</th><th>Openings</th></tr>
        ${{DATA.batches.shoulders.map(s=>`<tr><td><strong style="color:#38bdf8">${{s.total_assemblies}} assy (${{s.total_pieces}} pcs)</strong></td><td><strong>${{s.lumber}} (${{s.plies_per_side}}-ply)</strong></td><td><strong>${{s.length_label}}</strong></td><td>${{s.labels.join(', ')}}</td></tr>`).join('')}}
      </table>
    </div>
  `;
}}

function fmt16(v) {{
  const s = v < 0 ? '-' : ''; v = Math.abs(v);
  const w = Math.floor(v + 1e-9), sx = Math.round((v - w) * 16);
  if (sx === 0) return s + w + '"'; if (sx === 16) return s + (w + 1) + '"';
  let n = sx, d = 16; while (n % 2 === 0) {{ n /= 2; d /= 2; }}
  return s + (w > 0 ? w + '-' : '') + n + '/' + d + '"';
}}

function renderStairs() {{
  document.getElementById('tab-stairs').innerHTML = `
    <div class="card">
      <h2 style="margin-top:0">Stair Stringer Calculator — Plan Height vs. Field Measurement</h2>
      <div class="fgrid">
        <div><label>Plan Wall Stud Stock</label>
          <select id="st_stud" onchange="calcStairs()">
            <option value="92.625">92-5/8" (8' Wall)</option>
            <option value="104.625" selected>104-5/8" (9' Wall)</option>
            <option value="116.625">116-5/8" (10' Wall)</option>
            <option value="126.625">126-5/8" (Tall Wall)</option>
          </select>
        </div>
        <div><label>Plan Floor Assembly (In)</label><input id="st_floor" type="number" step="0.125" value="12.625" oninput="calcStairs()"></div>
        <div><label>ACTUAL FIELD TOTAL RISE (In)</label><input id="st_field" type="number" step="0.125" value="121.25" oninput="calcStairs()"></div>
        <div><label>Tread Thickness Drop (In)</label><input id="st_tread" type="number" step="0.125" value="1.5" oninput="calcStairs()"></div>
        <div><label>Unit Run (In)</label><input id="st_run" type="number" step="0.25" value="10.0" oninput="calcStairs()"></div>
      </div>
      <div id="stairOut"></div>
    </div>
  `;
  calcStairs();
}}

function calcStairs() {{
  const stud = parseFloat(document.getElementById('st_stud').value) || 104.625;
  const flr = parseFloat(document.getElementById('st_floor').value) || 12.625;
  const field = parseFloat(document.getElementById('st_field').value) || 121.25;
  const tread = parseFloat(document.getElementById('st_tread').value) || 1.5;
  const run = parseFloat(document.getElementById('st_run').value) || 10.0;
  const planTot = stud + 4.5 + flr, pR = Math.max(1, Math.round(planTot / 7.5)), pU = planTot / pR;
  const fR = Math.max(1, Math.round(field / 7.5)), fU = field / fR, totRun = (fR - 1) * run;
  document.getElementById('stairOut').innerHTML = `
    <table>
      <tr><th>Measurement</th><th>Plan Theoretical</th><th>ACTUAL FIELD CUT</th></tr>
      <tr><td>Total Rise</td><td>${{fmt16(planTot)}}</td><td><strong style="color:#4ade80">${{fmt16(field)}}</strong> (Delta: ${{fmt16(field - planTot)}})</td></tr>
      <tr><td>Risers / Treads</td><td>${{pR}} Risers / ${{pR-1}} Treads</td><td><strong>${{fR}} Risers / ${{fR-1}} Treads</strong></td></tr>
      <tr><td>Unit Rise</td><td>${{fmt16(pU)}}</td><td><strong style="color:#38bdf8;font-size:16px">${{fmt16(fU)}} (${{fU.toFixed(3)}}")</strong></td></tr>
      <tr><td>Unit Run / Total Run</td><td>${{fmt16(run)}}</td><td><strong>${{fmt16(run)}}</strong> &middot; Total Run: <strong>${{Math.floor(totRun/12)}}' ${{fmt16(totRun%12)}}</strong></td></tr>
      <tr><td>Bottom Riser Cut (-${{fmt16(tread)}} Tread)</td><td>—</td><td><strong style="color:#fbbf24">${{fmt16(fU - tread)}}</strong></td></tr>
    </table>
  `;
}}

function renderYard() {{
  document.getElementById('tab-yard').innerHTML = `
    <div class="card">
      <h2 style="margin-top:0">Jobsite Staging Map</h2>
      <table>
        <tr><th>Staging Zone</th><th>Placement &amp; Bunks</th></tr>
        <tr><td><strong style="color:#4ade80">Close Perimeter (Hand-Carried)</strong></td><td>I-Joists dropped right against foundation oriented parallel to span; Treated 2x6 sills &amp; rim at corner; Cut bench beside 2x10/2x12/2x6 header stock.</td></tr>
        <tr><td><strong style="color:#38bdf8">On-Deck Bunks</strong></td><td>104-5/8" stud bunk at South/East deck (W-1, W-3, W-4); 116-5/8" stud bunk at North/Center deck (W-2, W-5, W-6); 92-5/8" stud bunk at interior hall (W-7); 7/16" sheathing &amp; Tyvek at exterior plates.</td></tr>
        <tr><td><strong style="color:#fbbf24">Front Porch Pad (8'x4')</strong></td><td>8'x4' porch beams, roof deck, gable, and rake built directly on top of the front porch foundation walls before lifting.</td></tr>
        <tr><td><strong style="color:#f472b6">Outer SkyTrak Yard (Far Off Perimeter)</strong></td><td>Floor trusses in 4–6 packs reverse-staged (LIFO North->South, East->West); Roof trusses sorted in field (pack only 10+ identical commons); Ground-built completed gable ends; Steel I-beam &amp; teleposts (by others, field-set/welded).</td></tr>
      </table>
    </div>
  `;
}}

function renderBidding() {{
  document.getElementById('tab-bidding').innerHTML = `
    <div class="card">
      <h2 style="margin-top:0">Daily Goal &amp; Crew Baseline Hours (1-Man / 2-Man / Full Crew)</h2>
      <table>
        <tr><th>Done</th><th>Wall</th><th>Crew Assignment</th><th>Baseline Hours</th></tr>
        ${{DATA.walls.map(w=>`<tr><td><input type="checkbox" checked onchange="recalcGoal()" class="wchk" data-h="${{w.baseline_man_hours}}" data-id="${{w.wall_id}}"></td><td><strong>${{w.wall_id}}</strong> — ${{w.name}}</td><td>${{w.labor_tier}}</td><td><strong>${{w.baseline_man_hours}} hrs</strong></td></tr>`).join('')}}
      </table>
      <div id="goalOut" style="margin-top:10px;font-weight:700;color:#4ade80"></div>
    </div>
  `;
  recalcGoal();
}}

function recalcGoal() {{
  let done = 0, rem = 0, q = [];
  document.querySelectorAll('.wchk').forEach(c => {{
    const h = parseFloat(c.getAttribute('data-h')) || 0;
    if (c.checked) done += h; else {{ rem += h; q.push(c.getAttribute('data-id')); }}
  }});
  document.getElementById('goalOut').textContent = `Completed: ${{done.toFixed(1)}} hrs | Remaining: ${{rem.toFixed(1)}} hrs ${{q.length ? '(Next Goal: ' + q.join(', ') + ')' : '(Walls Complete)'}}`;
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
