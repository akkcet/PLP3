"""
Section Dispatcher replacing PLP Subprotocol 'Section Router' (LocalID 53).
Routes downloaded files to appropriate Biovia Notebook section creators based on extension.
Reuses the unified 'custom_filter' component.
"""
from pathlib import Path
from typing import Any, Dict, Optional, Union
from .custom_filter import custom_filter
from .biovia_notebook import BioviaNotebookClient


class SectionDispatcher:
    """
    Evaluates file extension using the unified custom_filter function with the original PLP scripts.
    Replaces PLP Subprotocol containing LocalIDs: 4, 1, 6, 9, 14, 15, 19, 20, 5.
    """

    @staticmethod
    def classify_file(file_name: str) -> Dict[str, Any]:
        """
        Classifies a file based on PLP Custom Filter expressions without requiring an active ELN client.
        """
        record = {"DocRelativepath": file_name}
        if custom_filter("findsubstring(DocRelativepath, '.pdf')>1", record=record):
            return {"file_name": file_name, "section_type": "pdf", "component_id": 48}
        elif custom_filter("findsubstring(DocRelativepath, '.xlsx')>1", record=record) or custom_filter("findsubstring(DocRelativepath, '.xls')>1", record=record):
            return {"file_name": file_name, "section_type": "excel", "component_id": 51}
        elif custom_filter("findsubstring(DocRelativepath, '.ppt')>1", record=record):
            return {"file_name": file_name, "section_type": "powerpoint", "component_id": 49}
        elif custom_filter("findsubstring(DocRelativepath, '.docx')>1", record=record) or custom_filter("findsubstring(DocRelativepath, '.doc')>1", record=record):
            return {"file_name": file_name, "section_type": "word", "component_id": 50}
        else:
            return {"file_name": file_name, "section_type": "attachment", "component_id": 52}

    @classmethod
    def dispatch_file(
        cls,
        file_path: Union[Path, str, Dict[str, Any]],
        section_title: Optional[str] = None,
        experiment_id: str = "EXP-DEFAULT-01",
        client: Optional[BioviaNotebookClient] = None
    ) -> Dict[str, Any]:
        """
        Dispatches a file to the appropriate ELN section creator using PLP Custom Filter rules.
        """
        # Support dict format e.g. {"file_name": "x.pdf", "section_title": "..."}
        if isinstance(file_path, dict):
            fn = file_path.get("file_name") or file_path.get("DocRelativepath") or "file.dat"
            title = section_title or file_path.get("section_title") or Path(fn).stem
            p_obj = Path(fn)
        else:
            p_obj = Path(file_path)
            title = section_title or p_obj.stem

        eln_client = client or BioviaNotebookClient(mock_mode=True)
        classification = cls.classify_file(p_obj.name)
        sec_type = classification["section_type"]
        comp_id = classification["component_id"]

        if sec_type == "pdf":
            sec_id = eln_client.add_pdf_section(experiment_id, title, p_obj)
        elif sec_type == "excel":
            sec_id = eln_client.add_excel_section(experiment_id, title, p_obj)
        elif sec_type == "powerpoint":
            sec_id = eln_client.add_powerpoint_section(experiment_id, title, p_obj)
        elif sec_type == "word":
            sec_id = eln_client.add_word_section(experiment_id, title, p_obj)
        else:
            sec_id = eln_client.add_attachment_section(experiment_id, title, p_obj)

        return {
            "fileName": p_obj.name,
            "section_type": sec_type,
            "sectionType": sec_type,
            "sectionTitle": title,
            "sectionId": sec_id,
            "component_id": comp_id
        }
