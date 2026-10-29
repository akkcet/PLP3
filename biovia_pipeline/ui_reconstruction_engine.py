from dataclasses import dataclass, field
from typing import List


@dataclass
class UIControlSchema:
    id: str
    type: str
    label: str
    source_component: str


@dataclass
class UIScreenSchema:
    screen_id: str
    screen_name: str

    controls: List[UIControlSchema] = field(
        default_factory=list
    )


@dataclass
class UIApplicationSchema:
    application_name: str

    screens: List[UIScreenSchema] = field(
        default_factory=list
    )


class UIReconstructionEngine:

    def reconstruct(
        self,
        protocol_analysis,
        screenshot_models
    ) -> UIApplicationSchema:

        schema = UIApplicationSchema(
            application_name=
            getattr(
                protocol_analysis,
                "protocol_name",
                "Migrated PLP App"
            )
        )

        screen_counter = 1

        for screenshot in screenshot_models:

            screen = UIScreenSchema(
                screen_id=f"screen_{screen_counter:03d}",
                screen_name=screenshot.screenshot_name
            )

            control_counter = 1

            for button in screenshot.buttons:

                screen.controls.append(
                    UIControlSchema(
                        id=f"btn_{control_counter}",
                        type="button",
                        label=button.label,
                        source_component=""
                    )
                )

                control_counter += 1

            for inp in screenshot.inputs:

                screen.controls.append(
                    UIControlSchema(
                        id=f"txt_{control_counter}",
                        type="textbox",
                        label=inp.label,
                        source_component=""
                    )
                )

                control_counter += 1

            for upload in screenshot.uploads:

                screen.controls.append(
                    UIControlSchema(
                        id=f"upl_{control_counter}",
                        type="file_upload",
                        label=upload.label,
                        source_component=""
                    )
                )

                control_counter += 1

            schema.screens.append(screen)

            screen_counter += 1

        return schema