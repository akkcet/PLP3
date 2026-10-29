"""
Protocol Migration & Component Discovery Engine for Biovia Pipeline Pilot
Analyzes whole protocol XMLs, resolves core component identities regardless of visual renaming,
identifies missing components, categorizes components into:
  - BLUE: Data Manipulator / Processing components (mapped directly to Python codebase)
  - GREEN: Web UI / User Interface generating components (responsible for application rendering)
and synthesizes runnable web application workflows matching original screenshots.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import xml.etree.ElementTree as ET
import re
import os

class PlpComponentRole(str, Enum):
    BLUE_DATA_MANIPULATOR = "BLUE_DATA_MANIPULATOR"  # Translated to Python code
    GREEN_UI_GENERATOR = "GREEN_UI_GENERATOR"        # Responsible for creating the UI of the application


class ComponentStatus(str, Enum):
    REUSABLE_AVAILABLE = "AVAILABLE"
    MISSING = "MISSING"


# Comprehensive registry of all pre-built, reusable Python components in biovia_pipeline
AVAILABLE_REUSABLE_COMPONENTS = {
    # 1. Custom Filter
    "custom_filter": {
        "core_name": "Custom Filter",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{470B2F2A-5A0D-47C0-8FD6-36BDD2C318F8}",
            "CustomFilter",
            "Custom Filter",
        ],
        "aliases": ["gatekeeper", "filter", "condition", "file filter", "pdf filter", "excel filter", "stage filter"],
        "module": "biovia_pipeline.custom_filter",
        "callable": "custom_filter",
        "category": "flow_control",
        "description": "Evaluates PilotScript Boolean filter expressions and gates records through Pass/Fail ports.",
    },
    # 2. Custom Manipulator
    "custom_manipulator": {
        "core_name": "Custom Manipulator",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{3E20B9B6-BC8B-4C03-A2C3-5D7E847C8B56}",
            "CustomManipulator",
            "Custom Manipulator",
        ],
        "aliases": ["manipulator", "calculator", "transformer", "script", "set properties", "format preview"],
        "module": "biovia_pipeline.custom_manipulator",
        "callable": "custom_manipulator",
        "category": "data_manipulation",
        "description": "Executes PilotScript statements to modify record properties, perform string manipulation, and scoping.",
    },
    # 3. Experiment Query
    "experiment_query": {
        "core_name": "Query Experiment",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{A542C30B-7D23-441F-82D0-2B3A4F4E23C1}",
            "ExperimentQuery",
            "Query Experiment",
            "Query Experiment from Notebook",
        ],
        "aliases": ["experiment query", "eln query", "query eln", "fetch experiment", "get experiment"],
        "module": "biovia_pipeline.experiment_query",
        "callable": "query_experiment",
        "category": "eln_integration",
        "description": "Queries Biovia Notebook ELN REST APIs (OData v1) to retrieve experiment metadata and section collections.",
    },
    # 4. Notebook Connection
    "notebook_connection": {
        "core_name": "Notebook Connection",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{9B1E4A32-12C5-4F8A-9871-332D76EF12A0}",
            "NotebookConnection",
            "Notebook Connection",
        ],
        "aliases": ["notebook connection", "eln connection", "auth connection", "login connection", "biovia session"],
        "module": "biovia_pipeline.notebook_connection",
        "callable": "connect_notebook",
        "category": "eln_integration",
        "description": "Initializes authenticated sessions to Biovia Notebook using API tokens or service credentials.",
    },
    # 5. Section Dispatcher
    "section_dispatcher": {
        "core_name": "Section Dispatcher",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{7C8E9F1A-3B2C-4D5E-6F7A-8B9C0D1E2F3A}",
            "SectionDispatcher",
            "Section Dispatcher",
        ],
        "aliases": ["dispatcher", "file type router", "route by extension", "route section"],
        "module": "biovia_pipeline.section_dispatcher",
        "callable": "dispatch_section",
        "category": "flow_control",
        "description": "Inspects incoming document attachment extensions and routes records to dedicated section handlers.",
    },
    # 6. Add Excel Section
    "add_excel_section": {
        "core_name": "Add Excel Section",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{E1F2A3B4-C5D6-4E7F-8A9B-0C1D2E3F4A5B}",
            "AddExcelSection",
            "Add Excel Section",
        ],
        "aliases": ["excel section", "add excel", "spreadsheet section", "xlsx section"],
        "module": "biovia_pipeline.add_excel_section",
        "callable": "add_excel_section",
        "category": "eln_sections",
        "description": "Creates or updates an ELN Excel/Spreadsheet section with sheet preview formatting and column constraints.",
    },
    # 7. Add File Attachment Section
    "add_file_attachment_section": {
        "core_name": "Add File Attachment Section",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{A1B2C3D4-E5F6-4A7B-8C9D-0E1F2A3B4C5D}",
            "AddFileAttachmentSection",
            "Add File Attachment Section",
        ],
        "aliases": ["file attachment", "attachment section", "attach files", "add attachment"],
        "module": "biovia_pipeline.add_file_attachment_section",
        "callable": "add_file_attachment_section",
        "category": "eln_sections",
        "description": "Attaches one or multiple arbitrary binary/text files to a Biovia Notebook experiment section.",
    },
    # 8. Add Image Section
    "add_image_section": {
        "core_name": "Add Image Section",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{B2C3D4E5-F6A7-4B8C-9D0E-1F2A3B4C5D6E}",
            "AddImageSection",
            "Add Image Section",
        ],
        "aliases": ["image section", "add image", "png section", "jpg section", "microscopy image"],
        "module": "biovia_pipeline.add_image_section",
        "callable": "add_image_section",
        "category": "eln_sections",
        "description": "Uploads and renders PNG, JPG, or SVG images directly on the experiment canvas.",
    },
    # 9. Add PDF Section
    "add_pdf_section": {
        "core_name": "Add PDF Section",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{C3D4E5F6-A7B8-4C9D-0E1F-2A3B4C5D6E7F}",
            "AddPdfSection",
            "Add PDF Section",
        ],
        "aliases": ["pdf section", "add pdf", "acrobat section", "report pdf"],
        "module": "biovia_pipeline.add_pdf_section",
        "callable": "add_pdf_section",
        "category": "eln_sections",
        "description": "Attaches PDF documents and configures embedded preview metadata for Notebook viewers.",
    },
    # 10. Add PowerPoint Presentation Section
    "add_powerpoint_section": {
        "core_name": "Add PowerPoint Presentation Section",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{D4E5F6A7-B8C9-4D0E-1F2A-3B4C5D6E7F8A}",
            "AddPowerPointSection",
            "Add PowerPoint Presentation Section",
            "Add PowerPoint Section",
        ],
        "aliases": ["powerpoint section", "add pptx", "presentation section", "powerpoint presentation", "pptx section"],
        "module": "biovia_pipeline.add_powerpoint_section",
        "callable": "add_powerpoint_section",
        "category": "eln_sections",
        "description": "Subprotocol composite that creates and embeds PPTX presentations into experiments.",
    },
    # 11. Add Word Section
    "add_word_section": {
        "core_name": "Add Word Section",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{F5A6B7C8-D9E0-4F1A-2B3C-4D5E6F7A8B9C}",
            "AddWordSection",
            "Add Word Section",
        ],
        "aliases": ["word section", "add docx", "document section", "word document section"],
        "module": "biovia_pipeline.add_word_section",
        "callable": "add_word_section",
        "category": "eln_sections",
        "description": "Uploads and structures DOCX Word documents within the Biovia Notebook experiment.",
    },
    # 12. Extract Sections from Experiment
    "extract_sections": {
        "core_name": "Extract Sections from Experiment",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{E6F7A8B9-C0D1-4E2F-3A4B-5C6D7E8F9A0B}",
            "ExtractSectionsFromExperiment",
            "Extract Sections from Experiment",
            "Extract Sections",
        ],
        "aliases": ["extract sections", "get sections", "filter sections", "section extractor"],
        "module": "biovia_pipeline.extract_sections",
        "callable": "extract_sections",
        "category": "eln_integration",
        "description": "Extracts, filters, and unpacks specific section types from an experiment record.",
    },
    # 13. Subprotocol Container
    "subprotocol": {
        "core_name": "Subprotocol",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{17001C74-63CE-4B4B-B37C-F0EAA19CE4AA}",
            "Subprotocol",
            "Subprotocol Container",
        ],
        "aliases": ["subprotocol", "sub-protocol", "container", "subgraph", "composite", "group"],
        "module": "biovia_pipeline.subprotocol",
        "callable": "run_subprotocol",
        "category": "flow_control",
        "description": "Composite execution container encapsulating child components with parameter promotion and scoping.",
    },
    # 14. Azure Blob Downloader
    "azure_downloader": {
        "core_name": "Azure Blob Downloader",
        "role": PlpComponentRole.BLUE_DATA_MANIPULATOR,
        "guids": [
            "{5B6C7D8E-9F0A-1B2C-3D4E-5F6A7B8C9D0E}",
            "AzureBlobDownloader",
            "Azure Blob Downloader",
        ],
        "aliases": ["azure downloader", "blob downloader", "download azure", "fetch blob"],
        "module": "biovia_pipeline.azure_downloader",
        "callable": "download_blob",
        "category": "storage",
        "description": "Downloads experiment raw data, spectra, or attachments stored in Azure Blob containers.",
    },
}

# Known Green Components (Web UI / Reporting / Interactive Display Builders)
GREEN_UI_COMPONENT_PATTERNS = {
    "web_page_builder": {
        "core_name": "Web Page Builder",
        "guids": ["{8A9B0C1D-2E3F-4A5B-6C7D-8E9F0A1B2C3D}", "WebPageBuilder", "HTMLPageBuilder"],
        "aliases": ["web page", "html page", "application page", "report page", "web report", "dashboard page", "ui builder", "portal"],
        "ui_widget": "web_canvas",
        "description": "Renders the outer HTML container, titles, branding headers, and interactive layout for the web app.",
    },
    "web_form_input": {
        "core_name": "Web Form Input",
        "guids": ["{1A2B3C4D-5E6F-7A8B-9C0D-1E2F3A4B5C6D}", "WebFormInput", "HTMLInput"],
        "aliases": ["web input", "form input", "user input", "text box", "parameter input", "input field", "search box", "experiment input"],
        "ui_widget": "text_input",
        "description": "Generates interactive form input fields for users to enter experiment numbers, parameters, and tokens.",
    },
    "web_file_uploader": {
        "core_name": "Web File Upload",
        "guids": ["{2B3C4D5E-6F7A-8B9C-0D1E-2F3A4B5C6D7E}", "WebFileUpload", "HTMLFileUpload"],
        "aliases": ["file upload", "upload input", "web file upload", "attachment picker", "drag drop upload", "file dropzone"],
        "ui_widget": "file_upload",
        "description": "Generates drag-and-drop file upload zones with multi-file selection for Excel, PDF, Word, and images.",
    },
    "web_data_table": {
        "core_name": "Web Table / Grid Viewer",
        "guids": ["{3C4D5E6F-7A8B-9C0D-1E2F-3A4B5C6D7E8F}", "WebTable", "HTMLTable", "GridViewer"],
        "aliases": ["web table", "html table", "table viewer", "grid view", "results table", "data table", "summary table"],
        "ui_widget": "data_table",
        "description": "Displays tabular experiment sections, parsing status, extracted properties, and processing logs.",
    },
    "web_action_button": {
        "core_name": "Web Action Button / Run Trigger",
        "guids": ["{4D5E6F7A-8B9C-0D1E-2F3A-4B5C6D7E8F9A}", "WebActionButton", "HTMLButton"],
        "aliases": ["run button", "submit button", "execute button", "action button", "trigger", "transfer button"],
        "ui_widget": "action_button",
        "description": "Renders the primary execution trigger button to dispatch the workflow pipeline.",
    },
    "web_status_card": {
        "core_name": "Web Status & Progress Display",
        "guids": ["{5E6F7A8B-9C0D-1E2F-3A4B-5C6D7E8F9A0B}", "WebStatusDisplay", "HTMLStatus"],
        "aliases": ["status display", "progress bar", "toast notification", "alert banner", "badge indicator"],
        "ui_widget": "status_badge",
        "description": "Shows real-time pass/fail status, batch progress, and Notebook connection health.",
    },
}


@dataclass
class ResolvedNode:
    local_id: str
    visual_name: str
    core_name: str
    component_type: str
    is_subprotocol: bool
    status: ComponentStatus
    role: PlpComponentRole
    matched_key: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    pilotscript_code: Optional[str] = None
    incoming_connections: List[str] = field(default_factory=list)
    outgoing_connections: List[str] = field(default_factory=list)
    remediation_note: Optional[str] = None
    ui_widget: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "localId": self.local_id,
            "visualName": self.visual_name,
            "coreName": self.core_name,
            "componentType": self.component_type,
            "isSubprotocol": self.is_subprotocol,
            "status": self.status.value,
            "role": self.role.value,
            "matchedKey": self.matched_key,
            "parameters": self.parameters,
            "pilotscriptCode": self.pilotscript_code,
            "incomingConnections": self.incoming_connections,
            "outgoingConnections": self.outgoing_connections,
            "remediationNote": self.remediation_note,
            "uiWidget": self.ui_widget,
        }


@dataclass
class ProtocolAnalysisResult:
    protocol_name: str
    protocol_version: str
    author: str
    total_nodes: int
    blue_count: int
    green_count: int
    matched_count: int
    missing_count: int
    coverage_percentage: float
    nodes: List[ResolvedNode]
    connections: List[Dict[str, str]]
    declared_globals: Dict[str, Any]
    web_app_schema: Dict[str, Any]
    summary_message: str
    ui_missing_components: List[str] = field(
        default_factory=list
    )

    backend_missing_components: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "protocolName": self.protocol_name,
            "protocolVersion": self.protocol_version,
            "author": self.author,
            "totalNodes": self.total_nodes,
            "blueCount": self.blue_count,
            "greenCount": self.green_count,
            "matchedCount": self.matched_count,
            "missingCount": self.missing_count,
            "coveragePercentage": round(self.coverage_percentage, 1),
            "nodes": [n.to_dict() for n in self.nodes],
            "connections": self.connections,
            "declaredGlobals": self.declared_globals,
            "webAppSchema": self.web_app_schema,
            "summaryMessage": self.summary_message,
        }
def classify_by_component_path(component_path: str):
    path = (component_path or "").lower()

    if (
        "reporting and visualization"
        in path
    ):
        return (
            PlpComponentRole
            .GREEN_UI_GENERATOR
        )

    if (
        "web application development"
        in path
    ):
        return (
            PlpComponentRole
            .GREEN_UI_GENERATOR
        )

    if (
        "html elements"
        in path
    ):
        return (
            PlpComponentRole
            .GREEN_UI_GENERATOR
        )

    if (
        "forms"
        in path
    ):
        return (
            PlpComponentRole
            .GREEN_UI_GENERATOR
        )


    if "web application development" in path:
        return PlpComponentRole.GREEN_UI_GENERATOR

    if "reporting\\" in path:
        return PlpComponentRole.GREEN_UI_GENERATOR

    # if "data access and manipulation" in path:
    #     return PlpComponentRole.BLUE_DATA_MANIPULATOR

    # if "utilities" in path:
    #     return PlpComponentRole.BLUE_DATA_MANIPULATOR

    return None

def match_component(visual_name: str, comp_type: str, component_class: str = "") -> Tuple[ComponentStatus, PlpComponentRole, Optional[str], str, Optional[str]]:
    """
    Dual-layer classifier distinguishing:
      - BLUE (Data Manipulator): checks against AVAILABLE_REUSABLE_COMPONENTS
      - GREEN (UI Generator): checks against GREEN_UI_COMPONENT_PATTERNS
    Returns: (status, role, matched_key, core_name, ui_widget)
    """
    norm_type = (comp_type or "").strip().lower()
    norm_vis = (visual_name or "").strip().lower()
    norm_class = (component_class or "").strip().lower()

    # 1. Check Blue (Data Manipulators) - exact GUIDs
    for key, info in AVAILABLE_REUSABLE_COMPONENTS.items():
        for guid in info["guids"]:
            if guid.lower() == norm_type or guid.lower() == norm_class:
                return ComponentStatus.REUSABLE_AVAILABLE, PlpComponentRole.BLUE_DATA_MANIPULATOR, key, info["core_name"], None

    # 2. Check Green (UI Generators) - exact GUIDs
    for key, info in GREEN_UI_COMPONENT_PATTERNS.items():
        for guid in info["guids"]:
            if guid.lower() == norm_type or guid.lower() == norm_class:
                return ComponentStatus.REUSABLE_AVAILABLE, PlpComponentRole.GREEN_UI_GENERATOR, key, info["core_name"], info["ui_widget"]

    # 3. Check Blue by core_name substring in comp_type
    for key, info in AVAILABLE_REUSABLE_COMPONENTS.items():
        if info["core_name"].lower() in norm_type:
            return ComponentStatus.REUSABLE_AVAILABLE, PlpComponentRole.BLUE_DATA_MANIPULATOR, key, info["core_name"], None

    # 4. Check Green by core_name substring in comp_type or visual_name
    for key, info in GREEN_UI_COMPONENT_PATTERNS.items():
        if info["core_name"].lower() in norm_type or info["core_name"].lower() in norm_vis:
            return ComponentStatus.REUSABLE_AVAILABLE, PlpComponentRole.GREEN_UI_GENERATOR, key, info["core_name"], info["ui_widget"]

    # 5. Check Green by known UI aliases
    for key, info in GREEN_UI_COMPONENT_PATTERNS.items():
        for alias in info["aliases"]:
            if re.search(r'\b' + re.escape(alias) + r'\b', norm_vis) or re.search(r'\b' + re.escape(alias) + r'\b', norm_type):
                return ComponentStatus.REUSABLE_AVAILABLE, PlpComponentRole.GREEN_UI_GENERATOR, key, info["core_name"], info["ui_widget"]

    # 6. Check Blue by known data manipulation aliases
    for key, info in AVAILABLE_REUSABLE_COMPONENTS.items():
        for alias in info["aliases"]:
            if re.search(r'\b' + re.escape(alias) + r'\b', norm_vis) or re.search(r'\b' + re.escape(alias) + r'\b', norm_type):
                return ComponentStatus.REUSABLE_AVAILABLE, PlpComponentRole.BLUE_DATA_MANIPULATOR, key, info["core_name"], None

    # 7. Check Subprotocol container
    if norm_type in ["subprotocol", "sub-protocol"] or "subprotocol" in norm_vis:
        return ComponentStatus.REUSABLE_AVAILABLE, PlpComponentRole.BLUE_DATA_MANIPULATOR, "subprotocol", "Subprotocol", None

    # Not matched in either blue or green catalog -> report as MISSING
    core_guess = comp_type or visual_name or "Unknown Component"
    # Infer likely role: if visual name or type looks like UI, mark as Green, otherwise Blue data manipulator
    is_ui_like = any(term in norm_vis or term in norm_type for term in ["html", "web", "view", "ui", "form", "page", "display", "button", "table"])
    role = PlpComponentRole.GREEN_UI_GENERATOR if is_ui_like else PlpComponentRole.BLUE_DATA_MANIPULATOR

    return ComponentStatus.MISSING, role, None, core_guess, None


def analyze_protocol_xml(xml_content: str) -> ProtocolAnalysisResult:
    """
    Analyzes a complete Biovia Pipeline Pilot protocol XML document.
    Extracts all component nodes, classifies into Blue (data manipulators) vs Green (UI generators),
    resolves core names, detects reusable component availability vs. missing ones,
    and builds the web app UI schema matching the original application.
    """
    clean_xml = xml_content.strip()
    if not clean_xml:
        raise ValueError("Provided XML string is empty.")

    root = ET.fromstring(clean_xml)

    #ns = {"sci": "http://www.scitegic.com/protocol"}
    def get_namespace(root):
        if root.tag.startswith("{"):
            return root.tag.split("}")[0][1:]
        return ""

    ns_uri = get_namespace(root)
    ns = {"sci": ns_uri}
    def find_all(element, path):
        res = element.findall(path, ns)
        if not res:
            res = element.findall(path.replace("sci:", ""))
        return res

    protocol_name = root.attrib.get("name") or "Unnamed Pipeline Pilot Protocol"
    protocol_version = root.attrib.get("version") or "1.0"
    author = root.attrib.get("author") or "Biovia Developer"

    # Extract Declared Globals
    declared_globals = {}
    for arg in find_all(root, ".//sci:protocol/sci:arg") or find_all(root, ".//sci:arg"):
        param_name = arg.attrib.get("name") or arg.attrib.get("id") or ""
        param_val = arg.text or arg.attrib.get("value") or ""
        if param_name and not param_name.startswith("_"):
            declared_globals[param_name] = param_val

    # Find all components/nodes
    #component_elements = find_all(root, ".//sci:component") or root.findall(".//component")
    component_elements = []

    for data_node in root.findall(".//{*}data"):
        component = data_node.find("{*}component")

        if component is not None:
            component_elements.append(
                (data_node, component)
            )
    for data_node, component in component_elements:

        visual_name = component.attrib.get("name", "")

        comp_type = (
            data_node.attrib.get("object")
            or component.attrib.get("type")
            or component.attrib.get("class")
            or visual_name
        )
    resolved_nodes: List[ResolvedNode] = []
    matched_count = 0
    missing_count = 0
    blue_count = 0
    green_count = 0
    ui_missing_components = []
    backend_missing_components = []
    
    # for elem in component_elements:
    #     local_id = elem.attrib.get("localid") or elem.attrib.get("id") or str(len(resolved_nodes) + 1)
    #     visual_name = elem.attrib.get("name") or elem.attrib.get("title") or f"Component {local_id}"
    #     comp_type = elem.attrib.get("type") or elem.attrib.get("class") or visual_name
    for data_node, elem in component_elements:

        local_id = (
            elem.attrib.get("localid")
            or elem.attrib.get("id")
            or str(len(resolved_nodes) + 1)
        )

        visual_name = (
            elem.attrib.get("name")
            or elem.attrib.get("title")
            or f"Component {local_id}"
        )

        comp_type = (
            data_node.attrib.get("object")
            or elem.attrib.get("type")
            or elem.attrib.get("class")
            or visual_name
        )
        is_subp = elem.tag.endswith("subprotocol") or elem.attrib.get("issubprotocol") == "true" or "subprotocol" in comp_type.lower()

        # Parse parameter arguments
        params = {}
        script_code = None
        
        for arg in find_all(elem, ".//sci:arg") or elem.findall(".//arg"):
            p_name = arg.attrib.get("name") or arg.attrib.get("id") or ""
            #p_val = arg.text or arg.attrib.get("value") or ""
            value_node = arg.find("{*}value")

            if value_node is not None:
                p_val = "".join(value_node.itertext()).strip()
            else:
                p_val = "".join(arg.itertext()).strip()
            if p_name:
                params[p_name] = p_val
            if p_name.lower() in ["expression", "script", "pilotscript", "code"]:
                script_code = p_val or arg.text
        component_path = ""
        component_guid = ""

        for arg in find_all(elem, ".//sci:arg") or elem.findall(".//arg"):

            p_name = arg.attrib.get("name") or ""

            value_node = arg.find("{*}value")

            if value_node is not None:
                p_val = "".join(value_node.itertext()).strip()
            else:
                p_val = "".join(arg.itertext()).strip()

            params[p_name] = p_val

            if p_name == "Component Path":
                component_path = p_val

            elif p_name == "ComponentGUID":
                component_guid = p_val
        # Classify & match
        path_role = classify_by_component_path(
            component_path
        )

        if path_role:

            role = path_role

            #
            # Green components are considered
            # reconstructable by the UI generator.
            #
            if role == PlpComponentRole.GREEN_UI_GENERATOR:

                status = (
                    ComponentStatus.REUSABLE_AVAILABLE
                )

                matched_key = (
                    "ui_reconstruction"
                )

                core_name = visual_name

                ui_widget = visual_name

            else:

                status, role, matched_key, core_name, ui_widget = (
                    match_component(
                        visual_name,
                        comp_type,
                        component_guid
                    )
                )

        else:

            status, role, matched_key, core_name, ui_widget = (
                match_component(
                    visual_name,
                    comp_type,
                    component_guid
                )
            )
        #status, role, matched_key, core_name, ui_widget = match_component(visual_name, comp_type, elem.attrib.get("class", ""))

        if role == PlpComponentRole.BLUE_DATA_MANIPULATOR:
            blue_count += 1
        else:
            green_count += 1

        if status == ComponentStatus.REUSABLE_AVAILABLE:

            matched_count += 1

            remediation = None

        else:

            missing_count += 1

            if role == PlpComponentRole.BLUE_DATA_MANIPULATOR:

                backend_missing_components.append(
                    visual_name
                )

                remediation = (
                    f"Blue Data Manipulator '{core_name}' "
                    f"(Visual: '{visual_name}') is not yet "
                    f"available in biovia_pipeline. "
                    f"Needs Python porting or replacement."
                )

            else:

                ui_missing_components.append(
                    visual_name
                )

                remediation = (
                    f"Green UI Component '{core_name}' "
                    f"(Visual: '{visual_name}') will be "
                    f"reconstructed through the UI generation "
                    f"pipeline."
                )

        resolved_node = ResolvedNode(
            local_id=local_id,
            visual_name=visual_name,
            core_name=core_name,
            component_type=comp_type,
            is_subprotocol=is_subp,
            status=status,
            role=role,
            matched_key=matched_key,
            parameters=params,
            pilotscript_code=script_code,
            remediation_note=remediation,
            ui_widget=ui_widget,
        )
        resolved_nodes.append(resolved_node)

    # Connections / Linkage
    connections = []
    for conn in find_all(root, ".//sci:connectid") or root.findall(".//connectid") or root.findall(".//connection"):
        from_id = conn.attrib.get("from") or conn.attrib.get("source") or ""
        to_id = conn.attrib.get("to") or conn.attrib.get("target") or ""
        if from_id and to_id:
            connections.append({"from": from_id, "to": to_id})
            for n in resolved_nodes:
                if n.local_id == from_id:
                    n.outgoing_connections.append(to_id)
                elif n.local_id == to_id:
                    n.incoming_connections.append(from_id)

    total_nodes = len(resolved_nodes)
    coverage = (matched_count / total_nodes * 100.0) if total_nodes > 0 else 0.0

    # Build Reconstructed Web App Schema
    interactive_fields = []
    for node in resolved_nodes:
        vis_low = node.visual_name.lower()
        if node.role == PlpComponentRole.GREEN_UI_GENERATOR or "input" in vis_low or "upload" in vis_low or "experiment" in vis_low or "file" in vis_low:
            if "file" in vis_low or "upload" in vis_low or "attachment" in vis_low:
                interactive_fields.append({
                    "id": f"field_{node.local_id}_file",
                    "label": node.parameters.get("Label") or f"Attach File ({node.visual_name})",
                    "type": "file",
                    "targetNodeId": node.local_id,
                    "paramKey": "FileLocation",
                    "defaultValue": node.parameters.get("FileLocation", "sample_analytical_data.xlsx"),
                    "description": "Upload document to attach into the experiment",
                    "role": "GREEN_UI_GENERATOR",
                })
            elif "experiment" in vis_low or "query" in vis_low or "id" in vis_low:
                exp_default = node.parameters.get("ExperimentNumber", node.parameters.get("ExperimentId", "EXP-2026-XRF-01"))
                interactive_fields.append({
                    "id": f"field_{node.local_id}_exp",
                    "label": node.parameters.get("Label") or f"Experiment ID ({node.visual_name})",
                    "type": "text",
                    "targetNodeId": node.local_id,
                    "paramKey": "ExperimentNumber",
                    "defaultValue": exp_default,
                    "description": "Unique Biovia Notebook experiment identifier or barcode",
                    "role": "GREEN_UI_GENERATOR",
                })
            elif "connection" in vis_low or "auth" in vis_low or "url" in vis_low:
                interactive_fields.append({
                    "id": f"field_{node.local_id}_url",
                    "label": node.parameters.get("Label") or f"Notebook URL ({node.visual_name})",
                    "type": "text",
                    "targetNodeId": node.local_id,
                    "paramKey": "BaseURL",
                    "defaultValue": node.parameters.get("BaseURL", "https://notebook.corp.internal/eln/api/v1"),
                    "description": "Endpoint for target Biovia Notebook deployment",
                    "role": "GREEN_UI_GENERATOR",
                })

    web_app_schema = {
        "title": protocol_name,
        "description": f"Reconstructed Web Application migrated from Biovia Pipeline Pilot protocol '{protocol_name}'",
        "interactiveFields": interactive_fields,
        "executionMode": "Sequential Subprotocol Stream",
        "supportedFormats": ["Excel", "PDF", "Word", "PowerPoint", "Images", "Generic Attachments"],
        "pipelineFlow": [n.visual_name for n in resolved_nodes],
    }

    summary = (
        f"Identified {total_nodes} components ({blue_count} Blue Data Manipulators, {green_count} Green UI Generators). "
        f"{matched_count} matched to reusable modules, {missing_count} missing. Coverage: {coverage:.1f}%."
    )

    return ProtocolAnalysisResult(
        protocol_name=protocol_name,
        protocol_version=protocol_version,
        author=author,
        total_nodes=total_nodes,
        blue_count=blue_count,
        green_count=green_count,
        matched_count=matched_count,
        missing_count=missing_count,
        coverage_percentage=coverage,
        nodes=resolved_nodes,
        connections=connections,
        declared_globals=declared_globals,
        web_app_schema=web_app_schema,
        summary_message=summary,
        ui_missing_components=
            ui_missing_components,

        backend_missing_components=
            backend_missing_components,
    )
