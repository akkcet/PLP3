"""
Biovia Pipeline Pilot Component: 'Add PowerPoint Presentation Section'
Component Path: Components\\Database and Application Integration\\Application Integration\\Notebook\\Experiments\\Add Section\\Add PowerPoint Presentation Section
Component GUID: {E5B6E23D-CC7F-4D04-878E-606E3B4B6E7E}
Component LocalID: 9

Replaces the PLP subprotocol containing:
  - Create New Section (LocalID 2, Section Type: 'PowerPoint Presentation', Connection: 'Connection1')
  - Edit PowerPoint Section (LocalID 18, Preview Text, Preview Image Width/Height)
  - Custom Manipulator (LocalID 16, @serial := nodeserialize(dataroot()))
  - Custom Manipulator (LocalID 17, #n := nodeappendchild(dataroot(), @serial); nodeproperty(#n, 'connectionname') := connectionname; nodeproperty(#n, 'ref') := ref;)
"""
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Union
import os
from .section_models import ElnSectionRecord, SectionType
from .biovia_notebook import BioviaNotebookClient
from .notebook_connection import (
    NotebookConnectionObject,
    notebook_connection
)
from .experiment_query import experiment_query
import pandas as pd
import base64
import matplotlib.pyplot as plt
import io
import logging
from pptx import Presentation

logger = logging.getLogger("biovia_pipeline.experiment_attachment")
def add_powerpoint_section(
    connection_name: Union[NotebookConnectionObject, str],
    section_title: str,
    powerpoint_file: str,
    preview_mode: str = "Preview will be generated when the file is edited.",
    experiment_id: Optional[str] = None,
    section_type_id: int = 39,
    client: Optional[BioviaNotebookClient] = None,
    author: Optional[str] = None,
    
) -> Dict[str, Any]:
    """
    Adds a PowerPoint Presentation section to the incoming experiment record.
    Replicates PLP 'Add PowerPoint Presentation Section' subprotocol behavior.

    Per Pipeline Pilot specification:
    - Creates a local Section record of type 'PowerPoint Presentation'
    - Creates a message preview instructing user that preview will be generated when file is edited in Notebook
    - Formats default preview width (600) and height (30)
    - Serializes node structure and appends to the experiment record

    :param section_title: The title of the new section (required).
    :param powerpoint_file: Path or filename of the PowerPoint presentation (required).
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
    # ---------------------------------------------------------
    # Resolve connection
    # ---------------------------------------------------------
    
    if isinstance(connection_name, str):
        conn_obj = notebook_connection(connection_name=connection_name)
    else:
        conn_obj = connection_name
    # STEP 0 - ESTABLISH CONNECTION
    # ============================================================================
    # TEMPORARY LOCAL TESTING WORKAROUND 
    # REMOVE AFTER NOTEBOOK INTEGRATION
    # ============================================================================
    
    if conn_obj is None:
        logger.warning(
            "No notebook connection provided. Creating temporary connection."
        )
    
        # Paste your working connection creation code here
        conn_obj = notebook_connection(
            server_url="https://notebook.unilever.com",
            authentication_method=
                "Use Username and Password Parameters",
            username="arun.khuntia",
            password="Pogoanaisha321!",)
    
    if conn_obj.session is None:
        raise RuntimeError(
            "Notebook Connection does not contain an authenticated requests session."
        )
    ## experiment query
    experiments = experiment_query(
        connection=conn_obj,
        filter_by="Experiment Number",
        filter_type="Equals",
        filter_value=experiment_id
    )
    #GET DOCUMENTID
    documentid = experiments[0]["ID"]
    # ---------------------------------------------------------
    # STEP 1 - CREATE SECTION
    # ---------------------------------------------------------
    
    create_section_url = (
        f"{conn_obj.api_endpoint}/sections"
        f"?documentid={documentid}"
    )
    
    section_payload = {
        "title": section_title,
        "sectiontypeid": section_type_id
    }
    logger.info(f"PAYLOAD:   {section_payload}")
    logger.info(
        f"Creating section in experiment {experiment_id}"
    )
    logger.info(f"create_section_url:   {create_section_url}")
    section_response = conn_obj.session.post(
        create_section_url,
        json=section_payload,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        timeout=30
    )
    section_response.raise_for_status()
    
    location_header = section_response.headers.get("Location")
    
    if not location_header:
        raise RuntimeError(
            "Notebook API did not return Location header."
        )
    
    # Example:
    # /v1/sections/12345
    section_id = location_header.rstrip("/").split("/")[-1]
    
    logger.info(
        f"Created section {section_id}"
    )
    # ---------------------------------------------------------
    # STEP 2 - UPLOAD FILE
    # ---------------------------------------------------------
    
    upload_url = (
        f"{conn_obj.api_endpoint}/sections/"
        f"{section_id}/data"
    )
    
    filename = os.path.basename(powerpoint_file)
    with open(powerpoint_file, "rb") as f:
        xlsx_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    
    prs = Presentation(powerpoint_file)

    slide_text = []

    for i in range(min(5, len(prs.slides))):
        slide = prs.slides[i]
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                slide_text.append(shape.text)

    text = "\n".join(slide_text[:30])

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis("off")
    ax.text(
        0.01,
        0.99,
        text,
        va="top",
        wrap=True,
        fontsize=10
    )

    buffer = io.BytesIO()

    plt.savefig(
        buffer,
        format="png",
        bbox_inches="tight"
    )

    buffer.seek(0)

    png_b64 = base64.b64encode(
        buffer.read()
    ).decode("utf-8")

    plt.close(fig)
    
    
    payload = {
        "datatypeid": 39,
        "Properties": {
            "FileName": "Scinet-new.pptx"
        },
        "Formats": [
            {
                ## .xls application/vnd.ms-excel
                "Mimetype":
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "Content": xlsx_b64
            },
            {
                "Mimetype": "image/png",
                "Content": png_b64
            }
        ]
    }
    upload_response = conn_obj.session.post(
        f"{conn_obj.api_endpoint}/sections/{section_id}/data",
        json=payload,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )
    upload_response.raise_for_status()
    
    attachment_location = (
        upload_response.headers.get("Location")
    )
    
    logger.info(
        f"Uploaded attachment {filename}"
    )

    return {
        "experiment_id": experiment_id,
        "section_id": section_id,
        "file_name": filename,
        "section_location": location_header,
        "attachment_location": attachment_location,
        "status": "success"
    }
