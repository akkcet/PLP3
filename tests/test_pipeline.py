"""
Comprehensive Unit & Integration Test Suite for Biovia Pipeline Pilot Python Refactoring
Can be executed with: python3 -m unittest discover tests
"""
import unittest
from pathlib import Path

from biovia_pipeline.pilotscript_parser import PilotScriptParser, PilotScriptEngine
from biovia_pipeline.custom_filter import custom_filter
from biovia_pipeline.plp_xml_parser import PlpProtocolXmlParser
from biovia_pipeline.xml_model_parser import parse_model_xml
from biovia_pipeline.file_utils import clean_section_title
from biovia_pipeline.pipeline_orchestrator import ElnDataTransferPipeline


class TestCustomFilterComponent(unittest.TestCase):
    """
    Unit tests for the unified 'custom_filter' function implementing the
    Pipeline Pilot Custom Filter component across all PLP script expressions.
    """

    def test_pdf_filter_expression(self):
        expr = "findsubstring(DocRelativepath, '.pdf')>1"
        self.assertTrue(custom_filter(expr, record={"DocRelativepath": "report.pdf"}))
        self.assertFalse(custom_filter(expr, record={"DocRelativepath": "table.xlsx"}))

    def test_excel_filter_expression(self):
        expr = "findsubstring(DocRelativepath, '.xlsx')>1"
        self.assertTrue(custom_filter(expr, record={"DocRelativepath": "data.xlsx"}))
        self.assertFalse(custom_filter(expr, record={"DocRelativepath": "slide.pptx"}))

    def test_powerpoint_filter_expression(self):
        expr = "findsubstring(DocRelativepath, '.ppt')>1"
        self.assertTrue(custom_filter(expr, record={"DocRelativepath": "deck.pptx"}))
        self.assertFalse(custom_filter(expr, record={"DocRelativepath": "notes.docx"}))

    def test_word_filter_expression(self):
        expr = "findsubstring(DocRelativepath, '.docx')>1"
        self.assertTrue(custom_filter(expr, record={"DocRelativepath": "protocol.docx"}))
        self.assertFalse(custom_filter(expr, record={"DocRelativepath": "raw.dat"}))

    def test_gatekeeper_1_custom_filter(self):
        expr = "@experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''"
        # Passing case
        self.assertTrue(custom_filter(expr, globals_dict={"experiment_number": "EXP-2026-001", "filelocation": ""}))
        # Missing experiment number
        self.assertFalse(custom_filter(expr, globals_dict={"experiment_number": "", "filelocation": ""}))
        # Filelocation already defined
        self.assertFalse(custom_filter(expr, globals_dict={"experiment_number": "EXP-2026-001", "filelocation": "users/path"}))

    def test_gatekeeper_2_custom_filter(self):
        expr = "@xml is defined and @xml ne '' and @filelist is eq ''"
        self.assertTrue(custom_filter(expr, globals_dict={"xml": "<root/>", "filelist": ""}))
        self.assertFalse(custom_filter(expr, globals_dict={"xml": "", "filelist": ""}))
        self.assertFalse(custom_filter(expr, globals_dict={"xml": "<root/>", "filelist": ["file1.pdf"]}))

    def test_gatekeeper_3_custom_filter(self):
        expr = "@filelist is defined and @filelist is ne ''"
        self.assertTrue(custom_filter(expr, globals_dict={"filelist": ["file1.pdf", "file2.xlsx"]}))
        self.assertFalse(custom_filter(expr, globals_dict={"filelist": []}))
        self.assertFalse(custom_filter(expr, globals_dict={"filelist": None}))

    def test_empty_expression_pass_through(self):
        self.assertTrue(custom_filter(""))
        self.assertTrue(custom_filter("   "))

    def test_plp_parser_custom_filter_mapping(self):
        parser = PlpProtocolXmlParser("sample_plp_protocol.xml")
        components = parser.parse()
        filter_comps = [c for c in components if c.name == "Custom Filter"]
        self.assertGreater(len(filter_comps), 0)
        for fc in filter_comps:
            self.assertEqual(fc.mapped_python_function, "custom_filter")
            self.assertEqual(fc.mapped_python_module, "biovia_pipeline.custom_filter")


