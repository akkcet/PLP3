# test_reconstruction.py

from pathlib import Path

from biovia_pipeline.one_click_reconstruction_engine import (
    OneClickReconstructionEngine
)
from dataclasses import dataclass
from typing import List


@dataclass
class TemplateMatch:

    template_name: str

    confidence: float

    missing_components: List[str]

    template: object
xml = Path(
    "tests/Data model UI.xml"
).read_text(
    encoding="utf-8"
)

engine = (
    OneClickReconstructionEngine()
)

result = engine.generate(

    protocol_xml=xml,

    screenshots=[

        "tests/Picture1.png",

        "tests/Picture2.png",

        "tests/Picture3.png"
    ],

    business_description="""
    User uploads XML.

    XML is parsed.

    Files are selected.

    Files are imported
    into ELN.
    """
    ,
    ui_pattern="single_page"
)

print(result)