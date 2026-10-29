# ai_request_optimizer.py

from dataclasses import dataclass


# ============================================================
# MODELS
# ============================================================

@dataclass
class OptimizedAIRequest:

    frontend_prompt: str

    backend_prompt: str

    missing_components_prompt: str

    combined_prompt: str


# ============================================================
# OPTIMIZER
# ============================================================

class AIRequestOptimizer:

    def build(
        self,
        context,
        reconstruction_prompt
    ):

        combined = f'''
{reconstruction_prompt.system_prompt}

===================================================

{reconstruction_prompt.user_prompt}

===================================================

TASKS

1. Generate React TSX Pages

2. Generate FastAPI Backend

3. Generate Missing Components

4. Generate API Contracts

5. Generate Runtime Notes

Return all outputs in a structured format.
'''

        return OptimizedAIRequest(

            frontend_prompt="",

            backend_prompt="",

            missing_components_prompt="",

            combined_prompt=
                combined
        )