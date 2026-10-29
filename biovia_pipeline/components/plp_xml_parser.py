"""
Biovia Pipeline Pilot Protocol XML Parser & Python Function Mapper
Parses SciTegic PLP XML export files and maps components directly to modular Python functions.
"""
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .pilotscript_parser import PilotScriptParser


@dataclass
class PlpArgument:
    name: str
    arg_type: str
    value: Optional[str] = None
    legalval_selected: Optional[str] = None


@dataclass
class PlpComponent:
    local_id: str
    name: str
    version: str
    arguments: Dict[str, PlpArgument] = field(default_factory=dict)
    subcomponents: List["PlpComponent"] = field(default_factory=list)
    mapped_python_function: Optional[str] = None
    mapped_python_module: Optional[str] = None
    generated_python_code: Optional[str] = None


class PlpProtocolXmlParser:
    """
    Parses Biovia Pipeline Pilot XML protocols and maps components to Python modules.
    """

    COMPONENT_MAP = {
        "Delete File": {
            "module": "biovia_pipeline.file_utils",
            "function": "cleanup_directory",
            "description": "Purges temporary staging folder before/after download"
        },
        "Custom Filter": {
            "module": "biovia_pipeline.custom_filter",
            "function": "custom_filter",
            "description": "Unified function for Custom Filter component; takes a PLP script expression as argument to filter records"
        },
        "Custom Manipulator": {
            "module": "biovia_pipeline.custom_manipulator",
            "function": "custom_manipulator",
            "description": "Unified function executing PLP PilotScript expression to manipulate record properties or globals"
        },
        "Custom Manipulator (PilotScript)": {
            "module": "biovia_pipeline.custom_manipulator",
            "function": "custom_manipulator",
            "description": "Applies a PilotScript expression to each data record or global property"
        },
        "Notebook Connection": {
            "module": "biovia_pipeline.notebook_connection",
            "function": "notebook_connection",
            "description": "Establishes authenticated session connection object with Biovia Notebook REST API"
        },
        "Experiment Query": {
            "module": "biovia_pipeline.experiment_query",
            "function": "experiment_query",
            "description": "Queries Biovia Notebook database for experiments matching criteria via Notebook Connection"
        },
        "Python (on Server)": {
            "module": "biovia_pipeline.xml_model_parser",
            "function": "parse_model_xml",
            "description": "Parses model export XML or runs Azure downloader"
        },
        "Directory Watcher": {
            "module": "biovia_pipeline.file_utils",
            "function": "scan_download_directory",
            "description": "Recursively scans downloaded files in staging folder"
        },
        "Subprotocol": {
            "module": "biovia_pipeline.section_dispatcher",
            "function": "SectionDispatcher.dispatch_file",
            "description": "Routes file by extension to corresponding Biovia Notebook section creator"
        },
        "Notebook Connection": {
            "module": "biovia_pipeline.biovia_notebook",
            "function": "BioviaNotebookClient.__init__",
            "description": "Establishes authenticated REST session with Biovia Notebook ELN"
        },
        "Add PDF Section": {
            "module": "biovia_pipeline.biovia_notebook",
            "function": "BioviaNotebookClient.add_pdf_section",
            "description": "Creates PDF section with page preview in Biovia Notebook"
        },
        "Add Excel Section": {
            "module": "biovia_pipeline.biovia_notebook",
            "function": "BioviaNotebookClient.add_excel_section",
            "description": "Creates Excel spreadsheet section with table preview in Biovia Notebook"
        },
        "Add PowerPoint Section": {
            "module": "biovia_pipeline.biovia_notebook",
            "function": "BioviaNotebookClient.add_powerpoint_section",
            "description": "Creates PowerPoint slide section in Biovia Notebook"
        },
        "Add Word Section": {
            "module": "biovia_pipeline.biovia_notebook",
            "function": "BioviaNotebookClient.add_word_section",
            "description": "Creates Word document section in Biovia Notebook"
        },
        "Add Attachment": {
            "module": "biovia_pipeline.biovia_notebook",
            "function": "BioviaNotebookClient.add_attachment_section",
            "description": "Creates generic attachment section for raw data files"
        },
        "Update Notebook": {
            "module": "biovia_pipeline.biovia_notebook",
            "function": "BioviaNotebookClient.update_notebook",
            "description": "Commits transaction and finalizes experiment changes in ELN"
        },
    }

    def __init__(self, xml_source: Union[str, Path]):
        self.xml_source = xml_source
        self.components: List[PlpComponent] = []

    def parse(self) -> List[PlpComponent]:
        if isinstance(self.xml_source, Path) or (isinstance(self.xml_source, str) and Path(self.xml_source).is_file()):
            tree = ET.parse(str(self.xml_source))
            root = tree.getroot()
        else:
            root = ET.fromstring(str(self.xml_source))

        self.components = []
        for elem in root:
            if elem.tag.endswith("component"):
                comp = self._parse_component(elem)
                self.components.append(comp)

        return self.components

    def _parse_component(self, elem: ET.Element) -> PlpComponent:
        local_id = elem.attrib.get("localid", "")
        name = elem.attrib.get("name", "")
        version = elem.attrib.get("version", "1")

        args: Dict[str, PlpArgument] = {}
        for child in elem:
            if child.tag.endswith("arg"):
                arg_name = child.attrib.get("name", "")
                arg_type = child.attrib.get("type", "")

                val_elem = child.find("{*}value")
                if val_elem is None:
                    val_elem = child.find("sci:value", {"sci": "http://www.scitegic.com"})
                if val_elem is None:
                    val_elem = child.find("value")

                legalval_elem = child.find("{*}legalval")
                if legalval_elem is None:
                    legalval_elem = child.find("sci:legalval", {"sci": "http://www.scitegic.com"})
                if legalval_elem is None:
                    legalval_elem = child.find("legalval")

                val_text = val_elem.text.strip() if val_elem is not None and val_elem.text else None
                legal_text = legalval_elem.text.strip() if legalval_elem is not None and legalval_elem.text else None

                args[arg_name] = PlpArgument(
                    name=arg_name,
                    arg_type=arg_type,
                    value=val_text,
                    legalval_selected=legal_text
                )

        # Parse nested subprotocol if present
        subcomponents: List[PlpComponent] = []
        subproto = elem.find("{*}subprotocol")
        if subproto is None:
            subproto = elem.find("sci:subprotocol", {"sci": "http://www.scitegic.com"})
        if subproto is None:
            subproto = elem.find("subprotocol")

        if subproto is not None:
            for sub_elem in subproto:
                if sub_elem.tag.endswith("component"):
                    subcomponents.append(self._parse_component(sub_elem))

        mapping = self.COMPONENT_MAP.get(name, {})
        py_module = mapping.get("module")
        py_func = mapping.get("function")

        # Refine mapping if this is embedded Python
        if name == "Python (on Server)":
            script_arg = args.get("Script")
            if script_arg and script_arg.value and "ShareServiceClient" in script_arg.value:
                py_module = "biovia_pipeline.azure_downloader"
                py_func = "AzureFileShareDownloader.download_selected_files"
            elif script_arg and script_arg.value and "XML_title" in script_arg.value:
                py_module = "biovia_pipeline.xml_model_parser"
                py_func = "parse_model_xml"

        # Generate Python snippet
        gen_code = None
        if name == "Custom Filter":
            expr_arg = args.get("Expression")
            expr_val = expr_arg.value if expr_arg and expr_arg.value else ""
            gen_code = (
                f"# Single function for Custom Filter component taking PLP script as argument\n"
                f"passed = custom_filter({repr(expr_val)}, record=record, globals_dict=globals_dict)"
            )
        elif name == "Custom Manipulator":
            expr_arg = args.get("Expression")
            if expr_arg and expr_arg.value:
                gen_code = PilotScriptParser(expr_arg.value).transpile_to_python()

        return PlpComponent(
            local_id=local_id,
            name=name,
            version=version,
            arguments=args,
            subcomponents=subcomponents,
            mapped_python_function=py_func,
            mapped_python_module=py_module,
            generated_python_code=gen_code
        )
