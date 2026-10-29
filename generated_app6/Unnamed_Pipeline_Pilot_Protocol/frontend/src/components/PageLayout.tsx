
import React from "react";

interface PageLayoutProps {

    title: string;

    children:
        React.ReactNode;
}

export default function
PageLayout(
    props: PageLayoutProps
) {

    return (

        <div
            className="
                max-w-7xl
                mx-auto
                p-8
            "
        >

            <h1
                className="
                    text-3xl
                    font-bold
                    mb-8
                "
            >
                {props.title}
            </h1>

            {props.children}

        </div>
    );
}
