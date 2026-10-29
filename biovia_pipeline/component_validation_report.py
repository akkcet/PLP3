# component_validation_report.py

from dataclasses import dataclass


@dataclass
class ComponentValidationReport:

    component_name: str

    quality_score: float

    passed: bool

    details: str