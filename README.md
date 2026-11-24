# Framing Factory Planner — Pre-Staged Jobsite Framing System (PWA + Python Engine)

**"Build the entire house on paper before stepping on site. Hand a carpenter one sheet, give the daily goal, and let the crew roll."**

Created by **James M. Doyle** (UBC Local 1781 Journeyman Carpenter; Founder of Doyle's Contracting LLC, 2015–2021, 100+ residential & commercial framing projects).

This repository packages the exact pre-planning and pre-staging system used to frame **1,800–2,500+ sq ft custom homes in 5–14 days** into both a **zero-dependency Python layout engine (`framing_engine.py`)** and a **downloadable offline Progressive Web App (`docs/index.html`)** that carpenters can install directly on their phones or print as single-wall crew work cards.

> **Proprietary Trading & IP Notice:** No proprietary trading strategies, live market execution code, or personal trading data have been placed in this repository. All personal and algorithmic trading systems are strictly proprietary information and are intentionally excluded from public repositories.

---

## Core Jobsite Problems This Solves

1. **Left-End `"X and Go"` Plate Layout (Architectural Scale Alignment):**
   - Instead of every framer guessing where to pull layout, every wall plate is indexed from its **LEFT end** against the master building grid using an architectural scale before stepping on site.
   - The layout callout tells the framer the exact first pull from the left end of the plate—**`8-1/4" & GO`**, **`10-1/4" & GO`**, **`15-1/4" & GO`**, **`2-3/4" & GO`**, **`5-1/2" & GO`**—and every stud after that steps off at `16" O.C.` automatically so lower-level walkout walls, tall main walls, floor trusses, and roof trusses stack dead on center.
2. **Left-End Tape Pulls for Every Intersecting Wall Channel & Door/Window Opening:**
   - The framer hooks the left end of the plate once and marks:
     - Every `16" O.C.` stud (`X`)
     - Every intersecting partition wall channel (`W-6`, `W-7`, `W-9`) with exact left-to-right tape numbers
     - Every door and window rough opening (`King | Pre-Made Supporting Shoulders | <-- Verified R.O. --> | Shoulders | King`)
3. **Window-Order Packet Verification Gate & Human-Sense Labels (`No "TZ172" Garbage`):**
   - Blueprints regularly carry cryptic or outdated architect window codes (`TZ172`, `W-204B`) that cause crews to frame the wrong rough opening and tear walls apart later.
   - Every opening is verified against the **actual manufacturer window/door order packet** during pre-planning and renamed to a self-explanatory Doyle label (**Room/Type + # + R.O. Width in Inches**):
     - `LLPD1-82` = Lower-Level Walkout Patio Door #1 (`82" x 82-1/2"` R.O.)
     - `PD1-82` = Main Deck Patio Door #1 (`82" x 82-1/2"` R.O.)
     - `GRW1-60` = Great Room Picture Window #1 (`60" x 62"` R.O.)
     - `MS1-60` = Master Bedroom Twin Window #1 (`60" x 62"` R.O.)
     - `BR2W1-48` / `BR3W1-48` = Bedroom #2 & Bedroom #3 Windows (`48" x 62"` R.O.)
     - `PDW1-28` = Powder Room Window #1 (`28" x 42"` R.O.)
     - `GD1-194` = 16'x7' Overhead Garage Door #1 (`194" x 85-1/2"` R.O.)
4. **Grouped Header & Pre-Made Supporting Shoulder Batches:**
   - Identical header lengths (`2-ply 2x12`, `2-ply 2x10`, `2-ply LVL`) and pre-made supporting shoulder assemblies (`81"` double and single jacks) are automatically grouped across the entire house so the cut man can batch-cut, pre-assemble, label, and stage them with the SkyTrak before a single wall is stood.
5. **Color-Coded Wall Height Legend & `"Goofy Area / Field Heads-Up"` Alerts:**
   - Mirrors the highlighted paper plan legend (`Green = 9'1-1/8" wall / 104-5/8" pre-cut studs`, `Orange = 10'1-1/8" tall wall / 116-5/8" studs`, `Blue = 8'1-1/8" wall / 92-5/8" studs`, `Purple = Vault / Tray Ceiling Transition`, `Red = Goofy Area / Field Heads-Up`) and attaches unmissable field alerts for dropped tray ceilings, walkout step-frost walls, stairwell hatches, and garage portal hold-downs.

---

## Pre-Loaded Reference Project

Comes pre-loaded with an **8-Wall, 3-Bedroom Custom Walkout Ranch** featuring:
- **Full Walkout Lower-Level Exposure Wall (`W-1`)** with step-foundation frost wall callout, `8-1/4" & GO` layout stacked directly under Main Floor `W-2`, walkout patio door `LLPD1-82`, and Bedroom #3 egress window `BR3W1-48`.
- **10' Tall Great Room Rear Wall (`W-2`) + Dropped Perimeter Tray Ceiling Ledger** (`9'0"` chalk line for `12"` dropped ladder soffit + ridge girder point-load pocket).
- **Master Suite (`W-3`) with Stepped Tray Ceiling**, **Bedroom #2 & Powder Room (`W-4`)**, **10' Front Entry Foyer & Walkout Stairwell Hatch (`W-5`)**, **3-Car Garage 10' Portal Wall (`W-6`)**, **Interior Bedroom/Powder Door Corridor (`W-7`)**, and **Vault-to-Tray Fireplace Feature Wall (`W-8`)**.
- Plus an interactive **Custom Wall & Opening Calculator** inside the app so a foreman can enter any new wall, `"X and Go"` offset, intersecting wall channel, or verified opening on the fly and print a single-page **Crew Work Card**.

---

## Run Locally

Python 3.9+ standard library only (`fractions`, `dataclasses`, `json`, `unittest`).

```bash
python framing_engine.py                     # print full cut batches + left-end pull sheets & export docs/project_data.json
python -m unittest discover -s tests -v      # run 6 unit tests verifying carpenter math
```

To open the downloadable crew app locally, open `docs/index.html` in any browser (or visit the live GitHub Pages deployment).
