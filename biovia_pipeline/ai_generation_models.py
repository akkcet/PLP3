# ai_generation_models.py

from dataclasses import dataclass


@dataclass
class ArtifactSummary:

    artifact_name: str

    what_was_generated: str

    api_dependencies: list[str]

    repository_components_used: list[str]

    important_assumptions: list[str]

    next_artifact_requirements: list[str]


@dataclass
class GeneratedArtifact:

    code: str

    summary: ArtifactSummary

    raw_response: str