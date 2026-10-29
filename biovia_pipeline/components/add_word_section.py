"""
Biovia Pipeline Pilot Component: 'Add Word Section'
Component Path: Components\\Database and Application Integration\\Application Integration\\Notebook\\Experiments\\Add Section\\Add Word Section
Component GUID: {AED5E9B3-0FD3-497E-B0DB-CA8DC212E03F}
Component LocalID: 11

Replaces the PLP subprotocol containing:
  - Create New Section (LocalID 2, Section Type: 'Word Document', Connection: 'Connection1')
  - Edit Word Section (LocalID 13, Preview Text, Preview Image Width/Height)
  - Custom Manipulator (LocalID 16, @serial := nodeserialize(dataroot()))
  - Custom Manipulator (LocalID 17, #n := nodeappendchild(dataroot(), @serial); nodeproperty(#n, 'connectionname') := connectionname; nodeproperty(#n, 'ref') := ref;)
"""
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .section_models import ElnSectionRecord, SectionType
from .biovia_notebook import BioviaNotebookClient


def add_word_section(
    section_title: str,
    word_file: Union[str, Path],
    preview_text: str = "Preview will be generated when the file is edited.",
    preview_width: int = 600,
    preview_height: int = 30,
    experiment_record: Optional[Dict[str, Any]] = None,
    experiment_id: Optional[str] = None,
    client: Optional[BioviaNotebookClient] = None,
    author: Optional[str] = None,
    connection_name: str = "Connection1",
) -> Dict[str, Any]:
    """
    Adds a Word section to the incoming experiment record.
    Replicates PLP 'Add Word Section' subprotocol behavior.

    Per Pipeline Pilot specification:
    - Creates a local Section record of type 'Word Document'
    - Creates a message preview instructing user that preview will be generated when file is edited in Notebook
    - Formats default preview width (600) and height (30)
    - Serializes node structure and appends to the experiment record

    :param section_title: The title of the new section (required).
    :param word_file: Path or filename of the Word document (.doc, .docx) (required).
    :param preview_text: Message rendered on canvas/chart (default: "Preview will be generated when the file is edited.").
    :param preview_width: Preview image width in pixels (default: 600).
    :param preview_height: Preview image height in pixels (default: 30).
    :param experiment_record: Optional dictionary representing incoming experiment record.
    :param experiment_id: Optional experiment identifier.
    :param client: Optional BioviaNotebookClient for direct ELN persistence.
    :param author: Optional section author.
    :param connection_name: Notebook connection identifier (default: "Connection1").
    :return: Updated experiment record dictionary with the newly added section.
    """
    if not section_title:
        raise ValueError("Section Title is required for Add Word Section.")
    if not word_file:
        raise ValueError("Word File is required for Add Word Section.")

    file_str = str(word_file)
    sec_id = f"sec_word_{uuid.uuid4().hex[:8]}"

    metadata = {
        "previewText": preview_text or "Preview will be generated when the file is edited.",
        "previewImageWidth": int(preview_width),
        "previewImageHeight": int(preview_height),
        "fileName": Path(file_str).name,
    }

    section_rec = ElnSectionRecord(
        section_id=sec_id,
        section_title=section_title,
        section_type=SectionType.WORD,
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
        remote_id = client.add_word_section(
            experiment_id=target_exp_id,
            title=section_title,
            file_path=Path(file_str),
        )
        record["last_added_section"]["remote_section_id"] = remote_id

    return record
