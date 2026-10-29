# repository_knowledge_builder.py

from .repository_knowledge_base import (
    RepositoryKnowledgeBase,
    KnowledgeComponent
)


class RepositoryKnowledgeBuilder:

    def build(
        self,
        repository_context
    ):

        knowledge_base = (
            RepositoryKnowledgeBase()
        )

        for component in (
            repository_context
            .available_components
        ):

            knowledge_base.components.append(

                KnowledgeComponent(

                    component_name=
                        component.name,

                    import_statement=
                        component.import_statement,

                    function_name=
                        self._function_name(
                            component
                        ),

                    category=
                        component.category,

                    parameters=
                        component.parameters,

                    purpose=
                        component.purpose,

                    usage_example=
                        component.usage_example
                )
            )

        return knowledge_base

    def _function_name(
        self,
        component
    ):

        statement = (
            component.import_statement
        )

        try:

            return (
                statement
                .split("import")[1]
                .strip()
            )

        except Exception:

            return (
                component.name
                .replace(" ", "_")
                .replace("-", "_")
                .lower()
            )
    