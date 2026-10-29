
import React from "react";

interface WizardStepperProps {

    steps: string[];

    activeStep: number;
}

export default function
WizardStepper(
    props: WizardStepperProps
) {

    return (

        <div
            className="
                flex
                gap-4
                mb-8
                flex-wrap
            "
        >

            {
                props.steps.map(

                    (
                        step,
                        index
                    ) => (

                        <div

                            key={index}

                            className={

                                index ===
                                props.activeStep

                                ?

                                `
                                px-4
                                py-2
                                rounded
                                bg-blue-600
                                text-white
                                `

                                :

                                `
                                px-4
                                py-2
                                rounded
                                bg-slate-200
                                `
                            }
                        >

                            {step}

                        </div>
                    )
                )
            }

        </div>
    );
}
