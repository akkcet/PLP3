# layout_enhancer.py

from dataclasses import dataclass
from typing import List


@dataclass
class EnhancedControl:

    control_type: str

    label: str

    placeholder: str = ""

    description: str = ""


class LayoutEnhancer:

    def enrich_controls(
        self,
        controls,
        screenshot_labels
    ):

        enhanced = []

        for control in controls:

            enhanced.append(

                EnhancedControl(

                    control_type=
                        control,

                    label=
                        self._resolve_label(
                            control,
                            screenshot_labels
                        )
                )
            )

        return enhanced

    def _resolve_label(
        self,
        control_type,
        screenshot_labels
    ):

        if not screenshot_labels:

            return control_type

        #
        # Upload Labels
        #
        if control_type == "FileUpload":

            for screen in screenshot_labels:

                for label in screen.labels:

                    if (
                        "browse"
                        in label.text.lower()
                    ):

                        return label.text

        #
        # Grid Labels
        #
        if control_type == "DataGrid":

            for screen in screenshot_labels:

                for label in screen.labels:

                    if (
                        "available"
                        in label.text.lower()
                    ):

                        return label.text

        #
        # Button Labels
        #
        if control_type == "PrimaryButton":

            for screen in screenshot_labels:

                for label in screen.labels:

                    value = (
                        label.text.lower()
                    )

                    if (

                        "process"
                        in value

                        or

                        "import"
                        in value

                        or

                        "submit"
                        in value

                    ):

                        return label.text

        return control_type