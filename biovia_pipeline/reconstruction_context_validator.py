# reconstruction_context_validator.py

from dataclasses import dataclass, field
from typing import List


# ============================================================
# MODELS
# ============================================================

@dataclass
class ContextValidationItem:

    name: str

    passed: bool

    details: str


@dataclass
class ContextValidationResult:

    items: List[
        ContextValidationItem
    ] = field(
        default_factory=list
    )

    @property
    def valid(self):

        return all(
            x.passed
            for x in self.items
        )
class ReconstructionContextValidator:

    def validate(
        self,
        context
    ):

        result = (
            ContextValidationResult()
        )

        #
        # Protocol
        #
        result.items.append(

            ContextValidationItem(

                name="Protocol Analysis",

                passed=
                    context.protocol_analysis
                    is not None,

                details=
                    "Protocol analysis available."
            )
        )

        #
        # Business Workflow
        #
        result.items.append(

            ContextValidationItem(

                name="Business Workflow",

                passed=
                    context.business_workflow
                    is not None,

                details=
                    "Business workflow available."
            )
        )

        #
        # Bindings
        #
        result.items.append(

            ContextValidationItem(

                name="Component Binding",

                passed=
                    context.binding_result
                    is not None,

                details=
                    f"{len(context.binding_result.bound_components)} mapped components."
            )
        )

        #
        # Backend Parameters
        #
        result.items.append(

            ContextValidationItem(

                name="Backend Parameters",

                passed=
                    context.backend_parameters
                    is not None,

                details=
                    "Backend parameters created."
            )
        )

        #
        # Workflow Bindings
        #
        result.items.append(

            ContextValidationItem(

                name="Workflow Bindings",

                passed=
                    context.workflow_bindings
                    is not None,

                details=
                    "Workflow bindings available."
            )
        )

        #
        # Stateful Workflow
        #
        result.items.append(

            ContextValidationItem(

                name="Stateful Workflow",

                passed=
                    context.stateful_workflow
                    is not None,

                details=
                    "State workflow generated."
            )
        )

        #
        # Pattern Catalog
        #
        pattern_catalog = getattr(
            context,
            "pattern_catalog",
            None
        )

        result.items.append(

            ContextValidationItem(

                name="Pattern Catalog",

                passed=
                    pattern_catalog
                    is not None,

                details=
                    "Pattern catalog generated."
            )
        )

        #
        # Template Catalog
        #
        template_catalog = getattr(
            context,
            "template_catalog",
            None
        )

        result.items.append(

            ContextValidationItem(

                name="Template Catalog",

                passed=
                    template_catalog
                    is not None,

                details=
                    "Template catalog generated."
            )
        )

        #
        # Page Graph
        #
        result.items.append(

            ContextValidationItem(

                name="Page Graph",

                passed=
                    context.page_graph
                    is not None,

                details=
                    f"{len(context.page_graph.pages)} pages discovered."
            )
        )

        #
        # Blueprint
        #
        result.items.append(

            ContextValidationItem(

                name="Application Blueprint",

                passed=
                    context.application_blueprint
                    is not None,

                details=
                    "Blueprint generated."
            )
        )

        #
        # API Contracts
        #
        result.items.append(

            ContextValidationItem(

                name="API Contracts",

                passed=
                    context.api_contracts
                    is not None,

                details=
                    f"{len(context.api_contracts)} contracts."
            )
        )

        return result
    def ensure_valid(
        self,
        validation
    ):

        failures = [

            x

            for x in validation.items

            if not x.passed
        ]

        if failures:

            message = "\n".join(

                f"{item.name} : {item.details}"

                for item in failures
            )

            raise RuntimeError(

                "Reconstruction Context Validation Failed\n\n"

                + message
            )
    def print_report(
        self,
        validation
    ):

        print()

        print("=" * 80)
        print("RECONSTRUCTION CONTEXT VALIDATION")
        print("=" * 80)

        print()

        for item in validation.items:

            status = (

                "PASS"

                if item.passed

                else

                "FAIL"
            )

            print(
                f"[{status}]"
            )

            print(
                item.name
            )

            print(
                item.details
            )

            print()

        print(
            f"OVERALL: "
            f"{'PASS' if validation.valid else 'FAIL'}"
        )