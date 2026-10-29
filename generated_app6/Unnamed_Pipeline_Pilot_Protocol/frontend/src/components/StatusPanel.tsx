
import React from "react";

interface StatusPanelProps {

    status?: string;
}

export default function
StatusPanel(
    props: StatusPanelProps
) {

    return (

        <div
            className="
                border
                bg-slate-50
                rounded-md
                p-4
            "
        >

            <strong>

                Status:

            </strong>

            {" "}

            {
                props.status ??
                "Ready"
            }

        </div>
    );
}
