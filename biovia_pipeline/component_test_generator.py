# component_test_generator.py

from dataclasses import dataclass
from pathlib import Path


# ============================================================
# MODELS
# ============================================================

@dataclass
class GeneratedTest:

    component_name: str

    test_file_name: str

    test_code: str


# ============================================================
# GENERATOR
# ============================================================

class ComponentTestGenerator:

    def generate(
        self,
        generated_component
    ) -> GeneratedTest:

        component_name = (
            generated_component
            .component_name
        )

        module_name = (
            component_name
            .replace(" ", "_")
            .replace("-", "_")
            .lower()
        )

        function_name = module_name

        test_file_name = (
            f"test_{module_name}.py"
        )

        test_code = f'''
import pytest

from generated_components.{module_name} import (
    {function_name}
)


def test_{function_name}_returns_value():

    result = {function_name}()

    assert result is not None


def test_{function_name}_returns_expected_type():

    result = {function_name}()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
'''

        return GeneratedTest(

            component_name=
                component_name,

            test_file_name=
                test_file_name,

            test_code=
                test_code
        )

    # ========================================================
    # SAVE
    # ========================================================

    def save(
        self,
        generated_test,
        output_dir
    ):

        output_dir = Path(
            output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        path = (

            output_dir

            /

            generated_test
            .test_file_name
        )

        path.write_text(

            generated_test.test_code,

            encoding="utf-8"
        )

        return path

    # ========================================================
    # DEBUG
    # ========================================================

    def print_test(
        self,
        generated_test
    ):

        print()

        print("=" * 80)

        print(
            generated_test.component_name
        )

        print("=" * 80)

        print()

        print(
            generated_test.test_code
        )