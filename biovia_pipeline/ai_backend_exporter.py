from pathlib import Path


class AIBackendExporter:

    def save(
        self,
        backend_result,
        output_folder
    ):

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        (
            output_folder /
            backend_result
            .workflow_code
            .file_name
        ).write_text(

            backend_result
            .workflow_code
            .code,

            encoding="utf-8"
        )

        (
            output_folder /
            backend_result
            .router_code
            .file_name
        ).write_text(

            backend_result
            .router_code
            .code,

            encoding="utf-8"
        )

        (
            output_folder /
            backend_result
            .service_code
            .file_name
        ).write_text(

            backend_result
            .service_code
            .code,

            encoding="utf-8"
        )