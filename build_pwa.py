"""Generate the mobile-phone-sized Framing Factory Planner PWA (docs/index.html).

Sized strictly as a 430px mobile phone screen (centered phone shell on desktop, full screen on phone)
with stacked touch cards, big thumb buttons, and bottom tab bar — zero wide desktop tables.
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
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<meta name="theme-color" content="#0f172a">
<title>Framing Factory — Mobile Crew App</title>
<link rel="manifest" href="manifest.json">
<style>
  :root {{
    --bg: #020617; --phone: #0f172a; --card: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #ea580c; --green: #16a34a; --blue: #2563eb;
  }}
  * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
  body {{
    margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg); color: var(--text); display: flex; justify-content: center;
  }}
  .phone-shell {{
    width: 100%; max-width: 430px; min-height: 100vh; background: var(--phone);
    border-left: 1px solid #1e293b; border-right: 1px solid #1e293b;
    padding-bottom: 78px; position: relative;
  }}
  header {{
    background: #020617; border-bottom: 2px solid var(--accent);
    padding: 12px 14px; position: sticky; top: 0; z-index: 20;
    display: flex; justify-content: space-between; align-items: center;
  }}
  h1 {{ margin: 0; font-size: 15.5px; letter-spacing: 0.2px; }}
  .sub {{ font-size: 11px; color: var(--muted); }}
  .btn {{
    background: var(--accent); color: #fff; border: none; padding: 9px 12px;
    border-radius: 8px; font-weight: 700; font-size: 12.5px; cursor: pointer;
  }}
  .btn.blu {{ background: var(--blue); width: 100%; margin-top: 8px; text-align: left; }}
  .content {{ padding: 12px; }}
  .goal-box {{
    background: var(--card); border-left: 4px solid var(--accent);
    padding: 10px 12px; border-radius: 8px; font-size: 12.5px; margin-bottom: 10px;
  }}
  .wall-strip {{
    display: flex; overflow-x: auto; gap: 7px; padding-bottom: 8px; margin-bottom: 10px;
  }}
  .w-btn {{
    flex: 0 0 auto; padding: 9px 13px; border-radius: 8px; border: 2px solid var(--border);
    background: var(--card); color: var(--text); font-weight: 800; font-size: 13px; cursor: pointer;
  }}
  .w-btn.active {{ background: #020617; outline: 2px solid #fff; }}
  .hero-pull {{
    background: #020617; border: 2px solid #22c55e; border-radius: 10px;
    padding: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;
  }}
  .hero-pull .big {{ font-size: 24px; font-weight: 900; color: #4ade80; }}
  .hero-pull .meta {{ text-align: right; font-size: 12.5px; color: #cbd5e1; }}
  .alert {{
    background: rgba(220,38,38,0.2); border: 1.5px solid #ef4444; color: #fecaca;
    padding: 10px 12px; border-radius: 8px; font-size: 12.5px; font-weight: 600; margin-bottom: 10px;
  }}
  .sec-hdr {{
    font-size: 11.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.6px;
    color: var(--muted); margin: 14px 0 6px;
  }}
  .m-card {{
    background: var(--card); border: 1px solid var(--border); border-radius: 9px;
    padding: 11px 12px; margin-bottom: 8px; font-size: 13px;
  }}
  .m-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
  .code {{ font-size: 16px; font-weight: 900; color: #38bdf8; }}
  .old {{ color: var(--muted); text-decoration: line-through; font-size: 11.5px; margin-left: 6px; }}
  .badge {{ display: inline-block; padding: 2px 7px; border-radius: 5px; font-size: 11px; font-weight: 700; }}
  .b-ver {{ background: rgba(22,163,74,0.25); color: #86efac; border: 1px solid #16a34a; }}
  .b-lock {{ background: rgba(220,38,38,0.25); color: #fca5a5; border: 1px solid #ef4444; }}
  .pull-row {{
    background: #020617; padding: 7px 9px; border-radius: 6px; margin: 4px 0;
    font-family: monospace; font-size: 12.5px;
  }}
  .tape {{ display: flex; flex-wrap: wrap; gap: 5px; }}
  .tk {{ background: #020617; border: 1px solid #475569; padding: 5px 8px; border-radius: 5px; font-family: monospace; font-size: 12.5px; }}
  .tk.st {{ background: #14532d; border-color: #22c55e; color: #bbf7d0; font-weight: 800; }}
  input, select {{
    width: 100%; padding: 10px; border-radius: 7px; border: 1px solid var(--border);
    background: #020617; color: var(--text); font-size: 14px; margin-bottom: 8px;
  }}
  label {{ font-size: 11.5px; color: var(--muted); display: block; margin-bottom: 3px; font-weight: 700; }}
  .bottom-nav {{
    position: fixed; bottom: 0; width: 100%; max-width: 430px; background: #020617;
    border-top: 2px solid var(--border); display: grid; grid-template-columns: repeat(5, 1fr);
    z-index: 30;
  }}
  .nav-btn {{
    background: none; border: none; color: var(--muted); padding: 10px 4px;
    font-size: 11px; font-weight: 700; cursor: pointer; text-align: center;
  }}
  .nav-btn.active {{ color: #fff; background: var(--accent); }}
  .mbg {{ display: none; position: fixed; inset: 0; background: rgba(2,6,23,0.86); z-index: 50; align-items: center; justify-content: center; padding: 16px; }}
  .mdl {{ background: var(--card); border: 2px solid var(--accent); border-radius: 10px; max-width: 398px; width: 100%; padding: 16px; }}
</style>
</head>
<body>
<div class="phone-shell">
  <header>
    <div>
      <h1>FRAMING FACTORY</h1>
      <div class="sub">3-Bed Walkout Ranch &middot; Mobile Crew Sheet</div>
    </div>
    <button class="btn" onclick="window.print()">Print</button>
  </header>

  <div class="content">
    <div id="tab-walls">
      <div class="wall-strip" id="wallStrip"></div>
      <div id="wallView"></div>
    </div>
    <div id="tab-batches" style="display:none"></div>
    <div id="tab-stairs" style="display:none"></div>
    <div id="tab-yard" style="display:none"></div>
    <div id="tab-goal" style="display:none"></div>
  </div>

  <nav class="bottom-nav">
    <button class="nav-btn active" onclick="showTab('walls', this)">1. Walls</button>
    <button class="nav-btn" onclick="showTab('batches', this)">2. Cut Bench</button>
    <button class="nav-btn" onclick="showTab('stairs', this)">3. Stairs</button>
    <button class="nav-btn" onclick="showTab('yard', this)">4. Yard Map</button>
    <button class="nav-btn" onclick="showTab('goal', this)">5. Goal Hrs</button>
  </nav>
</div>

<div class="mbg" id="modalBg" onclick="closeModal()">
  <div class="mdl" onclick="event.stopPropagation()">
    <div id="modalBody"></div>
    <button class="btn" style="width:100%;margin-top:12px" onclick="closeModal()">Close</button>
  </div>
</div>

<script>
const DATA = {data_js};
let cur = 0;

function showTab(name, btn) {{
  ['walls','batches','stairs','yard','goal'].forEach(t => document.getElementById('tab-' + t).style.display = (t === name) ? 'block' : 'none');
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  window.scrollTo(0, 0);
}}

function openModal(h) {{ document.getElementById('modalBody').innerHTML = h; document.getElementById('modalBg').style.display = 'flex'; }}
function closeModal() {{ document.getElementById('modalBg').style.display = 'none'; }}

function renderStrip() {{
  document.getElementById('wallStrip').innerHTML = DATA.walls.map((w, i) => `
    <button class="w-btn ${{i===cur?'active':''}}" style="border-color:${{w.color_info.hex}}" onclick="cur=${{i}};renderStrip();renderWall()">
      <span style="color:${{w.color_info.hex}}">&#9632;</span> ${{w.wall_id}}
    </button>
  `).join('');
}}

function showCab(wIdx, cIdx) {{
  const c = DATA.walls[wIdx].cabinet_checks[cIdx];
  openModal(`
    <div style="font-size:11px;color:#f87171;font-weight:800">${{c.room_type}}</div>
    <h3 style="margin:4px 0 10px;font-size:16px">${{c.title}}</h3>
    <div class="pull-row">Plan Drywall-to-Drywall: <strong style="color:#38bdf8">${{c.finished_label}}</strong></div>
    <div class="pull-row">Drywall Allowance: <strong>+ ${{c.drywall_allowance_label}}</strong></div>
    <div class="pull-row">Rough Stud-to-Stud: <strong style="color:#4ade80;font-size:16px">${{c.required_rough_label}} (+/- ${{c.max_tolerance_label}})</strong></div>
    <p style="font-size:12.5px;color:#cbd5e1;margin:8px 0 0">${{c.detail_note}}</p>
  `);
}}

function renderWall() {{
  const w = DATA.walls[cur];
  const cabBtns = (w.cabinet_checks || []).map((c, ci) =>
    `<button class="btn blu" onclick="showCab(${{cur}},${{ci}})">&#128269; ${{c.title}}<br><span style="font-weight:400;font-size:11.5px">Plan ${{c.finished_label}} DW &rarr; Frame ${{c.required_rough_label}} Rough (+/- ${{c.max_tolerance_label}})</span></button>`
  ).join('');

  const ops = w.openings.map(op => `
    <div class="m-card">
      <div class="m-top">
        <div><span class="code">${{op.label}}</span><span class="old">${{op.plan_old_code}}</span></div>
        <span class="badge b-ver">&#10003; R.O. ${{op.ro_size_label}}</span>
      </div>
      <div style="font-size:11.5px;color:var(--muted);margin-bottom:5px">${{op.room_and_type}}</div>
      <div class="pull-row">King(L): <strong>${{op.left_king_label}}</strong> | Sh(L): <strong>${{op.left_shoulder_label}}</strong></div>
      <div class="pull-row" style="color:#4ade80">R.O. Pull: <strong>${{op.left_ro_start_label}} to ${{op.right_ro_end_label}}</strong></div>
      <div class="pull-row">Sh(R): <strong>${{op.right_shoulder_end_label}}</strong> | King(R): <strong>${{op.right_king_end_label}}</strong></div>
      <div style="font-size:12px;margin-top:6px">
        <strong>Hdr:</strong> ${{op.header_stock}} @ <strong style="color:#38bdf8">${{op.header_length_label}}</strong><br>
        <strong>Shoulders:</strong> ${{op.shoulders_per_side}}x/side @ <strong>${{op.shoulder_length_label}}</strong> &middot; <strong>Sill:</strong> ${{op.sill_length_label}}
      </div>
    </div>
  `).join('') || `<div class="m-card">No openings.</div>`;

  const ixs = w.intersections.map(ix => `
    <div class="m-card">
      <div class="m-top">
        <strong style="color:#fbbf24;font-size:15px">${{ix.intersecting_wall_id}} Channel (${{ix.thickness_label}})</strong>
        <span class="badge b-lock">${{ix.tolerance_rule.split('—')[0]}}</span>
      </div>
      <div style="font-size:12px;color:var(--muted);margin-bottom:5px">${{ix.description}}</div>
      <div class="pull-row">Backer(L): <strong>${{ix.left_backer_label}}</strong></div>
      <div class="pull-row" style="color:#4ade80">Partition Pocket: <strong>${{ix.left_edge_label}} to ${{ix.right_edge_label}}</strong></div>
      <div class="pull-row">Backer(R): <strong>${{ix.right_backer_end_label}}</strong></div>
      <div style="font-size:12px;color:#38bdf8;margin-top:5px">${{ix.top_plate_lap_gap_label}}</div>
    </div>
  `).join('') || `<div class="m-card">No partition channels.</div>`;

  const blks = (w.blocking || []).map(b => `
    <div class="m-card">
      <div style="font-weight:800;color:#f472b6">${{b.kind}} — ${{b.label}}</div>
      <div style="font-size:12.5px;margin-top:3px"><strong>Stock:</strong> ${{b.lumber}} &middot; <strong style="color:#4ade80">${{b.height_aff_label}}</strong></div>
      <div style="font-size:12px;color:var(--muted);margin-top:2px">${{b.location_note}}</div>
    </div>
  `).join('');

  document.getElementById('wallView').innerHTML = `
    <div class="m-card" style="border-top:5px solid ${{w.color_info.hex}}">
      <div style="font-size:11.5px;font-weight:800;color:${{w.color_info.hex}}">${{w.color_info.color}} Zone &middot; ${{w.color_info.wall_height_label}} &middot; ${{w.lumber_size}}</div>
      <div style="font-size:17px;font-weight:900;margin:2px 0">${{w.wall_id}} — ${{w.name}}</div>
      <div style="font-size:11.5px;color:var(--muted)">${{w.labor_tier}} (${{w.baseline_man_hours}} hrs)</div>
      ${{cabBtns}}
    </div>

    <div class="hero-pull">
      <div>
        <div style="font-size:10.5px;color:var(--muted);text-transform:uppercase;font-weight:800">Left-End Stud Pull</div>
        <div class="big">${{w.x_and_go_callout}}</div>
      </div>
      <div class="meta">
        <div>Plate: <strong>${{w.length_label}}</strong></div>
        <div>Studs: <strong>${{w.precut_stud_count}} @ ${{w.color_info.precut_stud_label}}</strong></div>
      </div>
    </div>

    ${{w.goofy_alert ? `<div class="alert">&#9888; ${{w.goofy_alert}}</div>` : ''}}

    <div class="sec-hdr">Openings (Pulled From Left End)</div>
    ${{ops}}

    <div class="sec-hdr">On-Deck Partition Channels (From Left End)</div>
    ${{ixs}}

    <div class="sec-hdr">Blocking &amp; Mechanical</div>
    ${{blks}}

    <div class="sec-hdr">16" O.C. Tape Marks (${{w.x_and_go_callout}})</div>
    <div class="m-card"><div class="tape">${{w.oc_marks_short.map((m,i)=>`<span class="tk ${{i===0?'st':''}}">${{i===0?m+' & GO':m+' X'}}</span>`).join('')}}</div></div>
  `;
}}

function renderBatches() {{
  document.getElementById('tab-batches').innerHTML = `
    <div class="sec-hdr">Grouped Headers (Cut Bench)</div>
    ${{DATA.batches.headers.map(h => `
      <div class="m-card">
        <div class="m-top"><strong style="color:#4ade80;font-size:17px">${{h.count}}x</strong><strong style="color:#38bdf8;font-size:16px">${{h.length_label}}</strong></div>
        <div style="font-weight:700">${{h.stock}}</div>
        <div style="font-size:12px;color:var(--muted);margin-top:4px">Labels: ${{h.labels.join(', ')}}</div>
      </div>
    `).join('')}}
    <div class="sec-hdr">Pre-Made Supporting Shoulders</div>
    ${{DATA.batches.shoulders.map(s => `
      <div class="m-card">
        <div class="m-top"><strong style="color:#38bdf8;font-size:16px">${{s.total_assemblies}} assy (${{s.total_pieces}} pcs)</strong><strong style="color:#4ade80;font-size:16px">${{s.length_label}}</strong></div>
        <div style="font-weight:700">${{s.lumber}} (${{s.plies_per_side}}-ply)</div>
        <div style="font-size:12px;color:var(--muted);margin-top:4px">${{s.labels.join(', ')}}</div>
      </div>
    `).join('')}}
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
    <div class="m-card">
      <div style="font-weight:800;font-size:15px;margin-bottom:8px">Stair Stringer — Plan vs. Actual Field Cut</div>
      <label>Plan Wall Stud Stock</label>
      <select id="st_stud" onchange="calcStairs()">
        <option value="92.625">92-5/8" (8' Wall)</option>
        <option value="104.625" selected>104-5/8" (9' Wall)</option>
        <option value="116.625">116-5/8" (10' Wall)</option>
        <option value="126.625">126-5/8" (Tall Wall)</option>
      </select>
      <label>Plan Floor Assembly Depth (In)</label>
      <input id="st_floor" type="number" step="0.125" value="12.625" oninput="calcStairs()">
      <label>ACTUAL FIELD TOTAL RISE (In)</label>
      <input id="st_field" type="number" step="0.125" value="121.25" oninput="calcStairs()">
      <label>Tread Thickness Drop (In)</label>
      <input id="st_tread" type="number" step="0.125" value="1.5" oninput="calcStairs()">
      <label>Unit Run Per Tread (In)</label>
      <input id="st_run" type="number" step="0.25" value="10.0" oninput="calcStairs()">
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
    <div class="pull-row">Plan Theoretical Rise: <strong>${{fmt16(planTot)}}</strong> (${{pR}} @ ${{fmt16(pU)}})</div>
    <div class="pull-row" style="color:#4ade80">ACTUAL FIELD RISE: <strong>${{fmt16(field)}}</strong> (Delta: ${{fmt16(field - planTot)}})</div>
    <div class="pull-row" style="color:#38bdf8;font-size:14px">CUT STRINGER UNIT RISE: <strong>${{fmt16(fU)}}</strong> (${{fR}} Risers / ${{fR-1}} Treads)</div>
    <div class="pull-row">Unit Run: <strong>${{fmt16(run)}}</strong> &middot; Total Run: <strong>${{Math.floor(totRun/12)}}' ${{fmt16(totRun%12)}}</strong></div>
    <div class="pull-row" style="color:#fbbf24">Bottom Riser Cut (-${{fmt16(tread)}} Tread): <strong>${{fmt16(fU - tread)}}</strong></div>
  `;
}}

function renderYard() {{
  document.getElementById('tab-yard').innerHTML = `
    <div class="sec-hdr">Jobsite Yard &amp; Deck Staging Map</div>
    <div class="m-card" style="border-left:4px solid #4ade80">
      <strong style="color:#4ade80">Close Perimeter (Hand-Carried)</strong>
      <div style="font-size:12.5px;margin-top:4px">I-Joists dropped right against foundation parallel to span; Treated 2x6 sills &amp; rim at corner; Cut bench beside 2x10/2x12/2x6 header stock.</div>
    </div>
    <div class="m-card" style="border-left:4px solid #38bdf8">
      <strong style="color:#38bdf8">On-Deck Stud Bunks</strong>
      <div style="font-size:12.5px;margin-top:4px">104-5/8" bunk at South/East deck (W-1, W-3, W-4); 116-5/8" bunk at North/Center deck (W-2, W-5, W-6); 92-5/8" bunk at interior hall (W-7); 7/16" sheathing &amp; Tyvek at exterior plates.</div>
    </div>
    <div class="m-card" style="border-left:4px solid #fbbf24">
      <strong style="color:#fbbf24">Front Porch 8'x4' Pad</strong>
      <div style="font-size:12.5px;margin-top:4px">8'x4' porch beams, roof deck, gable, and rake built directly on top of the front porch foundation walls before lifting.</div>
    </div>
    <div class="m-card" style="border-left:4px solid #f472b6">
      <strong style="color:#f472b6">Outer SkyTrak Yard (Far Off Perimeter)</strong>
      <div style="font-size:12.5px;margin-top:4px">Floor trusses in 4–6 packs reverse-staged (LIFO North->South, East->West); Roof trusses sorted in field (pack only 10+ identical commons); Ground-completed gable ends; Steel I-beam &amp; teleposts (by others, field-set/welded).</div>
    </div>
  `;
}}

function renderGoal() {{
  document.getElementById('tab-goal').innerHTML = `
    <div class="goal-box">${{DATA.daily_goal}}</div>
    <div id="goalOut" style="font-weight:800;color:#4ade80;margin-bottom:8px;font-size:13.5px"></div>
    ${{DATA.walls.map(w => `
      <label class="m-card" style="display:flex;align-items:center;gap:10px;color:var(--text);cursor:pointer">
        <input type="checkbox" checked onchange="recalcGoal()" class="wchk" data-h="${{w.baseline_man_hours}}" data-id="${{w.wall_id}}" style="width:20px;height:20px;margin:0">
        <div>
          <div style="font-weight:800">${{w.wall_id}} — ${{w.name}}</div>
          <div style="font-size:11.5px;color:var(--muted)">${{w.labor_tier}} &middot; <strong>${{w.baseline_man_hours}} hrs</strong></div>
        </div>
      </label>
    `).join('')}}
  `;
  recalcGoal();
}}

function recalcGoal() {{
  let done = 0, rem = 0, q = [];
  document.querySelectorAll('.wchk').forEach(c => {{
    const h = parseFloat(c.getAttribute('data-h')) || 0;
    if (c.checked) done += h; else {{ rem += h; q.push(c.getAttribute('data-id')); }}
  }});
  document.getElementById('goalOut').textContent = `Done: ${{done.toFixed(1)}} hrs | Left: ${{rem.toFixed(1)}} hrs ${{q.length ? '(Next: ' + q.join(', ') + ')' : ''}}`;
}}

renderStrip(); renderWall(); renderBatches(); renderStairs(); renderYard(); renderGoal();
</script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(HTML_PATH), exist_ok=True)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote mobile framing app:", HTML_PATH, "bytes:", len(html))


if __name__ == "__main__":
    build_html()
