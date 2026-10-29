# react_service_generator.py

from pathlib import Path


class ReactServiceGenerator:

    def generate(
        self,
        api_contracts,
        output_dir
    ):

        root = Path(output_dir)

        root.mkdir(
            parents=True,
            exist_ok=True
        )

        functions = []

        for contract in (
            api_contracts.contracts
        ):

            functions.append(

                self._generate_function(
                    contract
                )
            )

        content = (
            "\n".join(functions)
        )

        (
            root /
            "generatedServices.ts"
        ).write_text(
            content,
            encoding="utf-8"
        )

    def _generate_function(
        self,
        contract
    ):

        return f"""
export async function
{contract.endpoint_name}(payload: any) {{

    const response =
        await fetch(
            "{contract.route}",

            {{
                method: "{contract.method}",

                headers: {{

                    "Content-Type":
                        "application/json"
                }},

                body: JSON.stringify(
                    payload
                )
            }}
        );

    return response.json();
}}
"""
