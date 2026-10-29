# ai_response_splitter.py

from dataclasses import dataclass


@dataclass
class SplitAIResponse:

    frontend_code: str

    backend_code: str

    component_code: str

    notes: str


class AIResponseSplitter:

    def split(
        self,
        response_text
    ):

        #
        # Initial version
        # Simple parser.
        #

        return SplitAIResponse(

            frontend_code=
                response_text,

            backend_code=
                response_text,

            component_code=
                response_text,

            notes=""
        )
    def generate_optimized(
        self,
        optimized_request
    ):

        return self.generate(
            optimized_request.combined_prompt
        )