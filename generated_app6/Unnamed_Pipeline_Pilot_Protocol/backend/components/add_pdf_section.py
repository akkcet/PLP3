import logging
import os
from pathlib import Path
from typing import Optional, Union, Dict, Any
import base64
from .notebook_connection import (
    NotebookConnectionObject,
    notebook_connection
)
from .experiment_query import experiment_query

logger = logging.getLogger("biovia_pipeline.experiment_attachment")


def add_attachment_to_experiment(
    connection_name: Union[NotebookConnectionObject, str],
    experiment_id: str,
    pdf_file: str,
    section_name: str = "Attachments",
    section_type_id: int = 29,
    author: str = None,
    client: str = None,
) -> Dict[str, Any]:
    """
    Creates a new section in an experiment and uploads a file attachment.

    Steps:
        1. Create section
        2. Upload file into section
        3. Return created identifiers

    Parameters
    ----------
    connection:
        Notebook connection object or connection name.

    experiment_id:
        Experiment document id.

    pdf_file:
        Local file path to upload.

    section_name:
        Name of section to create.

    section_type_id:
        Attachment/File section type.
    """

    # ---------------------------------------------------------
    # Resolve connection
    # ---------------------------------------------------------

    if isinstance(connection_name, str):
        conn_obj = notebook_connection(connection_name=connection_name)
    else:
        conn_obj = connection_name

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
        "title": section_name,
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
    # logger.info("=" * 80)
    # logger.info("STATUS: %s", section_response.status_code)
    # logger.info("HEADERS: %s", dict(section_response.headers))
    # logger.info("BODY: %s", section_response.text)
    # logger.info("=" * 80)
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

    filename = os.path.basename(pdf_file)
    with open(pdf_file, "rb") as f:
        pdf_content = base64.b64encode(f.read()).decode("utf-8")
        payload = {
            "datatypeid": 27,
            "Formats": [
                {
                    "Mimetype": "application/pdf",
                    "Content": pdf_content
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
    # with open(pdf_file, "rb") as f:

    #     files = {
    #         "file": (
    #             filename,
    #             f,
    #             "application/octet-stream"
    #         )
    #     }

    #     upload_response = conn_obj.session.post(
    #         upload_url,
    #         files=files,
    #         timeout=300
    #     )

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

# conn = notebook_connection(
#     server_url="https://notebook.unilever.com",
#     authentication_method=
#         "Use Username and Password Parameters",
#     username="arun.khuntia",
#     password="Pogoanaisha321!",)

# print(conn.session_token)
# print(conn.api_endpoint)

# experiments = experiment_query(
#     connection=conn,
#     filter_by="Experiment Number",
#     filter_type="Equals",
#     filter_value="EXP-26-BP7567"
# )

#print(experiments)
############################# to create a section with given title##########
# payload = {
#     "sectiontypeid": 29,
#     "title": "AI PLP:"
# }

# response = conn.session.post(
#     f"{conn.api_endpoint}/sections?documentid=160296",
#     json=payload,
#     headers={
#         "Accept": "application/json",
#         "Content-Type": "application/json"
#     }
# )

# print(response.status_code)
# print(response.text)
# print(response.headers)
####################################################

# section_id = 3613786

# # from pathlib import Path

# pdf_file = Path(__file__).parent / "LLD-Scinet.pdf"



# import base64

# with open(pdf_file, "rb") as f:
#     pdf_content = base64.b64encode(f.read()).decode("utf-8")

# payload = {
#     "datatypeid": 27,
#     "Formats": [
#         {
#             "Mimetype": "application/pdf",
#             "Content": pdf_content
#         }
#     ]
# }

# response = conn.session.post(
#     f"{conn.api_endpoint}/sections/{section_id}/data",
#     json=payload,
#     headers={
#         "Accept": "application/json",
#         "Content-Type": "application/json"
#     }
# )

# print(response.status_code)
# print(response.text)
# print(response.headers)


