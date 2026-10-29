# react_state_generator.py

class ReactStateGenerator:

    def generate(
        self,
        state_bindings
    ):

        lines = []

        for state in state_bindings:

            state_name = (
                state.state_name
            )

            setter = (

                "set" +
                state_name[0].upper() +
                state_name[1:]
            )

            default_value = (
                self._default_value(
                    state.state_type
                )
            )

            lines.append(

                f"""
const [
    {state_name},
    {setter}
] = useState(
    {default_value}
);
"""
            )

        return "\n".join(
            lines
        )

    def _default_value(
        self,
        state_type
    ):

        mapping = {

            "string":
                '""',

            "File | null":
                "null",

            "any[]":
                "[]"
        }

        return mapping.get(
            state_type,
            "null"
        )