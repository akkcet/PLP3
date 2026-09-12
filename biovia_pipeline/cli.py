"""
Command Line Interface for Biovia Pipeline Pilot Refactoring Suite
"""
import argparse
import json
import sys
from pathlib import Path

from .plp_xml_parser import PlpProtocolXmlParser
from .pilotscript_parser import PilotScriptParser, PilotScriptEngine
from .custom_filter import custom_filter
from .xml_model_parser import parse_model_xml
from .pipeline_orchestrator import ElnDataTransferPipeline


def main():
    parser = argparse.ArgumentParser(
        description="Biovia Pipeline Pilot to Modular Python CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command 1: custom-filter (Single function for Custom Filter component taking PLP script)
    p_filter = subparsers.add_parser("custom-filter", help="Execute Custom Filter component with a PLP script")
    p_filter.add_argument("expression", type=str, help="PilotScript expression (e.g. 'findsubstring(DocRelativepath, \".pdf\")>1')")
    p_filter.add_argument("--record", type=str, default="{}", help="JSON dictionary of record fields (e.g. '{\"DocRelativepath\": \"doc.pdf\"}')")
    p_filter.add_argument("--globals", type=str, default="{}", help="JSON dictionary of global variables (e.g. '{\"experiment_number\": \"EXP-01\"}')")

    # Command 2: parse-plp
    p_plp = subparsers.add_parser("parse-plp", help="Parse a Biovia PLP XML protocol export")
    p_plp.add_argument("xml_file", type=str, help="Path to PLP protocol XML file")

    # Command 2: transpile
    p_transpile = subparsers.add_parser("transpile", help="Transpile a PilotScript expression into Python")
    p_transpile.add_argument("expression", type=str, help="PilotScript expression string")

    # Command 3: parse-model
    p_model = subparsers.add_parser("parse-model", help="Parse instrument model export XML")
    p_model.add_argument("xml_file", type=str, help="Path to instrument model XML")

    # Command 4: run-pipeline
    p_run = subparsers.add_parser("run-pipeline", help="Run automated data transfer pipeline")
    p_run.add_argument("--xml", required=True, type=str, help="Path to model XML")
    p_run.add_argument("--exp", required=True, type=str, help="Experiment number (e.g. EXP-2026-XRF-01)")
    p_run.add_argument("--mock", action="store_true", default=True, help="Run in mock/dry-run mode")

    args = parser.parse_args()

    if args.command == "custom-filter":
        try:
            record_dict = json.loads(args.record)
        except Exception:
            record_dict = {}
        try:
            globals_dict = json.loads(args.globals)
        except Exception:
            globals_dict = {}

        passed = custom_filter(
            expression=args.expression,
            record=record_dict,
            globals_dict=globals_dict
        )
        print("\n--- Pipeline Pilot Custom Filter Component ---")
        print(f"PLP Script Expression: {args.expression}")
        print(f"Record Context:        {record_dict}")
        print(f"Globals Context:       {globals_dict}")
        print(f"Result (Filter Pass):  {passed}\n")

    elif args.command == "parse-plp":
        parser_obj = PlpProtocolXmlParser(args.xml_file)
        components = parser_obj.parse()
        print(f"\n[+] Successfully parsed PLP Protocol: {len(components)} root components found.\n")
        for comp in components:
            print(f"  Component #{comp.local_id.rjust(2)}: {comp.name}")
            print(f"    -> Mapped Python Module:   {comp.mapped_python_module}")
            print(f"    -> Mapped Python Function: {comp.mapped_python_function}")
            if comp.subcomponents:
                print(f"    -> Subcomponents: {len(comp.subcomponents)} nested steps")
                for sub in comp.subcomponents:
                    print(f"       [{sub.local_id}] {sub.name} -> {sub.mapped_python_function}")
            print()

    elif args.command == "transpile":
        parser_obj = PilotScriptParser(args.expression)
        code = parser_obj.transpile_to_python()
        print("\n--- Transpiled Python Code ---")
        print(code)
        print("\n--- AST Operations ---")
        for op in parser_obj.ast_operations:
            print(f"  * {op}")

    elif args.command == "parse-model":
        meta = parse_model_xml(args.xml_file)
        print(f"\n[+] Parsed Model XML: Section Name = '{meta.section_name}'")
        print(f"[+] Base Storage Path: '{meta.base_location}'")
        print(f"[+] Discovered Files ({len(meta.files)}):")
        for f in meta.files:
            print(f"  * {f.file_name} ({f.extension}) -> Title: '{f.section_title}'")

    elif args.command == "run-pipeline":
        pipeline = ElnDataTransferPipeline(mock_mode=args.mock)
        res = pipeline.run(
            xml_source=args.xml,
            experiment_number=args.exp
        )
        print("\n--- Pipeline Execution Result ---")
        print(f"Success:           {res.success}")
        print(f"Experiment Number: {res.experiment_number}")
        print(f"Experiment ID:     {res.experiment_id}")
        print(f"Files Processed:   {res.files_processed}")
        print(f"Duration:          {res.duration_seconds}s")
        print("\nCreated Sections in Biovia Notebook:")
        for s in res.sections_created:
            print(f"  * [{s['sectionType'].upper()}] {s['sectionTitle']} (ID: {s['sectionId']}) <- {s['fileName']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
