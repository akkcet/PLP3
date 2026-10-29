# component_test_runner.py

import subprocess


class ComponentTestRunner:

    def run(
        self,
        test_file
    ):

        result = subprocess.run(

            [
                "pytest",
                str(test_file),
                "-q"
            ],

            capture_output=True,

            text=True
        )

        return {

            "return_code":
                result.returncode,

            "stdout":
                result.stdout,

            "stderr":
                result.stderr,

            "passed":
                result.returncode == 0
        }