# ai_missing_component_exporter.py

from pathlib import Path


class AIMissingComponentExporter:

    def save(
        self,
        component,
        output_folder
    ):

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        file_name = (

            component.component_name

            .replace(" ", "_")

            .replace("-", "_")

            .lower()

            + ".py"
        )

        path = (
            output_folder /
            file_name
        )

        path.write_text(

            component.generated_code,

            encoding="utf-8"
        )

        return path