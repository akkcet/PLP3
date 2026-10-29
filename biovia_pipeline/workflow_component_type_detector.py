# workflow_component_type_detector.py

from dataclasses import dataclass
from typing import Dict, List, Optional


# ============================================================
# MODELS
# ============================================================

@dataclass
class ComponentTypeResult:

    component_name: str

    component_type: str

    confidence: float

    matched_keyword: Optional[str] = None


# ============================================================
# DETECTOR
# ============================================================

class WorkflowComponentTypeDetector:

    """
    Identifies the logical type of a PLP component.

    Examples:

    Experiment Query  -> QUERY
    Notebook Connection -> CONNECTION
    Custom Filter -> PILOTSCRIPT
    Add PDF Section -> ELN_SECTION
    File Chooser -> UI
    """

    PILOTSCRIPT_TYPES = [

        "custom filter",

        "custom manipulator",

        "pilotscript",

        "expression",

        "condition"
    ]

    CONNECTION_TYPES = [

        "notebook connection",

        "connection",

        "database connection"
    ]

    QUERY_TYPES = [

        "experiment query",

        "query",

        "search"
    ]

    ELN_SECTION_TYPES = [

        "add pdf section",

        "add excel section",

        "add word section",

        "add image section",

        "add powerpoint section",

        "extract sections"
    ]

    UI_TYPES = [

        "file chooser",

        "submit button",

        "input form",

        "list box",

        "html template",

        "bootstrap form group",

        "tile horizontal",

        "tile vertical",

        "product wizard page"
    ]

    FILE_TYPES = [

        "delete file",

        "directory watcher",

        "file reader",

        "file writer"
    ]

    PYTHON_TYPES = [

        "python",

        "python on server"
    ]

    # ========================================================
    # MAIN ENTRY
    # ========================================================

    def detect(
        self,
        component_name: str
    ) -> ComponentTypeResult:

        value = (
            component_name
            .strip()
            .lower()
        )

        result = self._match(
            value,
            self.PILOTSCRIPT_TYPES,
            "PILOTSCRIPT"
        )

        if result:
            return result

        result = self._match(
            value,
            self.CONNECTION_TYPES,
            "CONNECTION"
        )

        if result:
            return result

        result = self._match(
            value,
            self.QUERY_TYPES,
            "QUERY"
        )

        if result:
            return result

        result = self._match(
            value,
            self.ELN_SECTION_TYPES,
            "ELN_SECTION"
        )

        if result:
            return result

        result = self._match(
            value,
            self.UI_TYPES,
            "UI"
        )

        if result:
            return result

        result = self._match(
            value,
            self.FILE_TYPES,
            "FILE"
        )

        if result:
            return result

        result = self._match(
            value,
            self.PYTHON_TYPES,
            "PYTHON"
        )

        if result:
            return result

        return ComponentTypeResult(

            component_name=
                component_name,

            component_type=
                "UNKNOWN",

            confidence=0.0
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def _match(
        self,
        component_name: str,
        keywords: List[str],
        component_type: str
    ) -> Optional[ComponentTypeResult]:

        for keyword in keywords:

            if keyword in component_name:

                return ComponentTypeResult(

                    component_name=
                        component_name,

                    component_type=
                        component_type,

                    confidence=1.0,

                    matched_keyword=
                        keyword
                )

        return None

    # ========================================================
    # BOOLEAN HELPERS
    # ========================================================

    def is_pilotscript_component(
        self,
        component_name: str
    ) -> bool:

        result = self.detect(
            component_name
        )

        return (
            result.component_type
            == "PILOTSCRIPT"
        )

    def is_ui_component(
        self,
        component_name: str
    ) -> bool:

        result = self.detect(
            component_name
        )

        return (
            result.component_type
            == "UI"
        )

    def is_repository_component(
        self,
        component_name: str
    ) -> bool:

        result = self.detect(
            component_name
        )

        return result.component_type in [

            "CONNECTION",

            "QUERY",

            "ELN_SECTION",

            "FILE",

            "PYTHON",

            "PILOTSCRIPT"
        ]

    # ========================================================
    # BULK DETECTION
    # ========================================================

    def detect_multiple(
        self,
        component_names: List[str]
    ) -> List[ComponentTypeResult]:

        return [

            self.detect(
                component_name
            )

            for component_name
            in component_names
        ]

    # ========================================================
    # SUMMARY
    # ========================================================

    def build_summary(
        self,
        component_names: List[str]
    ) -> Dict[str, int]:

        summary = {}

        for component in component_names:

            result = self.detect(
                component
            )

            summary[
                result.component_type
            ] = (

                summary.get(
                    result.component_type,
                    0
                ) + 1
            )

        return summary

    # ========================================================
    # REPORT
    # ========================================================

    def print_report(
        self,
        component_names: List[str]
    ):

        print()

        print("=" * 80)

        print(
            "COMPONENT TYPE REPORT"
        )

        print("=" * 80)

        print()

        results = self.detect_multiple(
            component_names
        )

        for result in results:

            print(

                f"{result.component_name}"
                f" -> "
                f"{result.component_type}"
            )

        print()

        print(
            "SUMMARY"
        )

        print("-" * 80)

        summary = self.build_summary(
            component_names
        )

        for component_type, count in (
            summary.items()
        ):

            print(
                f"{component_type}: "
                f"{count}"
            )


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    components = [

        "Notebook Connection",

        "Experiment Query",

        "Custom Filter",

        "Custom Manipulator",

        "Add PDF Section",

        "Add Excel Section",

        "File Chooser",

        "Submit Button",

        "Directory Watcher",

        "Delete File",

        "Python (on Server)"
    ]

    detector = (
        WorkflowComponentTypeDetector()
    )

    detector.print_report(
        components
    )