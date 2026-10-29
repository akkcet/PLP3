# component_library_generator.py

from pathlib import Path


class ComponentLibraryGenerator:

    def generate(
        self,
        output_dir: str
    ):

        root = Path(output_dir)

        root.mkdir(
            parents=True,
            exist_ok=True
        )

        self._generate_file_upload(
            root
        )

        self._generate_primary_button(
            root
        )

        self._generate_data_grid(
            root
        )

        self._generate_progress_bar(
            root
        )

        self._generate_import_summary(
            root
        )

        self._generate_status_panel(
            root
        )

        self._generate_multi_select(
            root
        )

        self._generate_wizard_stepper(
            root
        )

        self._generate_page_layout(
            root
        )

    # =====================================================
    # FILE UPLOAD
    # =====================================================

    def _generate_file_upload(
        self,
        root: Path
    ):

        content = """
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
"""

        (
            root /
            "FileUpload.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # =====================================================
    # PRIMARY BUTTON
    # =====================================================

    def _generate_primary_button(
        self,
        root: Path
    ):

        content = """
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
"""

        (
            root /
            "PrimaryButton.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # =====================================================
    # DATA GRID
    # =====================================================

    def _generate_data_grid(
        self,
        root: Path
    ):

        content = """
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
"""

        (
            root /
            "DataGrid.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # =====================================================
    # PROGRESS BAR
    # =====================================================

    def _generate_progress_bar(
        self,
        root: Path
    ):

        content = """
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
"""

        (
            root /
            "ProgressBar.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # =====================================================
    # IMPORT SUMMARY
    # =====================================================

    def _generate_import_summary(
        self,
        root: Path
    ):

        content = """
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
"""

        (
            root /
            "ImportSummary.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # =====================================================
    # STATUS PANEL
    # =====================================================

    def _generate_status_panel(
        self,
        root: Path
    ):

        content = """
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
"""

        (
            root /
            "StatusPanel.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # =====================================================
    # MULTI SELECT
    # =====================================================

    def _generate_multi_select(
        self,
        root: Path
    ):

        content = """
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
"""

        (
            root /
            "MultiSelect.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # =====================================================
    # WIZARD STEPPER
    # =====================================================

    def _generate_wizard_stepper(
        self,
        root: Path
    ):

        content = """
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
"""

        (
            root /
            "WizardStepper.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # =====================================================
    # PAGE LAYOUT
    # =====================================================

    def _generate_page_layout(
        self,
        root: Path
    ):

        content = """
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
"""

        (
            root /
            "PageLayout.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )