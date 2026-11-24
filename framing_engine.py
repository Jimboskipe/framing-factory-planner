"""Framing Factory Planner v2 — Doyle's Contracting Pre-Staging, Left-End Plate Layout & Bidding Engine.

Origin & Prototype Notice:
  Digital reconstruction of the paper pre-staging, layout, and bidding workflow developed and
  used by James M. Doyle at Doyle's Contracting LLC (2015-2021 across 100+ builds). Built to
  demonstrate how the system would be deployed, tested, and critiqued as software today.

Core Systems Implemented:
  1. Left-End Plate Layout ("X and Go" architectural-scale grid offset + 16" O.C. step-off).
  2. Left-End Tape Locations for On-Deck Intersecting Partition Channels (left backer stud,
     partition pocket, right backer stud, and 2nd top-plate lap cutout) + Door/Window R.O.s.
  3. Window & Door Order Packet Verification Gate + Human-Readable Doyle Labels (PD1-82, MS1-60).
  4. 1" Foundation Square Tolerance Gate + Fixed Room Lock (1/8" max tolerance on Kitchens,
     Bathrooms, Hallways w/ clickable Drywall Cabinet Plan check; flex absorbed in Bedrooms/Living).
  5. Complete On-Deck Wall Assembly (sheathing, bottom-up shingled Tyvek, hand-lift vs SkyTrak rule,
     ground-built gable ends, and ground-built porch roofs framed on the porch foundation pad).
  6. Floor Truss 4-6 Pack Reverse Staging (LIFO, North->South, East->West) vs Roof Truss 10+ Common Rule.
  7. Plan-vs-Field Stair Stringer Double-Check Calculator (theoretical stud/wall height vs actual field tape).
  8. Whole-House Blocking & Backing Schedule (Kitchen cabinets, Bath towel bars, TV mount, Curtain rod hangers, Mechanical).
  9. 3-Tier Bidding & Daily Goal Labor Baseline Engine (1-Man Solo, 2-Man Wall Team, Full-Crew Truss/Lift).
"""
from dataclasses import dataclass, field
from fractions import Fraction
import json
import math
import os
from typing import List, Dict

STUD_THICK = Fraction(3, 2)       # 1-1/2"
PLATE_THICK = Fraction(3, 2)      # 1-1/2"

WALL_COLOR_LEGEND = {
    "BLUE_8FT": {
        "color": "Blue",
        "hex": "#2563eb",
        "wall_height_label": '8\' 1-1/8" Standard Wall',
        "precut_stud_in": Fraction(92 * 8 + 5, 8),   # 92-5/8"
        "plate_height_in": Fraction(97 * 8 + 1, 8),  # 97-1/8"
        "meaning": '8\' Wall — Factory 92-5/8" Pre-Cut Studs',
    },
    "GREEN_9FT": {
        "color": "Green",
        "hex": "#16a34a",
        "wall_height_label": '9\' 1-1/8" Tall Main Wall',
        "precut_stud_in": Fraction(104 * 8 + 5, 8),  # 104-5/8"
        "plate_height_in": Fraction(109 * 8 + 1, 8),
        "meaning": '9\' Wall — Factory 104-5/8" Pre-Cut Studs',
    },
    "ORANGE_10FT": {
        "color": "Orange",
        "hex": "#ea580c",
        "wall_height_label": '10\' 1-1/8" High / Garage Wall',
        "precut_stud_in": Fraction(116 * 8 + 5, 8),  # 116-5/8"
        "plate_height_in": Fraction(121 * 8 + 1, 8),
        "meaning": '10\' Wall — Factory 116-5/8" Pre-Cut Studs',
    },
    "PURPLE_RAKE": {
        "color": "Purple",
        "hex": "#7c3aed",
        "wall_height_label": "Vault / Tray / Custom Slope",
        "precut_stud_in": Fraction(104 * 8 + 5, 8),
        "plate_height_in": Fraction(109 * 8 + 1, 8),
        "meaning": "Rake / Tray Ceiling Transition — Custom Blocking & Soffit Drop",
    },
    "RED_GOOFY": {
        "color": "Red Alert",
        "hex": "#dc2626",
        "wall_height_label": "Goofy Area / Field Heads-Up",
        "precut_stud_in": Fraction(116 * 8 + 5, 8),
        "plate_height_in": Fraction(121 * 8 + 1, 8),
        "meaning": "GOOFY AREA — Extra Field Framing Knowledge / Check With Lead Before Cutting",
    },
}


def fmt_in(val: Fraction) -> str:
    f = Fraction(val).limit_denominator(16)
    whole = int(f)
    rem = f - whole
    if rem == 0:
        return f'{whole}"'
    if whole == 0:
        return f'{rem.numerator}/{rem.denominator}"'
    return f'{whole}-{rem.numerator}/{rem.denominator}"'