class TestPilotScriptEngine(unittest.TestCase):
    def test_find_substring(self):
        # 1-indexed in PLP
        self.assertEqual(PilotScriptEngine.find_substring("sample.pdf", ".pdf"), 7)
        self.assertEqual(PilotScriptEngine.find_substring("sample.docx", ".pdf"), 0)

    def test_substring(self):
        # 1-indexed in PLP
        self.assertEqual(PilotScriptEngine.substring("Spectroscopy: Report", 15, 6), "Report")

    def test_gatekeeper_1_pass(self):
        expr = "@experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''"
        res = PilotScriptEngine.evaluate(
            expr,
            globals_ctx={"experiment_number": "EXP-2026-001", "filelocation": ""},
            record_ctx={}
        )
        self.assertTrue(res)

    def test_gatekeeper_1_fail_when_filelocation_present(self):
        expr = "@experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''"
        res = PilotScriptEngine.evaluate(
            expr,
            globals_ctx={"experiment_number": "EXP-2026-001", "filelocation": "users/path"},
            record_ctx={}
        )
        self.assertFalse(res)

    def test_extension_filter_pdf(self):
        expr = "findsubstring(DocRelativepath, '.pdf')>1"
        self.assertTrue(PilotScriptEngine.evaluate(expr, {}, {"DocRelativepath": "report.pdf"}))
        self.assertFalse(PilotScriptEngine.evaluate(expr, {}, {"DocRelativepath": "table.xlsx"}))


class TestPlpProtocolXmlParser(unittest.TestCase):
    def test_parse_sample_protocol(self):
        xml_path = Path("sample_plp_protocol.xml")
        self.assertTrue(xml_path.exists())
        parser = PlpProtocolXmlParser(xml_path)
        components = parser.parse()
        self.assertGreater(len(components), 10)

        names = [c.name for c in components]
        self.assertIn("Delete File", names)
        self.assertIn("Custom Filter", names)
        self.assertIn("Python (on Server)", names)
        self.assertIn("Subprotocol", names)
        self.assertIn("Notebook Connection", names)


class TestModelXmlParser(unittest.TestCase):
    def test_parse_sample_model_xml(self):
        xml_path = Path("sample_model_data.xml")
        self.assertTrue(xml_path.exists())
        meta = parse_model_xml(xml_path)
        self.assertEqual(len(meta.files), 5)
        self.assertEqual(meta.base_location, "users/arun.khuntia/experiments")
        self.assertEqual(meta.files[0].file_name, "Quant_Analysis_Summary.pdf")
        self.assertEqual(meta.files[0].extension, ".pdf")


class TestStringUtils(unittest.TestCase):
    def test_clean_section_title(self):
        raw = "Spectroscopy: Quantitative Analysis Report"
        cleaned = clean_section_title(raw)
        self.assertEqual(cleaned, "Quantitative Analysis Report")


class TestPipelineOrchestrator(unittest.TestCase):
    def test_end_to_end_simulation(self):
        pipeline = ElnDataTransferPipeline(mock_mode=True)
        result = pipeline.run(
            xml_source=Path("sample_model_data.xml"),
            experiment_number="EXP-TEST-99"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.files_processed, 5)
        self.assertEqual(len(result.sections_created), 5)
        types = [s["sectionType"] for s in result.sections_created]
        self.assertIn("pdf", types)
        self.assertIn("excel", types)
        self.assertIn("powerpoint", types)
        self.assertIn("word", types)
        self.assertIn("attachment", types)


if __name__ == "__main__":
    unittest.main()
