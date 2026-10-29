"""
Biovia Pipeline Pilot Component: 'Add PDF Section'
Component Path: Components\\Database and Application Integration\\Application Integration\\Notebook\\Experiments\\Add Section\\Add PDF Section
Component GUID: {94F2211E-FD84-4A26-BB7F-58560EDFA824}

Replaces the PLP subprotocol containing:
  - Create New Section (LocalID 2, Section Type: 'PDF Document')
  - Edit PDF Section (LocalID 11, Preview Page List)
  - Custom Manipulator (LocalID 14, PilotScript serialization)
  - Custom Manipulator (LocalID 15, Node attachment to dataroot)
"""
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .section_models import ElnSectionRecord, SectionType
from .biovia_notebook import BioviaNotebookClient


def add_pdf_section(
    section_title: str,
    pdf_file: Union[str, Path],
    preview_page_list: str = "1-5",
    experiment_record: Optional[Dict[str, Any]] = None,
    experiment_id: Optional[str] = None,
    client: Optional[BioviaNotebookClient] = None,
    author: Optional[str] = None,
    connection_name: str = "Connection1",
) -> Dict[str, Any]:
    """
    Adds a PDF section to the incoming experiment record.
    Replicates PLP 'Add PDF Section' component behavior.

    Per Pipeline Pilot specification:
    - Creates a local Section record of type 'PDF Document'
    - Attaches the selected PDF file and configures the preview page range
    - Serializes the node structure matching @serial := nodeserialize(dataroot())

    :param section_title: The title of the new section (required).
    :param pdf_file: Path or filename of the PDF document (required).
    :param preview_page_list: Optional page list/range for thumbnail preview (e.g. '1-5', '1,2').
    :param experiment_record: Optional dictionary representing incoming experiment record.
    :param experiment_id: Optional experiment identifier.
    :param client: Optional BioviaNotebookClient for direct ELN persistence.
    :return: Updated experiment record dictionary with the newly added section.
    """
    if not section_title:
        raise ValueError("Section Title is required for Add PDF Section.")
    if not pdf_file:
        raise ValueError("PDF File is required for Add PDF Section.")

    file_str = str(pdf_file)
    sec_id = f"sec_pdf_{uuid.uuid4().hex[:8]}"

    metadata = {
        "previewPageList": preview_page_list or "1-5",
        "fileName": Path(file_str).name,
    }

    section_rec = ElnSectionRecord(
        section_id=sec_id,
        section_title=section_title,
        section_type=SectionType.PDF,
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

    if "simplesections" not in record:
        record["simplesections"] = []

    serialized_node = section_rec.to_serialized_node()
    record["simplesections"].append(serialized_node)
    record["last_added_section"] = section_rec.to_dict()

    if client:
        remote_id = client.add_pdf_section(
            experiment_id=target_exp_id,
            title=section_title,
            file_path=Path(file_str),
        )
        record["last_added_section"]["remote_section_id"] = remote_id

    return record
