
import React from "react";

interface MultiSelectProps {

    options?: string[];
}

export default function
MultiSelect(
    props: MultiSelectProps
) {

    const options =
        props.options ?? [];

    return (

        <select

            multiple

            className="
                border
                rounded
                w-full
                min-h-40
            "
        >

            {
                options.map(

                    (
                        option
                    ) => (

                        <option
                            key={option}
                        >

                            {option}

                        </option>
                    )
                )
            }

        </select>
    );
}
