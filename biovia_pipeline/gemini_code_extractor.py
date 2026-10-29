import json


class GeminiCodeExtractor:

    def extract(
        self,
        json_response
    ):

        data = json.loads(
            json_response
        )

        return {

            "frontend":
                data.get(
                    "frontend",
                    ""
                ),

            "backend":
                data.get(
                    "backend",
                    ""
                ),

            "notes":
                data.get(
                    "notes",
                    ""
                )
        }