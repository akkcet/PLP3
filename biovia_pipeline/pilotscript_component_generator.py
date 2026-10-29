# pilotscript_component_generator.py

from dataclasses import dataclass
from pathlib import Path

from .pilotscript_parser import (
    PilotScriptParser
)


# ============================================================
# MODELS
# ============================================================

@dataclass
class PilotScriptComponent:

    component_name: str

    pilotscript: str

    business_context: str = ""


@dataclass
class GeneratedPilotScriptComponent:

    component_name: str

    file_name: str

    generated_code: str


# ============================================================
# GENERATOR
# ============================================================

class PilotScriptComponentGenerator:

    def generate(
        self,
        component: PilotScriptComponent
    ) -> GeneratedPilotScriptComponent:

        transpiled_code = (
            self._transpile(
                component.pilotscript
            )
        )

        generated_code = (
            self._build_module(
                component,
                transpiled_code
            )
        )

        file_name = (
            component.component_name
            .replace(" ", "_")
            .replace("-", "_")
            .lower()
            + ".py"
        )

        return GeneratedPilotScriptComponent(

            component_name=
                component.component_name,

            file_name=
                file_name,

            generated_code=
                generated_code
        )

    # ========================================================
    # TRANSPILATION
    # ========================================================

    def _transpile(
        self,
        pilotscript: str
    ) -> str:

        parser = (
            PilotScriptParser(
                pilotscript
            )
        )

        try:

            return (
                parser.transpile_to_python()
            )

        except Exception:

            return f'''
# =====================================================
# TRANSPILATION FAILED
# =====================================================

expression = """
{pilotscript}
"""

# TODO:
# Manual review required.
'''

    # ========================================================
    # BUILD MODULE
    # ========================================================

    def _build_module(
        self,
        component: PilotScriptComponent,
        python_logic: str
    ) -> str:

        function_name = (
            component.component_name
            .replace(" ", "_")
            .replace("-", "_")
            .lower()
        )

        business_context = (
            component.business_context
            if component.business_context
            else "Not provided"
        )

        return f'''"""
AUTO-GENERATED COMPONENT

Original PLP Component:
{component.component_name}

Business Context:
{business_context}
"""

COMPONENT_METADATA = {{

    "component_name":
        "{component.component_name}",

    "category":
        "generated",

    "inputs": [],

    "outputs": [],

    "plp_aliases": [
        "{component.component_name}"
    ]
}}


def {function_name}(record=None):

    """
    Auto-generated from PLP PilotScript.
    """

    if record is None:

        record = {{}}

{self._indent_python_logic(python_logic)}

    return record
'''

    # ========================================================
    # INDENT GENERATED PYTHON
    # ========================================================

    def _indent_python_logic(
        self,
        code: str
    ) -> str:

        lines = []

        for line in code.splitlines():

            if line.strip():

                lines.append(
                    f"    {line}"
                )

            else:

                lines.append(
                    ""
                )

        return "\n".join(
            lines
        )

    # ========================================================
    # SAVE
    # ========================================================

    def save(
        self,
        generated_component:
            GeneratedPilotScriptComponent,

        output_dir
    ):

        output_dir = Path(
            output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path = (

            output_dir

            /

            generated_component
            .file_name
        )

        file_path.write_text(

            generated_component
            .generated_code,

            encoding="utf-8"
        )

        return file_path

    # ========================================================
    # REPORT
    # ========================================================

    def print_component(
        self,
        component:
            GeneratedPilotScriptComponent
    ):

        print()

        print("=" * 80)

        print(
            component.component_name
        )

        print("=" * 80)

        print()

        print(
            component.generated_code
        )

        print()


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    sample = PilotScriptComponent(

        component_name=
            "Custom Filter",

        pilotscript=
            """
            FindSubstring(
                FilePath,
                '.pdf'
            ) > 0
            """,

        business_context=
            "Filter PDF files"
    )

    generator = (
        PilotScriptComponentGenerator()
    )

    generated = (
        generator.generate(
            sample
        )
    )

    generator.print_component(
        generated
    )