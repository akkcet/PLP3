# layout_classifier.py

from dataclasses import dataclass, field
from typing import List


@dataclass
class LayoutControl:

    control_type: str
    label: str
    confidence: float = 1.0


@dataclass
class LayoutSection:

    title: str
    controls: List[LayoutControl] = field(
        default_factory=list
    )


@dataclass
class ScreenLayout:

    layout_type: str

    sections: List[LayoutSection]

    inferred_workflow: List[str]


CONTROL_PATTERNS = {

    "browse": "FileUpload",

    "upload": "FileUpload",

    "choose file": "FileUpload",

    "process": "PrimaryButton",

    "submit": "PrimaryButton",

    "import": "PrimaryButton",

    "table": "DataGrid",

    "list": "DataGrid",

    "experiment": "TextInput"
}


class LayoutClassifier:

    def classify(
        self,
        extracted_text: str
    ) -> ScreenLayout:

        controls = []

        text = (
            extracted_text.lower()
        )

        for keyword, control_type in (
            CONTROL_PATTERNS.items()
        ):

            if keyword in text:

                controls.append(

                    LayoutControl(
                        control_type=
                            control_type,

                        label=
                            keyword
                    )
                )

        section = LayoutSection(

            title="Main Section",

            controls=controls
        )

        return ScreenLayout(

            layout_type=
                self._detect_layout(
                    text
                ),

            sections=[
                section
            ],

            inferred_workflow=
                self._infer_workflow(
                    controls
                )
        )

    def _detect_layout(
        self,
        text: str
    ):

        if "wizard" in text:
            return "wizard"

        if (
            "upload" in text
            and
            "import" in text
        ):
            return "import_workflow"

        return "form"

    def _infer_workflow(
        self,
        controls
    ):

        workflow = []

        control_names = {

            c.control_type

            for c in controls
        }

        if (
            "FileUpload"
            in control_names
        ):
            workflow.append(
                "Upload XML"
            )

        if (
            "PrimaryButton"
            in control_names
        ):
            workflow.append(
                "Execute"
            )

        if (
            "DataGrid"
            in control_names
        ):
            workflow.append(
                "Review Data"
            )

        return workflow