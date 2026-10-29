from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from service import XMLImportService

router = APIRouter()
logger = logging.getLogger(__name__)

class ParsedFile(BaseModel):
    id: str = Field(..., description="Unique identifier for the parsed file/section, often derived from its path or name.")
    name: str = Field(..., description="Display name of the file/section as extracted from the XML.")
    type: str = Field(..., description="Type of the file (e.g., 'pdf', 'excel', 'word', 'image', 'powerpoint', 'file').")
    file_path: str = Field(..., description="Absolute or relative path to the file on the server/storage, required for import.")
    section_title: Optional[str] = Field(None, description="Optional title to be used for the ELN section.")

class ParseXmlResponse(BaseModel):
    status: str = Field(..., description="Status of the XML parsing operation (e.g., 'success', 'error').")
    message: str = Field(..., description="A descriptive message about the parsing result.")
    files: List[ParsedFile] = Field(..., description="List of files/sections discovered in the XML, ready for user selection.")

class SelectedFile(BaseModel):
    id: str = Field(..., description="The unique identifier of the file selected for import.")
    file_path: str = Field(..., description="The accessible path to the actual file on the server/storage.")
    file_type: str = Field(..., description="The type of the file (e.g., 'pdf', 'excel', 'word', 'image', 'powerpoint', 'file').")
    section_title: Optional[str] = Field(None, description="The title to be used for the ELN section.")

class ImportFilesRequest(BaseModel):
    selected_files: List[SelectedFile] = Field(..., description="A list of files selected by the user to be imported into the ELN.")
    experiment_id: str = Field(..., description="The ID of the target ELN experiment where the files will be imported.")
    client: Optional[str] = Field(None, description="Optional client identifier for ELN connection context.")
    author: Optional[str] = Field(None, description="Optional author for ELN entries.")
    connection_name: Optional[str] = Field(None, description="Optional connection name for ELN to use.")

# class ImportResult(BaseModel):
#     file_id: str = Field(..., description="The ID of the file for which the import was attempted.")
#     success: bool = Field(..., description="Indicates if the import of this specific file was successful.")
#     message: str = Field(..., description="A message describing the outcome for this individual file import.")
class ImportResult(BaseModel):
    experiment_id: str
    section_id: str
    file_name: str
    section_location: str
    attachment_location: str
    status: str

class ImportFilesResponse(BaseModel):
    status: str = Field(..., description="Overall status of the batch import operation (e.g., 'success', 'partial_success', 'error').")
    message: str = Field(..., description="A descriptive message about the overall import result.")
    results: List[ImportResult] = Field(..., description="A list of outcomes for each attempted file import.")

def get_xml_import_service() -> XMLImportService:
    """Dependency injector that provides an instance of XMLImportService."""
    return XMLImportService()

@router.post(
    "/api/custom-filter-(pilotscript)",
    response_model=ParseXmlResponse,
    summary="Upload and parse an XML file to discover extractable files",
    status_code=status.HTTP_200_OK
)
async def parse_xml_upload_endpoint(
    xml_file: UploadFile = File(..., description="The XML file to upload and parse for discoverable files."),
    xml_import_service: XMLImportService = Depends(get_xml_import_service)
):
    print("INSIDE ENDPOINT")
    """
    Accepts an XML file upload, delegates its parsing to the service layer,
    and returns a list of potential files/sections that can be imported into ELN.
    """
    logger.info(f"Received XML upload request for file: {xml_file.filename}")
    try:
        xml_content = await xml_file.read()
        if not xml_content:
            logger.warning("Uploaded XML file is empty.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded XML file is empty.")

        decoded_xml_content = xml_content.decode('utf-8')
        
        service_result: Dict[str, Any] = xml_import_service.parse_uploaded_xml(decoded_xml_content)
        
        parsed_files_data = service_result.get("files", [])
        response_files = [ParsedFile(**f) for f in parsed_files_data]

        return ParseXmlResponse(
            status=service_result.get("status", "success"),
            message=service_result.get("message", "XML parsed successfully."),
            files=response_files
        )
    except ValueError as ve:
        logger.warning(f"Validation error during XML parsing: {ve}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except UnicodeDecodeError as ude:
        logger.error(f"Unicode decode error during XML parsing: {ude}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not decode XML content. Ensure it's valid UTF-8.")
    except RuntimeError as re:
        logger.error(f"Runtime error during XML parsing: {re}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(re))
    except Exception as e:
        logger.exception(f"Unexpected error during XML parsing: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during XML parsing.")
# from fastapi import APIRouter, Request

# @router.post("/api/custom-filter-(pilotscript)")
# async def parse_xml_upload_endpoint(
#     xml_file: UploadFile = File(...)
# ):
#     print("INSIDE ENDPOINT")

#     content = await xml_file.read()

#     print("FILE RECEIVED")
#     print(len(content))

#     return {
#         "files": []
#     }

@router.post(
    "/api/import-files-to-eln",
    response_model=ImportFilesResponse,
    summary="Import selected files into an ELN experiment",
    status_code=status.HTTP_200_OK
)
async def import_selected_files_to_eln_endpoint(
    request: ImportFilesRequest,
    xml_import_service: XMLImportService = Depends(get_xml_import_service)
):
    """
    Receives a list of user-selected files and an ELN experiment ID,
    then delegates the batch import of these files as sections into the specified experiment.
    """
    logger.info(f"Received request to import {len(request.selected_files)} files into ELN experiment ID: {request.experiment_id}")
    if not request.selected_files:
        logger.warning("Import files request received with an empty 'selected_files' list.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files selected for import.")
    
    try:
        service_selected_files_dicts = [file.model_dump() for file in request.selected_files]

        service_result: Dict[str, Any] = xml_import_service.import_files_to_eln(
            selected_files=service_selected_files_dicts,
            experiment_id=request.experiment_id,
            client=request.client,
            author=request.author,
            connection_name=request.connection_name
        )
        
        import_results_data = service_result.get("results", [])
        response_results = [ImportResult(**r) for r in import_results_data]

        return ImportFilesResponse(
            status=service_result.get("status", "success"),
            message=service_result.get("message", "Files imported successfully."),
            results=response_results
        )
    except ValueError as ve:
        logger.warning(f"Validation error during file import: {ve}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except RuntimeError as re:
        logger.error(f"Runtime error during file import: {re}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(re))
    except Exception as e:
        logger.exception(f"Unexpected error during file import: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during file import.")