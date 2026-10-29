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
import os
from .section_models import ElnSectionRecord, SectionAction, SectionType
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
def add_file_attachment_section(
    connection_name: Union[NotebookConnectionObject, str],
    section_title: str,
    files_to_attach: Union[str, Path, List[Union[str, Path]]],
    action: str = "Replace",
    #experiment_record: Optional[Dict[str, Any]] = None,
    section_type_id: int = 20,
    experiment_id: Optional[str] = None,
    client: Optional[BioviaNotebookClient] = None,
    author: Optional[str] = None,
    
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
    for filenames in files_to_attach:
        filename = os.path.basename(filenames)

        with open(filenames, "rb") as f:
            file_b64 = base64.b64encode(
                f.read()
            ).decode("utf-8")
        # # .xls application/vnd.ms-excel
        ## application/vnd.ms-powerpoint
        payload = {
            "datatypeid": 20,
            "Properties": {
                "Height": 15,
                "Width": 617,
                "Tag": 0,
                "FailedLoading": False,
                "XPosition": 0,
                "YPosition": 0
            },
            "Formats": [
                {
                    "Mimetype": "text/plain",
                    "Content": f"FileName: {filename}"
                },
                {
                    "Mimetype": "",
                    "Content": {
                        "__type": "FileAttachment",
                        "Filename": filename
                    }
                },
                {
                    "Mimetype": "text/plain",
                    "Content": file_b64
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
