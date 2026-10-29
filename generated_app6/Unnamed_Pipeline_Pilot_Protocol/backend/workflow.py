import logging
from typing import List, Dict, Any, Optional

from components.xml_model_parser import parse_model_xml
from components.add_excel_section import add_excel_section
from components.add_pdf_section import add_attachment_to_experiment
from components.add_powerpoint_section import add_powerpoint_section
from components.add_word_section import add_word_section
from components.add_image_section import add_image_section
from components.add_file_attachment_section import add_file_attachment_section

logger = logging.getLogger(__name__)


class XmlToElnImportWorkflow:
    """
    Orchestrates the interactive XML import process into ELN experiments.

    This workflow handles parsing an uploaded XML to discover available files,
    and then imports user-selected files into ELN sections based on their type.
    It supports the frontend workflow where users first upload XML, then view
    parsed files, select specific files, and finally trigger their import.
    """

    def __init__(self, client: Optional[Any] = None, connection: Optional[Any] = None):
        """
        Initializes the XML to ELN Import Workflow.

        Args:
            client: An optional BioviaNotebookClient instance for direct ELN persistence.
            connection: An optional NotebookConnectionObject for ELN interaction.
        """
        self.client = client
        self.connection = connection
        self._parsed_files: List[Dict] = []
        logger.info("XmlToElnImportWorkflow initialized.")

    def parse_uploaded_xml(self, xml_content: str) -> List[Dict]:
        """
        Parses the provided XML content to identify files and sections for import.

        This method supports the "Upload XML" and "Parse XML" steps of the business flow.
        It extracts file paths and potential section titles from the XML, making them
        available for user selection in the frontend.

        Args:
            xml_content (str): The raw XML content as a string.

        Returns:
            List[Dict]: A list of dictionaries, where each dictionary represents a
                        discoverable file/section from the XML, including its type,
                        path, and a suggested title. This output is intended for UI display.
                        Example: [{'file_path': 'C:/temp/report.pdf', 'file_type': 'pdf', 'section_title': 'Experiment Report'}]
        Raises:
            ValueError: If XML parsing fails or returns no identifiable files.
        """
        logger.info("Attempting to parse uploaded XML content.")
        #logger.info("Attempting to parse uploaded XML content.")

        try:

            parsed_data = parse_model_xml(
                xml_source=xml_content
            )

            # print("=" * 80)
            # print("PARSED DATA TYPE")
            # print(type(parsed_data))

            # print("=" * 80)
            # print("PARSED DATA")
            # print(parsed_data)

            if not parsed_data.files:

                logger.warning(
                    "No files or sections were parsed from the provided XML."
                )

                raise ValueError(
                    "No identifiable files or sections found in the XML."
                )

            normalized_files = []

            for file_item in parsed_data.files:

                normalized_files.append(

                    {
                        "id":
                            file_item.file_location,

                        "name":
                            file_item.file_name,

                        "type":
                            file_item.extension.lstrip("."),

                        "file_path":
                            file_item.file_location,

                        "section_title":
                            file_item.section_title
                    }
                )

            self._parsed_files = normalized_files

            logger.info(
                f"Successfully parsed "
                f"{len(self._parsed_files)} files from XML."
            )

            return self._parsed_files

        except Exception as e:

            logger.error(
                f"Error parsing XML content: {e}",
                exc_info=True
            )

            raise ValueError(
                f"Failed to parse XML: {e}"
            ) from e

    def import_selected_files_to_eln(
        self,
        experiment_id: str,
        selected_files: List[Dict],
        author: Optional[str] = None,
        initial_experiment_record: Optional[Dict] = None,
        client: Optional[str] = None,
        connection_name: Optional[str] = None,
    ) -> Dict:
        """
        Imports user-selected files into the specified ELN experiment.

        This method supports the "User selects files" and "Import selected files"
        steps of the business flow. It iterates through the selected files,
        determines their type, and dispatches them to the appropriate ELN section
        creation component.

        The workflow specifically supports user-driven file selection and does NOT
        automatically import all files after parsing.

        Args:
            experiment_id (str): The ID of the ELN experiment to import into.
            selected_files (List[Dict]): A list of dictionaries, each representing
                                        a file selected by the user for import.
                                        Each dict should at least contain 'file_path'
                                        and 'file_type', and optionally 'section_title'.
                                        Example: [{'file_path': 'C:/temp/report.pdf', 'file_type': 'pdf', 'section_title': 'Experiment Report'}]
            author (str, optional): The author for the new ELN sections.
            initial_experiment_record (Dict, optional): An optional dictionary representing
                                                        the current state of the experiment
                                                        record. If not provided, the first
                                                        section added will initialize it.

        Returns:
            Dict: The final updated experiment record after all selected files have
                  been imported as sections.

        Raises:
            ValueError: If experiment_id is missing, or no files are selected.
            RuntimeError: If an error occurs during the ELN section creation process.
        """
        if not experiment_id:
            logger.error("Experiment ID is required for importing files.")
            raise ValueError("Experiment ID cannot be empty.")
        if not selected_files:
            logger.warning("No files selected for import to ELN experiment %s.", experiment_id)
            return initial_experiment_record if initial_experiment_record else {}

        current_experiment_record = initial_experiment_record or {}
        logger.info(f"Starting import of {len(selected_files)} selected files to ELN experiment {experiment_id}.")

        file_type_dispatch = {
            ".xlsx": (add_excel_section, "Excel Worksheet"),
            ".xls": (add_excel_section, "Excel Worksheet"),
            ".pdf": (add_attachment_to_experiment, "PDF Document"),
            ".pptx": (add_powerpoint_section, "PowerPoint Presentation"),
            ".ppt": (add_powerpoint_section, "PowerPoint Presentation"),
            ".docx": (add_word_section, "Word Document"),
            ".doc": (add_word_section, "Word Document"),
            # ".jpg": (add_image_section, "Image"),
            # ".jpeg": (add_image_section, "Image"),
            # ".png": (add_image_section, "Image"),
            # ".gif": (add_image_section, "Image"),
            # ".bmp": (add_image_section, "Image"),
            # ".tiff": (add_image_section, "Image"),
            # ".tif": (add_image_section, "Image"),
            # ".svg": (add_image_section, "Image"),
        }

        for i, file_info in enumerate(selected_files):
            file_path = file_info.get("file_path")
            suggested_title = file_info.get("section_title", f"Imported File {i + 1}")
            file_extension = (
                "." + file_path.split(".")[-1].lower() if "." in file_path else ""
            )

            if not file_path:
                logger.warning(f"Skipping file {i} due to missing 'file_path'. File info: {file_info}")
                continue

            section_func, section_type_name = file_type_dispatch.get(file_extension, (add_file_attachment_section, "File Attachment"))

            try:
                logger.debug(
                    f"Adding section '{suggested_title}' ({section_type_name}) for file: {file_path} "
                    f"to experiment {experiment_id}."
                )

                if section_func == add_excel_section:
                    current_experiment_record = section_func(
                        section_title=suggested_title,
                        excel_file=file_path,
                        preview_mode="Generate from Excel File Content",
                        #experiment_record=current_experiment_record,
                        experiment_id=experiment_id,
                        client=self.client,
                        author=author,
                        connection_name=self.connection.connection_name if self.connection else None,
                    )
                elif section_func == add_attachment_to_experiment:
                    current_experiment_record = section_func(
                        section_name=suggested_title,
                        pdf_file=file_path,
                        #experiment_record=current_experiment_record,
                        experiment_id=experiment_id,
                        client=self.client,
                        author=author,
                        connection_name=self.connection.connection_name if self.connection else None,
                    )
                elif section_func == add_powerpoint_section:
                    current_experiment_record = section_func(
                        section_title=suggested_title,
                        powerpoint_file=file_path,
                        #experiment_record=current_experiment_record,
                        experiment_id=experiment_id,
                        client=self.client,
                        author=author,
                        connection_name=self.connection.connection_name if self.connection else None,
                    )
                elif section_func == add_word_section:
                    current_experiment_record = section_func(
                        section_title=suggested_title,
                        word_file=file_path,
                        #experiment_record=current_experiment_record,
                        experiment_id=experiment_id,
                        client=self.client,
                        author=author,
                        connection_name=self.connection.connection_name if self.connection else None,
                    )
                elif section_func == add_image_section:
                    current_experiment_record = section_func(
                        section_title=suggested_title,
                        image_file=file_path,
                        experiment_record=current_experiment_record,
                        experiment_id=experiment_id,
                        client=self.client,
                        author=author,
                        connection_name=self.connection.connection_name if self.connection else None,
                    )
                # elif section_func == add_file_attachment_section:
                #     current_experiment_record = section_func(
                #         section_title=suggested_title,
                #         files_to_attach=[file_path],
                #         experiment_record=current_experiment_record,
                #         experiment_id=experiment_id,
                #         client=self.client,
                #         author=author,
                #         connection_name=self.connection.connection_name if self.connection else None,
                #     )
                else:
                    logger.warning(f"No specific handler for file type for {file_path}. Using generic file attachment.")
                    current_experiment_record = add_file_attachment_section(
                        section_title=suggested_title,
                        files_to_attach=[file_path],
                        #experiment_record=current_experiment_record,
                        experiment_id=experiment_id,
                        client=self.client,
                        author=author,
                        connection_name=self.connection.connection_name if self.connection else None,
                    )

                logger.info(f"Successfully added section '{suggested_title}' for file: {file_path}")

            except Exception as e:
                logger.error(
                    f"Failed to add section '{suggested_title}' for file '{file_path}' to ELN experiment {experiment_id}: {e}",
                    exc_info=True,
                )
                # Depending on business rules, could continue or re-raise. For now, re-raise for critical failure.
                raise RuntimeError(
                    f"Failed to import file '{file_path}' as section '{suggested_title}': {e}"
                ) from e

        logger.info(f"All selected files imported to ELN experiment {experiment_id}.")
        return current_experiment_record