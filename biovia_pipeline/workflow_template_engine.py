# workflow_template_engine.py

from dataclasses import dataclass, field
from typing import List, Dict
from .template_reconstruction_engine import (
    TemplateMatch
)

# ============================================================
# MODELS
# ============================================================

@dataclass
class WorkflowTemplate:

    template_name: str

    category: str

    components: List[str]

    usage_count: int = 0

    confidence: float = 1.0


@dataclass
class WorkflowTemplateCatalog:

    templates: List[
        WorkflowTemplate
    ] = field(
        default_factory=list
    )
class WorkflowTemplateEngine:

    def build(
        self,
        pattern_catalog
    ) -> WorkflowTemplateCatalog:

        catalog = (
            WorkflowTemplateCatalog()
        )

        for pattern in (
            pattern_catalog.patterns
        ):

            template = WorkflowTemplate(

                template_name=
                    self._template_name(
                        pattern
                    ),

                category=
                    pattern.category,

                components=
                    pattern.components,

                usage_count=
                    pattern.frequency,

                confidence=
                    self._confidence(
                        pattern
                    )
            )

            catalog.templates.append(
                template
            )

        return catalog
    def _template_name(
        self,
        pattern
    ):

        components = (
            pattern.components
        )

        joined = "_".join(
            components
        )

        return (

            f"{joined}_template"
        )
    def _confidence(
        self,
        pattern
    ):

        score = min(

            pattern.frequency / 10,

            1.0
        )

        return round(
            score,
            2
        )

class WorkflowTemplateMatcher:

    def find_matches(
        self,
        workflow,
        catalog
    ):

        workflow_components = {

            x.function_name

            for x in
            workflow.components
        }

        matches = []

        for template in (
            catalog.templates
        ):

            overlap = len(

                workflow_components.intersection(

                    set(
                        template.components
                    )
                )
            )

            if overlap:

                matches.append(

                    TemplateMatch(

                        template_name=
                            template.template_name,

                        confidence=
                            overlap,

                        missing_components=[],

                        template=
                            template
                    )
                )

        matches.sort(

            key=lambda x:
                x.confidence,

            reverse=True
        )

        return matches
class WorkflowTemplateReconstructor:

    def suggest(
        self,
        workflow,
        catalog
    ):

        matcher = (
            WorkflowTemplateMatcher()
        )

        return matcher.find_matches(

            workflow,

            catalog
        )
import json
from pathlib import Path


class WorkflowTemplateExporter:

    def save(
        self,
        catalog,
        output_dir
    ):

        output_dir = Path(
            output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        payload = []

        for template in (
            catalog.templates
        ):

            payload.append({

                "template_name":
                    template.template_name,

                "category":
                    template.category,

                "components":
                    template.components,

                "usage_count":
                    template.usage_count,

                "confidence":
                    template.confidence
            })

        output_file = (

            output_dir

            /

            "workflow_templates.json"
        )

        output_file.write_text(

            json.dumps(
                payload,
                indent=4
            ),

            encoding="utf-8"
        )

        return output_file
    def print_catalog(
        self,
        catalog
    ):

        print()

        print("=" * 80)

        print(
            "WORKFLOW TEMPLATE CATALOG"
        )

        print("=" * 80)

        print()

        for template in (
            catalog.templates
        ):

            print(
                template.template_name
            )

            print(
                f"Category: "
                f"{template.category}"
            )

            print(
                f"Usage Count: "
                f"{template.usage_count}"
            )

            print(
                f"Confidence: "
                f"{template.confidence}"
            )

            print(
                f"Components: "
                f"{template.components}"
            )

            print()