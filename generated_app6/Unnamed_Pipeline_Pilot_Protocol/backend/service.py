from typing import List, Dict, Any, Optional
import logging

from workflow import XmlToElnImportWorkflow

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class XMLImportService:
    """
    Service layer for handling XML file imports into ELN experiments.

    This service orchestrates the parsing of XML and the subsequent import
    of selected files into an ELN experiment by leveraging the
    XmlToElnImportWorkflow. It handles validation, logging, and exception
    handling for business operations.
    """

    def __init__(self):
        """
        Initializes the XMLImportService with an instance of XmlToElnImportWorkflow.
        """
        self.workflow = XmlToElnImportWorkflow()
        logger.info("XMLImportService initialized.")

    def parse_uploaded_xml(self, xml_content: str) -> Dict[str, Any]:
        """
        Parses the provided XML content to discover potential files for ELN import.

        This method validates the XML input, calls the workflow's parsing logic,
        and handles any exceptions that occur during parsing.

        Args:
            xml_content: A string containing the XML data to be parsed.

        Returns:
            A dictionary containing the parsed files and a status message.
            Example: {'status': 'success', 'message': 'XML parsed successfully', 'files': [...]}.

        Raises:
            ValueError: If the xml_content is empty or invalid.
            RuntimeError: If an unexpected error occurs during parsing in the workflow.
        """
        if not xml_content:
            logger.error("Attempted to parse empty XML content.")
            raise ValueError("XML content cannot be empty.")

        logger.info("Starting XML content parsing.")
        try:
            parsed_files = self.workflow.parse_uploaded_xml(xml_content=xml_content)
            logger.info("XML content parsed successfully. Found %d files.", len(parsed_files))
            return {
                'status': 'success',
                'message': 'XML parsed successfully',
                'files': parsed_files
            }
        except ValueError as ve:
            logger.error(f"Validation error during XML parsing: {ve}", exc_info=True)
            raise ValueError(f"Invalid XML content or structure: {ve}") from ve
        except Exception as e:
            logger.error(f"An unexpected error occurred during XML parsing: {e}", exc_info=True)
            raise RuntimeError(f"Failed to parse XML due to an internal error: {e}") from e

    def import_files_to_eln(
        self,
        selected_files: List[Dict[str, Any]],
        experiment_id: str,
        client: Optional[Any] = None,
        author: Optional[str] = None,
        connection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Imports a list of user-selected files into a specified ELN experiment.

        This method validates the input selections, invokes the workflow's import logic,
        and manages logging and exception handling.

        Args:
            selected_files: A list of dictionaries, where each dictionary represents
                            a file to be imported. Each dictionary is expected to
                            contain at least 'file_path', 'file_type', and 'section_title'
                            (or similar keys from `parse_uploaded_xml` output).
            experiment_id: The ID of the ELN experiment where files should be imported.
            client: An optional ELN client object for authentication/connection.
            author: An optional author for the ELN experiment sections.
            connection_name: An optional connection name for the ELN client.

        Returns:
            A dictionary containing the import results and a status message.
            Example: {'status': 'success', 'message': 'Files imported successfully', 'results': [...]}.

        Raises:
            ValueError: If selected_files is empty, experiment_id is missing, or file data is invalid.
            RuntimeError: If an unexpected error occurs during the import process in the workflow.
        """
        if not selected_files:
            logger.warning("Attempted to import an empty list of files.")
            raise ValueError("No files selected for import.")
        if not experiment_id:
            logger.error("Attempted to import files without a specified experiment_id.")
            raise ValueError("Experiment ID is required for importing files.")

        # Basic validation for selected_files structure
        for i, file_data in enumerate(selected_files):
            if not all(k in file_data for k in ['file_path', 'file_type']):
                logger.error(f"Missing 'file_path' or 'file_type' in selected_files[{i}]: {file_data}")
                raise ValueError(f"Invalid file data at index {i}. Each selected file must have 'file_path' and 'file_type'.")

        logger.info(f"Starting import of {len(selected_files)} files into ELN experiment ID: {experiment_id}")
        try:
            import_results = self.workflow.import_selected_files_to_eln(
                selected_files=selected_files,
                experiment_id=experiment_id,
                client=client,
                author=author,
                connection_name=connection_name
            )
            logger.info(f"type(import_results) = {type(import_results)}")
            logger.info(f"import results: {import_results}")
            success_count = 1 if import_results.get("status") == "success" else 0

            logger.info(
                f"Completed import into ELN experiment ID {experiment_id}. "
                f"{success_count} of {len(selected_files)} files imported successfully."
            )
            return {
                'status': 'success',
                'message': f"Import process completed. {success_count} files imported successfully.",
                'results': [import_results]
            }
        except ValueError as ve:
            logger.error(f"Validation error during file import: {ve}", exc_info=True)
            raise ValueError(f"Import failed due to invalid data: {ve}") from ve
        except Exception as e:
            logger.error(f"An unexpected error occurred during file import: {e}", exc_info=True)
            raise RuntimeError(f"Failed to import files due to an internal error: {e}") from e