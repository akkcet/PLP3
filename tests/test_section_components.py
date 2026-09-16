"""
Unit Tests for Pipeline Pilot Section Components:
  1. Add Excel Section ({3136A684-DFA5-448D-A426-731FB1723119})
  2. Add File Attachment Section ({26E8ED5E-1528-4272-B425-EAE5BD96C635})
  3. Add Image Section ({F4D376EB-B83C-449E-840C-E2EC31218298})
  4. Add PDF Section ({94F2211E-FD84-4A26-BB7F-58560EDFA824})
"""
import unittest
from pathlib import Path
from biovia_pipeline.add_excel_section import add_excel_section
from biovia_pipeline.add_file_attachment_section import add_file_attachment_section
from biovia_pipeline.add_image_section import add_image_section
from biovia_pipeline.add_pdf_section import add_pdf_section
from biovia_pipeline.add_powerpoint_section import add_powerpoint_section
from biovia_pipeline.add_word_section import add_word_section
from biovia_pipeline.extract_sections import extract_sections, build_section_filter
from biovia_pipeline.section_models import SectionType, SectionAction
from biovia_pipeline.biovia_notebook import BioviaNotebookClient


class TestAddExcelSectionIsolated(unittest.TestCase):
    """Tests the Add Excel Section component in isolation."""

    def test_add_excel_section_basic(self):
        rec = add_excel_section(
            section_title="ICP-MS Calibration",
            excel_file="calibration_curve.xlsx",
            preview_mode="Generate from Excel File Content",
            columns_to_preview=4,
            rows_to_preview=5,
        )
        self.assertIn("simplesections", rec)
        self.assertEqual(len(rec["simplesections"]), 1)
        node = rec["simplesections"][0]
        self.assertEqual(node["sectionTitle"], "ICP-MS Calibration")
        self.assertEqual(node["sectionType"], SectionType.EXCEL.value)
        self.assertEqual(node["metadata"]["previewCols"], 4)
        self.assertEqual(node["metadata"]["previewRows"], 5)
        self.assertEqual(node["files"], ["calibration_curve.xlsx"])
        self.assertIn("last_added_section", rec)

    def test_columns_to_preview_constraint(self):
        """PLP validscript requires columns to preview < 8."""
        with self.assertRaises(ValueError):
            add_excel_section(
                section_title="Too Many Cols",
                excel_file="data.xlsx",
                columns_to_preview=8,
            )

    def test_missing_required_parameters(self):
        with self.assertRaises(ValueError):
            add_excel_section(section_title="", excel_file="data.xlsx")
        with self.assertRaises(ValueError):
            add_excel_section(section_title="Title", excel_file="")

    def test_add_excel_section_with_client(self):
        client = BioviaNotebookClient(mock_mode=True)
        rec = add_excel_section(
            section_title="Prod Run",
            excel_file="prod_data.xlsx",
            client=client,
            experiment_id="EXP-2026-XRF-01",
        )
        self.assertIn("remote_section_id", rec["last_added_section"])
        self.assertTrue(rec["last_added_section"]["remote_section_id"].startswith("sec_excel_"))


class TestAddFileAttachmentSectionIsolated(unittest.TestCase):
    """Tests the Add File Attachment Section component in isolation."""

    def test_add_single_attachment(self):
        rec = add_file_attachment_section(
            section_title="Raw Sensor Log",
            files_to_attach="spectrometer_log.bin",
            action="Replace",
        )
        self.assertEqual(len(rec["simplesections"]), 1)
        node = rec["simplesections"][0]
        self.assertEqual(node["sectionTitle"], "Raw Sensor Log")
        self.assertEqual(node["sectionType"], SectionType.FILE_ATTACHMENT.value)
        self.assertEqual(node["files"], ["spectrometer_log.bin"])
        self.assertEqual(node["metadata"]["action"], "Replace")

    def test_add_multiple_attachments(self):
        files = ["run1.dat", "run2.dat", "metadata.json"]
        rec = add_file_attachment_section(
            section_title="Batch Datasets",
            files_to_attach=files,
            action="Append",
        )
        node = rec["simplesections"][0]
        self.assertEqual(node["files"], files)
        self.assertEqual(node["metadata"]["fileCount"], 3)
        self.assertEqual(node["metadata"]["action"], "Append")

    def test_replace_existing_section(self):
        # First add
        rec = add_file_attachment_section(
            section_title="Calibration Data",
            files_to_attach="calib_v1.bin",
            action="Replace",
        )
        # Second add with same title and action=Replace should replace
        rec2 = add_file_attachment_section(
            section_title="Calibration Data",
            files_to_attach="calib_v2.bin",
            action="Replace",
            experiment_record=rec,
        )
        self.assertEqual(len(rec2["simplesections"]), 1)
        self.assertEqual(rec2["simplesections"][0]["files"], ["calib_v2.bin"])

    def test_missing_files_raises(self):
        with self.assertRaises(ValueError):
            add_file_attachment_section(section_title="Test", files_to_attach=[])


