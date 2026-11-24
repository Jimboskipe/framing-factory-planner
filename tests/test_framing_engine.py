"""Unit tests for Framing Factory Planner engine.

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
            first_stud_pull_in=Fraction(33, 4),  # 8-1/4" & GO
        )
        self.assertEqual(w.x_and_go_callout, '8-1/4" & GO')
        marks = w.oc_stud_marks_in()
        self.assertEqual(marks[0], Fraction(33, 4))
        self.assertEqual(marks[1], Fraction(33, 4) + 16)
        self.assertEqual(marks[2], Fraction(33, 4) + 32)
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
        # Double shoulders (3" each side) -> header length = 82 + 6 = 88"
        self.assertEqual(op.header_length_in, Fraction(88))
        # Left shoulder starts 3" left of RO (76 - 3 = 73"); left king starts 1.5" left of shoulder (71.5")
        self.assertEqual(op.left_shoulder_start_in, Fraction(73))
        self.assertEqual(op.left_king_start_in, Fraction(143, 2))
        # Supporting shoulder sits on 1.5" bottom plate -> 82.5" - 1.5" = 81"
        self.assertEqual(op.shoulder_length_in, Fraction(81))

    def test_header_and_shoulder_batch_grouping(self):
        walls = fe.sample_custom_ranch_project()
        batches = fe.group_headers_and_shoulders(walls)
        # GRW1-60 (W-1) and MS1-60 (W-2) both use a 66" (5' 6") 2-ply 2x12 header -> grouped count == 2
        sixty_in_headers = [h for h in batches["headers"] if h["length_in"] == 66.0]
        self.assertEqual(len(sixty_in_headers), 1)
        self.assertEqual(sixty_in_headers[0]["count"], 2)

    def test_all_openings_verified_against_order_packet(self):
        for w in fe.sample_custom_ranch_project():
            for op in w.openings:
                self.assertTrue(op.order_packet_verified)
                self.assertNotEqual(op.label, op.plan_old_code)

    def test_wall_intersection_channel_math(self):
        ix = fe.WallIntersection("W-7", "Powder Room Partition", Fraction(84), Fraction(7, 2))
        self.assertEqual(ix.right_edge_in, Fraction(175, 2))  # 87-1/2"
        self.assertEqual(ix.left_channel_stud_start_in, Fraction(165, 2))  # 82-1/2"
        self.assertEqual(ix.right_channel_stud_end_in, Fraction(89))  # 89"

    def test_export_project_json_writes_valid_payload(self):
        tmp = os.path.join(tempfile.mkdtemp(), "project_data.json")
        payload = fe.export_project_json(tmp)
        self.assertTrue(os.path.exists(tmp))
        self.assertEqual(len(payload["walls"]), 8)


if __name__ == "__main__":
    unittest.main()
