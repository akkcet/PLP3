# ai_missing_component_engine.py

from dataclasses import dataclass


@dataclass
class AIMissingComponentRequest:

    component_name: str

    component_type: str

    component_xml: str

    pilotscript: str

    business_description: str

    similar_components: list

    knowledge_context: str


@dataclass
class AIMissingComponentResult:

    component_name: str

    generated_code: str

    confidence: float

    explanation: str

class AIMissingComponentEngine:

    def __init__(
        self,
        gemini_engine
    ):

        self.gemini_engine = (
            gemini_engine
        )

    def generate(
        self,
        request
    ):

        prompt = (
            self._build_prompt(
                request
            )
        )

        response = (
            self.gemini_engine.generate(
                prompt
            )
        )

        return AIMissingComponentResult(

            component_name=
                request.component_name,

            generated_code=
                response.generated_text,

            confidence=0.85,

            explanation=
                "Generated using Gemini."
        )
    def _build_prompt(
        self,
        request
    ):

        similar = "\n".join(

            [

                f"- {x.name}"

                for x in
                request.similar_components

            ]
        )

        return f"""
Generate a Python component.

Component Name:
{request.component_name}

Component Type:
{request.component_type}

Business Description:
{request.business_description}

PilotScript:
{request.pilotscript}

Knowledge Context:
{request.knowledge_context}

Similar Components:
{similar}

Requirements:

1. Generate production quality Python.

2. Generate COMPONENT_METADATA.

3. Follow PEP8.

4. Return executable code.

5. Reuse patterns from similar components.
"""