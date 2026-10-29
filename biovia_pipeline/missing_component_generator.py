# missing_component_generator.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


# ============================================================
# MODELS
# ============================================================

@dataclass
class MissingComponent:

    name: str

    component_type: str

    parameters: Dict = field(
        default_factory=dict
    )

    pilotscript: str = ""

    business_context: str = ""


@dataclass
class GeneratedComponent:

    component_name: str

    file_name: str

    code: str


# ============================================================
# GENERATOR
# ============================================================

class MissingComponentGenerator:

    def generate(
        self,
        component: MissingComponent
    ) -> GeneratedComponent:

        file_name = (

            component.name
            .replace(" ", "_")
            .replace("-", "_")
            .lower()

            + ".py"
        )

        code = self._build_code(
            component
        )

        return GeneratedComponent(

            component_name=
                component.name,

            file_name=
                file_name,

            code=
                code
        )

    # ========================================================
    # BUILD
    # ========================================================

    def _build_code(
        self,
        component
    ):

        metadata = self._build_metadata(
            component
        )

        parameters = self._parameter_signature(
            component
        )

        return f'''
"""
AUTO GENERATED COMPONENT

Original PLP Component:
{component.name}
"""

{metadata}


def {self._function_name(component.name)}(
    {parameters}
):

    """
    Generated from PLP.
    """

    result = {{}}

    # =========================================
    # TODO:
    # Reconstruct PLP behavior
    # =========================================

    return result
'''

    # ========================================================
    # METADATA
    # ========================================================

    def _build_metadata(
        self,
        component
    ):

        inputs = []

        outputs = []

        for key in (
            component.parameters.keys()
        ):

            inputs.append(key)

        return f'''
COMPONENT_METADATA = {{

    "component_name":
        "{component.name}",

    "category":
        "generated",

    "inputs":
        {inputs},

    "outputs":
        {outputs},

    "plp_aliases":
        ["{component.name}"]
}}
'''

    # ========================================================
    # FUNCTION NAME
    # ========================================================

    def _function_name(
        self,
        name
    ):

        return (

            name

            .replace(" ", "_")

            .replace("-", "_")

            .lower()
        )

    # ========================================================
    # PARAMS
    # ========================================================

    def _parameter_signature(
        self,
        component
    ):

        params = []

        for key in (
            component.parameters.keys()
        ):

            params.append(

                self._sanitize(
                    key
                )

            )

        return ", ".join(
            params
        )

    def _sanitize(
        self,
        value
    ):

        return (

            value

            .replace(" ", "_")

            .replace("-", "_")

            .lower()
        )

    # ========================================================
    # SAVE
    # ========================================================

    def save(
        self,
        generated_component,
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

            generated_component
            .file_name
        )

        path.write_text(

            generated_component.code,

            encoding="utf-8"
        )

        return path

    # ========================================================
    # REPORT
    # ========================================================

    def print_component(
        self,
        component
    ):

        print()

        print("=" * 80)

        print(
            component.component_name
        )

        print("=" * 80)

        print()

        print(
            component.code
        )