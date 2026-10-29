# ai_ui_generation_engine.py

from dataclasses import dataclass
from pathlib import Path
import json
import re
import yaml
# ============================================================
# MODELS
# ============================================================

@dataclass
class GeneratedUIPage:

    page_name: str

    tsx_code: str


@dataclass
class GeneratedUIResult:

    pages: list[GeneratedUIPage]
    summary: object = None

    raw_response: str = ""
class AIUIGenerationEngine:

    def __init__(
        self,
        gemini_engine
    ):

        self.gemini_engine = (
            gemini_engine
        )

    import json


    def parse_ui_response(
        self,
        response_text: str
    ):

        tsx_code = ""
        summary = ""

        #
        # Extract TSX
        #
        parts = response_text.split(
            "```"
        )

        for part in parts:

            part = part.strip()

            if part.startswith(
                "tsx"
            ):

                tsx_code = (
                    part[3:]
                    .strip()
                )

        #
        # Extract Summary
        #
        if (
            "SUMMARY START"
            in response_text
            and
            "SUMMARY END"
            in response_text
        ):

            summary = (
                response_text
                .split(
                    "SUMMARY START",
                    1
                )[1]
                .split(
                    "SUMMARY END",
                    1
                )[0]
                .strip()
            )

        return (
            tsx_code,
            summary
        )
        
    def generate(
        self,
        context,
        reconstruction_prompt
    ):

        pages = []

        #
        # Single Page Mode
        #
        if context.ui_pattern == "single_page":

            prompt = (
                self._build_single_page_prompt(
                    context,
                    reconstruction_prompt
                )
            )

            result = (
                self.gemini_engine.generate(
                    prompt
                )
            )
            
            tsx_code, summary = (
                self.parse_ui_response(
                    result.generated_text
                ))
            
            pages.append(

                GeneratedUIPage(

                    page_name="MainPage",
                    
                    tsx_code=
                        tsx_code
                )
            )

        #
        # Wizard Mode
        # all new changes are in single page. once working to be implemented here multi page scenario
        else:

            for page in (
                context.page_graph.pages
            ):

                prompt = (
                    self._build_page_prompt(
                        page,
                        context,
                        reconstruction_prompt
                    )
                )

                result = (
                    self.gemini_engine.generate(
                        prompt
                    )
                )

                pages.append(

                    GeneratedUIPage(

                        page_name=
                            page.page_name,
                        
                        tsx_code=
                            result.generated_text
                    )
                )

        return GeneratedUIResult(
            pages=pages,
            raw_response=
                result.generated_text,
            summary=summary

        )
    
    
    def _build_single_page_prompt(
        self,
        context,
        reconstruction_prompt
    ):

        workflow_steps = []

        for step in (
            context.business_workflow.workflow_steps
        ):

            workflow_steps.append(
                step.step_name
            )
        workflow_actions = []

        for contract in (
            context.api_contracts
        ):

            workflow_actions.append(
                f"{contract.route}"
            )

        return f"""
    Generate ONE React TSX page.

    UI PATTERN:
    single_page

    Business Goal:

    {context.business_workflow.business_goal}

    Workflow Steps:

    {chr(10).join(workflow_steps)}

    Backend APIs:

    {chr(10).join(workflow_actions)}

    Requirements:

    - Generate exactly one page.
    - Use React state.
    - Use useState.
    - Use async event handlers.
    - Call backend APIs.
    - Display parsed file list.
    - Allow user selection.
    - Import selected files.
    - Display import result.
    - Do not generate route navigation.
    - Do not generate multiple pages.

    BACKEND INTEGRATION

    - Use backend APIs.
    - Do NOT perform XML parsing in React.
    - Do NOT simulate file import.
    - Do NOT create mock data.
    - Do NOT create fake services.
    - Do NOT create simulated backend behavior.
    - Business processing belongs entirely to the backend.

    Frontend responsibilities:

    1. Collect user input.
    2. Call backend APIs.
    3. Display backend results.
    4. Update UI state.
    5. Render workflow progress.

    CRITICAL RULES

    - Generate production-ready React + TypeScript code.
    - Generate complete TSX code.
    - The code must compile.
    - The code must be self-contained.
    - Do NOT return markdown explanations.
    - Do NOT return prose outside the requested blocks.
    - Do NOT return any text before or after the requested blocks.
    - Return exactly TWO code blocks.

    FIRST BLOCK-THIS IS PLAIN TEXT

    ```tsx
    <complete TSX source code>
    '''
    SECOND BLOCK-THIS IS PLAIN TEXT
    SUMMARY START
    what_was_generated: |
    Brief description of what was generated.

    api_dependencies:
    - endpoint1
    - endpoint2

    repository_components_used:
    - component1
    - component2

    important_assumptions:
    - assumption1
    - assumption2

    next_artifact_requirements:
    - requirement1
    - requirement2
    SUMMARY END
    Return ONLY the TSX block and the summary block.
    """
    def _build_page_prompt(
        self,
        page,
        context,
        reconstruction_prompt
    ):

        return f"""
Generate a React TSX page.

Requirements:
UI Pattern:
{context.ui_pattern}

Page Name:
{page.page_name}

Page Title:
{page.title}

Page Type:
{page.page_type}

Controls:
{page.controls}

Business Workflow:
{context.business_workflow.workflow_name}

Business Goal:
{context.business_workflow.business_goal}

Use:

React

TypeScript

TSX

Tailwind CSS

Reusable Components:

FileUpload
PrimaryButton
DataGrid
ProgressBar
ImportSummary
StatusPanel

Return only TSX code.
"""