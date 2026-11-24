"""Framing Factory Planner — Doyle's Contracting Pre-Staging & Left-End Plate Layout Engine.

Implements James M. Doyle's ground-up pre-staging system used across 100+ residential &
commercial framing projects (2015-2021):
  1. Left-end plate layout ("X and Go" architectural-scale grid offset + 16" O.C. step-off).
  2. Window & door order packet verification gate + human-readable labels (PD1-82, PDW1-28, MS1-60).
  3. Left-end tape locations for every intersecting partition wall channel and door/window R.O.
  4. Grouped header & pre-made supporting shoulder cut batches + factory pre-cut stud tallies.
  5. Color-coded wall height / zone legend + "Goofy Area / Field Heads-Up" alerts.

Run CLI report:   python framing_engine.py
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
        "wall_height_label": "8' 1-1/8\" Standard Wall",
        "precut_stud_in": Fraction(92 * 8 + 5, 8),   # 92-5/8"
        "plate_height_in": Fraction(97 * 8 + 1, 8),  # 97-1/8" (bottom + stud + double top)
        "meaning": "8' Wall — Factory 92-5/8\" Pre-Cut Studs",
    },
    "GREEN_9FT": {
        "color": "Green",
        "hex": "#16a34a",
        "wall_height_label": "9' 1-1/8\" Tall Main Wall",
        "precut_stud_in": Fraction(104 * 8 + 5, 8),  # 104-5/8"
        "plate_height_in": Fraction(109 * 8 + 1, 8),
        "meaning": "9' Wall — Factory 104-5/8\" Pre-Cut Studs",
    },
    "ORANGE_10FT": {
        "color": "Orange",
        "hex": "#ea580c",
        "wall_height_label": "10' 1-1/8\" High / Garage Wall",
        "precut_stud_in": Fraction(116 * 8 + 5, 8),  # 116-5/8"
        "plate_height_in": Fraction(121 * 8 + 1, 8),
        "meaning": "10' Wall — Factory 116-5/8\" Pre-Cut Studs",
    },
    "PURPLE_RAKE": {
        "color": "Purple",
        "hex": "#7c3aed",
        "wall_height_label": "Vault / Rake / Custom Slope",
        "precut_stud_in": Fraction(104 * 8 + 5, 8),
        "plate_height_in": Fraction(109 * 8 + 1, 8),
        "meaning": "Rake / Vaulted Wall — Custom Tapered Studs (See Field Note)",
    },
    "RED_GOOFY": {
        "color": "Red Alert",
        "hex": "#dc2626",
        "wall_height_label": "Goofy Area / Field Heads-Up",
        "precut_stud_in": Fraction(104 * 8 + 5, 8),
        "plate_height_in": Fraction(109 * 8 + 1, 8),
        "meaning": "GOOFY AREA — Extra Field Framing Knowledge / Check With Lead Before Cutting",
    },
}


def fmt_in(val: Fraction) -> str:
    """Format inches (Fraction or float) as carpenter tape string, e.g. '8-1/4\"' or '14' 6-1/2\"'."""
    f = Fraction(val).limit_denominator(16)
    whole = int(f)
    rem = f - whole
    if rem == 0:
        return f'{whole}"'
    if whole == 0:
        return f'{rem.numerator}/{rem.denominator}"'
    return f'{whole}-{rem.numerator}/{rem.denominator}"'


