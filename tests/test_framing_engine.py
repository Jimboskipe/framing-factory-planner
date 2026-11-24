"""Unit tests for Framing Factory Planner v2 engine.

Run:  python -m unittest discover -s tests -v
"""
from fractions import Fraction
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import framing_engine as fe  # noqa: E402


class FramingEngineTests(unittest.TestCase):
    def test_x_and_go_left_end_pull_steps_by_16_inches(self):
        w = fe.WallPlan(
            wall_id="W-T",
            name="Test Wall",
            lumber_size="2x6",
            color_code="GREEN_9FT",
            length_in=Fraction(96),
            first_stud_pull_in=Fraction(33, 4),
        )
        self.assertEqual(w.x_and_go_callout, '8-1/4" & GO')
        marks = w.oc_stud_marks_in()
        for i in range(1, len(marks)):
            self.assertEqual(marks[i] - marks[i - 1], Fraction(16))

    def test_patio_door_pd1_82_opening_math(self):
        op = fe.Opening(
            label="PD1-82",
            room_and_type="Patio Door #1",
            kind="DOOR",
            left_ro_start_in=Fraction(76),
            ro_width_in=Fraction(82),
            ro_height_in=Fraction(165, 2),
            head_height_in=Fraction(165, 2),
            header_stock="2-ply 2x12",
            header_depth_in=Fraction(45, 4),
            shoulders_per_side=2,
            order_packet_verified=True,
            plan_old_code="TZ172",
        )
        self.assertEqual(op.header_length_in, Fraction(88))
        self.assertEqual(op.left_shoulder_start_in, Fraction(73))
        self.assertEqual(op.left_king_start_in, Fraction(143, 2))
        self.assertEqual(op.shoulder_length_in, Fraction(81))

    def test_cabinet_drywall_to_rough_stud_math(self):
        chk = fe.CabinetDrywallCheck(
            title="Kitchen Cabinet Plan",
            finished_drywall_to_drywall_in=Fraction(217, 2),  # 108-1/2"
            drywall_layers_total_in=Fraction(1),               # +1" (two 1/2" sheets)
        )
        self.assertEqual(chk.required_rough_stud_to_stud_in, Fraction(219, 2))  # 109-1/2"
        self.assertEqual(chk.max_tolerance_in, Fraction(1, 8))

    def test_foundation_one_inch_square_tolerance_rule(self):
        ok = fe.evaluate_foundation_square(0.75)
        self.assertTrue(ok["within_one_inch_tolerance"])
        adjust = fe.evaluate_foundation_square(1.5)
        self.assertFalse(adjust["within_one_inch_tolerance"])

    def test_stair_stringer_plan_vs_field_double_check(self):
        st = fe.calculate_stair_stringer(
            plan_stud_height_in=104.625,
            floor_assembly_depth_in=12.625,
            field_measured_total_rise_in=121.25,
            tread_thickness_in=1.5,
        )
        self.assertEqual(st["plan_total_rise_in"], 121.75)
        self.assertEqual(st["field_total_rise_in"], 121.25)
        self.assertEqual(st["field_riser_count"], 16)
        self.assertTrue(st["code_compliant"])

    def test_wall_intersection_channel_math(self):
        ix = fe.WallIntersection("W-7", "Powder Room Partition", Fraction(84), Fraction(7, 2))
        self.assertEqual(ix.right_edge_in, Fraction(175, 2))
        self.assertEqual(ix.left_channel_stud_start_in, Fraction(165, 2))
        self.assertEqual(ix.right_channel_stud_end_in, Fraction(89))

    def test_export_project_json_writes_valid_payload(self):
        tmp = os.path.join(tempfile.mkdtemp(), "project_data.json")
        payload = fe.export_project_json(tmp)
        self.assertTrue(os.path.exists(tmp))
        self.assertEqual(len(payload["walls"]), 8)
        self.assertEqual(len(payload["bidding_tiers"]), 3)


if __name__ == "__main__":
    unittest.main()
