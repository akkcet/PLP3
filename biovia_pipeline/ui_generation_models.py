# ui_generation_models.py

from dataclasses import dataclass


@dataclass
class GeneratedUILabel:

    control_type: str

    label: str

    placeholder: str = ""


@dataclass
class GeneratedPage:

    title: str

    controls: list


@dataclass
class GeneratedWizard:

    workflow_name: str

    pages: list