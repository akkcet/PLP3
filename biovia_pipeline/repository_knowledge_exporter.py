# repository_knowledge_exporter.py

from pathlib import Path
import json
from dataclasses import asdict


class RepositoryKnowledgeExporter:

    def save(
        self,
        knowledge_base,
        output_dir
    ):

        output_dir = Path(
            output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        payload = [

            asdict(x)

            for x in
            knowledge_base.components
        ]

        (
            output_dir
            /
            "repository_knowledge.json"
        ).write_text(

            json.dumps(
                payload,
                indent=4
            ),

            encoding="utf-8"
        )