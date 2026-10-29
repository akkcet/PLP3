"""
Biovia Pipeline Pilot Component: 'Add PDF Section'
Component Path: Components\\Database and Application Integration\\Application Integration\\Notebook\\Experiments\\Add Section\\Add PDF Section
Component GUID: {94F2211E-FD84-4A26-BB7F-58560EDFA824}

Replaces the PLP subprotocol containing:
  - Create New Section (LocalID 2, Section Type: 'PDF Document')
  - Edit PDF Section (LocalID 11, Preview Page List)
  - Custom Manipulator (LocalID 14, PilotScript serialization)
  - Custom Manipulator (LocalID 15, Node attachment to dataroot)

  Workflow:
1. Resolve Notebook connection
2. Locate experiment
3. Create PDF section
4. Convert PDF to Base64
5. Upload PDF into section
6. Return created object details
"""
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import base64
import logging


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

from .notebook_connection import (
    NotebookConnectionObject,
    notebook_connection
)
from .experiment_query import experiment_query

logger = logging.getLogger(
    "biovia_pipeline.add_pdf_attachment"
)


def add_pdf_attachment_to_experiment(
    connection: Union[NotebookConnectionObject, str],
    experiment_number: str,
    pdf_file_path: str,
    section_title: str = "PDF Document"
) -> Dict[str, Any]:
    """
    Add a PDF attachment to an ELN experiment.

    Parameters
    ----------
    connection
        Notebook connection object or connection name.

    experiment_number
        Experiment number (e.g. EXP-26-BP7567)

    pdf_file_path
        Local PDF file path.

    section_title
        Title shown in ELN.

    Returns
    -------
    Dict[str, Any]
    """

    # ---------------------------------------------------------
    # Resolve connection
    # ---------------------------------------------------------

    if isinstance(connection, str):
        conn_obj = notebook_connection(
            connection_name=connection
        )
    else:
        conn_obj = connection

    if conn_obj.session is None:
        raise RuntimeError(
            "Notebook connection is not authenticated."
        )

    # ---------------------------------------------------------
    # Find experiment
    # ---------------------------------------------------------

    experiments = experiment_query(
        connection=conn_obj,
        filter_by="Experiment Number",
        filter_type="Equals",
        filter_value=experiment_number
    )

    if not experiments:
        raise ValueError(
            f"Experiment '{experiment_number}' not found."
        )

    experiment = experiments[0]

    document_id = experiment["ID"]

    logger.info(
        f"Found experiment {experiment_number} "
        f"(document_id={document_id})"
    )

    # ---------------------------------------------------------
    # Create PDF section
    # ---------------------------------------------------------

    create_section_payload = {
        "sectiontypeid": 29,
        "title": section_title
    }

    section_response = conn_obj.session.post(
        (
            f"{conn_obj.api_endpoint}"
            f"/sections?documentid={document_id}"
        ),
        json=create_section_payload,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        timeout=30
    )

    section_response.raise_for_status()

    section_location = (
        section_response.headers["Location"]
    )

    section_id = (
        section_location.rstrip("/")
        .split("/")[-1]
    )

    logger.info(
        f"Created PDF section {section_id}"
    )

    # ---------------------------------------------------------
    # Read PDF
    # ---------------------------------------------------------

    pdf_path = Path(pdf_file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    with open(pdf_path, "rb") as f:
        pdf_content = base64.b64encode(
            f.read()
        ).decode("utf-8")

    # ---------------------------------------------------------
    # Upload PDF Data
    # ---------------------------------------------------------

    upload_payload = {
        "datatypeid": 27,
        "Formats": [
            {
                "Mimetype": "application/pdf",
                "Content": pdf_content
            }
        ]
    }

    upload_response = conn_obj.session.post(
        (
            f"{conn_obj.api_endpoint}"
            f"/sections/{section_id}/data"
        ),
        json=upload_payload,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        timeout=300
    )

    upload_response.raise_for_status()

    data_location = (
        upload_response.headers.get("Location")
    )

    data_id = None

    if data_location:
        data_id = (
            data_location.rstrip("/")
            .split("/")[-1]
        )

    logger.info(
        f"Uploaded PDF. data_id={data_id}"
    )

    return {
        "status": "success",
        "experiment_number": experiment_number,
        "document_id": document_id,
        "section_id": int(section_id),
        "data_id": (
            int(data_id)
            if data_id
            else None
        ),
        "file_name": pdf_path.name,
        "section_title": section_title
    }