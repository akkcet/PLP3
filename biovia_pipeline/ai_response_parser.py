# ai_response_parser.py

import json

from .ai_generation_models import (
    GeneratedArtifact,
    ArtifactSummary
)


class AIResponseParser:

    def parse(
        self,
        response_text,
        artifact_name
    ):

        data = json.loads(
            response_text
        )

        summary = ArtifactSummary(

            artifact_name=
                artifact_name,

            what_was_generated=
                data["summary"][
                    "what_was_generated"
                ],

            api_dependencies=
                data["summary"][
                    "api_dependencies"
                ],

            repository_components_used=
                data["summary"][
                    "repository_components_used"
                ],

            important_assumptions=
                data["summary"][
                    "important_assumptions"
                ],

            next_artifact_requirements=
                data["summary"][
                    "next_artifact_requirements"
                ]
        )

        return GeneratedArtifact(

            code=
                data["code"],

            summary=
                summary,

            raw_response=
                response_text
        )