def fmt_ft_in(val: Fraction) -> str:
    f = Fraction(val).limit_denominator(16)
    ft = int(f // 12)
    rem_in = f - ft * 12
    return f"{ft}' {fmt_in(rem_in)} ({fmt_in(f)})"


@dataclass
class BlockingSpec:
    kind: str           # "KITCHEN_CABINET", "BATH_TOWEL", "TV_MOUNT", "CURTAIN_ROD", "MECHANICAL"
    label: str          # e.g. "Kitchen Upper & Lower Cabinet Blocking"
    lumber: str         # e.g. "2x10 Solid Blocking" or "2x6 Flat Backing"
    height_aff_label: str  # e.g. "34-1/2\" & 54\" to 84\" AFF"
    location_note: str  # e.g. "Full run between W-6 and right corner + curtain rod blocks at GRW1-60"


@dataclass
class CabinetDrywallCheck:
    title: str                  # e.g. "CHECK DRYWALL CABINET PLAN — Kitchen South/West Run"
    finished_drywall_to_drywall_in: Fraction  # e.g. 108-1/2" on cabinet shop drawing
    drywall_layers_total_in: Fraction         # e.g. 1" (two sheets of 1/2" drywall)
    max_tolerance_in: Fraction = Fraction(1, 8)  # 1/8" max variance
    room_type: str = "KITCHEN (ZERO-TOLERANCE LOCKED)"
    detail_note: str = ""

    @property
    def required_rough_stud_to_stud_in(self) -> Fraction:
        return self.finished_drywall_to_drywall_in + self.drywall_layers_total_in


@dataclass
class Opening:
    label: str
    room_and_type: str
    kind: str
    left_ro_start_in: Fraction
    ro_width_in: Fraction
    ro_height_in: Fraction
    head_height_in: Fraction
    header_stock: str
    header_depth_in: Fraction
    shoulders_per_side: int
    order_packet_verified: bool = True
    plan_old_code: str = ""
    curtain_rod_blocking: bool = True

    @property
    def right_ro_end_in(self) -> Fraction:
        return self.left_ro_start_in + self.ro_width_in

    @property
    def shoulder_span_each_side_in(self) -> Fraction:
        return STUD_THICK * self.shoulders_per_side

    @property
    def left_shoulder_start_in(self) -> Fraction:
        return self.left_ro_start_in - self.shoulder_span_each_side_in

    @property
    def left_king_start_in(self) -> Fraction:
        return self.left_shoulder_start_in - STUD_THICK

    @property
    def right_shoulder_end_in(self) -> Fraction:
        return self.right_ro_end_in + self.shoulder_span_each_side_in

    @property
    def right_king_end_in(self) -> Fraction:
        return self.right_shoulder_end_in + STUD_THICK

    @property
    def header_length_in(self) -> Fraction:
        return self.ro_width_in + 2 * self.shoulder_span_each_side_in

    @property
    def shoulder_length_in(self) -> Fraction:
        return self.head_height_in - PLATE_THICK

    @property
    def sill_length_in(self) -> Fraction:
        return self.ro_width_in if self.kind == "WINDOW" else Fraction(0)


@dataclass
class WallIntersection:
    intersecting_wall_id: str
    description: str
    left_edge_in: Fraction
    wall_thickness_in: Fraction = Fraction(7, 2)
    tolerance_rule: str = "FLEX_ALLOWED"  # or "LOCKED_1_8_IN (Kitchen/Bath/Hall)"

    @property
    def right_edge_in(self) -> Fraction:
        return self.left_edge_in + self.wall_thickness_in

    @property
    def left_channel_stud_start_in(self) -> Fraction:
        return self.left_edge_in - STUD_THICK

    @property
    def right_channel_stud_end_in(self) -> Fraction:
        return self.right_edge_in + STUD_THICK


@dataclass
class WallPlan:
    wall_id: str
    name: str
    lumber_size: str
    color_code: str
    length_in: Fraction
    first_stud_pull_in: Fraction
    spacing_oc_in: Fraction = Fraction(16)
    openings: List[Opening] = field(default_factory=list)
    intersections: List[WallIntersection] = field(default_factory=list)
    blocking: List[BlockingSpec] = field(default_factory=list)
    cabinet_checks: List[CabinetDrywallCheck] = field(default_factory=list)
    lift_method: str = "HAND-LIFT (2-Man Frame + Crew Walk-Up — Faster Than SkyTrak)"
    tyvek_rule: str = "Complete on deck: Sheath, route openings, roll Tyvek from BOTTOM UP (shingle-lapped so water cannot enter wrap)."
    labor_tier: str = "TIER_2_PAIR"      # TIER_1_SOLO, TIER_2_PAIR, TIER_3_CREW
    baseline_man_hours: float = 3.5
    goofy_alert: str = ""
    crew_note: str = ""

    @property
    def x_and_go_callout(self) -> str:
        return f'{fmt_in(self.first_stud_pull_in)} & GO'

    def oc_stud_marks_in(self) -> List[Fraction]:
        marks: List[Fraction] = []
        pos = self.first_stud_pull_in
        while pos < self.length_in - STUD_THICK:
            marks.append(pos)
            pos += self.spacing_oc_in
        return marks

    def precut_stud_count(self) -> int:
        return 2 + len(self.oc_stud_marks_in()) + 2 * len(self.openings) + 2 * len(self.intersections)


def calculate_stair_stringer(
    plan_stud_height_in: float,
    floor_assembly_depth_in: float,
    field_measured_total_rise_in: float,
    tread_thickness_in: float = 1.5,
    target_riser_in: float = 7.5,
    unit_run_in: float = 10.0,
) -> dict:
    """Compare theoretical plan stair rise against real-world field laser/tape measurement."""
    # Wall height = bottom plate (1.5) + stud + double top plate (3.0) = stud + 4.5"
    plan_total_rise = plan_stud_height_in + 4.5 + floor_assembly_depth_in
    plan_risers = max(1, round(plan_total_rise / target_riser_in))
    plan_unit_rise = plan_total_rise / plan_risers

    field_risers = max(1, round(field_measured_total_rise_in / target_riser_in))
    field_unit_rise = field_measured_total_rise_in / field_risers
    field_total_run = (field_risers - 1) * unit_run_in
    bottom_riser_cut = field_unit_rise - tread_thickness_in
    delta_in = field_measured_total_rise_in - plan_total_rise

    return {
        "plan_total_rise_in": round(plan_total_rise, 3),
        "plan_total_rise_label": fmt_in(Fraction(plan_total_rise).limit_denominator(16)),
        "plan_riser_count": plan_risers,
        "plan_unit_rise_label": fmt_in(Fraction(plan_unit_rise).limit_denominator(16)),
        "field_total_rise_in": round(field_measured_total_rise_in, 3),
        "field_total_rise_label": fmt_in(Fraction(field_measured_total_rise_in).limit_denominator(16)),
        "field_riser_count": field_risers,
        "field_unit_rise_in": round(field_unit_rise, 4),
        "field_unit_rise_label": fmt_in(Fraction(field_unit_rise).limit_denominator(16)),
        "tread_count": field_risers - 1,
        "unit_run_label": fmt_in(Fraction(unit_run_in).limit_denominator(16)),
        "field_total_run_label": fmt_ft_in(Fraction(field_total_run).limit_denominator(16)),
        "bottom_kick_drop_label": fmt_in(Fraction(bottom_riser_cut).limit_denominator(16)),
        "plan_vs_field_delta_label": fmt_in(Fraction(abs(delta_in)).limit_denominator(16)),
        "code_compliant": field_unit_rise <= 7.75 and unit_run_in >= 10.0,
    }


def evaluate_foundation_square(out_of_square_in: float) -> dict:
    """Apply James M. Doyle's 1-inch foundation square tolerance & Fixed-vs-Flex room law."""
    within_one_inch = abs(out_of_square_in) <= 1.0
    return {
        "out_of_square_in": out_of_square_in,
        "within_one_inch_tolerance": within_one_inch,
        "action": (
            "<= 1\" OUT OF SQUARE: Build dead-square structure off straightest master wall (3-4-5) and set directly on foundation. Zero layout edits required."
            if within_one_inch
            else "> 1\" OUT OF SQUARE: Adjust field plates. LOCK Kitchens (108-1/2\" DW-to-DW / 109-1/2\" rough), Bathrooms (60\" tub alcoves), and Hallways to 1/8\" tolerance. Absorb all variance in Bedrooms and Living/Great Room."
        ),
        "locked_zones": [
            "Kitchen Cabinet Runs (1/8\" max variance — verify Drywall-to-Drywall + 1\" for 1/2\" drywall both sides)",
            "Bathroom Tub/Shower Alcoves & Vanity Walls (1/8\" max variance — 60\" tub pocket must fit tight)",
            "Hallways & Door Trim Clearances (1/8\" max variance)",
        ],
        "flex_zones": [
            "Bedrooms #1, #2, #3 (absorb +/- 1\" invisibly without affecting cabinetry or code)",
            "Great Room / Living Room open span (absorb variance outside kitchen cabinet line)",
        ],
    }


def group_headers_and_shoulders(walls: List[WallPlan]) -> Dict[str, List[dict]]:
    header_groups: Dict[tuple, dict] = {}
    shoulder_groups: Dict[tuple, dict] = {}
    sill_groups: Dict[tuple, dict] = {}

    for w in walls:
        for op in w.openings:
            h_key = (op.header_stock, op.header_length_in)
            if h_key not in header_groups:
                header_groups[h_key] = {
                    "stock": op.header_stock,
                    "length_in": float(op.header_length_in),
                    "length_label": fmt_ft_in(op.header_length_in),
                    "count": 0,
                    "labels": [],
                }
            header_groups[h_key]["count"] += 1
            header_groups[h_key]["labels"].append(f"{op.label} ({w.wall_id})")

            s_key = (w.lumber_size, op.shoulder_length_in, op.shoulders_per_side)
            if s_key not in shoulder_groups:
                shoulder_groups[s_key] = {
                    "lumber": w.lumber_size,
                    "length_in": float(op.shoulder_length_in),
                    "length_label": fmt_in(op.shoulder_length_in),
                    "plies_per_side": op.shoulders_per_side,
                    "total_assemblies": 0,
                    "total_pieces": 0,
                    "labels": [],
                }
            shoulder_groups[s_key]["total_assemblies"] += 2
            shoulder_groups[s_key]["total_pieces"] += 2 * op.shoulders_per_side
            shoulder_groups[s_key]["labels"].append(f"{op.label} ({w.wall_id})")

            if op.kind == "WINDOW":
                sl_key = (w.lumber_size, op.sill_length_in)
                if sl_key not in sill_groups:
                    sill_groups[sl_key] = {
                        "lumber": w.lumber_size,
                        "length_in": float(op.sill_length_in),
                        "length_label": fmt_in(op.sill_length_in),
                        "count": 0,
                        "labels": [],
                    }
                sill_groups[sl_key]["count"] += 1
                sill_groups[sl_key]["labels"].append(f"{op.label} ({w.wall_id})")

    return {
        "headers": list(header_groups.values()),
        "shoulders": list(shoulder_groups.values()),
        "sills": list(sill_groups.values()),
    }


def sample_custom_ranch_project() -> List[WallPlan]:
    """Realistic 3-Bedroom Custom Walkout Ranch (Full Basement Exposure, 9'/10' Tall Walls, Tray Ceilings)."""
    return [
        WallPlan(
            wall_id="W-1",
            name="Lower-Level Full Walkout Exposure Wall (South Rear)",
            lumber_size="2x6",
            color_code="GREEN_9FT",
            length_in=Fraction(36 * 12),
            first_stud_pull_in=Fraction(33, 4),  # 8-1/4" & GO
            openings=[
                Opening(
                    label="LLPD1-82",
                    room_and_type="Lower-Level Walkout Patio Door #1 (Rec Room)",
                    kind="DOOR",
                    left_ro_start_in=Fraction(72),
                    ro_width_in=Fraction(82),
                    ro_height_in=Fraction(165, 2),
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 1-3/4"x11-7/8" LVL',
                    header_depth_in=Fraction(95, 8),
                    shoulders_per_side=2,
                    order_packet_verified=True,
                    plan_old_code="TZ172-LL",
                ),
                Opening(
                    label="LLW1-72",
                    room_and_type="Lower-Level Exposure Twin Window #1 (Rec Room)",
                    kind="WINDOW",
                    left_ro_start_in=Fraction(192),
                    ro_width_in=Fraction(72),
                    ro_height_in=Fraction(62),
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 1-3/4"x11-7/8" LVL',
                    header_depth_in=Fraction(95, 8),
                    shoulders_per_side=2,
                    order_packet_verified=True,
                    plan_old_code="W-01A",
                ),
                Opening(
                    label="BR3W1-48",
                    room_and_type="Bedroom #3 Exposure Egress Window #1",
                    kind="WINDOW",
                    left_ro_start_in=Fraction(312),
                    ro_width_in=Fraction(48),
                    ro_height_in=Fraction(62),
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 2x12 w/ 1/2" OSB',
                    header_depth_in=Fraction(45, 4),
                    shoulders_per_side=2,
                    order_packet_verified=True,
                    plan_old_code="W-03E",
                ),
            ],
            intersections=[
                WallIntersection("W-9", "Bedroom #3 / Rec Room Demising Wall (2x4 — FLEX ROOM)", Fraction(282), Fraction(7, 2), "FLEX_ALLOWED (Bedroom #3 absorbs foundation variance)"),
            ],
            blocking=[
                BlockingSpec("CURTAIN_ROD", "Curtain Rod Hanger Blocking", "2x6 Solid Blocks", '84" to 88" AFF (Left & Right of Header)', "Install 16\" past each side of LLPD1-82, LLW1-72, and BR3W1-48 while wall is on deck."),
                BlockingSpec("MECHANICAL", "Lower-Level Hose Bib & ExteriorSconce Box Backing", "2x6 Flat Block", '18" & 78" AFF', "At 4' 8\" from left end next to walkout patio door."),
            ],
            labor_tier="TIER_2_PAIR (2-Man Frame on Deck -> Full Crew Hand-Lift)",
            baseline_man_hours=5.0,
            goofy_alert="FULL WALKOUT EXPOSURE WALL: Treated 2x6 bottom plate on concrete curb + step-foundation frost wall transition at left end. Build complete on deck, roll Tyvek from bottom up, hand-lift with crew. Verify floor-truss bearing ribbon elevation with laser!",
            crew_note="Pull from LEFT (Southwest foundation step): 8-1/4\" & GO. Stacks directly under Main Floor W-2.",
        ),
        WallPlan(
            wall_id="W-2",
            name="Great Room 10' Tall Rear Exposure Wall (Above Walkout)",
            lumber_size="2x6",
            color_code="ORANGE_10FT",
            length_in=Fraction(28 * 12),
            first_stud_pull_in=Fraction(33, 4),  # 8-1/4" & GO
            openings=[
                Opening(
                    label="PD1-82",
                    room_and_type="Main Deck Patio Door #1 — Great Room",
                    kind="DOOR",
                    left_ro_start_in=Fraction(76),
                    ro_width_in=Fraction(82),
                    ro_height_in=Fraction(165, 2),
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 2x12 w/ 1/2" OSB',
                    header_depth_in=Fraction(45, 4),
                    shoulders_per_side=2,
                    order_packet_verified=True,
                    plan_old_code="TZ172",
                ),
                Opening(
                    label="GRW1-60",
                    room_and_type="Great Room Picture Window #1",
                    kind="WINDOW",
                    left_ro_start_in=Fraction(204),
                    ro_width_in=Fraction(60),
                    ro_height_in=Fraction(62),
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 2x12 w/ 1/2" OSB',
                    header_depth_in=Fraction(45, 4),
                    shoulders_per_side=2,
                    order_packet_verified=True,
                    plan_old_code="W-204B",
                ),
            ],
            intersections=[
                WallIntersection("W-6", "Kitchen / Great Room Bearing Partition (2x6 — LOCKED KITCHEN LINE)", Fraction(174), Fraction(11, 2), "LOCKED_1_8_IN — 108-1/2\" Drywall-to-Drywall Kitchen Run (109-1/2\" Stud-to-Stud)!"),
            ],
            blocking=[
                BlockingSpec("KITCHEN_CABINET", "Kitchen Upper & Lower Cabinet + Island Electrical Backing", "2x10 Solid Blocking", '34-1/2" (Base) & 54" to 96" AFF (Uppers)', "From 14' 11-1/2\" (right face of W-6 channel) to 24' 1\" — zero-tolerance cabinet wall."),
                BlockingSpec("CURTAIN_ROD", "Curtain Rod Hanger Blocking", "2x6 Solid Blocks", '84" to 88" AFF', "16\" left and right of PD1-82 and GRW1-60 headers."),
            ],
            cabinet_checks=[
                CabinetDrywallCheck(
                    title="CHECK DRYWALL CABINET PLAN — Kitchen L-Run (W-6 Channel to East Corner)",
                    finished_drywall_to_drywall_in=Fraction(217, 2),  # 108-1/2" finished drywall-to-drywall
                    drywall_layers_total_in=Fraction(1),               # +1" (two layers of 1/2" drywall) = 109-1/2" rough
                    max_tolerance_in=Fraction(1, 8),
                    room_type="KITCHEN (1/8\" MAX VARIANCE — ZERO FUDGE ZONE)",
                    detail_note="Cabinet plan specifies 108-1/2\" finished drywall-to-drywall (36\" fridge + 24\" pantry + 48-1/2\" base/corner). Frame rough stud-to-stud at exactly 109-1/2\" (+/- 1/8\"). If foundation is out of square >1\", absorb variance in Great Room left of W-6—NEVER in Kitchen!",
                ),
            ],
            labor_tier="TIER_2_PAIR (2-Man Frame on Deck -> Full Crew Hand-Lift)",
            baseline_man_hours=4.5,
            goofy_alert="10'1-1/8\" TALL WALL (116-5/8\" Studs) + GREAT ROOM TRAY CEILING LEDGER: Snap chalk line at 9' 0\" AFF around inside face of W-2 and W-6 for 12\" dropped perimeter tray ceiling soffit ladder framing. Complete sheathing & bottom-up Tyvek on deck before lifting.",
            crew_note="Pull from LEFT: 8-1/4\" & GO so studs stack vertically over Lower-Level Walkout W-1.",
        ),
        WallPlan(
            wall_id="W-3",
            name="Bedroom #1 (Master Suite) Rear Exterior + Tray Ceiling",
            lumber_size="2x6",
            color_code="GREEN_9FT",
            length_in=Fraction(20 * 12),
            first_stud_pull_in=Fraction(41, 4),  # 10-1/4" & GO
            openings=[
                Opening(
                    label="MS1-60",
                    room_and_type="Master Bedroom Twin Window #1",
                    kind="WINDOW",
                    left_ro_start_in=Fraction(66),
                    ro_width_in=Fraction(60),
                    ro_height_in=Fraction(62),
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 2x12 w/ 1/2" OSB',
                    header_depth_in=Fraction(45, 4),
                    shoulders_per_side=2,
                    order_packet_verified=True,
                    plan_old_code="W-108A",
                ),
                Opening(
                    label="MBW1-36",
                    room_and_type="Master Bath Transom Window #1",
                    kind="WINDOW",
                    left_ro_start_in=Fraction(168),
                    ro_width_in=Fraction(36),
                    ro_height_in=Fraction(24),
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 2x10 w/ 1/2" OSB',
                    header_depth_in=Fraction(37, 4),
                    shoulders_per_side=1,
                    order_packet_verified=True,
                    plan_old_code="W-112T",
                ),
            ],
            intersections=[
                WallIntersection("W-7", "Master Bath Wet Wall (2x6 Plumbing — LOCKED 60\" SHOWER/VANITY)", Fraction(146), Fraction(11, 2), "LOCKED_1_8_IN — Master Bath Vanity & 60\" Shower Alcove"),
            ],
            blocking=[
                BlockingSpec("BATH_TOWEL", "Master Bath Towel Bar, Robe Hook & Shower Glass Blocking", "2x8 Solid Blocking", '42" to 76" AFF', "Between W-7 channel (12' 7-1/2\") and East corner."),
                BlockingSpec("CURTAIN_ROD", "Master Bedroom Curtain Rod Hanger Blocking", "2x6 Solid Blocks", '84" to 88" AFF', "16\" past both sides of MS1-60 header."),
            ],
            cabinet_checks=[
                CabinetDrywallCheck(
                    title="CHECK DRYWALL CABINET / TUB PLAN — Master Bath 72\" Double Vanity & 60\" Shower Pocket",
                    finished_drywall_to_drywall_in=Fraction(72),
                    drywall_layers_total_in=Fraction(1),
                    max_tolerance_in=Fraction(1, 8),
                    room_type="BATHROOM (1/8\" MAX VARIANCE — ZERO FUDGE ZONE)",
                    detail_note="Master Bath requires 73\" rough stud-to-stud for 72\" tight-fit vanity + 60-1/4\" rough pocket for 60\" acrylic shower base. Absorb any wall length variance on the Master Bedroom side (left of W-7 channel at 12' 2\").",
                ),
            ],
            labor_tier="TIER_2_PAIR (2-Man Team)",
            baseline_man_hours=3.5,
            goofy_alert="MASTER BEDROOM STEPPED TRAY CEILING: Raised scissor-heel truss pocket sits between 0' 0\" and 12' 2\". Pre-build 2x4 ladder soffit boxes (16\" deep x 10\" drop) on deck before lifting onto perimeter ledger.",
            crew_note="Pull from LEFT: 10-1/4\" & GO. Notice MS1-60 uses the exact same header & double-shoulder package as GRW1-60.",
        ),
        WallPlan(
            wall_id="W-4",
            name="Bedroom #2 & Powder Room West Exterior Wall",
            lumber_size="2x6",
            color_code="GREEN_9FT",
            length_in=Fraction(24 * 12),
            first_stud_pull_in=Fraction(61, 4),  # 15-1/4" & GO
            openings=[
                Opening(
                    label="BR2W1-48",
                    room_and_type="Bedroom #2 Casement Window #1",
                    kind="WINDOW",
                    left_ro_start_in=Fraction(54),
                    ro_width_in=Fraction(48),
                    ro_height_in=Fraction(62),
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 2x12 w/ 1/2" OSB',
                    header_depth_in=Fraction(45, 4),
                    shoulders_per_side=2,
                    order_packet_verified=True,
                    plan_old_code="W-104",
                ),
                Opening(
                    label="PDW1-28",
                    room_and_type="Powder Room Window #1",
                    kind="WINDOW",
                    left_ro_start_in=Fraction(198),
                    ro_width_in=Fraction(28),
                    ro_height_in=Fraction(42),
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 2x10 w/ 1/2" OSB',
                    header_depth_in=Fraction(37, 4),
                    shoulders_per_side=1,
                    order_packet_verified=True,
                    plan_old_code="W-02C",
                ),
            ],
            intersections=[
                WallIntersection("W-8", "Bedroom #2 Closet / Hall Partition (2x4)", Fraction(144), Fraction(7, 2), "FLEX_ALLOWED on Bedroom #2 side"),
                WallIntersection("W-10", "Powder Room South Partition (2x4 — LOCKED POWDER ROOM)", Fraction(180), Fraction(7, 2), "LOCKED_1_8_IN — Powder Room 60\" Clear Width"),
            ],
            blocking=[
                BlockingSpec("BATH_TOWEL", "Powder Room Towel Ring, Mirror & Grab Bar Blocking", "2x8 Solid Blocking", '36" to 72" AFF', "Between 15' 3-1/2\" and 20' 3-1/2\"."),
                BlockingSpec("CURTAIN_ROD", "Bedroom #2 Curtain Rod Hanger Blocking", "2x6 Solid Blocks", '84" to 88" AFF', "Both sides of BR2W1-48 header."),
            ],
            cabinet_checks=[
                CabinetDrywallCheck(
                    title="CHECK DRYWALL CABINET PLAN — Powder Room Vanity & Toilet Centerline",
                    finished_drywall_to_drywall_in=Fraction(60),
                    drywall_layers_total_in=Fraction(1),
                    max_tolerance_in=Fraction(1, 8),
                    room_type="BATHROOM / HALL (1/8\" MAX VARIANCE)",
                    detail_note="Powder Room finishes at 60\" drywall-to-drywall (61\" rough stud-to-stud). Keep stud layout clear of 15-1/2\" toilet flange centerline!",
                ),
            ],
            labor_tier="TIER_2_PAIR (2-Man Team)",
            baseline_man_hours=3.5,
            crew_note="Pull from LEFT: 15-1/4\" & GO. Notice BR2W1-48 shares the exact same 54\" 2x12 header batch as BR3W1-48 on W-1.",
        ),
        WallPlan(
            wall_id="W-5",
            name="Front Entry Foyer & Ground-Built 8'x4' Porch Bearing Wall (North)",
            lumber_size="2x6",
            color_code="ORANGE_10FT",
            length_in=Fraction(22 * 12),
            first_stud_pull_in=Fraction(11, 4),  # 2-3/4" & GO
            openings=[
                Opening(
                    label="FD1-66",
                    room_and_type="Front Entry Door #1 w/ Dual Sidelites (66\" x 82-1/2\" R.O.)",
                    kind="DOOR",
                    left_ro_start_in=Fraction(99),
                    ro_width_in=Fraction(66),
                    ro_height_in=Fraction(165, 2),
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 2x12 w/ 1/2" OSB',
                    header_depth_in=Fraction(45, 4),
                    shoulders_per_side=2,
                    order_packet_verified=True,
                    plan_old_code="D-101SL",
                ),
            ],
            intersections=[
                WallIntersection("W-11", "Foyer Coat Closet East Wall (2x4 — LOCKED 48\" HALLWAY)", Fraction(48), Fraction(7, 2), "LOCKED_1_8_IN — Entry Hallway Width"),
                WallIntersection("W-12", "Walkout Stairwell Bearing Wall (2x6 — LOCKED STAIR RO)", Fraction(192), Fraction(11, 2), "LOCKED_1_8_IN — Stairwell Rough Opening"),
            ],
            blocking=[
                BlockingSpec("MECHANICAL", "Exterior Entry Lantern & Doorbell Transformer Backing", "2x6 Block", '66" AFF', "Left and right king studs of FD1-66."),
            ],
            labor_tier="TIER_2_PAIR (Wall) + TIER_2_PAIR (Ground-Built 8'x4' Porch Roof on Foundation Pad)",
            baseline_man_hours=5.5,
            goofy_alert="8'x4' FRONT PORCH BUILT ON CONCRETE PAD BEFORE LIFTING: Snap beam lines right on the front porch foundation pad, frame beams, roof deck, gable, and rake right on top of the porch foundation walls at ground level for safety and speed—then pick with SkyTrak and lag to W-5! Keep subfloor unglued in W-12 stairwell hatch.",
            crew_note="Pull from LEFT: 2-3/4\" & GO.",
        ),
        WallPlan(
            wall_id="W-6",
            name="3-Car Garage 10' Front Portal Wall (1-Man Solo Build)",
            lumber_size="2x6",
            color_code="RED_GOOFY",
            length_in=Fraction(24 * 12),
            first_stud_pull_in=Fraction(11, 2),  # 5-1/2" & GO
            openings=[
                Opening(
                    label="GD1-194",
                    room_and_type="16'x7' Overhead Garage Door #1 (194\" x 85-1/2\" R.O.)",
                    kind="DOOR",
                    left_ro_start_in=Fraction(47),
                    ro_width_in=Fraction(194),
                    ro_height_in=Fraction(171, 2),
                    head_height_in=Fraction(171, 2),
                    header_stock='2-ply 1-3/4"x11-7/8" LVL + Bottom Flat 2x6',
                    header_depth_in=Fraction(95, 8),
                    shoulders_per_side=2,
                    order_packet_verified=True,
                    plan_old_code="OHD-16",
                ),
            ],
            intersections=[],
            blocking=[
                BlockingSpec("MECHANICAL", "Garage Door Torsion Spring Center Pad & Opener Track Backing", "2-ply 2x12 Solid Pad", '90" to 108" AFF @ R.O. Center (12\' 0" from left)', "Required for overhead door spring anchor bracket."),
            ],
            lift_method="SKYTRAK ASSIST FOR 200\" LVL HEADER + PORTAL STAND",
            labor_tier="TIER_1_SOLO (1 Carpenter Frames This Wall Solo — Does Not Need a 2nd Guy)",
            baseline_man_hours=2.5,
            goofy_alert="1-MAN SOLO WALL + 10'1-1/8\" PORTAL: One carpenter frames W-6 solo while 2-man team runs main walls. Hold-down anchor bolts embedded in concrete at both king posts; confirm Simpson hold-down bracket alignment before setting!",
            crew_note="Pull from LEFT: 5-1/2\" & GO. 2x12 torsion spring blocking centered above GD1-194.",
        ),
        WallPlan(
            wall_id="W-7",
            name="Master Hall / Bedroom #2 Interior Door Corridor (2x4 — Locked Hallway)",
            lumber_size="2x4",
            color_code="BLUE_8FT",
            length_in=Fraction(18 * 12),
            first_stud_pull_in=Fraction(61, 4),  # 15-1/4" & GO
            openings=[
                Opening(
                    label="MD1-34",
                    room_and_type="Master Bedroom Entry Door #1 (2/8 Prehung — 34\" x 82-1/2\" R.O.)",
                    kind="DOOR",
                    left_ro_start_in=Fraction(24),
                    ro_width_in=Fraction(34),
                    ro_height_in=Fraction(165, 2),
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 2x6 w/ 1/2" OSB',
                    header_depth_in=Fraction(11, 2),
                    shoulders_per_side=1,
                    order_packet_verified=True,
                    plan_old_code="D-104",
                ),
                Opening(
                    label="BR2D1-32",
                    room_and_type="Bedroom #2 Entry Door #1 (2/6 Prehung — 32\" x 82-1/2\" R.O.)",
                    kind="DOOR",
                    left_ro_start_in=Fraction(108),
                    ro_width_in=Fraction(32),
                    ro_height_in=Fraction(165, 2),
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 2x6 w/ 1/2" OSB',
                    header_depth_in=Fraction(11, 2),
                    shoulders_per_side=1,
                    order_packet_verified=True,
                    plan_old_code="D-105",
                ),
                Opening(
                    label="PDD1-30",
                    room_and_type="Powder Room Door #1 (2/4 Prehung — 30\" x 82-1/2\" R.O.)",
                    kind="DOOR",
                    left_ro_start_in=Fraction(162),
                    ro_width_in=Fraction(30),
                    ro_height_in=Fraction(165, 2),
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 2x6 w/ 1/2" OSB',
                    header_depth_in=Fraction(11, 2),
                    shoulders_per_side=1,
                    order_packet_verified=True,
                    plan_old_code="D-106",
                ),
            ],
            intersections=[
                WallIntersection("W-8", "Bedroom #2 / Master Closet Divider (2x4)", Fraction(84), Fraction(7, 2), "LOCKED_1_8_IN — Hallway Clear Width"),
            ],
            blocking=[
                BlockingSpec("MECHANICAL", "Main Hall Thermostat & Smoke/CO Return Backing", "2x4 Block", '60" AFF', "At 6' 2\" from left end."),
            ],
            labor_tier="TIER_1_SOLO (1 Carpenter Frames Interior Door Wall Solo)",
            baseline_man_hours=2.0,
            crew_note="Interior 2x4 Hall Wall (Locked 42\" finished hallway width — 43\" rough stud-to-stud). Pull from LEFT: 15-1/4\" & GO.",
        ),
        WallPlan(
            wall_id="W-8",
            name="Great Room Vault-to-Tray Transition & Fireplace Feature Wall",
            lumber_size="2x6",
            color_code="PURPLE_RAKE",
            length_in=Fraction(16 * 12),
            first_stud_pull_in=Fraction(33, 4),  # 8-1/4" & GO
            openings=[
                Opening(
                    label="FP1-50",
                    room_and_type="Direct-Vent Gas Fireplace Chase Rough Opening #1",
                    kind="WINDOW",
                    left_ro_start_in=Fraction(71),
                    ro_width_in=Fraction(50),
                    ro_height_in=Fraction(44),
                    head_height_in=Fraction(44),
                    header_stock='2-ply 2x10 w/ 1/2" OSB',
                    header_depth_in=Fraction(37, 4),
                    shoulders_per_side=1,
                    order_packet_verified=True,
                    plan_old_code="FP-42DV",
                ),
            ],
            intersections=[],
            blocking=[
                BlockingSpec("TV_MOUNT", "Living Room Heavy TV Mount & Mantle Solid Blocking", "2x12 Solid Blocking", '54" to 78" AFF across full 60" center span', "Above FP1-50 header so homeowner/AV crew can lag anywhere without hunting studs."),
                BlockingSpec("MECHANICAL", "HDMI Conduit & Recessed Outlet Box Backing", "2x6 Box Frame", '66" AFF Centered at 8\' 0" from left', "Center of fireplace chase."),
            ],
            labor_tier="TIER_2_PAIR (2-Man Feature & Tray Soffit Team)",
            baseline_man_hours=3.5,
            goofy_alert="TRAY CEILING & COFFERED SOFFIT RETURN + TV BACKING: Install 2x12 solid blocking between studs from 54\" to 78\" AFF above FP1-50 for mantle & TV mount. Top of wall steps down 12\" at both ends to catch tray ceiling perimeter soffit.",
            crew_note="Pull from LEFT: 8-1/4\" & GO. Verify fireplace manufacturer clearance-to-combustibles sheet before framing header.",
        ),
    ]


def export_project_json(out_path: str) -> dict:
    walls = sample_custom_ranch_project()
    batches = group_headers_and_shoulders(walls)
    stair_demo = calculate_stair_stringer(
        plan_stud_height_in=104.625,        # 9' wall (104-5/8" stud + 4-1/2" plates = 109-1/8")
        floor_assembly_depth_in=12.625,     # 11-7/8" floor truss + 3/4" subfloor = 121-3/4" theoretical
        field_measured_total_rise_in=121.25,  # Real field laser measurement: 121-1/4" (1/2" difference!)
        tread_thickness_in=1.5,
    )
    payload = {
        "project_name": "Doyle's Contracting — 3-Bedroom Custom Walkout Ranch (Full Exposure, 9'/10' Tall Walls, Tray Ceilings)",
        "prototype_notice": "PROTOTYPE & ORIGIN NOTE: This software is a digital reconstruction of the paper pre-staging, layout, and bidding workflow I developed and ran at Doyle's Contracting LLC (2015–2021 across 100+ projects). Because I am not actively framing houses full-time today, this app has not yet been field-tested on an active crew; I built it using my current software & data skillset to show how I would deploy, test, and refine my jobsite system in the present day.",
        "daily_goal": "Day 2 Goal (Computed from Day 1 Baseline): 2-Man Team frames & bottom-up Tyveks W-2 & W-3; Solo Framer builds W-6 Garage Portal & W-7 Hall Wall; Full Crew hand-lifts exterior walls & sets reverse-staged (LIFO) floor/roof packs.",
        "foundation_rule": evaluate_foundation_square(1.375),
        "stair_default": stair_demo,
        "bidding_tiers": [
            {
                "tier": "Tier 1 — 1-Man Solo Tasks",
                "rule": "Tasks where a 2nd carpenter adds zero speed. Bidded and assigned to 1 experienced guy working off a single sheet.",
                "examples": "W-6 Front Garage Portal Wall (2.5 hrs), W-7 Interior Door Hallway (2.0 hrs), Chop-Saw Header & Pre-Made Shoulder Batch Bench (3.0 hrs), Stair Stringer Field Measure & Cut (2.5 hrs).",
            },
            {
                "tier": "Tier 2 — 2-Man Wall & Ground-Roof Teams",
                "rule": "Optimal 2-carpenter pair framing complete walls flat on the deck (plates -> studs -> on-deck partition channels -> sheathing -> router openings -> bottom-up shingled Tyvek) or building small porches & gable ends completely on the ground.",
                "examples": "W-1 Walkout Exposure Wall (5.0 man-hrs), W-2 10' Great Room Wall (4.5 man-hrs), W-3 Master Suite + Tray Soffit (3.5 man-hrs), Ground-Built 8'x4' Front Porch Roof on Concrete Pad + Gable End Complete w/ Tyvek (4.0 man-hrs).",
            },
            {
                "tier": "Tier 3 — Full-Crew All-Hands Evolutions",
                "rule": "Short, high-output pushes where the whole crew comes together: hand-lifting completed exterior walls (faster than waiting on the SkyTrak), setting reverse-staged (LIFO North->South, East->West) 4–6 floor-truss packs, or booming 10+ identical common roof truss runs.",
                "examples": "Hand-Lift Completed Exterior Walls (15 min per wall), Set 4-6 Pack Floor Trusses (12 picks per 150-truss span), Boom Complete Ground-Built Gable Ends & 8'x4' Porch Roof & Lag to Structure.",
            },
        ],
        "color_legend": {
            k: {
                "color": v["color"],
                "hex": v["hex"],
                "wall_height_label": v["wall_height_label"],
                "precut_stud_label": fmt_in(v["precut_stud_in"]),
                "meaning": v["meaning"],
            }
            for k, v in WALL_COLOR_LEGEND.items()
        },
        "batches": batches,
        "walls": [
            {
                "wall_id": w.wall_id,
                "name": w.name,
                "lumber_size": w.lumber_size,
                "color_code": w.color_code,
                "color_info": {
                    "color": WALL_COLOR_LEGEND[w.color_code]["color"],
                    "hex": WALL_COLOR_LEGEND[w.color_code]["hex"],
                    "wall_height_label": WALL_COLOR_LEGEND[w.color_code]["wall_height_label"],
                    "precut_stud_label": fmt_in(WALL_COLOR_LEGEND[w.color_code]["precut_stud_in"]),
                },
                "length_in": float(w.length_in),
                "length_label": fmt_ft_in(w.length_in),
                "first_stud_pull_in": float(w.first_stud_pull_in),
                "x_and_go_callout": w.x_and_go_callout,
                "oc_marks": [fmt_ft_in(m) for m in w.oc_stud_marks_in()],
                "oc_marks_short": [fmt_in(m) for m in w.oc_stud_marks_in()],
                "precut_stud_count": w.precut_stud_count(),
                "lift_method": w.lift_method,
                "tyvek_rule": w.tyvek_rule,
                "labor_tier": w.labor_tier,
                "baseline_man_hours": w.baseline_man_hours,
                "goofy_alert": w.goofy_alert,
                "crew_note": w.crew_note,
                "openings": [
                    {
                        "label": op.label,
                        "plan_old_code": op.plan_old_code,
                        "room_and_type": op.room_and_type,
                        "kind": op.kind,
                        "order_packet_verified": op.order_packet_verified,
                        "ro_size_label": f"{fmt_in(op.ro_width_in)} x {fmt_in(op.ro_height_in)}",
                        "left_king_label": fmt_ft_in(op.left_king_start_in),
                        "left_shoulder_label": fmt_ft_in(op.left_shoulder_start_in),
                        "left_ro_start_label": fmt_ft_in(op.left_ro_start_in),
                        "right_ro_end_label": fmt_ft_in(op.right_ro_end_in),
                        "right_shoulder_end_label": fmt_ft_in(op.right_shoulder_end_in),
                        "right_king_end_label": fmt_ft_in(op.right_king_end_in),
                        "header_stock": op.header_stock,
                        "header_length_label": fmt_ft_in(op.header_length_in),
                        "shoulders_per_side": op.shoulders_per_side,
                        "shoulder_length_label": fmt_in(op.shoulder_length_in),
                        "sill_length_label": fmt_in(op.sill_length_in) if op.kind == "WINDOW" else "N/A (Door)",
                    }
                    for op in w.openings
                ],
                "intersections": [
                    {
                        "intersecting_wall_id": ix.intersecting_wall_id,
                        "description": ix.description,
                        "tolerance_rule": ix.tolerance_rule,
                        "left_backer_label": fmt_ft_in(ix.left_channel_stud_start_in),
                        "left_edge_label": fmt_ft_in(ix.left_edge_in),
                        "right_edge_label": fmt_ft_in(ix.right_edge_in),
                        "right_backer_end_label": fmt_ft_in(ix.right_channel_stud_end_in),
                        "thickness_label": fmt_in(ix.wall_thickness_in),
                        "top_plate_lap_gap_label": f'Leave {fmt_in(ix.wall_thickness_in)} gap in 2nd Top Plate ({fmt_ft_in(ix.left_edge_in)} to {fmt_ft_in(ix.right_edge_in)})',
                    }
                    for ix in w.intersections
                ],
                "blocking": [
                    {
                        "kind": b.kind,
                        "label": b.label,
                        "lumber": b.lumber,
                        "height_aff_label": b.height_aff_label,
                        "location_note": b.location_note,
                    }
                    for b in w.blocking
                ],
                "cabinet_checks": [
                    {
                        "title": c.title,
                        "finished_label": fmt_in(c.finished_drywall_to_drywall_in),
                        "drywall_allowance_label": fmt_in(c.drywall_layers_total_in),
                        "required_rough_label": fmt_in(c.required_rough_stud_to_stud_in),
                        "max_tolerance_label": fmt_in(c.max_tolerance_in),
                        "room_type": c.room_type,
                        "detail_note": c.detail_note,
                    }
                    for c in w.cabinet_checks
                ],
            }
            for w in walls
        ],
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return payload


def main():
    out_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "project_data.json")
    data = export_project_json(out_json)
    print(f"=== {data['project_name']} ===")
    print("NOTICE:", data["prototype_notice"])
    print("STAIR CHECK:", data["stair_default"])
    print("WALLS EXPORTED:", len(data["walls"]))


if __name__ == "__main__":
    main()
