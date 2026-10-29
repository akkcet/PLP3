# screenshot_interpreter.py

from dataclasses import dataclass, field
from typing import List


@dataclass
class UIWidget:

    widget_type: str
    label: str
    confidence: float = 1.0


@dataclass
class UIScreen:

    title: str
    widgets: List[UIWidget] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)


@dataclass
class UIScreenshotAnalysis:

    screens: List[UIScreen]


class ScreenshotInterpreter:

    def interpret(
        self,
        screenshot_descriptions: List[str]
    ) -> UIScreenshotAnalysis:

        screens = []

        for text in screenshot_descriptions:

            screen = self._extract_screen(text)

            screens.append(screen)

        return UIScreenshotAnalysis(
            screens=screens
        )

    def _extract_screen(
        self,
        text: str
    ) -> UIScreen:

        widgets = []

        ltext = text.lower()

        if "browse" in ltext:
            widgets.append(
                UIWidget(
                    widget_type="FileUpload",
                    label="Browse"
                )
            )

        if "process" in ltext:
            widgets.append(
                UIWidget(
                    widget_type="Button",
                    label="Process"
                )
            )

        if "import" in ltext:
            widgets.append(
                UIWidget(
                    widget_type="Button",
                    label="Import"
                )
            )

        if "list" in ltext:
            widgets.append(
                UIWidget(
                    widget_type="DataGrid",
                    label="File List"
                )
            )

        return UIScreen(
            title="Detected Screen",
            widgets=widgets
        )