def fmt_ft_in(val: Fraction) -> str:
    """Format total inches as feet & inches plus raw inches, e.g. 6' 4\" (76\")."""
    f = Fraction(val).limit_denominator(16)
    ft = int(f // 12)
    rem_in = f - ft * 12
    return f"{ft}' {fmt_in(rem_in)} ({fmt_in(f)})"


@dataclass
class Opening:
    label: str                  # Human-readable Doyle code: PD1-82, PDW1-28, MS1-60
    room_and_type: str          # "Patio Door #1 (Great Room)"
    kind: str                   # "DOOR" or "WINDOW"
    left_ro_start_in: Fraction  # Distance from LEFT end of plate to left edge of Rough Opening
    ro_width_in: Fraction       # Verified R.O. width from window/door order packet
    ro_height_in: Fraction      # Verified R.O. height from window/door order packet
    head_height_in: Fraction    # Top of R.O. from subfloor (e.g. 82-1/2" standard head line)
    header_stock: str           # e.g. "2-ply 2x12 w/ 1/2\" OSB" or "2-ply 1-3/4\"x11-7/8\" LVL"
    header_depth_in: Fraction   # e.g. 11-1/4" for 2x12, 9-1/4" for 2x10
    shoulders_per_side: int     # 1 each side (<60" RO) or 2 each side (>=60" RO)
    order_packet_verified: bool = True
    plan_old_code: str = ""     # What the architect plan called it (e.g. "TZ172")

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
        # Supporting shoulder sits on bottom plate (1-1/2") and supports underside of header
        return self.head_height_in - PLATE_THICK

    @property
    def sill_length_in(self) -> Fraction:
        return self.ro_width_in if self.kind == "WINDOW" else Fraction(0)

    @property
    def sill_height_from_deck_in(self) -> Fraction:
        return self.head_height_in - self.ro_height_in if self.kind == "WINDOW" else Fraction(0)


@dataclass
class WallIntersection:
    intersecting_wall_id: str   # e.g. "W-7"
    description: str            # e.g. "Master Closet Partition (2x4)"
    left_edge_in: Fraction      # Distance from LEFT end of plate to left edge of intersecting wall
    wall_thickness_in: Fraction = Fraction(7, 2)  # 3-1/2" for 2x4, 5-1/2" for 2x6

    @property
    def right_edge_in(self) -> Fraction:
        return self.left_edge_in + self.wall_thickness_in

    @property
    def left_channel_stud_start_in(self) -> Fraction:
        """Left 1-1/2" channel backer stud nailed in while building the wall on the deck."""
        return self.left_edge_in - STUD_THICK

    @property
    def right_channel_stud_end_in(self) -> Fraction:
        """Right outer face of the right 1-1/2" channel backer stud."""
        return self.right_edge_in + STUD_THICK


@dataclass
class WallPlan:
    wall_id: str                # e.g. "W-1"
    name: str                   # e.g. "Great Room Rear Exterior (2x6)"
    lumber_size: str            # "2x6" or "2x4"
    color_code: str             # Key in WALL_COLOR_LEGEND
    length_in: Fraction         # Full plate length in inches
    first_stud_pull_in: Fraction  # "X and Go" from LEFT end (e.g. 8-1/4", 10-1/4", 15-1/4")
    spacing_oc_in: Fraction = Fraction(16)
    openings: List[Opening] = field(default_factory=list)
    intersections: List[WallIntersection] = field(default_factory=list)
    goofy_alert: str = ""       # Field Heads-Up note for tricky framing areas
    crew_note: str = ""

    @property
    def x_and_go_callout(self) -> str:
        return f'{fmt_in(self.first_stud_pull_in)} & GO'

    def oc_stud_marks_in(self) -> List[Fraction]:
        """Return every 16\" O.C. stud layout mark pulled from the LEFT end of the plate."""
        marks: List[Fraction] = []
        pos = self.first_stud_pull_in
        while pos < self.length_in - STUD_THICK:
            marks.append(pos)
            pos += self.spacing_oc_in
        return marks

    def precut_stud_count(self) -> int:
        """Estimate full pre-cut studs needed (end studs + O.C. studs + kings + channel backers)."""
        oc_count = len(self.oc_stud_marks_in())
        king_count = 2 * len(self.openings)
        channel_studs = 2 * len(self.intersections)
        return 2 + oc_count + king_count + channel_studs


def group_headers_and_shoulders(walls: List[WallPlan]) -> Dict[str, List[dict]]:
    """Group headers and pre-made supporting shoulders across the house for batch cutting."""
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
            length_in=Fraction(36 * 12),  # 36' 0"
            first_stud_pull_in=Fraction(33, 4),  # 8-1/4" & GO
            openings=[
                Opening(
                    label="LLPD1-82",
                    room_and_type="Lower-Level Walkout Patio Door #1 (Rec Room)",
                    kind="DOOR",
                    left_ro_start_in=Fraction(72),         # 6' 0" from left end
                    ro_width_in=Fraction(82),              # 82" verified order width
                    ro_height_in=Fraction(165, 2),         # 82-1/2" verified order height
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
                    left_ro_start_in=Fraction(192),        # 16' 0" from left end
                    ro_width_in=Fraction(72),              # 72" R.O.
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
                    left_ro_start_in=Fraction(312),        # 26' 0" from left end
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
                WallIntersection("W-9", "Bedroom #3 / Rec Room Demising Wall (2x4)", Fraction(282), Fraction(7, 2)),
            ],
            goofy_alert="FULL WALKOUT EXPOSURE WALL: Treated 2x6 bottom plate on concrete curb + step-foundation frost wall transition at left end. Anchor bolts every 48\" max and within 12\" of plate breaks. Verify floor-truss bearing ribbon elevation with laser before sheeting!",
            crew_note="Pull from LEFT (Southwest foundation step): 8-1/4\" & GO. Stacks directly under Main Floor W-2.",
        ),
        WallPlan(
            wall_id="W-2",
            name="Great Room 10' Tall Rear Exposure Wall (Above Walkout)",
            lumber_size="2x6",
            color_code="ORANGE_10FT",
            length_in=Fraction(28 * 12),  # 28' 0"
            first_stud_pull_in=Fraction(33, 4),  # 8-1/4" & GO (stacks over W-1!)
            openings=[
                Opening(
                    label="PD1-82",
                    room_and_type="Main Deck Patio Door #1 — Great Room",
                    kind="DOOR",
                    left_ro_start_in=Fraction(76),         # 6' 4" from left end
                    ro_width_in=Fraction(82),              # 82" verified order width
                    ro_height_in=Fraction(165, 2),         # 82-1/2" verified order height
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 2x12 w/ 1/2" OSB',
                    header_depth_in=Fraction(45, 4),
                    shoulders_per_side=2,
                    order_packet_verified=True,
                    plan_old_code="TZ172",
                ),
                Opening(
                    label="GRW1-60",
                    room_and_type="Great Room Picture Window #1 (w/ 18\" Transom Above)",
                    kind="WINDOW",
                    left_ro_start_in=Fraction(204),        # 17' 0" from left end
                    ro_width_in=Fraction(60),              # 60" R.O.
                    ro_height_in=Fraction(62),              # 62" R.O.
                    head_height_in=Fraction(165, 2),
                    header_stock='2-ply 2x12 w/ 1/2" OSB',
                    header_depth_in=Fraction(45, 4),
                    shoulders_per_side=2,
                    order_packet_verified=True,
                    plan_old_code="W-204B",
                ),
            ],
            intersections=[
                WallIntersection("W-6", "Kitchen / Great Room Bearing Partition (2x6)", Fraction(174), Fraction(11, 2)),
            ],
            goofy_alert="10'1-1/8\" TALL WALL (116-5/8\" Studs) + GREAT ROOM TRAY CEILING LEDGER: Snap chalk line at 9' 0\" AFF around inside face of W-2 and W-6 for 12\" dropped perimeter tray ceiling soffit Ladder Framing. Point load from ridge girder truss at 14' 6\" from left end.",
            crew_note="Pull from LEFT: 8-1/4\" & GO so studs stack vertically over Lower-Level Walkout W-1.",
        ),
        WallPlan(
            wall_id="W-3",
            name="Bedroom #1 (Master Suite) Rear Exterior + Tray Ceiling",
            lumber_size="2x6",
            color_code="GREEN_9FT",
            length_in=Fraction(20 * 12),  # 20' 0"
            first_stud_pull_in=Fraction(41, 4),  # 10-1/4" & GO
            openings=[
                Opening(
                    label="MS1-60",
                    room_and_type="Master Bedroom Twin Window #1",
                    kind="WINDOW",
                    left_ro_start_in=Fraction(66),         # 5' 6" from left end
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
                    left_ro_start_in=Fraction(168),        # 14' 0" from left end
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
                WallIntersection("W-7", "Master Bath Wet Wall (2x6 Plumbing)", Fraction(146), Fraction(11, 2)),
            ],
            goofy_alert="MASTER BEDROOM STEPPED TRAY CEILING: Raised scissor-heel truss pocket sits between 0' 0\" and 12' 2\". Pre-build 2x4 ladder soffit boxes (16\" deep x 10\" drop) on deck before lifting onto perimeter ledger.",
            crew_note="Pull from LEFT: 10-1/4\" & GO. Notice MS1-60 uses the exact same header & double-shoulder package as GRW1-60.",
        ),
        WallPlan(
            wall_id="W-4",
            name="Bedroom #2 & Powder Room West Exterior Wall",
            lumber_size="2x6",
            color_code="GREEN_9FT",
            length_in=Fraction(24 * 12),  # 24' 0"
            first_stud_pull_in=Fraction(61, 4),  # 15-1/4" & GO
            openings=[
                Opening(
                    label="BR2W1-48",
                    room_and_type="Bedroom #2 Casement Window #1",
                    kind="WINDOW",
                    left_ro_start_in=Fraction(54),         # 4' 6" from left end
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
                    left_ro_start_in=Fraction(198),        # 16' 6" from left end
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
                WallIntersection("W-8", "Bedroom #2 Closet / Hall Partition (2x4)", Fraction(144), Fraction(7, 2)),
                WallIntersection("W-10", "Powder Room South Partition (2x4)", Fraction(180), Fraction(7, 2)),
            ],
            crew_note="Pull from LEFT: 15-1/4\" & GO. Notice BR2W1-48 shares the exact same 54\" 2x12 header batch as BR3W1-48 on W-1.",
        ),
        WallPlan(
            wall_id="W-5",
            name="Front Entry Foyer & Covered Porch Bearing Wall (North)",
            lumber_size="2x6",
            color_code="ORANGE_10FT",
            length_in=Fraction(22 * 12),  # 22' 0"
            first_stud_pull_in=Fraction(11, 4),  # 2-3/4" & GO
            openings=[
                Opening(
                    label="FD1-66",
                    room_and_type="Front Entry Door #1 w/ Dual Sidelites (66\" x 82-1/2\" R.O.)",
                    kind="DOOR",
                    left_ro_start_in=Fraction(99),         # 8' 3" from left end
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
                WallIntersection("W-11", "Foyer Coat Closet East Wall (2x4)", Fraction(48), Fraction(7, 2)),
                WallIntersection("W-12", "Walkout Stairwell Bearing Wall (2x6)", Fraction(192), Fraction(11, 2)),
            ],
            goofy_alert="10' FOYER ENTRY + WALKOUT STAIRWELL OPENING: Stairwell header pocket frames into W-12 at 16' 0\" from left end. Keep subfloor sheathing unglued inside stairwell hatch zone for clean cutout after walls are braced.",
            crew_note="Pull from LEFT: 2-3/4\" & GO.",
        ),
        WallPlan(
            wall_id="W-6",
            name="3-Car Garage 10' Front Portal Wall",
            lumber_size="2x6",
            color_code="RED_GOOFY",
            length_in=Fraction(24 * 12),  # 24' 0"
            first_stud_pull_in=Fraction(11, 2),  # 5-1/2" & GO
            openings=[
                Opening(
                    label="GD1-194",
                    room_and_type="16'x7' Overhead Garage Door #1 (194\" x 85-1/2\" R.O.)",
                    kind="DOOR",
                    left_ro_start_in=Fraction(47),         # 3' 11" from left end
                    ro_width_in=Fraction(194),             # 16' 2" R.O.
                    ro_height_in=Fraction(171, 2),         # 85-1/2" R.O.
                    head_height_in=Fraction(171, 2),
                    header_stock='2-ply 1-3/4"x11-7/8" LVL + Bottom Flat 2x6',
                    header_depth_in=Fraction(95, 8),
                    shoulders_per_side=2,
                    order_packet_verified=True,
                    plan_old_code="OHD-16",
                ),
            ],
            intersections=[],
            goofy_alert="GOOFY AREA — 10'1-1/8\" Garage Wall (116-5/8\" studs) + Narrow Portal Return: Hold-down anchor bolts embedded in concrete at both king posts; confirm Simpson hold-down bracket alignment before standing wall!",
            crew_note="Pull from LEFT: 5-1/2\" & GO. Stage LVL header with SkyTrak before standing.",
        ),
        WallPlan(
            wall_id="W-7",
            name="Master Hall / Bedroom #2 Interior Door Corridor (2x4)",
            lumber_size="2x4",
            color_code="BLUE_8FT",
            length_in=Fraction(18 * 12),  # 18' 0"
            first_stud_pull_in=Fraction(61, 4),  # 15-1/4" & GO
            openings=[
                Opening(
                    label="MD1-34",
                    room_and_type="Master Bedroom Entry Door #1 (2/8 Prehung — 34\" x 82-1/2\" R.O.)",
                    kind="DOOR",
                    left_ro_start_in=Fraction(24),         # 2' 0" from left end
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
                    left_ro_start_in=Fraction(108),        # 9' 0" from left end
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
                    left_ro_start_in=Fraction(162),        # 13' 6" from left end
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
                WallIntersection("W-8", "Bedroom #2 / Master Closet Divider (2x4)", Fraction(84), Fraction(7, 2)),
            ],
            crew_note="Interior 2x4 Hall Wall. Pull from LEFT: 15-1/4\" & GO. All 3 interior door shoulders are identical 81\" 2x4 single shoulders.",
        ),
        WallPlan(
            wall_id="W-8",
            name="Great Room Vault-to-Tray Transition & Fireplace Feature Wall",
            lumber_size="2x6",
            color_code="PURPLE_RAKE",
            length_in=Fraction(16 * 12),  # 16' 0"
            first_stud_pull_in=Fraction(33, 4),  # 8-1/4" & GO
            openings=[
                Opening(
                    label="FP1-50",
                    room_and_type="Direct-Vent Gas Fireplace Chase Rough Opening #1",
                    kind="WINDOW",
                    left_ro_start_in=Fraction(71),         # 5' 11" from left end
                    ro_width_in=Fraction(50),
                    ro_height_in=Fraction(44),
                    head_height_in=Fraction(44),           # Floor-level fireplace box opening
                    header_stock='2-ply 2x10 w/ 1/2" OSB',
                    header_depth_in=Fraction(37, 4),
                    shoulders_per_side=1,
                    order_packet_verified=True,
                    plan_old_code="FP-42DV",
                ),
            ],
            intersections=[],
            goofy_alert="TRAY CEILING & COFFERED SOFFIT RETURN + TV BACKING: Install 2x12 solid blocking between studs from 54\" to 78\" AFF above FP1-50 for mantle & TV mount. Top of wall steps down 12\" at both ends to catch tray ceiling perimeter soffit.",
            crew_note="Pull from LEFT: 8-1/4\" & GO. Verify fireplace manufacturer clearance-to-combustibles sheet before framing header.",
        ),
    ]


def export_project_json(out_path: str) -> dict:
    walls = sample_custom_ranch_project()
    batches = group_headers_and_shoulders(walls)
    payload = {
        "project_name": "Doyle's Contracting — 2,150 Sq Ft Custom Ranch (Pre-Staged Jobsite Package)",
        "daily_goal": "Day 1 Goal: Snap deck lines, pre-assemble all grouped headers & supporting shoulders at cut bench, frame & stand Exterior Walls W-1 through W-4.",
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
                        "left_backer_label": fmt_ft_in(ix.left_channel_stud_start_in),
                        "left_edge_label": fmt_ft_in(ix.left_edge_in),
                        "right_edge_label": fmt_ft_in(ix.right_edge_in),
                        "right_backer_end_label": fmt_ft_in(ix.right_channel_stud_end_in),
                        "thickness_label": fmt_in(ix.wall_thickness_in),
                        "top_plate_lap_gap_label": f'Leave {fmt_in(ix.wall_thickness_in)} gap in 2nd Top Plate ({fmt_ft_in(ix.left_edge_in)} to {fmt_ft_in(ix.right_edge_in)})',
                    }
                    for ix in w.intersections
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
    print("DAILY GOAL:", data["daily_goal"])
    print("\nGROUPED HEADER PRE-CUT BATCHES:")
    for h in data["batches"]["headers"]:
        print(f"  [{h['count']}x] {h['stock']} @ {h['length_label']}  ->  {', '.join(h['labels'])}")
    print("\nGROUPED PRE-MADE SUPPORTING SHOULDER BATCHES:")
    for s in data["batches"]["shoulders"]:
        print(f"  [{s['total_assemblies']} assemblies / {s['total_pieces']} pcs] {s['lumber']} @ {s['length_label']} ({s['plies_per_side']}-ply)  ->  {', '.join(s['labels'])}")
    print("\nWALL LEFT-END PULL SHEETS:")
    for w in data["walls"]:
        print(f"\n  {w['wall_id']} — {w['name']} [{w['color_info']['color']}: {w['color_info']['wall_height_label']}]")
        print(f"    Plate Length: {w['length_label']}  |  Left-End Stud Pull: {w['x_and_go_callout']}  |  Pre-Cut Studs: {w['precut_stud_count']} pcs @ {w['color_info']['precut_stud_label']}")
        for op in w["openings"]:
            print(f"    OPENING {op['label']} (replaces plan '{op['plan_old_code']}'): R.O. {op['ro_size_label']} [VERIFIED={op['order_packet_verified']}]")
            print(f"      Left-End Tape: King {op['left_king_label']} | Shoulders {op['left_shoulder_label']} | R.O. {op['left_ro_start_label']} to {op['right_ro_end_label']}")
            print(f"      Header: {op['header_stock']} @ {op['header_length_label']} | Pre-Made Shoulders: {op['shoulders_per_side']}x each side @ {op['shoulder_length_label']}")
        for ix in w["intersections"]:
            print(f"    WALL CHANNEL {ix['intersecting_wall_id']} ({ix['description']}): Left-End Tape {ix['left_edge_label']} to {ix['right_edge_label']}")
        if w["goofy_alert"]:
            print(f"    *** FIELD HEADS-UP: {w['goofy_alert']} ***")


if __name__ == "__main__":
    main()
