from dataclasses import dataclass, field
from typing import List


# =====================================================
# UI SCHEMA MODELS
# =====================================================

@dataclass
class UIComponent:

    component_id: str

    component_type: str

    label: str

    props: dict = field(
        default_factory=dict
    )


@dataclass
class UIPage:

    page_name: str

    route: str

    components: List[UIComponent] = field(
        default_factory=list
    )


@dataclass
class UIApplicationSchema:

    app_name: str

    pages: List[UIPage] = field(
        default_factory=list
    )


# =====================================================
# GENERATOR
# =====================================================

class UISchemaGenerator:

    def generate(
        self,
        application_blueprint
    ) -> UIApplicationSchema:

        schema = UIApplicationSchema(
            app_name=
                application_blueprint.app_name
        )

        for page in application_blueprint.pages:

            ui_page = UIPage(
                page_name=page.page_name,
                route=page.route
            )

            for idx, control in enumerate(
                page.controls
            ):

                ui_page.components.append(
                    UIComponent(
                        component_id=
                            f"{control.lower()}_{idx}",

                        component_type=control,

                        label=control
                    )
                )

            schema.pages.append(
                ui_page
            )

        return schema