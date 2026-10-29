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
import os
from .section_models import ElnSectionRecord, ExcelPreviewConfig, SectionType
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


logger = logging.getLogger("biovia_pipeline.experiment_attachment")
def add_excel_section(
    connection_name: Union[NotebookConnectionObject, str],
    experiment_id: str,
    excel_file: str,
    section_title: str = "Attachments",
    section_type_id: int = 10,
    preview_mode: str = "Generate from Excel File Content",
    author: str = None,
    client: str = None,
        
    
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

    filename = os.path.basename(excel_file)
    with open(excel_file, "rb") as f:
        xlsx_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    

    xlsx = pd.ExcelFile(excel_file)

    parts = []

    for sheet in xlsx.sheet_names:
        parts.append(f"Sheet: {sheet}")

        df = pd.read_excel(
            excel_file,
            sheet_name=sheet,
            dtype=str
        ).fillna("")

        for _, row in df.iterrows():
            parts.append("\t".join(row.astype(str)))

    ascii_text = "\n".join(parts)
    df = pd.read_excel(
        excel_file,
        nrows=20
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis("off")

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc="center"
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
        "datatypeid": 12,
        "Properties": {
            "FileName": "Unique-standard_UDA_Size_Report.xlsx"
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
            },
            {
                "Mimetype": "text/plain",
                "Content": ascii_text
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
    ##############################################
    
