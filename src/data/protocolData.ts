import { PlpComponent, PlpConnection, PlpProtocol } from "../types/pipeline";

export const PLP_COMPONENTS: PlpComponent[] = [
  {
    id: "node_56",
    name: "Delete File (Pre-cleanup)",
    type: "file_op",
    displayName: "Delete File",
    description: "Cleans up previously downloaded temporary files from the local storage folder prior to execution.",
    guid: "{38A20EDC-8D3C-42EF-97BA-D1B40B74FFE0}",
    point: { x: 50, y: 50 },
    parameters: {
      Filename: "E:\\Model Data Transfer\\DownloadedFile",
      Recursive: false,
      "Include Read Only": true,
      "Generate Error on Failure": false,
    },
    mappedPythonFunction: {
      module: "pipeline.file_utils",
      functionName: "cleanup_directory",
      signature: "def cleanup_directory(target_dir: Union[str, Path], recursive: bool = False, ignore_errors: bool = True) -> int:",
      docstring: "Safely removes temporary files in target download directory.",
      code: `def cleanup_directory(target_dir: Union[str, Path], recursive: bool = False, ignore_errors: bool = True) -> int:
    """
    Equivalent to Pipeline Pilot 'Delete File' component (LocalID: 56).
    Cleans up temporary files in target folder before/after pipeline execution.
    """
    path = Path(target_dir)
    deleted_count = 0
    if not path.exists():
        return 0

    try:
        if path.is_file():
            path.unlink()
            return 1
        for item in path.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)
                deleted_count += 1
            elif recursive and item.is_dir():
                shutil.rmtree(item, ignore_errors=ignore_errors)
                deleted_count += 1
    except Exception as exc:
        if not ignore_errors:
            raise RuntimeError(f"Failed cleaning {target_dir}: {exc}") from exc
        logger.warning(f"Directory cleanup warning on {target_dir}: {exc}")
    return deleted_count`,
    },
    threatAnalysis: {
      risk: "Path traversal / arbitrary directory deletion if directory path is unsanitized.",
      countermeasure: "Enforce strict Path.resolve() confinement within allowable sandbox temporary folders.",
    },
  },
  {
    id: "node_59",
    name: "Stage 1 Gatekeeper Filter",
    type: "filter",
    displayName: "Custom Filter: Stage 1 Gatekeeper",
    description: "Pipeline Pilot 'Custom Filter' component taking PLP script expression as argument to check if experiment number is defined and file location is empty.",
    guid: "{DD58ECD1-516F-48FE-A5DB-8328AED680F2}",
    point: { x: 180, y: 150 },
    pilotScript: "@experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''",
    parameters: {
      Expression: "@experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''",
      KeepCalculatedProperties: false,
    },
    mappedPythonFunction: {
      module: "biovia_pipeline.custom_filter",
      functionName: "custom_filter",
      signature: "def custom_filter(expression: str, record: Optional[Dict[str, Any]] = None, globals_dict: Optional[Dict[str, Any]] = None) -> bool:",
      docstring: "Unified function for the Pipeline Pilot 'Custom Filter' component. Takes a PLP script expression as argument and evaluates condition.",
      code: `# Unified Custom Filter Component taking PLP script expression:
passed = custom_filter(
    "@experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''",
    globals_dict={
        "experiment_number": experiment_number,
        "filelocation": file_location or ""
    }
)`,
    },
    threatAnalysis: {
      risk: "Null reference exceptions or empty string bypass in PilotScript condition.",
      countermeasure: "Safe evaluation sandbox with AST transpiler and strict parameter isolation.",
    },
  },
  {
    id: "node_44",
    name: "Stage 2 Gatekeeper Filter",
    type: "filter",
    displayName: "Custom Filter: Stage 2 Gatekeeper",
    description: "Pipeline Pilot 'Custom Filter' component taking PLP script expression to check if XML model export is loaded but file list is pending.",
    guid: "{DD58ECD1-516F-48FE-A5DB-8328AED680F2}",
    point: { x: 180, y: 320 },
    pilotScript: "@xml is defined and @xml ne '' and @filelist is eq ''",
    parameters: {
      Expression: "@xml is defined and @xml ne '' and @filelist is eq ''",
      KeepCalculatedProperties: false,
    },
    mappedPythonFunction: {
      module: "biovia_pipeline.custom_filter",
      functionName: "custom_filter",
      signature: "def custom_filter(expression: str, record: Optional[Dict[str, Any]] = None, globals_dict: Optional[Dict[str, Any]] = None) -> bool:",
      docstring: "Unified function for the Pipeline Pilot 'Custom Filter' component. Takes a PLP script expression as argument.",
      code: `# Unified Custom Filter Component taking PLP script expression:
passed = custom_filter(
    "@xml is defined and @xml ne '' and @filelist is eq ''",
    globals_dict={
        "xml": xml_source or "",
        "filelist": filelist or ""
    }
)`,
    },
  },
  {
    id: "node_22",
    name: "XML Parser Component",
    type: "python",
    displayName: "Python (on Server): Parse Model XML",
    description: "Parses model export XML to extract file names, paths on remote Azure store, and section title.",
    guid: "{6BDAE1C4-8CD8-4bae-B52B-90DE19791B00}",
    point: { x: 340, y: 320 },
    pythonScript: `source_xml_path = context.getComponentParameters().get("Source").getValue().getString().strip()
tree = ET.parse(abs_path)
root = tree.getroot()
for generic in root.findall('generic'):
    eln_value_elem = generic.find('ELN_value')
    # extracts file_name, file_location, section_name`,
    parameters: {
      Source: "xml",
      UsePackage: "scitegic/integration",
    },
    mappedPythonFunction: {
      module: "pipeline.xml_model_parser",
      functionName: "parse_model_xml",
      signature: "def parse_model_xml(xml_content_or_path: Union[str, Path]) -> ModelXmlMetadata:",
      docstring: "Parses instrument/model export XML, extracts generic elements, section title, and remote storage paths.",
      code: `import defusedxml.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

@dataclass
class ModelXmlMetadata:
    section_name: str
    base_location: str
    file_names: List[str]
    file_locations: List[str]
    name_to_location: Dict[str, str]

def parse_model_xml(xml_content_or_path: Union[str, Path]) -> ModelXmlMetadata:
    """
    Translates Pipeline Pilot embedded Python component (LocalID: 22).
    Extracts XML_title, ELN_value paths, and maps files to storage locations safely.
    Defends against XXE (XML External Entity) attacks using defusedxml.
    """
    if isinstance(xml_content_or_path, Path) or (isinstance(xml_content_or_path, str) and Path(xml_content_or_path).is_file()):
        tree = ET.parse(str(xml_content_or_path))
        root = tree.getroot()
    else:
        root = ET.fromstring(str(xml_content_or_path))

    file_names: List[str] = []
    file_locations: List[str] = []
    name_locations: Dict[str, str] = {}
    section_name = ""
    location = ""

    for generic in root.findall("generic"):
        eln_value_elem = generic.find("ELN_value")
        if eln_value_elem is not None and eln_value_elem.text:
            eln_val = eln_value_elem.text.strip()
            if "\\\\" in eln_val or "/" in eln_val:
                # Sanitize path to extract base name
                file_name = Path(eln_val.replace("\\\\", "/")).name
                file_location = eln_val
                name_locations[file_name] = file_location
                file_names.append(file_name)
                file_locations.append(file_location)

                # Extract directory path relative to 'users'
                norm_path = eln_val.replace("\\\\", "/")
                users_idx = norm_path.find("users")
                last_slash = norm_path.rfind("/")
                if users_idx != -1 and last_slash != -1:
                    location = norm_path[users_idx:last_slash]

        xml_title_elem = generic.find("XML_title")
        if xml_title_elem is not None and xml_title_elem.text:
            section_name = xml_title_elem.text.strip()

    return ModelXmlMetadata(
        section_name=section_name,
        base_location=location,
        file_names=file_names,
        file_locations=file_locations,
        name_to_location=name_locations
    )`,
    },
    threatAnalysis: {
      risk: "XXE injection attacks when parsing arbitrary XML files; path traversal inside ELN_value.",
      countermeasure: "Use defusedxml.ElementTree, strip leading directory markers, sanitize file basenames.",
    },
  },
  {
    id: "node_28",
    name: "Section Name Cleaner",
    type: "manipulator",
    displayName: "PilotScript: Clean Section Name",
    description: "Extracts clean section name after colon separator using Substring and FindSubstring.",
    guid: "{0995D675-7EE2-432C-95DF-E91C14052B22}",
    point: { x: 480, y: 320 },
    pilotScript: `@sectionName := Substring(SectionName, FindSubstring(SectionName, ':') + 2, StringLen(SectionName));
@location := location;`,
    parameters: {},
    mappedPythonFunction: {
      module: "pipeline.string_utils",
      functionName: "clean_section_title",
      signature: "def clean_section_title(raw_title: str) -> str:",
      docstring: "Cleans section title by extracting text after the first colon.",
      code: `def clean_section_title(raw_title: str) -> str:
    """
    Translates PilotScript:
    @sectionName := Substring(SectionName, FindSubstring(SectionName, ':')+2, StringLen(SectionName));
    """
    if not raw_title:
        return "Model Import Section"
    if ":" in raw_title:
        parts = raw_title.split(":", 1)
        return parts[1].strip()
    return raw_title.strip()`,
    },
  },
  {
    id: "node_47",
    name: "Stage 3 Execution Trigger Filter",
    type: "filter",
    displayName: "Custom Filter: Files Selected for Execution",
    description: "Pipeline Pilot 'Custom Filter' component taking PLP script expression to verify that filelist is defined and not empty.",
    guid: "{DD58ECD1-516F-48FE-A5DB-8328AED680F2}",
    point: { x: 180, y: 500 },
    pilotScript: "@filelist is defined and @filelist is ne ''",
    parameters: {
      Expression: "@filelist is defined and @filelist is ne ''",
    },
    mappedPythonFunction: {
      module: "biovia_pipeline.custom_filter",
      functionName: "custom_filter",
      signature: "def custom_filter(expression: str, record: Optional[Dict[str, Any]] = None, globals_dict: Optional[Dict[str, Any]] = None) -> bool:",
      docstring: "Unified function for the Pipeline Pilot 'Custom Filter' component. Takes a PLP script expression as argument.",
      code: `# Unified Custom Filter Component taking PLP script expression:
has_files = custom_filter(
    "@filelist is defined and @filelist is ne ''",
    globals_dict={"filelist": selected_files}
)`,
    },
  },
  {
    id: "node_54",
    name: "XML Title Hashtable Extractor",
    type: "python",
    displayName: "Python (on Server): Map XML Titles",
    description: "Builds a hashtable mapping each file name to its specific section XML_title from the model XML.",
    guid: "{6BDAE1C4-8CD8-4bae-B52B-90DE19791B00}",
    point: { x: 340, y: 500 },
    pythonScript: `for generic in root.findall('generic'):
    title = generic.find('XML_title').text
    file_name = os.path.basename(eln_value)
    name_title[file_name] = title
props.defineHashTableProperty("file_xmltitle", name_title)`,
    parameters: {
      Source: "sectiontitle",
    },
    mappedPythonFunction: {
      module: "pipeline.xml_model_parser",
      functionName: "build_filename_to_title_map",
      signature: "def build_filename_to_title_map(xml_content_or_path: Union[str, Path]) -> Dict[str, str]:",
      docstring: "Builds lookup table mapping file basenames to their designated section XML titles.",
      code: `def build_filename_to_title_map(xml_content_or_path: Union[str, Path]) -> Dict[str, str]:
    """
    Translates Python (on Server) LocalID 54:
    Maps filename -> section title for exact ELN section creation.
    """
    if isinstance(xml_content_or_path, Path) or (isinstance(xml_content_or_path, str) and Path(xml_content_or_path).is_file()):
        tree = ET.parse(str(xml_content_or_path))
        root = tree.getroot()
    else:
        root = ET.fromstring(str(xml_content_or_path))

    name_title: Dict[str, str] = {}
    for generic in root.findall("generic"):
        title_elem = generic.find("XML_title")
        eln_elem = generic.find("ELN_value")
        if title_elem is not None and title_elem.text and eln_elem is not None and eln_elem.text:
            file_name = Path(eln_elem.text.strip().replace("\\\\", "/")).name
            name_title[file_name] = title_elem.text.strip()
    return name_title`,
    },
  },
  {
    id: "node_46",
    name: "Azure File Share Downloader",
    type: "python",
    displayName: "Python (on Server): Azure File Share Downloader",
    description: "Connects to Azure Storage File Share and downloads selected model files to local working directory.",
    guid: "{6BDAE1C4-8CD8-4bae-B52B-90DE19791B00}",
    point: { x: 500, y: 500 },
    pythonScript: `from azure.storage.fileshare import ShareServiceClient
service_client = ShareServiceClient(account_url=f"https://{account_name}.file.core.windows.net/", credential=account_key)
share_client = service_client.get_share_client(share_name)
directory_client = share_client.get_directory_client(directory_path)
for file_name in selected_files:
    file_client = directory_client.get_file_client(file_name)
    with open(local_path, "wb") as f:
        f.write(file_client.download_file().readall())`,
    parameters: {
      filesx: "filenames",
      location: "filelocation",
    },
    mappedPythonFunction: {
      module: "pipeline.azure_storage",
      functionName: "AzureFileShareClient",
      signature: "class AzureFileShareClient:\n    def download_files(self, share_name: str, directory_path: str, file_names: List[str], target_dir: Path) -> List[Path]:",
      docstring: "Production-grade Azure File Share client with zero-hardcoded secrets and streaming chunk downloads.",
      code: `import os
import logging
from pathlib import Path
from typing import List, Optional
from azure.storage.fileshare import ShareServiceClient
from azure.core.exceptions import AzureError

logger = logging.getLogger("biovia_pipeline.azure")

class AzureFileShareClient:
    """
    Refactored from Pipeline Pilot Python component LocalID 46.
    IMPORTANT SECURITY UPGRADE:
    Replaces hardcoded account_key in legacy PLP script with environment variable
    or Cloud Secret Manager injection (AZURE_STORAGE_KEY / AZURE_STORAGE_CONNECTION_STRING).
    """
    def __init__(
        self,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
        connection_string: Optional[str] = None
    ):
        self.account_name = account_name or os.getenv("AZURE_STORAGE_ACCOUNT", "bnlwestges01005")
        self.account_key = account_key or os.getenv("AZURE_STORAGE_KEY")
        self.connection_string = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")

        if not self.connection_string and not (self.account_name and self.account_key):
            raise ValueError(
                "Azure Storage credentials missing! Set AZURE_STORAGE_KEY or AZURE_STORAGE_CONNECTION_STRING."
            )

        if self.connection_string:
            self.service_client = ShareServiceClient.from_connection_string(self.connection_string)
        else:
            account_url = f"https://{self.account_name}.file.core.windows.net/"
            self.service_client = ShareServiceClient(account_url=account_url, credential=self.account_key)

    def download_files(
        self,
        share_name: str,
        directory_path: str,
        file_names: List[str],
        destination_dir: Path
    ) -> List[Path]:
        destination_dir.mkdir(parents=True, exist_ok=True)
        downloaded: List[Path] = []

        share_client = self.service_client.get_share_client(share_name)
        # Normalize backslashes to forward slashes for Azure directory client
        norm_dir = directory_path.replace("\\\\", "/").strip("/")
        dir_client = share_client.get_directory_client(norm_dir)

        for file_name in file_names:
            safe_name = Path(file_name).name  # Prevent directory traversal
            local_target = destination_dir / safe_name
            try:
                logger.info(f"Downloading {safe_name} from Azure share '{share_name}/{norm_dir}'...")
                file_client = dir_client.get_file_client(safe_name)
                with open(local_target, "wb") as f_out:
                    stream = file_client.download_file()
                    f_out.write(stream.readall())
                downloaded.append(local_target)
                logger.info(f"Successfully saved {local_target.stat().st_size} bytes to {local_target}")
            except AzureError as err:
                logger.error(f"Failed downloading {file_name} from Azure File Share: {err}")
                raise

        return downloaded`,
    },
    threatAnalysis: {
      risk: "CRITICAL FLAW in original PLP: Account key was hardcoded in cleartext in XML export!",
      countermeasure: "Migrate to AZURE_STORAGE_KEY / Secret Manager; never commit plaintext credentials; validate safe_name filename.",
    },
  },
  {
    id: "node_51",
    name: "Directory Watcher",
    type: "file_op",
    displayName: "Directory Watcher: Enumerate Files",
    description: "Recursively scans downloaded files directory and passes records to downstream subprotocol.",
    guid: "{9E1AC481-78FB-4A63-8A58-2B71A5D367C4}",
    point: { x: 660, y: 500 },
    parameters: {
      Directory: "E:\\Model Data Transfer\\DownloadedFile",
      RecurseDirectories: true,
      FindNewFiles: true,
    },
    mappedPythonFunction: {
      module: "pipeline.file_utils",
      functionName: "scan_download_directory",
      signature: "def scan_download_directory(directory_path: Union[str, Path]) -> List[Path]:",
      docstring: "Scans downloaded directory and returns list of file paths for section dispatch.",
      code: `def scan_download_directory(directory_path: Union[str, Path]) -> List[Path]:
    """
    Translates Pipeline Pilot 'Directory Watcher' component (LocalID: 51).
    Finds all downloaded files ready to be committed as Notebook sections.
    """
    p = Path(directory_path)
    if not p.exists():
        return []
    return [f for f in p.glob("**/*") if f.is_file()]`,
    },
  },
  {
    id: "node_53",
    name: "Section Dispatcher Subprotocol",
    type: "subprotocol",
    displayName: "Subprotocol: Add Sections by File Type",
    description: "Dispatches each file based on extension (.pdf, .xlsx, .ppt/.pptx, .docx, or other) and connects to Biovia Notebook API.",
    guid: "{17001C74-63CE-4B4B-B37C-F0EAA19CE4AA}",
    point: { x: 820, y: 500 },
    pilotScript: `@file_path := DocFilepath; 
@file_name := DocRelativepath;
IF (HashContains(@_xmltitle, DocRelativepath)) THEN
  @sec_title := HashFind(@_xmltitle, DocRelativepath);
END IF;`,
    parameters: {
      RunToCompletion: "True - For Each Data Record",
    },
    mappedPythonFunction: {
      module: "biovia_pipeline.section_dispatcher",
      functionName: "SectionDispatcher.dispatch_file",
      signature: "def dispatch_file(file_path: Path, section_title: Optional[str], experiment_id: str, client: BioviaNotebookClient) -> Dict[str, str]:",
      docstring: "Evaluates each file using the unified custom_filter function with original PLP scripts and calls Notebook section creator.",
      code: `def dispatch_file(file_path: Path, section_title: Optional[str], experiment_id: str, client: BioviaNotebookClient) -> Dict[str, str]:
    """
    Subprotocol router driven by unified 'custom_filter' component function:
    - Component 4 (Custom Filter): custom_filter("findsubstring(DocRelativepath, '.pdf')>1", record) -> Add PDF
    - Component 6 (Custom Filter): custom_filter("findsubstring(DocRelativepath, '.xlsx')>1", record) -> Add Excel
    - Component 14 (Custom Filter): custom_filter("findsubstring(DocRelativepath, '.ppt')>1", record) -> Add PPT
    - Component 19 (Custom Filter): custom_filter("findsubstring(DocRelativepath, '.docx')>1", record) -> Add Word
    - Component 5: Add Attachment (Fallback)
    """
    title = section_title or file_path.stem
    record = {"DocRelativepath": file_path.name}

    if custom_filter("findsubstring(DocRelativepath, '.pdf')>1", record=record):
        sec_type = "pdf"
        sec_id = client.add_pdf_section(experiment_id, title, file_path)
    elif custom_filter("findsubstring(DocRelativepath, '.xlsx')>1", record=record):
        sec_type = "excel"
        sec_id = client.add_excel_section(experiment_id, title, file_path)
    elif custom_filter("findsubstring(DocRelativepath, '.ppt')>1", record=record):
        sec_type = "powerpoint"
        sec_id = client.add_powerpoint_section(experiment_id, title, file_path)
    elif custom_filter("findsubstring(DocRelativepath, '.docx')>1", record=record):
        sec_type = "word"
        sec_id = client.add_word_section(experiment_id, title, file_path)
    else:
        sec_type = "attachment"
        sec_id = client.add_attachment_section(experiment_id, title, file_path)

    return {"fileName": file_path.name, "sectionType": sec_type, "sectionTitle": title, "sectionId": sec_id}`,
    },
    threatAnalysis: {
      risk: "Malicious file extensions, polyglot files, mime-type spoofing.",
      countermeasure: "Validate file extensions and magic headers; quarantine unrecognized formats into safe generic attachment.",
    },
  },
  {
    id: "node_24",
    name: "Biovia Notebook Client & Connection",
    type: "notebook",
    displayName: "Notebook Connection & Update",
    description: "Authenticates via Session Token, queries experiment, executes section additions, and commits update to ELN.",
    guid: "{B81BB235-6C10-4EBA-BB1F-D8261494B7B0}",
    point: { x: 960, y: 500 },
    parameters: {
      AuthenticationMethod: "Use Notebook Session Token",
      ConnectionName: "NotebookConnection",
    },
    mappedPythonFunction: {
      module: "pipeline.biovia_notebook",
      functionName: "BioviaNotebookClient",
      signature: "class BioviaNotebookClient:\n    def __init__(self, base_url: str, session_token: str):",
      docstring: "Biovia Notebook REST API client implementing Experiment Query, Add Section, and Update Notebook.",
      code: `import requests
from pathlib import Path
from typing import Any, Dict, Optional

class BioviaNotebookClient:
    """
    Python replacement for:
    - Notebook Connection (LocalID: 24)
    - Experiment Query (LocalID: 0, 8, 12, 18, 21)
    - Add PDF / Excel / PPT / Word / Attachment Section
    - Update Notebook (LocalID: 3, 10, 14, 19, 22)
    """
    def __init__(self, base_url: str, session_token: str, verify_ssl: bool = True):
        self.base_url = base_url.rstrip("/")
        self.session_token = session_token
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {session_token}",
            "X-Biovia-Session-Token": session_token,
            "Accept": "application/json"
        })

    def query_experiment(self, experiment_number: str) -> Dict[str, Any]:
        """Queries Notebook database for an experiment by experiment number."""
        url = f"{self.base_url}/api/v2/experiments"
        resp = self.session.get(url, params={"number": experiment_number, "status": "Not Submitted"}, verify=self.verify_ssl)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("items"):
            raise ValueError(f"Experiment '{experiment_number}' not found in Biovia Notebook.")
        return data["items"][0]

    def add_pdf_section(self, experiment_id: str, title: str, file_path: Path, preview_pages: int = 5) -> str:
        return self._upload_section_file(experiment_id, "pdf", title, file_path, {"previewPages": preview_pages})

    def add_excel_section(self, experiment_id: str, title: str, file_path: Path) -> str:
        return self._upload_section_file(experiment_id, "excel", title, file_path)

    def add_powerpoint_section(self, experiment_id: str, title: str, file_path: Path) -> str:
        return self._upload_section_file(experiment_id, "powerpoint", title, file_path)

    def add_word_section(self, experiment_id: str, title: str, file_path: Path) -> str:
        return self._upload_section_file(experiment_id, "word", title, file_path)

    def add_attachment_section(self, experiment_id: str, title: str, file_path: Path) -> str:
        return self._upload_section_file(experiment_id, "attachment", title, file_path)

    def _upload_section_file(self, experiment_id: str, section_type: str, title: str, file_path: Path, metadata: Optional[Dict] = None) -> str:
        url = f"{self.base_url}/api/v2/experiments/{experiment_id}/sections"
        with open(file_path, "rb") as f_data:
            files = {"file": (file_path.name, f_data)}
            data = {"type": section_type, "title": title, **(metadata or {})}
            resp = self.session.post(url, data=data, files=files, verify=self.verify_ssl)
            resp.raise_for_status()
            return resp.json().get("sectionId", "")

    def update_notebook(self, experiment_id: str) -> bool:
        """Commits and persists all section additions to Biovia Notebook."""
        url = f"{self.base_url}/api/v2/experiments/{experiment_id}/commit"
        resp = self.session.post(url, json={"action": "update"}, verify=self.verify_ssl)
        resp.raise_for_status()
        return True`,
    },
    threatAnalysis: {
      risk: "Session token leakage in logs; MITM tampering without TLS validation.",
      countermeasure: "Mask tokens in logs; enforce strict HTTPS; verify SSL certificates.",
    },
  },
  {
    id: "node_55",
    name: "Delete File (Post-cleanup)",
    type: "file_op",
    displayName: "Delete File: Post Cleanup",
    description: "Cleans up local downloaded files after successful upload to Biovia Notebook.",
    guid: "{38A20EDC-8D3C-42EF-97BA-D1B40B74FFE0}",
    point: { x: 1100, y: 500 },
    parameters: {
      Filename: "E:\\Model Data Transfer\\DownloadedFile",
      Recursive: true,
    },
    mappedPythonFunction: {
      module: "pipeline.file_utils",
      functionName: "cleanup_directory",
      signature: "def cleanup_directory(target_dir: Union[str, Path]) -> int:",
      docstring: "Post-execution cleanup of temporary files.",
      code: `# Re-uses pipeline.file_utils.cleanup_directory`,
    },
  },
];

