# missing_component_extractor.py

from dataclasses import dataclass


class MissingComponentExtractor:

    def extract(
        self,
        protocol_analysis
    ):

        missing = []

        for node in (
            protocol_analysis.nodes
        ):

            status = str(
                node.status
            )

            if (
                "MISSING"
                in status
            ):

                missing.append(
                    node
                )

        return missing