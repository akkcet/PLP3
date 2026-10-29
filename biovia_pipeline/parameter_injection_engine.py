# parameter_injection_engine.py

class ParameterInjectionEngine:

    def build_function_call(
        self,
        function_name,
        parameters
    ):

        lines = []

        lines.append(
            f"{function_name}("
        )

        for key, value in (
            parameters.items()
        ):

            lines.append(

                f'    {self._sanitize(key)}="{value}",'
            )

        lines.append(
            ")"
        )

        return "\n".join(
            lines
        )

    def _sanitize(
        self,
        parameter_name
    ):

        return (
            parameter_name
            .replace(" ", "_")
            .replace("-", "_")
            .lower()
        )