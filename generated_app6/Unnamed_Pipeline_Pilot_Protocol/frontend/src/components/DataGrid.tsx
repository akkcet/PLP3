
import React from "react";

interface DataGridProps {

    title?: string;

    data?: Record<
        string,
        any
    >[];
}

export default function
DataGrid(
    props: DataGridProps
) {

    const data =
        props.data ?? [];

    return (

        <div
            className="
                border
                rounded-md
                p-4
            "
        >

            <h3
                className="
                    font-semibold
                    mb-4
                "
            >
                {props.title ??
                    "Results"}
            </h3>

            <pre>

                {
                    JSON.stringify(
                        data,
                        null,
                        2
                    )
                }

            </pre>

        </div>
    );
}
