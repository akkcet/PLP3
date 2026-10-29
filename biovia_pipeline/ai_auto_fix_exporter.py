import json
from pathlib import Path


class AutoFixExporter:

    def save(
        self,
        result,
        output_dir
    ):

        payload = [

            {

                "category":
                    x.category,

                "action":
                    x.action,

                "confidence":
                    x.confidence
            }

            for x in result.fixes
        ]

        Path(
            output_dir
        ).mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = (

            Path(output_dir)

            /

            "auto_fixes.json"
        )

        output_file.write_text(

            json.dumps(
                payload,
                indent=4
            ),

            encoding="utf-8"
        )
