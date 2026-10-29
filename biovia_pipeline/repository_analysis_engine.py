# repository_analysis_engine.py

from dataclasses import dataclass, field
from typing import List
import inspect
import importlib
import pkgutil

@dataclass
class RepositoryKnowledge:

    component_name: str
    module_name: str
    import_statement: str
    function_name: str
    parameters: List[str]
    docstring: str
    category: str
    usage_example: str


@dataclass
class RepositoryKnowledgeBase:

    components: List[
        RepositoryKnowledge
    ] = field(
        default_factory=list
    )


class RepositoryAnalysisEngine:

    def analyze(
        self,
        package_name=
        "biovia_pipeline.components"
    ):

        knowledge_base = (
            RepositoryKnowledgeBase()
        )

        package = (
            importlib.import_module(
                package_name
            )
        )

        for module_info in (
            pkgutil.iter_modules(
                package.__path__
            )
        ):

            module_name = (
                module_info.name
            )

            full_name = (
                f"{package_name}."
                f"{module_name}"
            )

            try:

                module = (
                    importlib.import_module(
                        full_name
                    )
                )

                knowledge = (
                    self._analyze_module(
                        module,
                        full_name
                    )
                )

                if knowledge:

                    knowledge_base.components.append(
                        knowledge
                    )

            except Exception as ex:

                print(
                    f"Skipping "
                    f"{full_name}: {ex}"
                )

        return knowledge_base
    def _analyze_module(
        self,
        module,
        full_name
    ):
        IGNORE_FUNCTIONS = {

            "dataclass",

            "field",

            "build_section_filter",

            "clean_section_title"
        }

        functions = [

            x

            for x in

            inspect.getmembers(
                module,
                inspect.isfunction
            )

            # if not x[0].startswith("_")
            if x[0] not in IGNORE_FUNCTIONS
        ]

        if not functions:

            return None

        function_name = (
            functions[0][0]
        )

        function_ref = (
            functions[0][1]
        )

        signature = (
            inspect.signature(
                function_ref
            )
        )

        parameters = [

            x

            for x in
            signature.parameters
        ]

        return RepositoryKnowledge(

            component_name=
                self._component_name(
                    function_name
                ),

            module_name=
                full_name,

            import_statement=
                (
                    f"from "
                    f"{full_name} "
                    f"import "
                    f"{function_name}"
                ),

            function_name=
                function_name,

            parameters=
                parameters,

            docstring=
                inspect.getdoc(
                    function_ref
                )
                or "",

            category=
                self._infer_category(
                    full_name
                ),

            usage_example=
                self._usage_example(
                    full_name,
                    function_name,
                    parameters
                )
        )
    def _infer_category(
        self,
        module_name
    ):

        lower = (
            module_name.lower()
        )

        if (
            "query"
            in lower
        ):
            return "query"

        if (
            "connection"
            in lower
        ):
            return "connection"

        if (
            "section"
            in lower
        ):
            return "eln"

        if (
            "filter"
            in lower
        ):
            return "filter"

        if (
            "manipulator"
            in lower
        ):
            return "transform"

        return "generic"
    def _component_name(
        self,
        function_name
    ):

        return (

            function_name

            .replace("_", " ")

            .title()
        )
    def _usage_example(
        self,
        module_name,
        function_name,
        parameters
    ):

        args = []

        for parameter in (
            parameters
        ):

            args.append(
                f"{parameter}=..."
            )

        return f"""
from {module_name} import {function_name}

result = {function_name}(

    {', '.join(args)}

)
"""