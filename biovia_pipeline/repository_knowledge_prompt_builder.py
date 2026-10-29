# repository_knowledge_prompt_builder.py

class RepositoryKnowledgePromptBuilder:

    def build(
        self,
        knowledge_base
    ):

        lines = []

        lines.append(
            "REPOSITORY REUSE CONTRACT"
        )

        lines.append("")

        lines.append(
            "The following components already exist."
        )

        lines.append(
            "You MUST reuse them."
        )

        lines.append(
            "You MUST NOT recreate them."
        )

        lines.append("")

        for component in (
            knowledge_base.components
        ):

            lines.append(
                "=" * 60
            )

            lines.append(
                f"COMPONENT: "
                f"{component.component_name}"
            )

            lines.append("")

            lines.append(
                f"PURPOSE: "
                f"{component.docstring}"
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
                f"CATEGORY: "
                f"{component.category}"
            )

            lines.append(
                f"PARAMETERS: "
                f"{component.parameters}"
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
                "FORBIDDEN"
            )

            lines.append(
                f"class {component.component_name}"
            )

            lines.append(
                f"def {component.function_name}"
            )

            lines.append("")

        return "\n".join(
            lines
        )
    