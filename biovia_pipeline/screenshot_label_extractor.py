# screenshot_label_extractor.py

from dataclasses import dataclass, field
from typing import List


@dataclass
class UILabel:

    text: str

    label_type: str

    confidence: float = 1.0


@dataclass
class UIScreenshotLabels:

    screenshot_name: str

    page_title: str = ""

    labels: List[UILabel] = field(
        default_factory=list
    )


class ScreenshotLabelExtractor:

    BUTTON_TERMS = [
        "submit",
        "process",
        "upload",
        "import",
        "save",
        "query",
        "search",
        "next",
        "back",
        "browse"
    ]

    INPUT_TERMS = [
        "experiment",
        "user",
        "password",
        "title",
        "description"
    ]

    def extract(
        self,
        screenshot_name: str,
        ocr_lines: List[str]
    ) -> UIScreenshotLabels:

        result = UIScreenshotLabels(
            screenshot_name=screenshot_name
        )

        if ocr_lines:
            result.page_title = ocr_lines[0]

        for line in ocr_lines:

            value = line.lower()

            label_type = "text"

            if any(
                x in value
                for x in self.BUTTON_TERMS
            ):
                label_type = "button"

            elif any(
                x in value
                for x in self.INPUT_TERMS
            ):
                label_type = "input"

            result.labels.append(

                UILabel(
                    text=line,
                    label_type=label_type,
                    confidence=0.95
                )
            )

        return result