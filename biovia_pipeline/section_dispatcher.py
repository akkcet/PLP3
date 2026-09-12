"""
Section Dispatcher replacing PLP Subprotocol 'Section Router' (LocalID 53).
Routes downloaded files to appropriate Biovia Notebook section creators based on extension.
"""
from pathlib import Path
from typing import Dict, Optional
from .custom_filter import custom_filter
from .biovia_notebook import BioviaNotebookClient


class SectionDispatcher:
    """
    Evaluates file extension using the unified custom_filter function with the original PLP scripts.
    Replaces PLP Subprotocol containing LocalIDs: 4, 1, 6, 9, 14, 15, 19, 20, 5.
    """

    @staticmethod
    def dispatch_file(
        file_path: Path,
        section_title: Optional[str],
        experiment_id: str,
        client: BioviaNotebookClient
    ) -> Dict[str, str]:
        title = section_title or file_path.stem
        record = {"DocRelativepath": str(file_path.name)}

        # Component 4: Custom Filter (PLP Script: findsubstring(DocRelativepath, '.pdf')>1)
        if custom_filter("findsubstring(DocRelativepath, '.pdf')>1", record=record):
            # PLP Component 1: Add PDF Section
            sec_type = "pdf"
            sec_id = client.add_pdf_section(experiment_id, title, file_path)

        # Component 6: Custom Filter (PLP Script: findsubstring(DocRelativepath, '.xlsx')>1)
        elif custom_filter("findsubstring(DocRelativepath, '.xlsx')>1", record=record) or custom_filter("findsubstring(DocRelativepath, '.xls')>1", record=record):
            # PLP Component 9: Add Excel Section
            sec_type = "excel"
            sec_id = client.add_excel_section(experiment_id, title, file_path)

        # Component 14: Custom Filter (PLP Script: findsubstring(DocRelativepath, '.ppt')>1)
        elif custom_filter("findsubstring(DocRelativepath, '.ppt')>1", record=record):
            # PLP Component 15: Add PowerPoint Section
            sec_type = "powerpoint"
            sec_id = client.add_powerpoint_section(experiment_id, title, file_path)

        # Component 19: Custom Filter (PLP Script: findsubstring(DocRelativepath, '.docx')>1)
        elif custom_filter("findsubstring(DocRelativepath, '.docx')>1", record=record) or custom_filter("findsubstring(DocRelativepath, '.doc')>1", record=record):
            # PLP Component 20: Add Word Section
            sec_type = "word"
            sec_id = client.add_word_section(experiment_id, title, file_path)

        else:
            # PLP Component 5: Add Attachment (Fallback for all non-matched file types)
            sec_type = "attachment"
            sec_id = client.add_attachment_section(experiment_id, title, file_path)

        return {
            "fileName": file_path.name,
            "sectionType": sec_type,
            "sectionTitle": title,
            "sectionId": sec_id
        }

