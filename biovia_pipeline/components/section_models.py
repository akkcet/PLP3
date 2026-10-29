"""
Data structures and models representing Biovia Notebook ELN sections.
Mirrors Pipeline Pilot internal Section records and XML node serialization structures.
"""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json
import uuid


class SectionType(str, Enum):
    EXCEL = "Excel Worksheet"
    FILE_ATTACHMENT = "File Attachment"
    IMAGE = "Image"
    PDF = "PDF Document"
    WORD = "Word Document"
    POWERPOINT = "PowerPoint Presentation"
    BODY_TEXT = "Body Text"


# Section Type mapping to PLP SectionTypeID (from 'Extract Sections from Experiment')
PLP_SECTION_TYPE_IDS: Dict[str, int] = {
    "RichText": 0,
    "AnsiText": 1,
    "Date": 2,
    "ExperimentTitle": 3,
    "ExperimentNumber": 4,
    "ProjectReference": 5,
    "Project": 5,
    "ExperimentCreationDate": 6,
    "ExperimentAuthor": 7,
    "ExperimentType": 8,
    "Experiment Type": 8,
    "ChemicalSketch": 9,
    "Chemical Sketch": 9,
    "Excel": 10,
    "Excel Worksheet": 10,
    "Image": 11,
    "ExperimentReference": 12,
    "Related Experiments": 12,
    "AccordForExcel": 18,
    "AutomaticPagebreak": 19,
    "FileAttachment": 20,
    "File Attachment": 20,
    "ManualPageBreak": 21,
    "Page Break": 21,
    "PartFooter": 22,
    "ExperimentProjectReference": 23,
    "SiteSpecificLookupSection": 24,
    "FormattedText": 25,
    "Text Field": 25,
    "LocalLookup": 26,
    "Errata": 27,
    "Errata Section": 27,
    "ChemicalReaction": 28,
    "Chemical Reaction": 28,
    "PDF": 29,
    "PDF Document": 29,
    "RDC": 30,
    "PPP": 31,
    "Body Text": 32,
    "AdvancedRichText": 32,
    "SDFile": 33,
    "CombiChem": 34,
    "Numeric": 36,
    "Word": 37,
    "Word Document": 37,
    "PowerPoint Presentation": 39,
    "PowerPoint": 39,
}


class SectionAction(str, Enum):
    REPLACE = "Replace"
    APPEND = "Append"


@dataclass
class ExcelPreviewConfig:
    preview_mode: str = "Generate from Excel File Content"  # or "Use Custom Image"
    columns_to_preview: int = 2
    rows_to_preview: int = 3
    column_preview_width: int = 120
    row_preview_height: int = 20
    custom_image: Optional[str] = None

    def validate(self) -> None:
        if self.columns_to_preview >= 8:
            raise ValueError(f"Number of Columns to Preview ({self.columns_to_preview}) must be less than 8 (per PLP specification).")
        if self.rows_to_preview < 1:
            raise ValueError(f"Number of Rows to Preview must be at least 1.")


@dataclass
class ElnSectionRecord:
    """
    In-memory representation of an ELN Section record in Pipeline Pilot.
    Created by 'Create New Section' and edited by 'Edit <Type> Section'.
    """
    section_id: str
    section_title: str
    section_type: SectionType
    files: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    author: Optional[str] = None
    index_in_document: Optional[int] = None
    connection_name: str = "Connection1"

    def to_serialized_node(self) -> Dict[str, Any]:
        """
        Emulates PLP PilotScript statement:
          @serial := nodeserialize(dataroot());
          #n := nodeappendchild(dataroot(), @serial);
          nodeproperty(#n, 'connectionname') := connectionname;
          nodeproperty(#n, 'ref') := ref;
        """
        return {
            "sectionId": self.section_id,
            "sectionTitle": self.section_title,
            "sectionType": self.section_type.value,
            "files": self.files,
            "metadata": self.metadata,
            "connectionName": self.connection_name,
            "author": self.author,
            "ref": f"sec-ref-{self.section_id}",
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.section_id,
            "title": self.section_title,
            "sectionType": self.section_type.value,
            "files": self.files,
            "metadata": self.metadata,
            "author": self.author,
            "indexInDocument": self.index_in_document,
            "connectionName": self.connection_name,
        }
