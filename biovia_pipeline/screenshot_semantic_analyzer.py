"""
Maps screenshot OCR data into
UI semantic controls.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class DetectedControl:
    control_type: str
    label: str
    confidence: float


@dataclass
class ScreenshotSemanticModel:
    screenshot_name: str

    buttons: List[DetectedControl] = field(
        default_factory=list
    )

    inputs: List[DetectedControl] = field(
        default_factory=list
    )

    uploads: List[DetectedControl] = field(
        default_factory=list
    )

    tables: List[DetectedControl] = field(
        default_factory=list
    )

    text_blocks: List[DetectedControl] = field(
        default_factory=list
    )


class ScreenshotSemanticAnalyzer:

    BUTTON_WORDS = {
        "submit",
        "run",
        "execute",
        "save",
        "next",
        "back",
        "cancel",
        "upload",
        "query",
        "search",
        "launch"
    }

    INPUT_WORDS = {
        "experiment",
        "number",
        "username",
        "password",
        "title",
        "name"
    }

    UPLOAD_WORDS = {
        "upload",
        "attachment",
        "file",
        "browse"
    }

    def analyze(
        self,
        screenshot_name: str,
        text_lines: List[str]
    ) -> ScreenshotSemanticModel:

        model = ScreenshotSemanticModel(
            screenshot_name=screenshot_name
        )

        for line in text_lines:

            value = line.lower()

            if any(
                x in value
                for x in self.BUTTON_WORDS
            ):
                model.buttons.append(
                    DetectedControl(
                        control_type="button",
                        label=line,
                        confidence=0.9
                    )
                )

            elif any(
                x in value
                for x in self.UPLOAD_WORDS
            ):
                model.uploads.append(
                    DetectedControl(
                        control_type="upload",
                        label=line,
                        confidence=0.9
                    )
                )

            elif any(
                x in value
                for x in self.INPUT_WORDS
            ):
                model.inputs.append(
                    DetectedControl(
                        control_type="textbox",
                        label=line,
                        confidence=0.8
                    )
                )

            else:
                model.text_blocks.append(
                    DetectedControl(
                        control_type="text",
                        label=line,
                        confidence=0.5
                    )
                )

        return model