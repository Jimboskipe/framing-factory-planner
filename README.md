# Framing Factory Planner — Pre-Staged Jobsite Framing System (PWA + Python Engine)

**"Build the entire house on paper before stepping on site. Hand a carpenter one sheet, give the daily goal, and let the crew roll."**

Created by **James M. Doyle** (UBC Local 1781 Journeyman Carpenter; Founder of Doyle's Contracting LLC, 2015–2021, 100+ residential & commercial framing projects).

> **Prototype & Field-Testing Notice:** This repository and Progressive Web App are the digital groundwork of the paper pre-staging, layout, and bidding workflow I developed and ran at Doyle's Contracting LLC (2015–2021). Because I am not actively framing houses full-time today, this software build has not yet been put to work on an active residential crew; I built it now that I have software and data engineering skills to demonstrate how I would deploy, test, and refine my jobsite system in the present day.
>
> **Proprietary Trading & IP Notice:** No proprietary trading strategies, live market execution code, or personal trading data have been placed in this repository. All personal and algorithmic trading systems are strictly proprietary information and are intentionally excluded from public repositories.

---

## Live Crew App

- **Live Downloadable Crew App (GitHub Pages):** [https://jimboskipe.github.io/framing-factory-planner/](https://jimboskipe.github.io/framing-factory-planner/)

The crew UI is intentionally stripped of "how-to-frame" textbook clutter—a seasoned framer already knows how to square a wall on the deck or nail off sheathing. The screen shows **strictly the pre-figured measurements, labels, cut batches, blocking locations, stair plan-vs-field numbers, yard staging zones, and daily goal hours** that cannot be memorized without looking at the plan:

1. **Wall Pull Sheets (Left-End Tape):**
   - Left-end first stud pull (`8-1/4" & GO`, `10-1/4" & GO`, `15-1/4" & GO`, `2-3/4" & GO`, `5-1/2" & GO`) determined off the master grid with an architectural scale, plus every `16" O.C.` mark.
   - **Order-Verified Door & Window Openings:** Left-end tape pulls for `King(L)`, `Shoulders(L)`, `R.O.`, `Shoulders(R)`, `King(R)` with human-readable Doyle labels (`LLPD1-82`, `PD1-82`, `GRW1-60`, `MS1-60`, `BR2W1-48`, `BR3W1-48`, `PDW1-28`, `FD1-66`, `GD1-194`).
   - **Partition Channels Built On Deck:** Exact left-end tape pulls for left channel backer stud, partition pocket (`3-1/2"` or `5-1/2"`), right channel backer stud, and 2nd top-plate lap gap—plus clickable **`CHECK DRYWALL CABINET PLAN`** popups (`108-1/2"` finished drywall-to-drywall = `109-1/2"` rough stud-to-stud, `1/8"` max tolerance) on locked Kitchen, Bathroom, and Hallway lines.
   - **Blocking & Mechanical Locations:** Exact heights (AFF) and spans for Kitchen cabinet blocking (`2x10`), Bathroom towel/grab blocking (`2x8`), Living Room TV/mantle blocking (`2x12` from `54"` to `78"` AFF), Curtain rod hangers, and Plumbing/HVAC boxes.
2. **Cut Bench (Grouped Headers & Pre-Made Supporting Shoulders):** Batch quantities, stock, exact cut lengths, and keel labels across all 8 walls.
3. **Stairs (Plan Height vs. Actual Field Measurement):** Compares theoretical plan rise (from `92-5/8"`, `104-5/8"`, `116-5/8"`, or `126-5/8"` stud stock + floor assembly) against the real-world field measurement to output the exact stringer unit rise, unit run, and bottom riser kick drop.
4. **Jobsite Staging Map:** Hand-carried materials staged close and parallel to span (`I-Joists`, sills, cut bench); on-deck stud bunks spotted by wall height color zone; `8'x4'` front porch framed right on the porch concrete foundation pad; SkyTrak materials staged far off the working perimeter (`4–6` floor-truss packs reverse-staged `LIFO North->South, East->West`; roof trusses only packed when `10+` commons match; ground-completed gable ends).
5. **Daily Goal & Crew Baseline Hours:** Tracks `1-Man Solo` walls (`W-6` garage portal, `W-7` interior door corridor), `2-Man Team` walls (`W-1` through `W-5`, `W-8`), and `Full-Crew` lifts/truss sets.

---

## Run Locally

Python 3.9+ standard library only (`fractions`, `dataclasses`, `json`, `unittest`).

```bash
python framing_engine.py                     # export docs/project_data.json
python build_pwa.py                          # build clean docs/index.html PWA
python -m unittest discover -s tests -v      # run 7 unit tests
```
