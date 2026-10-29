```python
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
import logging

# Initialize logging for Pipeline Pilot.
# This ensures messages appear in the Pipeline Pilot job log.
logger = logging.getLogger(__name__)


# COMPONENT_METADATA describes the component to Pipeline Pilot.
# It defines parameters, input/output ports, and component type.
COMPONENT_METADATA = {
    "name": "XML File Parser for ELN Import",
    "description": "Parses an XML document to extract file paths and ELN section metadata, "
                   "generating a record for each file to be imported into an ELN.",
    "component_type": "Filter", # Filter takes input, processes, and produces output
    "inputs": {
        "input_records": {
            "description": "Optional input records. If provided, the XML content or path "
                           "can be read from properties on these records.",
            "data_type": "record",
            "is_multiple": True,
        }
    },
    "outputs": {
        "output_records": {
            "description": "Records, each representing a file to be imported into ELN, "
                           "with its path and ELN section name.",
            "data_type": "record",
            "is_multiple": True,
        }
    },
    "parameters": {
        "xml_file_path": {
            "type": "string",
            "description": "Absolute path to the XML file to parse. "
                           "If 'XML Content Property' is set, this parameter "
                           "will be ignored for records where that property exists.",
            "default": "",
            "is_required": False,
        },
        "xml_file_path_property": {
            "type": "string",
            "description": "Name of the input record property containing the path "
                           "to the XML file. If empty, 'XML Content Property' or "
                           "'XML File Path' parameter is used.",
            "default": "",
            "is_required": False,
        },
        "xml_content_property": {
            "type": "string",
            "description": "Name of the input record property containing the XML content itself. "
                           "If specified and present on an input record, this takes precedence.",
            "default": "",
            "is_required": False,
        },
        "file_element_xpath": {
            "type": "string",
            "description": "XPath expression to select the XML elements representing individual files. "
                           "E.g., './Experiment/File' or './/File'.",
            "default": ".//File",
            "is_required": True,
        },
        "path_attribute_name": {
            "type": "string",
            "description": "Name of the attribute within the file element that holds the file's path. "
                           "E.g., 'path' for <File path='/a/b.pdf' />.",
            "default": "path",
            "is_required": True,
        },
        "section_attribute_name": {
            "type": "string",
            "description": "Name of the attribute within the file element that holds the ELN section name. "
                           "E.g., 'section' for <File section='PDF Attachment' />.",
            "default": "section",
            "is_required": True,
        },
        "experiment_id_attribute_xpath": {
            "type": "string",
            "description": "XPath expression relative to the 'file_element_xpath' to extract the "
                           "Experiment ID. E.g., '../@id' if the ID is on the parent <Experiment id='...'/>. "
                           "Leave empty if no experiment ID is needed or available.",
            "default": "",
            "is_required": False,
        },
        "output_file_path_property": {
            "type": "string",
            "description": "Name of the output record property for the file's absolute path.",
            "default": "FilePath",
            "is_required": True,
        },
        "output_file_name_property": {
            "type": "string",
            "description": "Name of the output record property for the file's name (without path).",
            "default": "FileName",
            "is_required": True,
        },
        "output_section_name_property": {
            "type": "string",
            "description": "Name of the output record property for the ELN section name.",
            "default": "ELNSectionName",
            "is_required": True,
        },
        "output_experiment_id_property": {
            "type": "string",
            "description": "Name of the output record property for the Experiment ID. "
                           "Only used if 'Experiment ID Attribute XPath' is specified.",
            "default": "ELNExperimentID",
            "is_required": False,
        },
        "fail_on_missing_file": {
            "type": "boolean",
            "description": "If true, the component will fail if a file specified in the XML does not exist. "
                           "If false, a warning is logged and the file is skipped.",
            "default": False,
            "is_required": False,
        },
    }
}


class PyServerComponent:
    def __init__(self, ppc_instance):
        self.ppc = ppc_instance

    def run(self):
        """
        Main execution method for the Pipeline Pilot component.
        """
        params = self.ppc.get_parameters()

        xml_file_path_param = params.get("xml_file_path", "")
        xml_file_path_prop_name = params.get("xml_file_path_property", "")
        xml_content_prop_name = params.get("xml_content_property", "")
        file_element_xpath = params["file_element_xpath"]
        path_attr_name = params["path_attribute_name"]
        section_attr_name = params["section_attribute_name"]
        exp_id_attr_xpath = params.get("experiment_id_attribute_xpath", "")
        out_file_path_prop = params["output_file_path_property"]
        out_file_name_prop = params["output_file_name_property"]
        out_section_name_prop = params["output_section_name_property"]
        out_exp_id_prop = params.get("output_experiment_id_property", "")
        fail_on_missing_file = params["fail_on_missing_file"]

        # Determine XML source strategy
        # 1. Input records with XML content property
        # 2. Input records with XML file path property
        # 3. Component parameter XML file path
        
        input_records_processed = 0

        if self.ppc.input.has_incoming_connections():
            for record in self.ppc.input.records():
                input_records_processed += 1
                xml_source_found = False

                xml_content = None
                if xml_content_prop_name and record.has_property(xml_content_prop_name):
                    xml_content = record.get_property(xml_content_prop_name)
                    if xml_content:
                        logger.info(f"Parsing XML content from property '{xml_content_prop_name}' on input record.")
                        self._parse_and_emit(
                            xml_content=xml_content,
                            file_element_xpath=file_element_xpath,
                            path_attr_name=path_attr_name,
                            section_attr_name=section_attr_name,
                            exp_id_attr_xpath=exp_id_attr_xpath,
                            out_file_path_prop=out_file_path_prop,
                            out_file_name_prop=out_file_name_prop,
                            out_section_name_prop=out_section_name_prop,
                            out_exp_id_prop=out_exp_id_prop,
                            fail_on_missing_file=fail_on_missing_file
                        )
                        xml_source_found = True

                if not xml_source_found and xml_file_path_prop_name and record.has_property(xml_file_path_prop_name):
                    xml_path = record.get_property(xml_file_path_prop_name)
                    if xml_path:
                        logger.info(f"Parsing XML file from path '{xml_path}' specified by property '{xml_file_path_prop_name}' on input record.")
                        self._parse_and_emit(
                            xml_file_path=xml_path,
                            file_element_xpath=file_element_xpath,
                            path_attr_name=path_attr_name,
                            section_attr_name=section_attr_name,
                            exp_id_attr_xpath=exp_id_attr_xpath,
                            out_file_path_prop=out_file_path_prop,
                            out_file_name_prop=out_file_name_prop,
                            out_section_name_prop=out_section_name_prop,
                            out_exp_id_prop=out_exp_id_prop,
                            fail_on_missing_file=fail_on_missing_file
                        )
                        xml_source_found = True

                if not xml_source_found:
                    logger.warning(
                        "Input record received, but no XML content or path found via specified properties. "
                        "If XML is expected per record, check property names."
                    )
        
        # If no input records or no XML found on them, try the component parameter
        if input_records_processed == 0 and xml_file_path_param:
            logger.info(f"Parsing XML file from component parameter path: '{xml_file_path_param}'")
            self._parse_and_emit(
                xml_file_path=xml_file_path_param,
                file_element_xpath=file_element_xpath,
                path_attr_name=path_attr_name,
                section_attr_name=section_attr_name,
                exp_id_attr_xpath=exp_id_attr_xpath,
                out_file_path_prop=out_file_path_prop,
                out_file_name_prop=out_file_name_prop,
                out_section_name_prop=out_section_name_prop,
                out_exp_id_prop=out_exp_id_prop,
                fail_on_missing_file=fail_on_missing_file
            )
        elif input_records_processed == 0 and not xml_file_path_param:
            logger.warning("No XML input (neither file path parameter, nor content/path from input records) provided. No files will be processed.")


    def _parse_and_emit(
        self,
        xml_file_path=None,
        xml_content=None,
        file_element_xpath=None,
        path_attr_name=None,
        section_attr_name=None,
        exp_id_attr_xpath=None,
        out_file_path_prop=None,
        out_file_name_prop=None,
        out_section_name_prop=None,
        out_exp_id_prop=None,
        fail_on_missing_file=False
    ):
        """
        Helper method to parse XML and emit records.
        """
        try:
            if xml_file_path:
                if not os.path.exists(xml_file_path):
                    raise FileNotFoundError(f"XML file not found: {xml_file_path}")
                tree = ET.parse(xml_file_path)
                root = tree.getroot()
                logger.debug(f"Successfully loaded XML from file: {xml_file_path}")
            elif xml_content:
                root = ET.fromstring(xml_content)
                logger.debug("Successfully loaded XML from content string.")
            else:
                logger.error("No XML file path or content provided for parsing.")
                return

            files_found = 0
            for file_elem in root.findall(file_element_xpath):
                file_path = file_elem.get(path_attr_name)
                section_name = file_elem.get(section_attr_name)
                experiment_id = None
                if exp_id_attr_xpath:
                    # Use find() with XPath for attribute (e.g., parent/@id)
                    parent_id_node = file_elem.find(exp_id_attr_xpath)
                    if parent_id_node is not None:
                        # For attribute values, find returns the element, need to get the attribute
                        # This part assumes exp_id_attr_xpath targets an attribute (e.g., '../@id')
                        # ElementTree.find() typically returns an Element. For attribute values,
                        # we need to be careful with XPath syntax and how ElementTree handles it.
                        # For simple attributes like '../@id', ElementTree.find() might not directly
                        # return the attribute value. We might need to get the parent first.
                        # A more robust way for parent attributes:
                        if exp_id_attr_xpath.startswith("../@"):
                            parent_elem = file_elem.find('..')
                            if parent_elem:
                                attr_name = exp_id_attr_xpath.split('/@')[1]
                                experiment_id = parent_elem.get(attr_name)
                        else:
                            # For attributes on the current element or a child
                            # ElementTree.find() with '@attr' syntax is not directly supported
                            # The typical way is to find the element and then get its attribute.
                            # For simplicity, if exp_id_attr_xpath points to an attribute directly,
                            # we'll assume it's like 'Experiment/@id' which should be resolved from root.
                            # Or if it's on the current node 'file_elem', it would be 'file_elem.get(ID_ATTRIBUTE)'.
                            # Let's adjust this for common patterns. If '../@id', handled above.
                            # If it's a child element's text or attribute, e.g., 'IdElement', 'IdElement/@value'
                            id_elem = file_elem.find(exp_id_attr_xpath)
                            if id_elem is not None:
                                # Check if it's an attribute reference or text
                                if '/' in exp_id_attr_xpath and '@' in exp_id_attr_xpath.split('/')[-1]:
                                    attr_part = exp_id_attr_xpath.split('/')[-1]
                                    attr_name = attr_part[1:] # remove '@'
                                    experiment_id = id_elem.get(attr_name)
                                else:
                                    experiment_id = id_elem.text # Assuming it's the text of an element

                if not file_path:
                    logger.warning(f"Skipping file element due to missing '{path_attr_name}' attribute: {ET.tostring(file_elem, encoding='unicode').strip()}")
                    continue
                if not section_name:
                    logger.warning(f"Skipping file '{file_path}' due to missing '{section_attr_name}' attribute.")
                    continue

                if not os.path.exists(file_path):
                    msg = f"Referenced file not found: '{file_path}'"
                    if fail_on_missing_file:
                        raise FileNotFoundError(msg)
                    else:
                        logger.warning(f"{msg}. Skipping this file.")
                        continue

                # Create output record
                output_record = self.ppc.make_record()
                output_record.set_property(out_file_path_prop, file_path)
                output_record.set_property(out_file_name_prop, os.path.basename(file_path))
                output_record.set_property(out_section_name_prop, section_name)
                
                if out_exp_id_prop and experiment_id:
                    output_record.set_property(out_exp_id_prop, experiment_id)

                self.ppc.output.write(output_record)
                files_found += 1
            
            if files_found == 0:
                logger.warning(
                    f"No files found in the XML document matching XPath '{file_element_xpath}'. "
                    f"Ensure the XPath and attribute names ('{path_attr_name}', '{section_attr_name}') are correct."
                )

        except FileNotFoundError as e:
            self.ppc.log(f"ERROR: {e}", severity="error")
            raise  # Re-raise to fail the component
        except ParseError as e:
            self.ppc.log(f"ERROR: XML parsing failed: {e}", severity="error")
            raise  # Re-raise to fail the component
        except Exception as e:
            self.ppc.log(f"ERROR: An unexpected error occurred during XML processing: {e}", severity="error")
            raise


# Example of how you might test this locally without Pipeline Pilot,
# or for understanding the expected XML structure.
# This part will not be executed when run within Pipeline Pilot.
if __name__ == "__main__":
    class MockPPCInput:
        def __init__(self, records_data=None):
            self._records_data = records_data if records_data is not None else []
            self._iterator = iter(self._records_data)

        def has_incoming_connections(self):
            return bool(self._records_data)

        def records(self):
            return self._iterator
        
        def __iter__(self):
            return self._iterator

    class MockPPCRecord:
        def __init__(self, properties=None):
            self._properties = properties if properties is not None else {}

        def get_property(self, name):
            return self._properties.get(name)
        
        def set_property(self, name, value):
            self._properties[name] = value

        def has_property(self, name):
            return name in self._properties

        def __str__(self):
            return f"Record({self._properties})"
        
        def __repr__(self):
            return str(self)

    class MockPPCOutput:
        def __init__(self):
            self.emitted_records = []

        def write(self, record):
            self.emitted_records.append(record)
            logger.info(f"Emitted record: {record}")

    class MockPPC:
        def __init__(self, parameters=None, input_records_data=None):
            self._parameters = parameters if parameters is not None else {}
            self.input = MockPPCInput(input_records_data)
            self.output = MockPPCOutput()

        def get_parameters(self):
            return self._parameters

        def make_record(self):
            return MockPPCRecord()

        def log(self, message, severity="info"):
            if severity == "error":
                logger.error(message)
            elif severity == "warning":
                logger.warning(message)
            else:
                logger.info(message)

    # --- Test Case 1: XML from component parameter file path ---
    logger.info("\n--- Running Test Case 1: XML from component parameter file path ---")
    
    # Create a dummy XML file for testing
    test_xml_content = """
    <ELNImport>
        <Experiment id="EXP-001">
            <File path="/tmp/data/report.pdf" section="PDF Attachment"/>
            <File path="/tmp/data/results.xlsx" section="Excel Data"/>
            <File path="/tmp/data/image.jpg" section="Image File"/>
        </Experiment>
        <Experiment id="EXP-002">
            <File path="/tmp/data/summary.docx" section="Word Document"/>
            <File path="/tmp/data/missing_file.txt" section="Text Log"/>
        </Experiment>
        <UnrelatedElement/>
    </ELNImport>
    """
    temp_xml_file = "/tmp/test_eln_import.xml"
    # Ensure dummy files exist for the test to pass (or set fail_on_missing_file=False)
    for f in ["/tmp/data", "/tmp/data/report.pdf", "/tmp/data/results.xlsx", "/tmp/data/image.jpg", "/tmp/data/summary.docx"]:
        if not os.path.exists(f):
            if os.path.isdir(f):
                os.makedirs(f, exist_ok=True)
            else:
                with open(f, "w") as tf:
                    tf.write(f"This is a dummy file: {os.path.basename(f)}\n")

    with open(temp_xml_file, "w") as f:
        f.write(test_xml_content)

    mock_params_1 = {
        "xml_file_path": temp_xml_file,
        "file_element_xpath": ".//File",
        "path_attribute_name": "path",
        "section_attribute_name": "section",
        "experiment_id_attribute_xpath": "../@id", # Example for parent attribute
        "output_file_path_property": "FilePath",
        "output_file_name_property": "FileName",
        "output_section_name_property": "ELNSection",
        "output_experiment_id_property": "ExperimentID",
        "fail_on_missing_file": False,
    }
    mock_ppc_1 = MockPPC(parameters=mock_params_1)
    component_1 = PyServerComponent(mock_ppc_1)
    component_1.run()
    
    expected_files_1 = [
        {"FilePath": "/tmp/data/report.pdf", "FileName": "report.pdf", "ELNSection": "PDF Attachment", "ExperimentID": "EXP-001"},
        {"FilePath": "/tmp/data/results.xlsx", "FileName": "results.xlsx", "ELNSection": "Excel Data", "ExperimentID": "EXP-001"},
        {"FilePath": "/tmp/data/image.jpg", "FileName": "image.jpg", "ELNSection": "Image File", "ExperimentID": "EXP-001"},
        {"FilePath": "/tmp/data/summary.docx", "FileName": "summary.docx", "ELNSection": "Word Document", "ExperimentID": "EXP-002"},
    ]
    # Note: 'missing_file.txt' should be skipped due to fail_on_missing_file=False

    assert len(mock_ppc_1.output.emitted_records) == len(expected_files_1), f"Expected {len(expected_files_1)} records, got {len(mock_ppc_1.output.emitted_records)}"
    for i, rec in enumerate(mock_ppc_1.output.emitted_records):
        for prop, val in expected_files_1[i].items():
            assert rec.get_property(prop) == val, f"Record {i} property '{prop}' mismatch. Expected '{val}', got '{rec.get_property(prop)}'"
    logger.info("Test Case 1 Passed!")

    # --- Test Case 2: XML content from input record property ---
    logger.info("\n--- Running Test Case 2: XML content from input record property ---")
    mock_xml_content_2 = """
    <Attachments>
        <Item ID="DOC-001" path="/tmp/data/doc1.pdf" type="Report PDF"/>
        <Item ID="DOC-002" path="/tmp/data/chart.png" type="Chart Image"/>
    </Attachments>
    """
    with open("/tmp/data/doc1.pdf", "w") as tf: tf.write("dummy doc1")
    with open("/tmp/data/chart.png", "w") as tf: tf.write("dummy chart")

    mock_params_2 = {
        "xml_content_property": "MyXML",
        "file_element_xpath": ".//Item",
        "path_attribute_name": "path",
        "section_attribute_name": "type",
        "experiment_id_attribute_xpath": "./@ID", # Example for current element attribute
        "output_file_path_property": "FilePath",
        "output_file_name_property": "FileName",
        "output_section_name_property": "DocType",
        "output_experiment_id_property": "DocumentID",
        "fail_on_missing_file": True, # Test fail condition
    }
    input_record_2 = MockPPCRecord(properties={"MyXML": mock_xml_content_2, "OtherData": "Value"})
    mock_ppc_2 = MockPPC(parameters=mock_params_2, input_records_data=[input_record_2])
    component_2 = PyServerComponent(mock_ppc_2)
    component_2.run()

    expected_files_2 = [
        {"FilePath": "/tmp/data/doc1.pdf", "FileName": "doc1.pdf", "DocType": "Report PDF", "DocumentID": "DOC-001"},
        {"FilePath": "/tmp/data/chart.png", "FileName": "chart.png", "DocType": "Chart Image", "DocumentID": "DOC-002"},
    ]
    assert len(mock_ppc_2.output.emitted_records) == len(expected_files_2)
    for i, rec in enumerate(mock_ppc_2.output.emitted_records):
        for prop, val in expected_files_2[i].items():
            assert rec.get_property(prop) == val
    logger.info("Test Case 2 Passed!")

    # --- Test Case 3: Fail on missing file ---
    logger.info("\n--- Running Test Case 3: Fail on missing file ---")
    mock_xml_content_3 = """
    <Root><File path="/tmp/data/truly_missing.txt" section="Bad File"/></Root>
    """
    mock_params_3 = {
        "xml_content_property": "Content",
        "file_element_xpath": ".//File",
        "path_attribute_name": "path",
        "section_attribute_name": "section",
        "output_file_path_property": "Path",
        "output_section_name_property": "Type",
        "fail_on_missing_file": True,
    }
    input_record_3 = MockPPCRecord(properties={"Content": mock_xml_content_3})
    mock_ppc_3 = MockPPC(parameters=mock_params_3, input_records_data=[input_record_3])
    component_3 = PyServerComponent(mock_ppc_3)
    
    try:
        component_3.run()
        assert False, "Expected FileNotFoundError but component did not fail."
    except FileNotFoundError:
        logger.info("Test Case 3 Passed! (Component failed as expected for missing file)")
    except Exception as e:
        assert False, f"Test Case 3 Failed! Expected FileNotFoundError, got {type(e).__name__}: {e}"

    # Clean up dummy files
    os.remove(temp_xml_file)
    os.remove("/tmp/data/report.pdf")
    os.remove("/tmp/data/results.xlsx")
    os.remove("/tmp/data/image.jpg")
    os.remove("/tmp/data/summary.docx")
    os.remove("/tmp/data/doc1.pdf")
    os.remove("/tmp/data/chart.png")
    os.rmdir("/tmp/data")
```