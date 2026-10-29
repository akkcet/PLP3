# ai_prompt_builder.py

from dataclasses import dataclass
import json


# ============================================================
# MODELS
# ============================================================

@dataclass
class ReconstructionPrompt:

    system_prompt: str

    user_prompt: str


# ============================================================
# BUILDER
# ============================================================

class AIPromptBuilder:

    def build(
        self,
        context
    ) -> ReconstructionPrompt:

        system_prompt = self._build_system_prompt()

        user_prompt = self._build_user_prompt(
            context
        )

        return ReconstructionPrompt(

            system_prompt=
                system_prompt,

            user_prompt=
                user_prompt
        )

    # ========================================================
    # SYSTEM PROMPT
    # ========================================================

    def _build_system_prompt(
        self
    ):

        return """
You are a senior software architect.

Your job is to reconstruct a complete
React + TypeScript frontend code and
FastAPI backend code from a migrated
Pipeline Pilot protocol.

Rules:

1. Reuse existing repository components whenever possible.

2. Never recreate Notebook Connection,
   Experiment Query,
   Extract Sections,
   Add PDF Section,
   Add Excel Section,
   Add Image Section,
   Add Word Section,
   Add PowerPoint Section
   if they already exist.

3. Generate production-quality code.

4. Use React + TypeScript + TSX.

5. Use FastAPI for backend APIs.

6. Use the business workflow,
   page graph,
   workflow graph,
   screenshots,
   and knowledge graph
   as the source of truth.
7. UI Pattern Rules

If UI pattern is single_page:

- Generate a single page.

- Use React state.

- Use conditional rendering.

- Generate event handlers.

- Connect frontend to backend APIs.

- Do NOT generate route-to-route navigation.

- Do NOT generate wizard pages.

If UI pattern is wizard:

- Generate multiple pages.

- Use React Router.

- Generate page navigation.

- Continue buttons must navigate to the next route.

BACKEND REUSE RULES

The backend is already generated.

The frontend MUST call backend APIs.

The frontend MUST NOT:

- simulate backend processing
- use mock data
- use fake XML parsing
- use DOMParser
- use FileReader for business logic

The frontend MUST:

- use fetch()
- call FastAPI endpoints
- wait for API responses
- render backend results
"""
    
    def _build_user_prompt(
        self,
        context
    ):

        protocol_summary = (
            self._protocol_summary(
                context
            )
        )

        workflow_summary = (
            self._workflow_summary(
                context
            )
        )

        pages_summary = (
            self._page_summary(
                context
            )
        )

        components_summary = (
            self._component_summary(
                context
            )
        )

        business_summary = (
            self._business_summary(
                context
            )
        )
        # repository_summary = (
        #     context.repository_knowledge_base
        # )
        ui_pattern = (
            context.ui_pattern
        )   
        api_summary = (
            self._api_summary(
                context
            )
        )

        return f"""
APPLICATION RECONSTRUCTION

==========================================

BUSINESS WORKFLOW

{business_summary}

==========================================

PROTOCOL

{protocol_summary}

==========================================

WORKFLOW

{workflow_summary}

==========================================
UI PATTERN

{ui_pattern}
==========================================
PAGES

{pages_summary}

==========================================

COMPONENTS

{components_summary}

==========================================

API CONTRACTS

{api_summary}

==========================================


TASK

Generate:

1. Frontend React TSX

2. FastAPI Backend

3. API Endpoints

4. Routing

5. State Management

6. Data Flow

Use repository components whenever possible.
"""
    def _business_summary(
        self,
        context
    ):

        workflow = (
            context.business_workflow
        )

        lines = []

        lines.append(
            f"Workflow: "
            f"{workflow.workflow_name}"
        )

        lines.append("")

        lines.append(
            f"Goal: "
            f"{workflow.business_goal}"
        )

        lines.append("")

        lines.append(
            "Steps:"
        )

        for step in (
            workflow.workflow_steps
        ):

            lines.append(

                f"- {step.step_name}"
            )

        return "\n".join(
            lines
        )
    def _protocol_summary(
        self,
        context
    ):

        protocol = (
            context.protocol_analysis
        )

        lines = []

        lines.append(
            f"Protocol Name: "
            f"{protocol.protocol_name}"
        )

        lines.append(
            f"Total Nodes: "
            f"{protocol.total_nodes}"
        )

        lines.append(
            f"Blue Components: "
            f"{protocol.blue_count}"
        )

        lines.append(
            f"Green Components: "
            f"{protocol.green_count}"
        )

        return "\n".join(
            lines
        )
    def _workflow_summary(
        self,
        context
    ):

        workflow = (
            context.stateful_workflow
        )

        return "\n".join(

            [

                f"- {x.component_name}"

                for x in

                workflow.components
            ]
        )
    def _page_summary(
        self,
        context
    ):

        graph = (
            context.page_graph
        )

        lines = []

        for page in (
            graph.pages
        ):

            lines.append(

                f"{page.page_name} "
                f"({page.page_type})"
            )

        return "\n".join(
            lines
        )
    def _component_summary(
        self,
        context
    ):

        lines = []

        lines.append(
            "Mapped Components"
        )

        lines.append("")

        for component in (

            context.binding_result
            .bound_components
        ):

            lines.append(

                f"- {component.component_name}"
            )

        lines.append("")

        lines.append(
            "Missing Components"
        )

        lines.append("")

        for component in (

            context.binding_result
            .missing_components
        ):

            lines.append(
                f"- {component}"
            )

        return "\n".join(
            lines
        )
    def print_prompt(
        self,
        prompt
    ):

        print()

        print("=" * 80)

        print(
            "SYSTEM PROMPT"
        )

        print("=" * 80)

        print()

        print(
            prompt.system_prompt
        )

        print()

        print("=" * 80)

        print(
            "USER PROMPT"
        )

        print("=" * 80)

        print()

        print(
            prompt.user_prompt
        )
    def _api_summary(
        self,
        context
    ):

        lines = []

        for api in (
            context.api_contracts
        ):

            lines.append(
                f"Endpoint: {api.route}"
            )

            lines.append(
                f"Function: {api.function_name}"
            )

            lines.append("")

        return "\n".join(
            lines
        )