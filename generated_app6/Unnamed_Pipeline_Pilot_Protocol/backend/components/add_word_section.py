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
from docx import Document

logger = logging.getLogger("biovia_pipeline.experiment_attachment")

def add_word_section(
        connection_name: Union[NotebookConnectionObject, str],
        section_title: str,
        word_file: str,
        #preview_mode: str = "Preview will be generated when the file is edited.",
        experiment_id: Optional[str] = None,
        section_type_id: int = 37,
        client: Optional[BioviaNotebookClient] = None,
        author: Optional[str] = None,
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
    import xml.etree.ElementTree as ET

    # =========================================================
    # STEP 2A - Get the placeholder Data ID
    # =========================================================

    section_details =conn_obj.session.get(
        f"{conn_obj.api_endpoint}/sections/{section_id}?$expand=sectiondata",
        headers={"Accept": "application/xml"}
    )
    
    section_details.raise_for_status()
    logger.info(
        f"Content-Type = "
        f"{section_details.headers.get('Content-Type')}"
    )
    logger.info(
        f"Section XML:\n{section_details.text}"
    )

    root = ET.fromstring(section_details.text)
    data_nodes = root.findall(".//*")
    for elem in root.iter():
        print(elem.tag)
    for node in data_nodes:
        
        if node.tag.endswith("Data"):
            logger.info(
                f"Found Data node: {ET.tostring(node, encoding='unicode')}"
            )
    data_id = root.findtext(".//sectiondata/Data/id")
    # Find first Data node under sectiondata
    # data_node = root.find(".//Data")

    # if data_node is None:
    #     raise RuntimeError(
    #         f"No Data node found for section {section_id}"
    #     )

    # data_id = data_node.findtext("id")

    logger.info(
        f"Found placeholder Data ID: {data_id}"
    )

    upload_url = (
        f"{conn_obj.api_endpoint}/sections/"
        f"{section_id}/data"
    )
    
    filename = os.path.basename(word_file)
    with open(word_file, "rb") as f:
        doc_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    
    doc = Document(word_file)

    paragraph_text = []

    # Get first 30 non-empty paragraphs
    for para in doc.paragraphs:
        if para.text.strip():
            paragraph_text.append(para.text.strip())

        if len(paragraph_text) >= 30:
            break

    text = "\n".join(paragraph_text)

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
        "id": int(data_id),
        "datatypeid": 37,
        "indexinsection": 1,
        "sectionid": int(section_id),
        "documentId": int(documentid),
        "Properties": {
            "Height": 200,
            "Tag": 20,
            "FailedLoading": False,
            "YPosition": 0,
            "Width": 500,
            "XPosition": 0,
            "AnnotationData": "",
            "FileName": filename
        },
        "Formats": [
            {
                "Mimetype": "text/plain",
                "Content": filename
            },
            {
                "Mimetype":
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "Content": doc_b64
            },
            {
                "Mimetype": "image/png",
                "Content": png_b64
            }
        ]
    }
    logger.info(
        f"Updating Data ID {data_id} "
        f"for Section {section_id}"
    )

    logger.info(
        f"doc_b64 length = {len(doc_b64)}"
    )

    logger.info(
        f"png_b64 length = {len(png_b64)}"
    )
    upload_response = conn_obj.session.put(
        f"{conn_obj.api_endpoint}/data/{data_id}",
        json=payload,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )
    logger.info(
        f"PUT status = {upload_response.status_code}"
    )
    logger.info(
        f"PUT body = {upload_response.text}"
    )
    upload_response.raise_for_status()
    
    attachment_location = (
        upload_response.headers.get("Location")
    )
    logger.info(f"response Text: {upload_response.text}")
    logger.info(f"Status: {upload_response.status_code}")
    logger.info(f"Headers: {upload_response.headers}")
    logger.info(f"Location: {upload_response.headers.get('Location')}")
    logger.info(f"Body: {upload_response.text}")
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
