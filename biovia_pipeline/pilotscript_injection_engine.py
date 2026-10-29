# pilotscript_injection_engine.py

from dataclasses import dataclass
from typing import Dict, List


# ============================================================
# MODELS
# ============================================================

@dataclass
class InjectedWorkflowComponent:

    component_name: str

    generated_code: str

    insertion_index: int


@dataclass
class InjectionResult:

    injected_components: List[
        InjectedWorkflowComponent
    ]

    modified_workflow_code: str


# ============================================================
# ENGINE
# ============================================================

class PilotScriptInjectionEngine:

    def inject(
        self,
        workflow_code: str,
        reconstructed_components
    ) -> InjectionResult:

        injected = []

        modified_code = workflow_code

        marker = (
            "def execute(self):"
        )

        if marker not in workflow_code:

            return InjectionResult(

                injected_components=[],

                modified_workflow_code=
                    workflow_code
            )

        injection_block = []

        for index, component in enumerate(
            reconstructed_components
        ):

            code = (
                self._indent_code(
                    component.generated_code
                )
            )

            injection_block.append(

                f"\n"
                f"        # "
                f"{component.component_name}\n"
                f"{code}\n"
            )

            injected.append(

                InjectedWorkflowComponent(

                    component_name=
                        component.component_name,

                    generated_code=
                        component.generated_code,

                    insertion_index=
                        index
                )
            )

        insert_text = (
            "\n".join(
                injection_block
            )
        )

        modified_code = (
            workflow_code.replace(

                marker,

                marker
                + insert_text
            )
        )

        return InjectionResult(

            injected_components=
                injected,

            modified_workflow_code=
                modified_code
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def _indent_code(
        self,
        code: str
    ):

        lines = []

        for line in code.splitlines():

            lines.append(
                "        " + line
            )

        return "\n".join(
            lines
        )

    # ========================================================
    # REPORT
    # ========================================================

    def print_report(
        self,
        result: InjectionResult
    ):

        print()

        print("=" * 80)

        print(
            "PILOTSCRIPT INJECTION REPORT"
        )

        print("=" * 80)

        print()

        print(
            "Injected Components:"
        )

        print(
            len(
                result.injected_components
            )
        )

        print()

        for component in (
            result.injected_components
        ):

            print(
                component.component_name
            )