class TestAddImageSectionIsolated(unittest.TestCase):
    """Tests the Add Image Section component in isolation."""

    def test_add_image_section_basic(self):
        rec = add_image_section(
            section_title="Crystal Morphology",
            image_file="microscope_sample_40x.png",
            action="Replace",
        )
        self.assertEqual(len(rec["simplesections"]), 1)
        node = rec["simplesections"][0]
        self.assertEqual(node["sectionTitle"], "Crystal Morphology")
        self.assertEqual(node["sectionType"], SectionType.IMAGE.value)
        self.assertEqual(node["files"], ["microscope_sample_40x.png"])
        self.assertEqual(node["metadata"]["fileExtension"], ".png")

    def test_add_image_with_client(self):
        client = BioviaNotebookClient(mock_mode=True)
        rec = add_image_section(
            section_title="SEM Snapshot",
            image_file="sem_scan.tif",
            client=client,
            experiment_id="EXP-101",
        )
        self.assertIn("remote_section_id", rec["last_added_section"])
        self.assertTrue(rec["last_added_section"]["remote_section_id"].startswith("sec_image_"))

    def test_missing_title_raises(self):
        with self.assertRaises(ValueError):
            add_image_section(section_title="", image_file="plot.png")


class TestAddPdfSectionIsolated(unittest.TestCase):
    """Tests the Add PDF Section component in isolation."""

    def test_add_pdf_section_basic(self):
        rec = add_pdf_section(
            section_title="Final Analytical Report",
            pdf_file="report_q3_2026.pdf",
            preview_page_list="1-3",
        )
        self.assertEqual(len(rec["simplesections"]), 1)
        node = rec["simplesections"][0]
        self.assertEqual(node["sectionTitle"], "Final Analytical Report")
        self.assertEqual(node["sectionType"], SectionType.PDF.value)
        self.assertEqual(node["metadata"]["previewPageList"], "1-3")
        self.assertEqual(node["metadata"]["fileName"], "report_q3_2026.pdf")

    def test_add_pdf_with_client(self):
        client = BioviaNotebookClient(mock_mode=True)
        rec = add_pdf_section(
            section_title="SOP Compliance",
            pdf_file="sop_001.pdf",
            client=client,
            experiment_id="EXP-102",
        )
        self.assertIn("remote_section_id", rec["last_added_section"])
        self.assertTrue(rec["last_added_section"]["remote_section_id"].startswith("sec_pdf_"))

    def test_missing_file_raises(self):
        with self.assertRaises(ValueError):
            add_pdf_section(section_title="Missing", pdf_file="")


class TestAddPowerPointSectionIsolated(unittest.TestCase):
    """Tests the Add PowerPoint Presentation Section component in isolation."""

    def test_add_powerpoint_section_basic(self):
        rec = add_powerpoint_section(
            section_title="Synthesis Pitch",
            powerpoint_file="synthesis_overview.pptx",
        )
        self.assertEqual(len(rec["simplesections"]), 1)
        node = rec["simplesections"][0]
        self.assertEqual(node["sectionTitle"], "Synthesis Pitch")
        self.assertEqual(node["sectionType"], SectionType.POWERPOINT.value)
        self.assertEqual(node["files"], ["synthesis_overview.pptx"])
        self.assertEqual(node["metadata"]["previewText"], "Preview will be generated when the file is edited.")
        self.assertEqual(node["metadata"]["previewImageWidth"], 600)
        self.assertEqual(node["metadata"]["previewImageHeight"], 30)

    def test_missing_title_raises(self):
        with self.assertRaises(ValueError):
            add_powerpoint_section(section_title="", powerpoint_file="deck.pptx")

    def test_missing_file_raises(self):
        with self.assertRaises(ValueError):
            add_powerpoint_section(section_title="Deck", powerpoint_file="")

    def test_add_powerpoint_with_client(self):
        client = BioviaNotebookClient(mock_mode=True)
        rec = add_powerpoint_section(
            section_title="Review Deck",
            powerpoint_file="review.pptx",
            client=client,
            experiment_id="EXP-PPT-01",
        )
        self.assertIn("remote_section_id", rec["last_added_section"])
        self.assertTrue(rec["last_added_section"]["remote_section_id"].startswith("sec_powerpoint_"))


