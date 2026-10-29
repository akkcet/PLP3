"""
screenhot_ocr_engine.py

Extracts text from screenshots and returns
a normalized OCR representation.

Provider agnostic.

Current implementation:
- Tesseract-compatible
- Easy to replace with Gemini Vision
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import re


@dataclass
class OCRLine:
    text: str
    confidence: float


@dataclass
class OCRResult:
    image_path: str
    lines: List[OCRLine] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return "\n".join(x.text for x in self.lines)


class ScreenshotOCREngine:

    def __init__(self):
        pass

    def extract_text(
        self,
        image_path: str
    ) -> OCRResult:

        try:
            import pytesseract
            from PIL import Image

        except ImportError as ex:
            raise RuntimeError(
                "Please install pytesseract and pillow"
            ) from ex

        image = Image.open(image_path)

        raw = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT
        )

        lines = []

        for txt, conf in zip(
            raw["text"],
            raw["conf"]
        ):

            txt = str(txt).strip()

            if not txt:
                continue

            try:
                c = float(conf)
            except:
                c = 0.0

            lines.append(
                OCRLine(
                    text=txt,
                    confidence=c
                )
            )

        return OCRResult(
            image_path=image_path,
            lines=lines
        )

    @staticmethod
    def normalize_text(text: str) -> str:

        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()