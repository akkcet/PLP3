# repository_context_builder.py

from dataclasses import dataclass, field
from typing import List


# @dataclass
# class RepositoryComponent:

#     name: str

#     module_name: str

#     category: str

#     inputs: List[str]

#     outputs: List[str]

#     parameters: List[str]

#     import_path: str
@dataclass
class RepositoryComponent:

    name: str

    purpose: str

    import_path: str
    category: str
    inputs: List[str]

    outputs: List[str]

    parameters: List[str]

    usage_example: str
    import_statement: str


@dataclass
class RepositoryContext:

    available_components: List[
        RepositoryComponent
    ] = field(
        default_factory=list
    )
    prompt_section: str = ""
class RepositoryContextBuilder:

    def build(
        self,
        binding_result
    ) -> RepositoryContext:

        components = []

        for bound in (
            binding_result.bound_components
        ):

            components.append(

                RepositoryComponent(

                    name=
                        bound.component_name,

                    purpose=
                        self._purpose(
                            bound
                        ),

                    import_path=
                        bound.repository_component
                        .python_module,
                    import_statement=
                        bound.repository_component
                        .import_statement,
                    category=
                         bound.repository_component
                            .category,

                    inputs=
                        component.inputs,

                    outputs=
                        component.outputs,

                    parameters=
                        component.parameters,

                    usage_example=
                        self._usage_example(
                            bound
                        )
                )
            )
        context = RepositoryContext(

            available_components=
                components
        )

        context.prompt_section = (
            self.build_prompt_section(
                context
            )
        )

        return context
        # return RepositoryContext(

        #     available_components=
        #         components
        # )
    def build_prompt_section(
        self,
        repository_context
    ):

        lines = []

        lines.append(
            "REPOSITORY REUSE RULES"
        )

        lines.append("")

        lines.append(
            "You MUST reuse repository components."
        )

        lines.append(
            "Do NOT recreate them."
        )

        lines.append(
            "Generate orchestration only."
        )

        lines.append("")

        lines.append(
            "AVAILABLE REPOSITORY COMPONENTS"
        )

        lines.append("")

        for component in (
            repository_context
            .available_components
        ):

            lines.append(
                "=" * 60
            )

            lines.append(
                f"COMPONENT: {component.name}"
            )

            lines.append(
                f"PURPOSE: {component.purpose}"
            )

            lines.append("")

            lines.append(
                "MANDATORY IMPORT"
            )

            lines.append(
                component.import_statement
            )

            lines.append("")

            lines.append(
                f"CATEGORY: {component.category}"
            )

            lines.append(
                f"INPUTS: {component.inputs}"
            )

            lines.append(
                f"OUTPUTS: {component.outputs}"
            )

            lines.append(
                f"PARAMETERS: {component.parameters}"
            )

            lines.append("")

            lines.append(
                "USAGE EXAMPLE"
            )

            lines.append(
                component.usage_example
            )

            lines.append("")

            lines.append(
                "DO NOT REIMPLEMENT THIS COMPONENT."
            )

            lines.append(
                "YOU MUST REUSE THE IMPORT ABOVE."
            )

            lines.append("")

        return "\n".join(
            lines
        )
    def _purpose(
        self,
        component
    ):

        category = (
            component.category
            .lower()
        )

        mapping = {

            "query":
                "Query data from ELN.",

            "connection":
                "Connect to ELN or external systems.",

            "eln":
                "Create or update notebook sections.",

            "filter":
                "Filter records.",

            "transformer":
                "Transform data.",

            "generated":
                "AI generated component."
        }

        return mapping.get(
            category,
            "Reusable repository component."
        )
    def _usage_example(
        self,
        component
    ):

        args = []

        for parameter in (
            component.parameters
        ):

            args.append(
                f"{parameter}=..."
            )

        argument_text = ", ".join(
            args
        )

        function_name = (

            component.name

            .replace(" ", "_")

            .replace("-", "_")

            .lower()
        )

        return f"""
    from {component.import_path}
    import {function_name}

    result = {function_name}(
        {argument_text}
    )
    """
    def _import_statement(
        self,
        component
    ):

        function_name = (

            component.name

            .replace(" ", "_")

            .replace("-", "_")

            .lower()
        )

        return (

            f"from {component.module_name} "
            f"import {function_name}"
        )
    def print_context(
        self,
        repository_context
    ):

        print()
        print("=" * 80)
        print("REPOSITORY CONTEXT")
        print("=" * 80)
        print()

        print(
            f"Available Components: "
            f"{len(repository_context.available_components)}"
        )

        print()

        for component in (
            repository_context.available_components
        ):

            print(
                f"Component: {component.name}"
            )

            print(
                f"Purpose: {component.purpose}"
            )

            print(
                f"Import Path: {component.import_path}"
            )

            print(
                f"Import Statement:"
            )

            print(
                component.import_statement
            )

            print(
                f"Inputs: {component.inputs}"
            )

            print(
                f"Outputs: {component.outputs}"
            )

            print(
                f"Parameters: {component.parameters}"
            )

            print()

            print(
                "Usage Example:"
            )

            print(
                component.usage_example
            )

            print()

            print("-" * 80)

            print()    

import json
from pathlib import Path


class RepositoryContextExporter:

    def save(
        self,
        repository_context,
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

        for component in (
            repository_context
            .available_components
        ):

            payload.append({

                "name":
                    component.name,

                "module":
                    component.import_path,

                "category":
                    component.category,

                "inputs":
                    component.inputs,

                "outputs":
                    component.outputs,

                "parameters":
                    component.parameters
            })

        (
            output_dir /
            "repository_context.json"
        ).write_text(

            json.dumps(
                payload,
                indent=4
            ),

            encoding="utf-8"
        )