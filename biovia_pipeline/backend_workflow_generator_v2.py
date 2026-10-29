# backend_workflow_generator_v2.py

from pathlib import Path


class BackendWorkflowGeneratorV2:

    def generate(
        self,
        workflow,
        binding_result,
        backend_parameters,
        workflow_bindings,
        output_dir: str
    ):

        output_dir = Path(output_dir)

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        workflow_name = (
            workflow.workflow_name
            .replace(" ", "_")
            .replace("-", "_")
            .lower()
        )

        file_path = (
            output_dir /
            f"{workflow_name}.py"
        )

        file_path.write_text(

            self._build_module(
                workflow,
                binding_result,
                backend_parameters,
                workflow_bindings
            ),

            encoding="utf-8"
        )

    # =====================================================
    # MODULE
    # =====================================================

    def _build_module(
        self,
        workflow,
        binding_result,
        backend_parameters,
        workflow_bindings
    ):

        imports = self._generate_imports(
            binding_result
        )

        body = self._generate_workflow_body(
            workflow,
            backend_parameters,
            workflow_bindings
        )

        class_name = (
            workflow.workflow_name
            .replace(" ", "")
            .replace("-", "")
        )

        return f"""
{imports}


class {class_name}:

    def __init__(self):

        self.state = {{}}

    def execute(self):

{body}

        return self.state


if __name__ == "__main__":

    workflow = {class_name}()

    result = workflow.execute()

    print(result)
"""

    # =====================================================
    # IMPORTS
    # =====================================================

    def _generate_imports(
        self,
        binding_result
    ):

        imports = {"import json"}

        for component in (
            binding_result.bound_components
        ):

            imports.add(

                component
                .repository_component
                .import_statement
            )

        return "\n".join(
            sorted(imports)
        )

    # =====================================================
    # BODY
    # =====================================================

    def _generate_workflow_body(
        self,
        workflow,
        backend_parameters,
        workflow_bindings
    ):

        parameter_lookup = {

            x.component_name: x

            for x in backend_parameters
        }
        binding_lookup = {}
        for binding in workflow_bindings.bindings:
                binding_lookup.setdefault(
                    binding.target_component,
                    []
                    )
                
                binding_lookup[
                binding.target_component
                ].append(
                binding
                )
        lines = []

        lines.append(
            '        print("Starting Workflow")'
        )

        lines.append("")

        for component in (
            workflow.components
        ):

            params = (
                parameter_lookup.get(
                    component.component_name
                )
            )

            lines.extend(

                self._generate_component(
                    component,
                    params,
                    binding_lookup
                )

            )

            lines.append("")

        lines.append(
            '        print("Workflow Complete")'
        )

        return "\n".join(lines)

    # =====================================================
    # COMPONENT
    # =====================================================

    def _generate_component(
        self,
        component,
        parameter_set,
        binding_lookup
    ):

        lines = []

        function_name = (
            component.function_name
        )

        lines.append(
            f'        print("Executing: {component.component_name}")'
        )

        arguments = []

        #
        # State Inputs
        #
        if (
            component.component_name
            in binding_lookup
        ):

            for binding in (

                binding_lookup[
                    component.component_name
                ]
            ):

                arguments.append(

                    f"{binding.target_parameter}="
                    f"self.state.get('{binding.source_output}')"
                )

        else:

            for input_name in (
                component.inputs
            ):

                arguments.append(

                    f"{input_name}="
                    f"self.state.get('{input_name}')"
                )

        #
        # XML Parameters
        #
        if parameter_set:

            for key, value in (
                parameter_set.parameters.items()
            ):

                if isinstance(value, bool):

                    arguments.append(
                        #f"{key}={str(value)}"
                        f"{key}={str(value).lower()}"
                    )

                elif isinstance(
                    value,
                    (int, float)
                ):

                    arguments.append(
                        f"{key}={value}"
                    )

                else:

                    arguments.append(
                        f'{key}="{value}"'
                    )


        output_var = None

        if component.outputs:

            output_var = (
                component.outputs[0]
            )

        #
        # Output Component
        #
        if output_var:

            lines.append(
                f"        {output_var} = {function_name}("
            )

            for index, arg in enumerate(
                arguments
            ):

                if index < len(arguments)-1:

                    lines.append(
                        f"            {arg},"
                    )

                else:

                    lines.append(
                        f"            {arg}"
                    )

            lines.append(
                "        )"
            )

            lines.append(
                f"        self.state['{output_var}'] = {output_var}"
            )

        #
        # No Output Component
        #
        else:

            lines.append(
                f"        {function_name}("
            )

            for index, arg in enumerate(
                arguments
            ):

                if index < len(arguments)-1:

                    lines.append(
                        f"            {arg},"
                    )

                else:

                    lines.append(
                        f"            {arg}"
                    )

            lines.append(
                "        )"
            )

        return lines

    # =====================================================
    # DEBUG
    # =====================================================

    def print_workflow(
        self,
        workflow
    ):

        print()

        print("=" * 80)

        print(
            workflow.workflow_name
        )

        print("=" * 80)

        print()

        for component in (
            workflow.components
        ):

            print(
                component.component_name
            )

            print(
                f"Function : {component.function_name}"
            )

            print(
                f"Inputs   : {component.inputs}"
            )

            print(
                f"Outputs  : {component.outputs}"
            )

            print()