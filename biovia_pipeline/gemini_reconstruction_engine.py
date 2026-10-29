# gemini_reconstruction_engine.py

from dataclasses import dataclass
import time
from google import genai


# ============================================================
# MODELS
# ============================================================

@dataclass
class GeminiGenerationResult:

    prompt: str

    generated_text: str

    success: bool


# ============================================================
# ENGINE
# ============================================================

class GeminiReconstructionEngine:

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model: str = "gemini-2.5-flash"
    ):
        self.model = model
        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )

        self.model = model

    # ========================================================
    # GENERATE
    # ========================================================

    def generate(
        self,
        reconstruction_prompt
    ):

        #
        # Plain string prompt
        #
        if isinstance(
            reconstruction_prompt,
            str
        ):

            combined_prompt = (
                reconstruction_prompt
            )

        #
        # ReconstructionPrompt object
        #
        else:

            combined_prompt = f"""

    SYSTEM PROMPT

    {reconstruction_prompt.system_prompt}


    USER PROMPT

    {reconstruction_prompt.user_prompt}

    """
        start = time.time()
        response = (
            self.client.models.generate_content(
                model=self.model,
                contents=combined_prompt
            )
        )
        print(
            f"Gemini completed in "
            f"{round(time.time() - start, 2)} sec"
        )
        return GeminiGenerationResult(

            prompt=
                combined_prompt,

            generated_text=
                response.text,

            success=True
        )
    def generate_json(
        self,
        reconstruction_prompt
    ):

        prompt = f"""

    Return ONLY JSON.

    Schema:

    {{
    "frontend": "...",
    "backend": "...",
    "notes": "..."
    }}

    {reconstruction_prompt.user_prompt}

    """

        response = (
            self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
        )

        return response.text
    