"""
Model and Instrument Export XML Parser
Extracts <generic> data items, ELN file paths, and section titles safely.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Union
import xml.etree.ElementTree as ET


@dataclass
class ModelFileItem:
    file_name: str
    file_location: str
    section_title: str
    extension: str


@dataclass
class ModelXmlMetadata:
    section_name: str
    base_location: str
    files: List[ModelFileItem] = field(default_factory=list)
    filename_to_title: Dict[str, str] = field(default_factory=dict)
    filename_to_location: Dict[str, str] = field(default_factory=dict)

    @property
    def file_names(self) -> List[str]:
        return [f.file_name for f in self.files]


def parse_model_xml(xml_source: Union[str, Path]) -> ModelXmlMetadata:
    """
    Parses model export XML, extracting generic files, paths, and section titles.
    Supports both <generics><generic>...</generic></generics> format from Pipeline Pilot
    and <Files><File> format.
    """
    if isinstance(xml_source, Path) or (isinstance(xml_source, str) and Path(xml_source).is_file()):
        tree = ET.parse(str(xml_source))
        root = tree.getroot()
    else:
        root = ET.fromstring(str(xml_source))

    files: List[ModelFileItem] = []
    name_to_title: Dict[str, str] = {}
    name_to_location: Dict[str, str] = {}
    section_name = root.attrib.get("SectionName") or root.attrib.get("section_name") or ""
    base_location = root.attrib.get("BaseLocation") or root.attrib.get("base_location") or ""

    # Check for <generic> elements (Pipeline Pilot default)
    generics = list(root.iter("generic"))
    if generics:
        for generic in generics:
            eln_elem = generic.find("ELN_value")
            title_elem = generic.find("XML_title")

            title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Untitled Section"
            if not section_name:
                section_name = title

            if eln_elem is not None and eln_elem.text:
                raw_path = eln_elem.text.strip()
                norm_path = raw_path.replace("\\", "/")
                parts = [p for p in norm_path.split("/") if p]
                file_name = parts[-1] if parts else raw_path

                if not base_location:
                    users_pos = norm_path.find("users")
                    last_slash = norm_path.rfind("/")
                    if users_pos != -1 and last_slash != -1:
                        base_location = norm_path[users_pos:last_slash]

                ext = Path(file_name).suffix.lower()
                files.append(ModelFileItem(file_name=file_name, file_location=raw_path, section_title=title, extension=ext))
                name_to_title[file_name] = title
                name_to_location[file_name] = raw_path

    # Fallback / alternate schema check: <File Name="..." Extension="..." Title="..." />
    if not files:
        for f_elem in root.iter("File"):
            fn = f_elem.attrib.get("Name") or f_elem.attrib.get("name") or "file.dat"
            title = f_elem.attrib.get("Title") or f_elem.attrib.get("title") or Path(fn).stem
            ext = f_elem.attrib.get("Extension") or Path(fn).suffix.lstrip(".")
            if not ext.startswith("."):
                ext_with_dot = f".{ext}"
            else:
                ext_with_dot = ext
            loc = f_elem.attrib.get("Location") or f"{base_location}/{fn}" if base_location else fn
            files.append(ModelFileItem(file_name=fn, file_location=loc, section_title=title, extension=ext_with_dot))
            name_to_title[fn] = title
            name_to_location[fn] = loc

    return ModelXmlMetadata(
        section_name=section_name or "Spectroscopy Data Model",
        base_location=base_location or "users/arun.khuntia/experiments",
        files=files,
        filename_to_title=name_to_title,
        filename_to_location=name_to_location,
    )
