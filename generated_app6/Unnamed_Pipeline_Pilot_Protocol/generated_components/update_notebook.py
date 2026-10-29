```python
import sys
import os
import xml.etree.ElementTree as ET
import logging
import json
from typing import Dict, Any, List, Optional

# --- COMPONENT_METADATA ---
# This block defines the component's metadata for Pipeline Pilot.
# It should be placed at the very top of the script.
COMPONENT_METADATA = """
<component name="Update Notebook" category="ELN Integration" type="Manipulator"
           description="Parses uploaded XML, selects files based on XPath, and imports them into an Electronic Lab Notebook (ELN).">
    <icon name="python_script_manipulator_icon" />
    <properties>
        <property name="ELN_URL" type="string" default=""
                  description="The base URL of the Electronic Lab Notebook (ELN) system." />
        <property name="ELN_Username" type="string" default=""
                  description="Username for authenticating with the ELN system." />
        <property name="ELN_Password" type="password" default=""
                  description="Password for authenticating with the ELN system." />
        <property name="XML_Content_Property" type="string" default="XML_Content"
                  description="The name of the input record property containing the XML content to be parsed." />
        <property name="File_Path_XPath" type="string" default="//File"
                  description="XPath expression to find file elements within the XML content. The attribute 'path' will be extracted from these elements. (e.g., '//File' for &lt;File path='...'&gt;)" />
        <property name="File_Path_Attribute" type="string" default="path"
                  description="The attribute name on the elements found by 'File_Path_XPath' that contains the file path." />
        <property name="Notebook_ID_Property" type="string" default="NotebookID"
                  description="The name of the input record property containing the target Notebook ID in the ELN." />
        <property name="Section_Name_Prefix" type="string" default="Imported File - "
                  description="Prefix to use for the section names created in the ELN for imported files." />
    </properties>
    <inputs>
        <input name="in1" type="chemical/x-mdl-rdfile" primary="true"
               description="Input records containing XML content and Notebook ID." />
    </inputs>
    <outputs>
        <output name="out1" type="chemical/x-mdl-rdfile" primary="true"
                description="Output records with added status and details of imported files." />
    </outputs>
</component>
"""

# --- ELN Client Mock (Replace with actual ELN API integration) ---
class ELNClient:
    """
    A mock client for interacting with an Electronic Lab Notebook (ELN) system.
    In a production environment, this class would implement actual API calls
    to the ELN, likely using a library like 'requests'.
    """

    def __init__(self, url: str, username: str, password: str):
        """
        Initializes the ELN client.

        Args:
            url (str): The base URL of the ELN system.
            username (str): Username for authentication.
            password (str): Password for authentication.
        """
        self.url = url
        self.username = username
        self.password = password
        logging.info("ELNClient initialized for %s with user %s", url, username)
        # In a real scenario, this would involve establishing a session or
        # performing initial authentication (e.g., getting an auth token).

    def import_file_to_notebook(self, notebook_id: str, file_path: str,
                                section_name: str, file_content: bytes) -> str:
        """
        Mocks the process of importing a file into a specified ELN notebook.

        Args:
            notebook_id (str): The ID of the target notebook in the ELN.
            file_path (str): The original path of the file being imported.
            section_name (str): The name to give the new section in the ELN.
            file_content (bytes): The binary content of the file.

        Returns:
            str: A mock ELN section ID representing the imported file.

        Raises:
            Exception: In a real implementation, this would raise an exception
                       if the API call fails (e.g., network error, API error).
        """
        logging.info("Attempting to import file '%s' into notebook '%s' as section '%s' "
                     "(content length: %d bytes)",
                     file_path, notebook_id, section_name, len(file_content))

        # --- Placeholder for actual ELN API call ---
        # Example using 'requests' library (uncomment and adapt for real use):
        # import requests
        # try:
        #     # Prepare file for multipart/form-data upload
        #     files = {'file': (os.path.basename(file_path), file_content)}
        #     # Additional data to send with the file
        #     data = {
        #         'name': section_name,
        #         'notebookId': notebook_id,
        #         'type': 'attachment' # Or specific type like 'PDF', 'Word', 'Excel'
        #     }
        #     response = requests.post(
        #         f"{self.url}/api/notebooks/{notebook_id}/sections", # Example ELN API endpoint
        #         auth=(self.username, self.password), # Basic Auth, or use 'headers' for token auth
        #         files=files,
        #         data=data,
        #         timeout=60 # Timeout in seconds for the request
        #     )
        #     response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        #     # Assuming the ELN API returns a JSON response with a 'sectionId'
        #     return response.json().get('sectionId', f"ELN_SECTION_ID_UNKNOWN_FOR_{notebook_id}")
        # except requests.exceptions.RequestException as e:
        #     logging.error("ELN API call failed: %s", e)
        #     raise RuntimeError(f"ELN import failed for '{file_path}': {e}") from e
        # ---------------------------------------------

        # For this mock, just return a dummy ID
        mock_section_id = (
            f"ELN_SECTION_{notebook_id}_{os.path.basename(file_path).replace('.', '_')}"
            f"_{len(file_content)}_{os.urandom(4).hex()}" # Add random part to ensure uniqueness
        )
        logging.info("Successfully mocked import of '%s'. Mock section ID: %s",
                     file_path, mock_section_id)
        return mock_section_id


class UpdateNotebookComponent:
    """
    Pipeline Pilot component to parse XML, identify files, and import them into an ELN.
    """

    def __init__(self, properties: Dict[str, str]):
        """
        Initializes the component with properties defined in Pipeline Pilot.

        Args:
            properties (Dict[str, str]): A dictionary of component properties.
        """
        self.properties = properties
        self.eln_url: str = properties.get("ELN_URL", "")
        self.eln_username: str = properties.get("ELN_Username", "")
        self.eln_password: str = properties.get("ELN_Password", "")
        self.xml_content_property: str = properties.get("XML_Content_Property", "XML_Content")
        self.file_path_xpath: str = properties.get("File_Path_XPath", "//File")
        self.file_path_attribute: str = properties.get("File_Path_Attribute", "path")
        self.notebook_id_property: str = properties.get("Notebook_ID_Property", "NotebookID")
        self.section_name_prefix: str = properties.get("Section_Name_Prefix", "Imported File - ")

        if not all([self.eln_url, self.eln_username, self.eln_password]):
            raise ValueError(
                "ELN_URL, ELN_Username, and ELN_Password are required component properties "
                "and cannot be empty."
            )

        self.eln_client = ELNClient(self.eln_url, self.eln_username, self.eln_password)

    def process_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single input record.
        1. Extracts XML content and Notebook ID from the record.
        2. Parses XML to find file paths based on XPath and attribute name.
        3. Reads file content from disk and imports each file into the ELN.
        4. Updates the record with processing status and import details.

        Args:
            record (Dict[str, Any]): The input record from Pipeline Pilot.

        Returns:
            Dict[str, Any]: The modified record with added status properties.
        """
        xml_content: Optional[str] = record.get(self.xml_content_property)
        notebook_id: Optional[str] = record.get(self.notebook_id_property)

        # Initialize status properties for the current record
        record["UpdateNotebook_Status"] = "Processing"
        record["UpdateNotebook_Success"] = False
        record["UpdateNotebook_ImportedFiles"] = []

        if not xml_content:
            logging.warning("Record missing '%s' property. Skipping record processing.",
                            self.xml_content_property)
            record["UpdateNotebook_Status"] = "Skipped (Missing XML content)"
            return record

        if not notebook_id:
            logging.warning("Record missing '%s' property. Cannot import without a target ELN notebook ID.",
                            self.notebook_id_property)
            record["UpdateNotebook_Status"] = "Skipped (Missing Notebook ID)"
            return record

        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logging.error("Failed to parse XML content for record: %s", e)
            record["UpdateNotebook_Status"] = f"Failed (XML Parse Error: {e})"
            return record

        file_paths: List[str] = []
        found_elements = root.findall(self.file_path_xpath)
        if not found_elements:
            logging.warning("No elements found in XML using XPath '%s'.", self.file_path_xpath)
        else:
            for element in found_elements:
                path = element.get(self.file_path_attribute)
                if path:
                    file_paths.append(path)
                else:
                    logging.warning(
                        "Element found by XPath '%s' does not have attribute '%s'. Element tag: %s, Attributes: %s",
                        self.file_path_xpath, self.file_path_attribute, element.tag, element.attrib
                    )

        if not file_paths:
            logging.warning(
                "No file paths found in XML using XPath '%s' and attribute '%s'. "
                "Please check XML structure and component properties.",
                self.file_path_xpath, self.file_path_attribute
            )
            record["UpdateNotebook_Status"] = "Skipped (No files found in XML)"
            return record

        imported_files_info: List[Dict[str, Any]] = []
        all_succeeded = True

        for file_path in file_paths:
            if not file_path:
                logging.warning("Found empty file path in XML. Skipping.")
                continue

            file_import_status: Dict[str, Any] = {"file": file_path, "status": "Pending"}
            try:
                # Ensure the path is absolute or resolve it relative to a known base directory.
                # In Pipeline Pilot, file paths on the server are usually absolute or relative
                # to the protocol's execution directory.
                # For this component, we assume the path is directly accessible by the server.

                if not os.path.exists(file_path):
                    error_msg = f"File not found on server at path: {file_path}"
                    logging.error(error_msg)
                    file_import_status["status"] = f"Failed ({error_msg})"
                    all_succeeded = False
                    imported_files_info.append(file_import_status)
                    continue

                with open(file_path, 'rb') as f:
                    file_content = f.read()

                section_name = f"{self.section_name_prefix}{os.path.basename(file_path)}"
                eln_section_id = self.eln_client.import_file_to_notebook(
                    notebook_id, file_path, section_name, file_content
                )
                file_import_status["status"] = "Success"
                file_import_status["eln_section_id"] = eln_section_id
                logging.info("Successfully processed file '%s' for ELN import.", file_path)

            except IOError as e:
                logging.error("Error reading file '%s': %s", file_path, e)
                file_import_status["status"] = f"Failed (File I/O Error: {e})"
                all_succeeded = False
            except Exception as e:  # Catch any other exceptions during ELN interaction
                logging.error("Error importing file '%s' to ELN: %s", file_path, e, exc_info=True)
                file_import_status["status"] = f"Failed (ELN Import Error: {e})"
                all_succeeded = False
            finally:
                imported_files_info.append(file_import_status)

        record["UpdateNotebook_Status"] = "Success" if all_succeeded else "Partial Success"
        record["UpdateNotebook_Success"] = all_succeeded
        record["UpdateNotebook_ImportedFiles"] = imported_files_info
        return record


# --- Pipeline Pilot I/O Helper Functions ---
def _get_properties() -> Dict[str, str]:
    """
    Reads component properties from stdin in Pipeline Pilot format.
    Properties are read until an empty line is encountered.
    """
    properties = {}
    for line in sys.stdin:
        line = line.strip()
        if not line:
            break  # End of properties
        try:
            key, value = line.split("=", 1)
            properties[key] = value
        except ValueError:
            logging.warning("Invalid property line: %s", line)
    return properties


def _emit_record(record: Dict[str, Any]):
    """
    Emits a record to stdout in Pipeline Pilot format.
    Complex types (lists, dicts) are serialized to JSON strings.
    """
    for key, value in record.items():
        if isinstance(value, (list, dict)):
            value = json.dumps(value)
        # Ensure all values are strings for output to Pipeline Pilot
        print(f"{key}={str(value)}")
    print("ETX")  # End of record marker


def main():
    """
    Main execution function for the Pipeline Pilot component.
    Initializes logging, reads properties, creates the component instance,
    and processes input records one by one.
    """
    # Configure logging to show timestamps and level
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Update Notebook component started.")

    properties = _get_properties()
    logging.info("Component properties received: %s", properties)

    try:
        component = UpdateNotebookComponent(properties)
    except ValueError as e:
        logging.error("Component initialization failed: %s", e)
        # Print error to stderr so Pipeline Pilot can capture it as a component error
        sys.stderr.write(f"ERROR: Component initialization failed: {e}\n")
        sys.exit(1)  # Indicate failure to Pipeline Pilot

    current_record: Dict[str, Any] = {}
    for line in sys.stdin:
        line = line.strip()
        if line == "ETX":
            if current_record:
                logging.debug("Processing record: %s", current_record)
                output_record = component.process_record(current_record)
                _emit_record(output_record)
                logging.debug("Emitted record: %s", output_record)
            current_record = {}
        elif line:
            try:
                key, value = line.split("=", 1)
                current_record[key] = value
            except ValueError:
                logging.warning("Invalid record line: %s", line)

    # Process the last record if there was no final ETX or input ended abruptly
    if current_record:
        logging.debug("Processing final record: %s", current_record)
        output_record = component.process_record(current_record)
        _emit_record(output_record)
        logging.debug("Emitted final record: %s", output_record)

    logging.info("Update Notebook component finished.")


if __name__ == "__main__":
    main()
```