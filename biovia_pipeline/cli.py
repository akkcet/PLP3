"""
Command Line Interface for Biovia Pipeline Pilot Refactoring Suite
Allows independent testing of individual PLP components:
  1. custom-filter
  2. custom-manipulator
  3. notebook-connection
  4. experiment-query
  5. parse-model
  6. parse-plp
  7. run-pipeline
  8. test-components (runs end-to-end component suite)
"""
import argparse
import json
import sys
from pathlib import Path

from .plp_xml_parser import PlpProtocolXmlParser
from .pilotscript_parser import PilotScriptParser, PilotScriptEngine
from .custom_filter import custom_filter
from .custom_manipulator import custom_manipulator
from .notebook_connection import notebook_connection
from .experiment_query import experiment_query
from .xml_model_parser import parse_model_xml
from .pipeline_orchestrator import ElnDataTransferPipeline


def main():
    parser = argparse.ArgumentParser(
        description="Biovia Pipeline Pilot to Modular Python CLI - Component Testing Workbench"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available component testing commands")

    # Command 1: custom-filter
    p_filter = subparsers.add_parser("custom-filter", help="Execute Custom Filter component with a PLP script")
    p_filter.add_argument("expression", type=str, help="PilotScript expression (e.g. 'findsubstring(DocRelativepath, \".pdf\")>1')")
    p_filter.add_argument("--record", type=str, default="{}", help="JSON dictionary of record fields")
    p_filter.add_argument("--globals", type=str, default="{}", help="JSON dictionary of global variables")

    # Command 2: custom-manipulator
    p_manip = subparsers.add_parser("custom-manipulator", help="Execute Custom Manipulator component with a PLP script")
    p_manip.add_argument("expression", type=str, help="PilotScript statements (e.g. 'A := 10; B := A * 2; #local := 5;')")
    p_manip.add_argument("--record", type=str, default="{}", help="Incoming record JSON")
    p_manip.add_argument("--globals", type=str, default="{}", help="Incoming globals JSON")
    p_manip.add_argument("--locals", type=str, default="{}", help="Incoming locals JSON")
    p_manip.add_argument("--init", type=str, default="", help="Initial expression")
    p_manip.add_argument("--final", type=str, default="", help="Final expression")

    # Command 3: notebook-connection
    p_conn = subparsers.add_parser("notebook-connection", help="Execute Notebook Connection component")
    p_conn.add_argument("--name", type=str, default="NotebookConnection", help="Connection Name")
    p_conn.add_argument("--url", type=str, default="https://notebook.corp.internal/eln", help="Server URL")
    p_conn.add_argument("--auth", type=str, default="Use Notebook Session Token", help="Authentication Method")
    p_conn.add_argument("--user", type=str, default="arun.khuntia", help="Notebook Username")
    p_conn.add_argument("--token", type=str, default="", help="Session token")

    # Command 4: experiment-query
    p_query = subparsers.add_parser("experiment-query", help="Execute Experiment Query component via a Notebook Connection")
    p_query.add_argument("--connection", type=str, default="NotebookConnection", help="Connection Name")
    p_query.add_argument("--filter-by", type=str, default="Experiment Number", help="Filter By: 'Experiment Number', 'Title', 'Project'")
    p_query.add_argument("--filter-type", type=str, default="Equals", help="Filter Type: 'Equals', 'Contains', 'Starts With'")
    p_query.add_argument("--filter-val", type=str, default="EXP-2026-XRF-01", help="Filter Value")
    p_query.add_argument("--max", type=int, default=10, help="Maximum records")

    # Command 5: parse-plp
    p_plp = subparsers.add_parser("parse-plp", help="Parse a Biovia PLP XML protocol export")
    p_plp.add_argument("xml_file", type=str, help="Path to PLP protocol XML file")

    # Command 6: transpile
    p_transpile = subparsers.add_parser("transpile", help="Transpile a PilotScript expression into Python")
    p_transpile.add_argument("expression", type=str, help="PilotScript expression string")

    # Command 7: parse-model
    p_model = subparsers.add_parser("parse-model", help="Parse instrument model export XML")
    p_model.add_argument("xml_file", type=str, help="Path to instrument model XML")

    # Command 8: run-pipeline
    p_run = subparsers.add_parser("run-pipeline", help="Run automated data transfer pipeline")
    p_run.add_argument("--xml", required=True, type=str, help="Path to model XML")
    p_run.add_argument("--exp", required=True, type=str, help="Experiment number (e.g. EXP-2026-XRF-01)")
    p_run.add_argument("--mock", action="store_true", default=True, help="Run in mock/dry-run mode")

    # Command 9: test-components
    subparsers.add_parser("test-components", help="Run full independent component unit test suite")

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
        print("\n--- Pipeline Pilot 'Custom Filter' Component Result ---")
        print(f"PLP Script Expression: {args.expression}")
        print(f"Record Context:        {record_dict}")
        print(f"Globals Context:       {globals_dict}")
        print(f"Filter Passed:         {passed}\n")

    elif args.command == "custom-manipulator":
        try:
            record_dict = json.loads(args.record)
        except Exception:
            record_dict = {}
        try:
            globals_dict = json.loads(args.globals)
        except Exception:
            globals_dict = {}
        try:
            locals_dict = json.loads(args.locals)
        except Exception:
            locals_dict = {}

        res_rec, res_globs, res_locs = custom_manipulator(
            expression=args.expression,
            record=record_dict,
            globals_dict=globals_dict,
            locals_dict=locals_dict,
            initial_expression=args.init if args.init else None,
            final_expression=args.final if args.final else None
        )
        print("\n--- Pipeline Pilot 'Custom Manipulator' Component Result ---")
        print(f"PLP Expression:    {args.expression}")
        print(f"Initial Script:    {args.init or '(None)'}")
        print(f"Final Script:      {args.final or '(None)'}")
        print(f"Manipulated Record: {json.dumps(res_rec, indent=2)}")
        print(f"Updated Globals:    {json.dumps(res_globs, indent=2)}")
        print(f"Updated Locals:     {json.dumps(res_locs, indent=2)}\n")

    elif args.command == "notebook-connection":
        conn = notebook_connection(
            connection_name=args.name,
            server_url=args.url,
            authentication_method=args.auth,
            username=args.user,
            session_token=args.token or None,
            mock_mode=True
        )
        print("\n--- Pipeline Pilot 'Notebook Connection' Component Result ---")
        print(f"Connection Name:       {conn.connection_name}")
        print(f"Server URL:            {conn.server_url}")
        print(f"API Endpoint:          {conn.api_endpoint}")
        print(f"Authentication Method: {conn.auth_method}")
        print(f"Username:              {conn.username}")
        print(f"Session Token:         {conn.session_token}")
        print(f"Encoded Hash String:   {conn.to_hash_string()[:50]}...")
        print(f"Connection Hash Dict:  {json.dumps(conn.raw_connection_hash, indent=2)}\n")

    elif args.command == "experiment-query":
        conn = notebook_connection(connection_name=args.connection, mock_mode=True)
        records = experiment_query(
            connection=conn,
            filter_by=args.filter_by,
            filter_type=args.filter_type,
            filter_value=args.filter_val,
            maximum=args.max,
            mock_data_fallback=True
        )
        print(f"\n--- Pipeline Pilot 'Experiment Query' Component Result ({len(records)} found) ---")
        for rec in records:
            print(f"  * Experiment #{rec.get('experimentNumber')} (ID: {rec.get('id')})")
            print(f"    Title:             {rec.get('title')}")
            print(f"    Author:            {rec.get('author')}")
            print(f"    Signing Status:    {rec.get('signingStatus')}")
            print(f"    Submission Status: {rec.get('submissionStatus')}")
            print(f"    Simple Sections:   {len(rec.get('simplesections', []))} sections")
            for s in rec.get('simplesections', []):
                print(f"      - [{s.get('sectionType')}] {s.get('title')}")
            print()

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

    elif args.command == "test-components":
        import unittest
        suite = unittest.defaultTestLoader.discover("tests")
        runner = unittest.TextTestRunner(verbosity=2)
        res = runner.run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
