# generated_application_validator.py

from dataclasses import dataclass, field
from pathlib import Path
import subprocess
import sys


# ============================================================
# MODELS
# ============================================================

@dataclass
class ValidationIssue:

    category: str

    severity: str

    message: str


@dataclass
class ApplicationValidationResult:

    passed: bool

    issues: list[ValidationIssue] = field(
        default_factory=list
    )
class GeneratedApplicationValidator:

    def validate(
        self,
        application_root
    ):

        result = (
            ApplicationValidationResult(
                passed=True
            )
        )

        root = Path(
            application_root
        )

        self._validate_structure(
            root,
            result
        )

        self._validate_python(
            root,
            result
        )

        self._validate_tsx(
            root,
            result
        )

        if result.issues:

            result.passed = False

        return result
    def _validate_structure(
        self,
        root,
        result
    ):

        expected = [

            root / "frontend",

            root / "backend",

            root / "frontend" / "src",

            root / "backend" / "workflows"
        ]

        for item in expected:

            if not item.exists():

                result.issues.append(

                    ValidationIssue(

                        category=
                            "Structure",

                        severity=
                            "HIGH",

                        message=
                            f"Missing: {item}"
                    )
                )
    def _validate_python(
        self,
        root,
        result
    ):

        backend = (
            root / "backend"
        )

        for file in (
            backend.rglob("*.py")
        ):

            command = [

                sys.executable,

                "-m",

                "py_compile",

                str(file)
            ]

            process = subprocess.run(

                command,

                capture_output=True,

                text=True
            )

            if process.returncode != 0:

                result.issues.append(

                    ValidationIssue(

                        category=
                            "Python",

                        severity=
                            "HIGH",

                        message=
                            f"{file.name}: "
                            f"{process.stderr}"
                    )
                )
    def _validate_tsx(
        self,
        root,
        result
    ):

        frontend = (
            root
            / "frontend"
            / "src"
        )

        for file in (
            frontend.rglob("*.tsx")
        ):

            text = file.read_text(
                encoding="utf-8"
            )

            if "&lt;" in text:

                result.issues.append(

                    ValidationIssue(

                        category=
                            "React",

                        severity=
                            "HIGH",

                        message=
                            f"{file.name}: "
                            f"contains escaped JSX"
                    )
                )

            if "from " in text and "import" not in text:

                result.issues.append(

                    ValidationIssue(

                        category=
                            "React",

                        severity=
                            "MEDIUM",

                        message=
                            f"{file.name}: "
                            f"suspicious import"
                    )
                )
    def print_report(
        self,
        report
    ):

        print()

        print("=" * 80)

        print(
            "APPLICATION VALIDATION"
        )

        print("=" * 80)

        print()

        if report.passed:

            print(
                "PASSED"
            )

            return

        for issue in (
            report.issues
        ):

            print(
                f"[{issue.severity}] "
                f"{issue.category}"
            )

            print(
                issue.message
            )

            print()