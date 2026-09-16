"""
Unit tests for Pipeline Pilot Subprotocol component (GUID: {17001C74-63CE-4B4B-B37C-F0EAA19CE4AA}).
"""
import unittest
from biovia_pipeline.subprotocol import (
    Subprotocol,
    SubprotocolContext,
    run_subprotocol,
    create_add_powerpoint_subprotocol,
    create_extract_sections_subprotocol,
)


class TestSubprotocolIsolated(unittest.TestCase):
    """Tests the Subprotocol composite execution container in isolation."""

    def test_declare_local_parsing(self):
        ctx = SubprotocolContext("serial, top:=5, step_name:=\"Processing\", flag:=true")
        self.assertIn("serial", ctx.locals)
        self.assertIsNone(ctx.locals["serial"])
        self.assertEqual(ctx.locals["top"], 5)
        self.assertEqual(ctx.locals["step_name"], "Processing")
        self.assertEqual(ctx.locals["flag"], True)

    def test_subprotocol_streaming_mode(self):
        """RunToCompletion = False: records pass sequentially through inner nodes."""
        subp = Subprotocol(name="StreamSubP", run_to_completion="False")

        # Node 1: Add prefix to title
        def step1(rec, ctx, params):
            rec["title"] = f"Processed: {rec.get('title', '')}"
            return rec, True

        # Node 2: Filter out records with score < 50
        def step2(rec, ctx, params):
            if rec.get("score", 0) < 50:
                return None, True  # filtered out
            return rec, True

        subp.add_node("1", "TitlePrefixer", "Custom Manipulator", step1)
        subp.add_node("2", "ScoreFilter", "Custom Filter", step2)
        subp.connect("1", "2")

        input_data = [
            {"title": "Sample A", "score": 90},
            {"title": "Sample B", "score": 30},
            {"title": "Sample C", "score": 75},
        ]
        res = subp.execute(input_data)
        self.assertEqual(res["total_input"], 3)
        self.assertEqual(res["passed_count"], 2)
        self.assertEqual(res["passed_records"][0]["title"], "Processed: Sample A")
        self.assertEqual(res["passed_records"][1]["title"], "Processed: Sample C")

    def test_subprotocol_parameter_promotion(self):
        """Verifies subprotocol promoted parameters propagate down to child nodes."""
        subp = Subprotocol(name="PromotedParamSubP")
        subp.set_parameter("CustomMultiplier", 10)

        def step_multiply(rec, ctx, params):
            mult = params.get("Multiplier", 1)
            rec["computed"] = rec.get("value", 1) * mult
            return rec, True

        subp.add_node("10", "MathNode", "Custom Manipulator", step_multiply)
        subp.promote_parameter("CustomMultiplier", "10", "Multiplier")

        res = subp.execute([{"value": 5}, {"value": 12}])
        self.assertEqual(res["passed_records"][0]["computed"], 50)
        self.assertEqual(res["passed_records"][1]["computed"], 120)

    def test_subprotocol_topology_inspection(self):
        """Verifies that subprotocol structural topology (nodes, connections, promotions) can be inspected."""
        subp = Subprotocol(name="GraphSubP", description="Test subprotocol graph")
        subp.add_node("1", "FirstNode", "Custom Filter", lambda r, c, p: (r, True))
        subp.add_node("2", "SecondNode", "Custom Manipulator", lambda r, c, p: (r, True))
        subp.connect("1", "2")
        subp.promote_parameter("ExposedParam", "2", "InnerParam", default_value="Hello")

        topo = subp.inspect_topology()
        self.assertEqual(topo["name"], "GraphSubP")
        self.assertEqual(len(topo["nodes"]), 2)
        self.assertEqual(len(topo["connections"]), 1)
        self.assertEqual(topo["connections"][0]["from"], "1")
        self.assertEqual(topo["connections"][0]["to"], "2")
        self.assertEqual(len(topo["parameter_promotions"]), 1)

    def test_prebuilt_powerpoint_subprotocol(self):
        """Verifies pre-built Add PowerPoint Presentation Section subprotocol."""
        subp = create_add_powerpoint_subprotocol(
            section_title="Deck Overview",
            powerpoint_file="presentation.pptx",
        )
        rec = {"experimentnumber": "EXP-01", "simplesections": []}
        res = subp.execute([rec])
        self.assertEqual(res["passed_count"], 1)
        out_rec = res["passed_records"][0]
        self.assertEqual(len(out_rec["simplesections"]), 1)
        self.assertEqual(out_rec["simplesections"][0]["sectionTitle"], "Deck Overview")
        self.assertEqual(out_rec["simplesections"][0]["sectionType"], "PowerPoint Presentation")

    def test_prebuilt_extract_sections_subprotocol(self):
        """Verifies pre-built Extract Sections subprotocol."""
        subp = create_extract_sections_subprotocol(
            experiment_id="EXP-2026-XRF-01",
            what_to_extract="All Section Types",
        )
        rec = {
            "id": "EXP-2026-XRF-01",
            "simplesections": [
                {"id": "s1", "sectionTitle": "Test Sec", "sectionType": "Excel Worksheet", "indexindocument": 1}
            ]
        }
        res = subp.execute([rec])
        self.assertEqual(res["passed_count"], 1)
        self.assertIn("_extracted_sections", res["passed_records"][0])
        self.assertEqual(len(res["passed_records"][0]["_extracted_sections"]), 1)

    def test_subprotocol_run_to_completion_for_each_record(self):
        """RunToCompletion = True - For Each Data Record: fresh context per record."""
        subp = Subprotocol(
            name="PerRecordSubP",
            run_to_completion="True - For Each Data Record",
            declare_local="counter:=0",
        )

        def step_count(rec, ctx, params):
            ctx.locals["counter"] += 1
            rec["iter"] = ctx.locals["counter"]
            return rec, True

        subp.add_node("1", "Counter", "Custom Manipulator", step_count)
        res = subp.execute([{"item": "X"}, {"item": "Y"}, {"item": "Z"}])
        for r in res["passed_records"]:
            self.assertEqual(r["iter"], 1)

    def test_subprotocol_categorize_using(self):
        """RunToCompletion = True - For Each Category."""
        subp = Subprotocol(
            name="CategorySubP",
            run_to_completion="True - For Each Category",
            categorize_using="section_type",
            declare_local="category_idx:=0",
        )

        def step_cat(rec, ctx, params):
            ctx.locals["category_idx"] += 1
            rec["batch_idx"] = ctx.locals["category_idx"]
            rec["cat_group"] = ctx.locals["_CurrentCategory"]
            return rec, True

        subp.add_node("1", "CatBatchStep", "Custom Manipulator", step_cat)

        records = [
            {"id": 1, "section_type": "Excel"},
            {"id": 2, "section_type": "Excel"},
            {"id": 3, "section_type": "PDF"},
            {"id": 4, "section_type": "PDF"},
            {"id": 5, "section_type": "PDF"},
        ]

        res = subp.execute(records)
        self.assertEqual(res["passed_count"], 5)
        excel_items = [r for r in res["passed_records"] if r["section_type"] == "Excel"]
        pdf_items = [r for r in res["passed_records"] if r["section_type"] == "PDF"]

        self.assertEqual([r["batch_idx"] for r in excel_items], [1, 2])
        self.assertEqual([r["batch_idx"] for r in pdf_items], [1, 2, 3])

    def test_categorize_without_property_raises(self):
        with self.assertRaises(ValueError):
            Subprotocol(
                name="BadSubP",
                run_to_completion="True - For Each Category",
                categorize_using=None,
            )

    def test_fail_port_routing(self):
        subp = Subprotocol(name="FailPortSubP")

        def step_failing(rec, ctx, params):
            if rec.get("has_error"):
                return rec, False
            return rec, True

        subp.add_node("1", "Validator", "Custom Filter", step_failing)
        res = subp.execute([
            {"id": 1, "has_error": False},
            {"id": 2, "has_error": True},
            {"id": 3, "has_error": False},
        ])
        self.assertEqual(res["passed_count"], 2)
        self.assertEqual(res["failed_count"], 1)
        self.assertEqual(res["failed_records"][0]["id"], 2)


if __name__ == "__main__":
    unittest.main()
