# component_repository_report.py

class ComponentRepositoryReport:

    def build(
        self,
        metadata_registry
    ):

        report = {

            "component_count":
                len(
                    metadata_registry
                    .components
                ),

            "components":
                []
        }

        for component in (
            metadata_registry
            .components
            .values()
        ):

            report[
                "components"
            ].append({

                "name":
                    component.component_name,

                "module":
                    component.module_name,

                "category":
                    component.category
            })

        return report