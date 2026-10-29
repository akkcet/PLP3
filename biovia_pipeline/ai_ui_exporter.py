# ai_ui_exporter.py

from pathlib import Path


class AIUIExporter:

    def save(
        self,
        generated_pages,
        pages_folder
    ):

        pages_folder = Path(
            pages_folder
        )

        pages_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        for page in (
            generated_pages.pages
        ):

            path = (
                pages_folder
                /
                f"{page.page_name}.tsx"
            )

            path.write_text(

                page.tsx_code,

                encoding="utf-8"
            )