
import React from "react";

interface ProgressBarProps {

    percent: number;
}

export default function
ProgressBar(
    props: ProgressBarProps
) {

    return (

        <div
            className="
                w-full
                border
                rounded
                h-6
            "
        >

            <div

                className="
                    bg-green-500
                    h-full
                    rounded
                    transition-all
                "

                style={{
                    width:
                        `${props.percent}%`
                }}
            />

        </div>
    );
}
