"""
Biovia Pipeline Pilot Component: 'Add Image Section'
Component Path: Components\\Database and Application Integration\\Application Integration\\Notebook\\Experiments\\Add Section\\Add Image Section
Component GUID: {F4D376EB-B83C-449E-840C-E2EC31218298}

Replaces the PLP subprotocol containing:
  - Create New Section (LocalID 2, Section Type: 'Image')
  - Edit Image Section (LocalID 10, Action: Replace/Append)
  - Custom Manipulator (LocalID 13, PilotScript serialization)
  - Custom Manipulator (LocalID 14, Node attachment to dataroot)
"""
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .section_models import ElnSectionRecord, SectionAction, SectionType
from .biovia_notebook import BioviaNotebookClient


def add_image_section(
    section_title: str,
    image_file: Union[str, Path],
    action: str = "Replace",
    experiment_record: Optional[Dict[str, Any]] = None,
    experiment_id: Optional[str] = None,
    client: Optional[BioviaNotebookClient] = None,
    author: Optional[str] = None,
    connection_name: str = "Connection1",
) -> Dict[str, Any]:
    """
    Adds an Image section to the incoming experiment record.
    Replicates PLP 'Add Image Section' component behavior.

    Per Pipeline Pilot specification:
    - Creates a local Section record of type 'Image'
    - Adds the image selected in the Image File parameter (PNG, JPG, BMP, TIFF, SVG)
    - Action modes: 'Replace' (replaces existing image content) or 'Append'
    - Serializes the node structure matching @serial := nodeserialize(dataroot())

    :param section_title: The title of the new section (required).
    :param image_file: Path or filename of the image (required).
    :param action: 'Replace' or 'Append' (default 'Replace').
    :param experiment_record: Optional dictionary representing incoming experiment record.
    :param experiment_id: Optional experiment identifier.
    :param client: Optional BioviaNotebookClient for direct ELN persistence.
    :return: Updated experiment record dictionary with the newly added section.
    """
    if not section_title:
        raise ValueError("Section Title is required for Add Image Section.")
    if not image_file:
        raise ValueError("Image File is required for Add Image Section.")

    file_str = str(image_file)
    ext = Path(file_str).suffix.lower()
    valid_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".svg", ".webp"}
    if ext and ext not in valid_extensions:
        # Note: PLP warns about non-standard image formats
        pass

    normalized_action = SectionAction.APPEND if str(action).lower() == "append" else SectionAction.REPLACE
    sec_id = f"sec_img_{uuid.uuid4().hex[:8]}"

    metadata = {
        "action": normalized_action.value,
        "fileName": Path(file_str).name,
        "fileExtension": ext,
    }

    section_rec = ElnSectionRecord(
        section_id=sec_id,
        section_title=section_title,
        section_type=SectionType.IMAGE,
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

    if normalized_action == SectionAction.REPLACE:
        record["simplesections"] = [
            s for s in record["simplesections"]
            if not (s.get("sectionTitle") == section_title and s.get("sectionType") == SectionType.IMAGE.value)
        ]

    serialized_node = section_rec.to_serialized_node()
    record["simplesections"].append(serialized_node)
    record["last_added_section"] = section_rec.to_dict()

    if client:
        remote_id = client.add_image_section(
            experiment_id=target_exp_id,
            title=section_title,
            file_path=Path(file_str),
            action=normalized_action.value,
        )
        record["last_added_section"]["remote_section_id"] = remote_id

    return record