class TestAddWordSectionIsolated(unittest.TestCase):
    """Tests the Add Word Section component in isolation."""

    def test_add_word_section_basic(self):
        rec = add_word_section(
            section_title="Protocol Documentation",
            word_file="assay_protocol_v2.docx",
        )
        self.assertEqual(len(rec["simplesections"]), 1)
        node = rec["simplesections"][0]
        self.assertEqual(node["sectionTitle"], "Protocol Documentation")
        self.assertEqual(node["sectionType"], SectionType.WORD.value)
        self.assertEqual(node["files"], ["assay_protocol_v2.docx"])
        self.assertEqual(node["metadata"]["previewText"], "Preview will be generated when the file is edited.")
        self.assertEqual(node["metadata"]["previewImageWidth"], 600)
        self.assertEqual(node["metadata"]["previewImageHeight"], 30)

    def test_missing_title_raises(self):
        with self.assertRaises(ValueError):
            add_word_section(section_title="", word_file="doc.docx")

    def test_missing_file_raises(self):
        with self.assertRaises(ValueError):
            add_word_section(section_title="Doc", word_file="")

    def test_add_word_with_client(self):
        client = BioviaNotebookClient(mock_mode=True)
        rec = add_word_section(
            section_title="SOP Details",
            word_file="sop_procedure.docx",
            client=client,
            experiment_id="EXP-WORD-01",
        )
        self.assertIn("remote_section_id", rec["last_added_section"])
        self.assertTrue(rec["last_added_section"]["remote_section_id"].startswith("sec_word_"))


class TestExtractSectionsIsolated(unittest.TestCase):
    """Tests the Extract Sections from Experiment component in isolation."""

    def setUp(self):
        self.sample_experiment = {
            "experimentnumber": "EXP-2026-XRF-01",
            "connectionname": "Connection1",
            "ref": "exp-ref-1",
            "simplesections": [
                {
                    "id": "sec_003",
                    "sectionTitle": "Summary Report",
                    "sectionType": "PDF Document",
                    "indexindocument": 3,
                },
                {
                    "id": "sec_001",
                    "sectionTitle": "Calibration",
                    "sectionType": "Excel Worksheet",
                    "indexindocument": 1,
                },
                {
                    "id": "sec_002",
                    "sectionTitle": "Microscopy Photo",
                    "sectionType": "Image",
                    "indexindocument": 2,
                },
                {
                    "id": "sec_001",  # duplicate ID
                    "sectionTitle": "Duplicate Calibration",
                    "sectionType": "Excel Worksheet",
                    "indexindocument": 4,
                },
            ],
        }

    def test_extract_all_sections_sorted_and_deduped(self):
        sections = extract_sections(
            experiment_record=self.sample_experiment,
            what_to_extract="All Section Types",
        )
        # Duplicate sec_001 should be deduplicated (LocalID 35 First Occurrence Filter)
        self.assertEqual(len(sections), 3)
        # Verify sorting by indexindocument ascending (LocalID 56 Sort Data)
        self.assertEqual([s["id"] for s in sections], ["sec_001", "sec_002", "sec_003"])
        self.assertEqual(sections[0]["Experiment"]["id"], "EXP-2026-XRF-01")

    def test_extract_selected_sections(self):
        sections = extract_sections(
            experiment_record=self.sample_experiment,
            what_to_extract="Selected Section Types",
            section_types=["PDF Document", "Excel Worksheet"],
        )
        self.assertEqual(len(sections), 2)
        titles = [s["sectionTitle"] for s in sections]
        self.assertIn("Calibration", titles)
        self.assertIn("Summary Report", titles)
        self.assertNotIn("Microscopy Photo", titles)

    def test_gatekeeper_zero_selected_returns_empty(self):
        """Replicates PLP LocalID 44: 'not (@What To Extract eq Selected Section Types and numvalues(@Section Type) == 0)'"""
        sections = extract_sections(
            experiment_record=self.sample_experiment,
            what_to_extract="Selected Section Types",
            section_types=[],
        )
        self.assertEqual(sections, [])

    def test_missing_experiment_id_raises(self):
        with self.assertRaises(ValueError):
            extract_sections(experiment_record={"title": "No experiment ID"})

    def test_build_section_filter_all_types(self):
        f = build_section_filter("All Section Types")
        self.assertEqual(f, "")

    def test_build_section_filter_selected_types(self):
        f = build_section_filter("Selected Section Types", ["Excel Worksheet", "PDF Document"])
        # Excel is 10, PDF is 29
        self.assertIn("sectiontypeid eq 10", f)
        self.assertIn("sectiontypeid eq 29", f)
        self.assertTrue(f.startswith("&$filter="))

    def test_build_section_filter_custom_sections(self):
        f = build_section_filter("Selected Section Types", ["Custom Sections", "Excel Worksheet"])
        self.assertIn("sectiontypeid ne", f)
        self.assertIn(" and ", f)


if __name__ == "__main__":
    unittest.main()
