
import React from "react";

interface PrimaryButtonProps {

    children:
        React.ReactNode;

    onClick?: () => void;

    disabled?: boolean;
}

export default function
PrimaryButton(
    props: PrimaryButtonProps
) {

    return (

        <button

            onClick={
                props.onClick
            }

            disabled={
                props.disabled
            }

            className="
                bg-blue-600
                hover:bg-blue-500
                text-white
                px-4
                py-2
                rounded-md
                disabled:opacity-50
            "
        >

            {props.children}

        </button>
    );
}
