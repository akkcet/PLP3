# ai_review_exporter.py

from pathlib import Path
from dataclasses import asdict
import json


class AIReviewExporter:

    def save(
        self,
        review,
        output_dir
    ):

        output_dir = Path(
            output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        path = (
            output_dir
            /
            "ai_review.json"
        )

        path.write_text(

            json.dumps(
                asdict(
                    review
                ),
                indent=4
            ),

            encoding="utf-8"
        )

        return path