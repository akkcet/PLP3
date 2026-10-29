"""
Biovia Pipeline Pilot Component: 'Add Excel Section'
Component Path: Components\\Database and Application Integration\\Application Integration\\Notebook\\Experiments\\Add Section\\Add Excel Section
Component GUID: {3136A684-DFA5-448D-A426-731FB1723119}

Replaces the PLP subprotocol containing:
  - Create New Section (LocalID 2, Section Type: 'Excel Worksheet')
  - Edit Excel Section (LocalID 13)
  - Custom Manipulator (LocalID 11, PilotScript serialization)
  - Custom Manipulator (LocalID 12, Node attachment to dataroot)
"""
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .section_models import ElnSectionRecord, ExcelPreviewConfig, SectionType
from .biovia_notebook import BioviaNotebookClient


def add_excel_section(
    section_title: str,
    excel_file: Union[str, Path],
    preview_mode: str = "Generate from Excel File Content",
    columns_to_preview: int = 2,
    rows_to_preview: int = 3,
    column_preview_width: int = 120,
    row_preview_height: int = 20,
    preview_custom_image: Optional[str] = None,
    experiment_record: Optional[Dict[str, Any]] = None,
    experiment_id: Optional[str] = None,
    client: Optional[BioviaNotebookClient] = None,
    author: Optional[str] = None,
    connection_name: str = "Connection1",
) -> Dict[str, Any]:
    """
    Adds an Excel section to the incoming experiment record.
    Replicates PLP 'Add Excel Section' component behavior.

    Per Pipeline Pilot specification:
    - Creates a local Section record of type 'Excel Worksheet'
    - Attaches the specified Excel file and configures table preview settings
    - Validates that columns_to_preview < 8
    - Appends the section to the experiment record's simplesections list
    - Serializes the node structure matching @serial := nodeserialize(dataroot())

    :param section_title: The title of the new section (required).
    :param excel_file: Path or filename of the Excel spreadsheet (required).
    :param preview_mode: 'Generate from Excel File Content' or 'Use Custom Image'.
    :param columns_to_preview: Number of preview columns (must be < 8).
    :param rows_to_preview: Number of preview rows.
    :param column_preview_width: Width of column preview in pixels.
    :param row_preview_height: Height of row preview in pixels.
    :param preview_custom_image: Optional image path when preview_mode is 'Use Custom Image'.
    :param experiment_record: Optional dictionary representing incoming experiment record.
    :param experiment_id: Optional experiment identifier.
    :param client: Optional BioviaNotebookClient for direct ELN persistence.
    :return: Updated experiment record dictionary with the newly added section.
    """
    if not section_title:
        raise ValueError("Section Title is required for Add Excel Section.")
    if not excel_file:
        raise ValueError("Excel File is required for Add Excel Section.")

    preview_config = ExcelPreviewConfig(
        preview_mode=preview_mode,
        columns_to_preview=int(columns_to_preview),
        rows_to_preview=int(rows_to_preview),
        column_preview_width=int(column_preview_width),
        row_preview_height=int(row_preview_height),
        custom_image=preview_custom_image,
    )
    preview_config.validate()

    file_str = str(excel_file)
    sec_id = f"sec_excel_{uuid.uuid4().hex[:8]}"

    metadata = {
        "previewMode": preview_config.preview_mode,
        "previewCols": preview_config.columns_to_preview,
        "previewRows": preview_config.rows_to_preview,
        "columnWidth": preview_config.column_preview_width,
        "rowHeight": preview_config.row_preview_height,
        "customImage": preview_config.custom_image,
        "fileName": Path(file_str).name,
    }

    section_rec = ElnSectionRecord(
        section_id=sec_id,
        section_title=section_title,
        section_type=SectionType.EXCEL,
        files=[file_str],
        metadata=metadata,
        author=author,
        connection_name=connection_name,
    )

    record = dict(experiment_record) if experiment_record else {}
    target_exp_id = (
        experiment_id
        or record.get("id")
        or record.get("experimentNumber")
        or "EXP-LOCAL-01"
    )

    # Initialize simplesections collection if absent
    if "simplesections" not in record:
        record["simplesections"] = []

    # Emulate PLP node append to dataroot()
    serialized_node = section_rec.to_serialized_node()
    record["simplesections"].append(serialized_node)

    # Keep track of last added section
    record["last_added_section"] = section_rec.to_dict()

    # If client is provided, persist directly to ELN database
    if client:
        remote_id = client.add_excel_section(
            experiment_id=target_exp_id,
            title=section_title,
            file_path=Path(file_str),
        )
        record["last_added_section"]["remote_section_id"] = remote_id

    return record
