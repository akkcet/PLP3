"""
Biovia Pipeline Pilot Component: 'Add File Attachment Section'
Component Path: Components\\Database and Application Integration\\Application Integration\\Notebook\\Experiments\\Add Section\\Add File Attachment Section
Component GUID: {26E8ED5E-1528-4272-B425-EAE5BD96C635}

Replaces the PLP subprotocol containing:
  - Create New Section (LocalID 2, Section Type: 'File Attachment')
  - Edit File Attachment Section (LocalID 9, Action: Replace/Append)
  - Custom Manipulator (LocalID 12, PilotScript serialization)
  - Custom Manipulator (LocalID 13, Node attachment to dataroot)
"""
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .section_models import ElnSectionRecord, SectionAction, SectionType
from .biovia_notebook import BioviaNotebookClient


def add_file_attachment_section(
    section_title: str,
    files_to_attach: Union[str, Path, List[Union[str, Path]]],
    action: str = "Replace",
    experiment_record: Optional[Dict[str, Any]] = None,
    experiment_id: Optional[str] = None,
    client: Optional[BioviaNotebookClient] = None,
    author: Optional[str] = None,
    connection_name: str = "Connection1",
) -> Dict[str, Any]:
    """
    Adds a file attachment section to the incoming experiment record.
    Replicates PLP 'Add File Attachment Section' component behavior.

    Per Pipeline Pilot specification:
    - Creates a local Section record of type 'File Attachment'
    - Attaches the selected files (supporting single file or list of files)
    - Supports Action modes: 'Replace' (overwrites existing files in section) or 'Append'
    - Serializes the node structure matching @serial := nodeserialize(dataroot())

    :param section_title: The title of the new section (required).
    :param files_to_attach: One or more files to add to the section (required).
    :param action: 'Replace' or 'Append' (default 'Replace').
    :param experiment_record: Optional dictionary representing incoming experiment record.
    :param experiment_id: Optional experiment identifier.
    :param client: Optional BioviaNotebookClient for direct ELN persistence.
    :return: Updated experiment record dictionary with the newly added section.
    """
    if not section_title:
        raise ValueError("Section Title is required for Add File Attachment Section.")
    if not files_to_attach:
        raise ValueError("Files to Attach is required for Add File Attachment Section.")

    normalized_action = SectionAction.APPEND if str(action).lower() == "append" else SectionAction.REPLACE

    if isinstance(files_to_attach, (list, tuple)):
        file_list = [str(f) for f in files_to_attach if f]
    else:
        file_list = [str(files_to_attach)]

    if not file_list:
        raise ValueError("At least one file must be specified in Files to Attach.")

    sec_id = f"sec_attach_{uuid.uuid4().hex[:8]}"

    metadata = {
        "action": normalized_action.value,
        "fileCount": len(file_list),
        "fileNames": [Path(f).name for f in file_list],
    }

    section_rec = ElnSectionRecord(
        section_id=sec_id,
        section_title=section_title,
        section_type=SectionType.FILE_ATTACHMENT,
        files=file_list,
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

    # If action is Replace and an existing section with same title exists, handle replacement
    if normalized_action == SectionAction.REPLACE:
        record["simplesections"] = [
            s for s in record["simplesections"]
            if not (s.get("sectionTitle") == section_title and s.get("sectionType") == SectionType.FILE_ATTACHMENT.value)
        ]

    serialized_node = section_rec.to_serialized_node()
    record["simplesections"].append(serialized_node)
    record["last_added_section"] = section_rec.to_dict()

    if client:
        # Register attachment section with the primary file
        primary_file = Path(file_list[0])
        remote_id = client.add_attachment_section(
            experiment_id=target_exp_id,
            title=section_title,
            file_path=primary_file,
        )
        record["last_added_section"]["remote_section_id"] = remote_id

    return record
