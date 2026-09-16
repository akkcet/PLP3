"""
Unit Tests for Protocol Migration & Component Discovery Engine
Validates Blue (Data Manipulators) vs Green (UI Generators) classification,
missing component flagging, visual alias matching, and web app UI schema generation.
"""

import unittest
from biovia_pipeline.protocol_migration_engine import (
    analyze_protocol_xml,
    match_component,
    ComponentStatus,
    PlpComponentRole,
)

SAMPLE_FULL_PROTOCOL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<sci:protocol xmlns:sci="http://www.scitegic.com/protocol" name="XRF Analytical Report Ingestion Web App" version="2.4" author="Biovia Specialist">
    <sci:arg name="DefaultNotebookURL">https://notebook.corp.internal/eln/api/v1</sci:arg>
    <sci:arg name="BatchRunMode">Online</sci:arg>

    <!-- Green Component 1: Web Page Builder / Header -->
    <sci:component localid="1" name="ELN Transfer Web Portal" type="WebPageBuilder">
        <sci:arg name="PageTitle">Biovia Notebook Analytical Uploader</sci:arg>
    </sci:component>

    <!-- Green Component 2: Web Form Input for Experiment Number -->
    <sci:component localid="2" name="Experiment ID Input Box" type="WebFormInput">
        <sci:arg name="Label">Target Experiment Number</sci:arg>
        <sci:arg name="ExperimentNumber">EXP-2026-XRF-01</sci:arg>
    </sci:component>

    <!-- Green Component 3: Drag & Drop File Upload -->
    <sci:component localid="3" name="Document File Dropzone" type="WebFileUpload">
        <sci:arg name="Label">Select Files to Attach</sci:arg>
        <sci:arg name="FileLocation">sample_attachment.xlsx</sci:arg>
    </sci:component>

    <!-- Blue Component 1: Notebook Connection (Translated to Python) -->
    <sci:component localid="4" name="Step 1: Check Session Token" type="{9B1E4A32-12C5-4F8A-9871-332D76EF12A0}">
        <sci:arg name="BaseURL">https://notebook.corp.internal/eln/api/v1</sci:arg>
        <sci:arg name="ApiKey">secret_key_123</sci:arg>
    </sci:component>

    <!-- Blue Component 2: Query Experiment (Translated to Python) -->
    <sci:component localid="5" name="Fetch Experiment Details" type="Query Experiment">
        <sci:arg name="ExperimentNumber">EXP-2026-XRF-01</sci:arg>
    </sci:component>

    <!-- Blue Component 3: Custom Filter / Gatekeeper (Translated to Python) -->
    <sci:component localid="6" name="Gatekeeper 1: PDF Only" type="{470B2F2A-5A0D-47C0-8FD6-36BDD2C318F8}">
        <sci:arg name="Expression">Find(FileLocation, ".pdf") gt 0</sci:arg>
    </sci:component>

    <!-- Blue Component 4: Custom Manipulator (Translated to Python) -->
    <sci:component localid="7" name="Format Canvas Preview" type="{3E20B9B6-BC8B-4C03-A2C3-5D7E847C8B56}">
        <sci:arg name="Expression">status := "Ready"; previewWidth := 800;</sci:arg>
    </sci:component>

    <!-- Blue Component 5: Add PDF Section (Translated to Python) -->
    <sci:component localid="8" name="Embed PDF Report" type="Add PDF Section">
        <sci:arg name="SectionTitle">Final Analytical PDF</sci:arg>
        <sci:arg name="FileLocation">report.pdf</sci:arg>
    </sci:component>

    <!-- Green Component 4: Web Data Table (Results Display) -->
    <sci:component localid="9" name="Processing Results Table" type="WebTable">
        <sci:arg name="ShowColumns">SectionID, SectionTitle, Status</sci:arg>
    </sci:component>

    <!-- Missing Blue Component: Unimplemented database syncer -->
    <sci:component localid="10" name="Legacy Oracle DB Sync" type="LegacyOracleConnector">
        <sci:arg name="ConnectionString">jdbc:oracle:thin:@db01:1521:xe</sci:arg>
    </sci:component>

    <!-- Connections -->
    <sci:connectid from="1" to="2" />
    <sci:connectid from="2" to="3" />
    <sci:connectid from="3" to="4" />
    <sci:connectid from="4" to="5" />
    <sci:connectid from="5" to="6" />
    <sci:connectid from="6" to="7" />
    <sci:connectid from="7" to="8" />
    <sci:connectid from="8" to="9" />
    <sci:connectid from="9" to="10" />
</sci:protocol>
"""

class TestProtocolMigrationEngine(unittest.TestCase):

    def test_component_matching_blue_data_manipulator(self):
        status, role, key, core_name, widget = match_component(
            visual_name="My Custom Filter Check",
            comp_type="{470B2F2A-5A0D-47C0-8FD6-36BDD2C318F8}",
        )
        self.assertEqual(status, ComponentStatus.REUSABLE_AVAILABLE)
        self.assertEqual(role, PlpComponentRole.BLUE_DATA_MANIPULATOR)
        self.assertEqual(key, "custom_filter")
        self.assertEqual(core_name, "Custom Filter")

    def test_component_matching_green_ui_generator(self):
        status, role, key, core_name, widget = match_component(
            visual_name="Experiment ID Input Box",
            comp_type="WebFormInput",
        )
        self.assertEqual(status, ComponentStatus.REUSABLE_AVAILABLE)
        self.assertEqual(role, PlpComponentRole.GREEN_UI_GENERATOR)
        self.assertEqual(key, "web_form_input")
        self.assertEqual(widget, "text_input")

    def test_missing_component_flagging(self):
        status, role, key, core_name, widget = match_component(
            visual_name="Legacy Oracle DB Sync",
            comp_type="LegacyOracleConnector",
        )
        self.assertEqual(status, ComponentStatus.MISSING)
        self.assertEqual(role, PlpComponentRole.BLUE_DATA_MANIPULATOR)
        self.assertIsNone(key)
        self.assertEqual(core_name, "LegacyOracleConnector")

    def test_full_protocol_analysis_with_roles(self):
        result = analyze_protocol_xml(SAMPLE_FULL_PROTOCOL_XML)
        
        self.assertEqual(result.protocol_name, "XRF Analytical Report Ingestion Web App")
        self.assertEqual(result.total_nodes, 10)
        
        # 6 Blue data manipulators (5 matched + 1 missing)
        self.assertEqual(result.blue_count, 6)
        # 4 Green UI components (all 4 matched)
        self.assertEqual(result.green_count, 4)
        
        # 9 should match, 1 missing
        self.assertEqual(result.matched_count, 9)
        self.assertEqual(result.missing_count, 1)
        self.assertEqual(result.coverage_percentage, 90.0)
        
        # Node 10 is missing Blue data manipulator
        node10 = next(n for n in result.nodes if n.local_id == "10")
        self.assertEqual(node10.status, ComponentStatus.MISSING)
        self.assertEqual(node10.role, PlpComponentRole.BLUE_DATA_MANIPULATOR)
        self.assertIn("LegacyOracleConnector", node10.remediation_note)


if __name__ == "__main__":
    unittest.main()