export const PLP_CONNECTIONS: PlpConnection[] = [
  { from: "node_56", to: "node_59", type: "pass" },
  { from: "node_59", to: "node_44", type: "pass" },
  { from: "node_44", to: "node_22", type: "pass" },
  { from: "node_22", to: "node_28", type: "pass" },
  { from: "node_28", to: "node_47", type: "pass" },
  { from: "node_47", to: "node_54", type: "pass" },
  { from: "node_54", to: "node_46", type: "pass" },
  { from: "node_46", to: "node_51", type: "pass" },
  { from: "node_51", to: "node_53", type: "pass" },
  { from: "node_53", to: "node_24", type: "pass" },
  { from: "node_24", to: "node_55", type: "pass" },
];

export const SAMPLE_INPUT_XML = `<?xml version="1.0" encoding="UTF-8"?>
<root>
    <generic>
        <XML_title>Spectroscopy: Quantitative Analysis Report</XML_title>
        <ELN_value>users\\arun.khuntia\\experiments\\EXP-2026-XRF\\Quant_Analysis_Summary.pdf</ELN_value>
    </generic>
    <generic>
        <XML_title>Calibration: Standards Curve &amp; Regression</XML_title>
        <ELN_value>users\\arun.khuntia\\experiments\\EXP-2026-XRF\\Calibration_Curves.xlsx</ELN_value>
    </generic>
    <generic>
        <XML_title>Review Presentation: Formulation Deck</XML_title>
        <ELN_value>users\\arun.khuntia\\experiments\\EXP-2026-XRF\\Project_Milestone.pptx</ELN_value>
    </generic>
    <generic>
        <XML_title>Study Protocol: Method Validation</XML_title>
        <ELN_value>users\\arun.khuntia\\experiments\\EXP-2026-XRF\\Method_Validation_SOP.docx</ELN_value>
    </generic>
    <generic>
        <XML_title>Raw Spectral Data: Emission Readings</XML_title>
        <ELN_value>users\\arun.khuntia\\experiments\\EXP-2026-XRF\\Raw_Spectral_Readings.dat</ELN_value>
    </generic>
</root>`;
