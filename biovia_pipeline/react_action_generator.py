# react_action_generator.py

class ReactActionGenerator:

    def generate(
        self,
        action_bindings
    ):

        functions = []

        for action in (
            action_bindings
        ):

            name = (
                action.action_name
                .replace(" ", "")
            )

            functions.append(

f"""
async function {name}() {{

    const result =
        await fetch(

            "{action.api_endpoint}",

            {{
                method: "POST"
            }}
        );

    return result.json();
}}
"""
            )

        return "\n".join(
            functions
        )