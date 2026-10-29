
import React from "react";

interface FileUploadProps {

    label?: string;

    accept?: string;

    onChange?: (
        file: File | null
    ) => void;
}

export default function FileUpload(
    props: FileUploadProps
) {

    return (

        <div
            className="
                flex
                flex-col
                gap-2
            "
        >

            <label
                className="
                    text-sm
                    font-medium
                "
            >
                {props.label ??
                 "Choose File"}
            </label>

            <input

                type="file"

                accept={
                    props.accept
                }

                onChange={(
                    e
                ) => {

                    props.onChange?.(

                        e.target.files?.[0]
                        ?? null

                    );
                }}
            />

        </div>
    );
}
