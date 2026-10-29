
import React from "react";

interface ImportSummaryProps {

    successCount?: number;

    failureCount?: number;
}

export default function
ImportSummary(
    props: ImportSummaryProps
) {

    return (

        <div
            className="
                border
                rounded-md
                p-4
            "
        >

            <h2
                className="
                    text-lg
                    font-bold
                    mb-4
                "
            >
                Import Summary
            </h2>

            <p>

                Successful:
                {props.successCount ?? 0}

            </p>

            <p>

                Failed:
                {props.failureCount ?? 0}

            </p>

        </div>
    );
}
