"""
Unit Test Suite for Individual Pipeline Pilot Reusable Components
Tests each component in isolation to guarantee modular reusability:
  1. custom_filter (Custom Filter PilotScript component)
  2. custom_manipulator (Custom Manipulator PilotScript component)
  3. notebook_connection (Notebook Connection component)
  4. experiment_query (Experiment Query component)
  5. parse_model_xml (Model XML Parser component)
  6. section_dispatcher (Section Dispatcher with Custom Filter router)
"""
import os
import unittest
from biovia_pipeline.custom_filter import custom_filter
from biovia_pipeline.custom_manipulator import custom_manipulator
from biovia_pipeline.notebook_connection import notebook_connection, NotebookConnectionObject
from biovia_pipeline.experiment_query import (
    experiment_query,
    decode_experiment_signing_status,
    decode_experiment_submission_status,
    decode_section_type
)
from biovia_pipeline.xml_model_parser import parse_model_xml
from biovia_pipeline.section_dispatcher import SectionDispatcher


class TestCustomFilterIsolated(unittest.TestCase):
    """Verifies that the unified custom_filter component evaluates PLP expressions correctly."""

    def test_extension_filter_pdf(self):
        expr = "findsubstring(DocRelativepath, '.pdf')>1"
        self.assertTrue(custom_filter(expr, record={"DocRelativepath": "sample_report.pdf"}))
        self.assertFalse(custom_filter(expr, record={"DocRelativepath": "data.xlsx"}))

    def test_extension_filter_xlsx(self):
        expr = "findsubstring(DocRelativepath, '.xlsx')>1"
        self.assertTrue(custom_filter(expr, record={"DocRelativepath": "experiment_data.xlsx"}))
        self.assertFalse(custom_filter(expr, record={"DocRelativepath": "summary.pdf"}))

    def test_gatekeeper_combined_logic(self):
        expr = "@experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''"
        # Passing case
        self.assertTrue(custom_filter(expr, globals_dict={"experiment_number": "EXP-2026-001", "filelocation": ""}))
        # Failing case: missing experiment_number
        self.assertFalse(custom_filter(expr, globals_dict={"experiment_number": "", "filelocation": ""}))
        # Failing case: filelocation already populated
        self.assertFalse(custom_filter(expr, globals_dict={"experiment_number": "EXP-01", "filelocation": "/tmp/files"}))

    def test_stage_transition_filter(self):
        expr = "@xml is defined and @xml ne '' and @filelist is eq ''"
        self.assertTrue(custom_filter(expr, globals_dict={"xml": "<root/>", "filelist": ""}))
        self.assertFalse(custom_filter(expr, globals_dict={"xml": "", "filelist": ""}))


class TestCustomManipulatorIsolated(unittest.TestCase):
    """Verifies that custom_manipulator alters records, globals, and locals via PilotScript."""

    def test_record_property_assignment(self):
        # A := 10 creates a property named A on the data record (per PLP help docs)
        script = "A := 10; B := A * 2; Title := 'Assay Results';"
        rec, globs, locs = custom_manipulator(script, record={"Initial": "yes"})
        self.assertEqual(rec.get("A"), 10)
        self.assertEqual(rec.get("B"), 20)
        self.assertEqual(rec.get("Title"), "Assay Results")
        self.assertEqual(rec.get("Initial"), "yes")

    def test_variable_scoping_locals_and_globals(self):
        # #local variable vs @global variable vs %record property
        script = """
        #counter := 1;
        #counter++;
        @targetExperiment := 'EXP-999';
        CleanTitle := 'Clean_' . SectionName;
        """
        rec, globs, locs = custom_manipulator(
            script,
            record={"SectionName": "Report1"},
            globals_dict={"targetExperiment": ""},
            locals_dict={"counter": 0}
        )
        self.assertEqual(locs.get("counter"), 2)
        self.assertEqual(globs.get("targetExperiment"), "EXP-999")
        self.assertEqual(rec.get("CleanTitle"), "Clean_Report1")

    def test_string_concatenation_and_functions(self):
        script = """
        #clean := trim(SectionTitle);
        #clean := toupper(#clean);
        Formatted := #clean . '_VERIFIED';
        """
        rec, globs, locs = custom_manipulator(
            script,
            record={"SectionTitle": "   spectroscopy report  "}
        )
        self.assertEqual(rec.get("Formatted"), "SPECTROSCOPY REPORT_VERIFIED")

    def test_conditional_if_then_logic(self):
        script = """
        if Score >= 90 then
            Grade := 'A';
        elsif Score >= 75 then
            Grade := 'B';
        else
            Grade := 'C';
        end if;
        """
        rec1, _, _ = custom_manipulator(script, record={"Score": 95})
        self.assertEqual(rec1.get("Grade"), "A")

        rec2, _, _ = custom_manipulator(script, record={"Score": 80})
        self.assertEqual(rec2.get("Grade"), "B")

        rec3, _, _ = custom_manipulator(script, record={"Score": 60})
        self.assertEqual(rec3.get("Grade"), "C")

    def test_for_loop_execution(self):
        script = """
        #sum := 0;
        for #i in 1 .. 4 loop
            #sum += #i;
        end loop;
        TotalSum := #sum;
        """
        rec, _, locs = custom_manipulator(script, record={})
        self.assertEqual(locs.get("sum"), 10)
        self.assertEqual(rec.get("TotalSum"), 10)


