#workflow_label_extractor.py
from dataclasses import dataclass, field
from typing import List, Dict


# ============================================================
# MODELS
# ============================================================

@dataclass
class WorkflowStep:
    """
    Represents a single business step.
    """

    step_id: str

    name: str

    action_type: str

    confidence: float = 1.0

    source_labels: List[str] = field(
        default_factory=list
    )


@dataclass
class WorkflowDefinition:
    """
    Final workflow representation.
    """

    workflow_name: str

    steps: List[WorkflowStep]

    workflow_type: str

    confidence: float


# ============================================================
# RULES
# ============================================================

STEP_PATTERNS = {

    "upload": {

        "keywords": [
            "browse",
            "upload",
            "choose file",
            "select file"
        ],

        "action": "UPLOAD"
    },

    "parse": {

        "keywords": [
            "process xml",
            "parse xml",
            "analyze",
            "validate"
        ],

        "action": "PROCESS"
    },

    "select": {

        "keywords": [
            "select files",
            "available files",
            "choose files",
            "file list"
        ],

        "action": "SELECTION"
    },

    "import": {

        "keywords": [
            "import",
            "attach",
            "import files",
            "import files to eln"
        ],

        "action": "IMPORT"
    },

    "review": {

        "keywords": [
            "preview",
            "review",
            "verify",
            "summary"
        ],

        "action": "REVIEW"
    },

    "complete": {

        "keywords": [
            "completed",
            "finished",
            "success",
            "done"
        ],

        "action": "COMPLETE"
    }
}


# ============================================================
# EXTRACTOR
# ============================================================

class WorkflowLabelExtractor:

    def extract(
        self,
        labels: List[str]
    ) -> WorkflowDefinition:

        detected_steps = []

        lower_labels = [
            l.lower()
            for l in labels
        ]

        #
        # Detect steps
        #
        for step_type, rule in (
            STEP_PATTERNS.items()
        ):

            matches = []

            for label in lower_labels:

                for keyword in rule["keywords"]:

                    if keyword in label:

                        matches.append(label)

            if matches:

                detected_steps.append(

                    WorkflowStep(
                        step_id=f"step_{len(detected_steps)+1}",

                        name=self._prettify(
                            step_type
                        ),

                        action_type=rule["action"],

                        source_labels=matches,

                        confidence=0.9
                    )
                )

        #
        # Determine workflow type
        #
        workflow_type = self._detect_workflow_type(
            lower_labels
        )

        workflow_name = (
            self._generate_workflow_name(
                workflow_type
            )
        )

        confidence = self._calculate_confidence(
            detected_steps
        )

        return WorkflowDefinition(

            workflow_name=workflow_name,

            workflow_type=workflow_type,

            steps=detected_steps,

            confidence=confidence
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def _prettify(
        self,
        value: str
    ):

        return (
            value
            .replace("_", " ")
            .title()
        )

    def _calculate_confidence(
        self,
        steps: List[WorkflowStep]
    ):

        if not steps:
            return 0.0

        return round(

            sum(
                x.confidence
                for x in steps
            )
            /
            len(steps),

            2
        )

    def _detect_workflow_type(
        self,
        labels: List[str]
    ):

        text = " ".join(labels)

        #
        # Data Model Import
        #
        if (
            "xml" in text
            and "import" in text
        ):

            return "DATA_MODEL_IMPORT"

        #
        # ELN Attachment
        #
        if (
            "eln" in text
            or "notebook" in text
        ):

            return "ELN_ATTACHMENT"

        #
        # Generic File Import
        #
        if (
            "file"
            in text
        ):

            return "FILE_IMPORT"

        return "GENERIC"

    def _generate_workflow_name(
        self,
        workflow_type: str
    ):

        mapping = {

            "DATA_MODEL_IMPORT":
                "Data Model Import Workflow",

            "ELN_ATTACHMENT":
                "ELN Attachment Workflow",

            "FILE_IMPORT":
                "File Import Workflow",

            "GENERIC":
                "Generated Workflow"
        }

        return mapping.get(
            workflow_type,
            "Generated Workflow"
        )

    # ========================================================
    # DEBUG
    # ========================================================

    def print_workflow(
        self,
        workflow: WorkflowDefinition
    ):

        print()

        print(
            "=" * 50
        )

        print(
            workflow.workflow_name
        )

        print(
            "=" * 50
        )

        print()

        print(
            "Workflow Type:",
            workflow.workflow_type
        )

        print(
            "Confidence:",
            workflow.confidence
        )

        print()

        for step in workflow.steps:

            print(
                f"{step.step_id}"
            )

            print(
                f"Name: {step.name}"
            )

            print(
                f"Action: {step.action_type}"
            )

            print(
                f"Labels: {step.source_labels}"
            )

            print()