class TestNotebookConnectionIsolated(unittest.TestCase):
    """Verifies that notebook_connection produces compliant PLP connection objects."""

    def test_connection_with_session_token(self):
        conn = notebook_connection(
            connection_name="MyNotebookConn",
            server_url="https://eln.biovia.company.com/eln",
            authentication_method="Use Notebook Session Token",
            username="analyst_1",
            session_token="sec_token_xyz123",
            header_1_name="X-Tenant-ID",
            header_1_value="PharmaCorp",
            mock_mode=True
        )
        self.assertIsInstance(conn, NotebookConnectionObject)
        self.assertEqual(conn.connection_name, "MyNotebookConn")
        self.assertEqual(conn.server_url, "https://eln.biovia.company.com/eln")
        self.assertEqual(conn.api_endpoint, "https://eln.biovia.company.com/eln/api/v1")
        self.assertEqual(conn.session_token, "sec_token_xyz123")
        self.assertEqual(conn.additional_headers.get("X-Tenant-ID"), "PharmaCorp")

        # Verify hash string serialization
        hash_str = conn.to_hash_string()
        self.assertTrue(len(hash_str) > 10)

    def test_connection_with_credentials(self):
        conn = notebook_connection(
            connection_name="TestConn",
            authentication_method="Use Username and Password Parameters",
            username="john.doe",
            password="secret_password",
            mock_mode=True
        )
        self.assertTrue(conn.session_token.startswith("tok_eln_mock_"))


class TestExperimentQueryIsolated(unittest.TestCase):
    """Verifies that experiment_query filters and retrieves experiments via a Notebook Connection."""

    def setUp(self):
        self.conn = notebook_connection(
            connection_name="TestQueryConn",
            session_token="tok_test_abc",
            mock_mode=True
        )

    def test_single_experiment_query(self):
        results = experiment_query(
            connection=self.conn,
            filter_by="Experiment Number",
            filter_type="Equals",
            filter_value="EXP-2026-XRF-01",
            return_simple_section_data=True,
            mock_data_fallback=True
        )
        self.assertTrue(len(results) >= 1)
        exp = results[0]
        self.assertEqual(exp.get("experimentNumber"), "EXP-2026-XRF-01")
        self.assertIn("signingStatus", exp)
        self.assertIn("submissionStatus", exp)
        self.assertTrue(len(exp.get("simplesections", [])) > 0)
        # Check that sections are decoded
        first_sec = exp["simplesections"][0]
        self.assertIn("sectionType", first_sec)

    def test_status_decoders(self):
        self.assertEqual(decode_experiment_signing_status(1), "Not submitted")
        self.assertEqual(decode_experiment_signing_status(3), "Signed by witness")
        self.assertEqual(decode_experiment_submission_status(3), "Fully Submitted")
        self.assertEqual(decode_section_type(1), "PDF")
        self.assertEqual(decode_section_type(2), "Excel")


class TestModelXmlParserIsolated(unittest.TestCase):
    """Verifies parse_model_xml component extracting instrument files."""

    def test_parse_sample_xml(self):
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
        <DataSet SectionName="Spectroscopy Report" BaseLocation="/data/transfers/batch01">
            <Files>
                <File Name="sample_spectrum.pdf" Extension="pdf" Title="Absorption Spectrum" />
                <File Name="calibration_table.xlsx" Extension="xlsx" Title="Calibration Matrix" />
            </Files>
        </DataSet>
        """
        meta = parse_model_xml(xml_content)
        self.assertEqual(meta.section_name, "Spectroscopy Report")
        self.assertEqual(meta.base_location, "/data/transfers/batch01")
        self.assertEqual(len(meta.files), 2)
        self.assertEqual(meta.files[0].file_name, "sample_spectrum.pdf")
        self.assertEqual(meta.files[0].extension, ".pdf")


class TestSectionDispatcherIsolated(unittest.TestCase):
    """Verifies section_dispatcher classifies files into ELN sections using PLP Custom Filter expressions."""

    def setUp(self):
        self.dispatcher = SectionDispatcher()

    def test_dispatch_pdf_file(self):
        file_record = {"file_name": "assay_summary.pdf", "section_title": "Assay Summary"}
        res = self.dispatcher.dispatch_file(file_record)
        self.assertEqual(res["section_type"], "pdf")
        self.assertEqual(res["component_id"], 48)

    def test_dispatch_excel_file(self):
        file_record = {"file_name": "raw_readouts.xlsx", "section_title": "Raw Readouts"}
        res = self.dispatcher.dispatch_file(file_record)
        self.assertEqual(res["section_type"], "excel")
        self.assertEqual(res["component_id"], 51)


if __name__ == "__main__":
    unittest.main()
