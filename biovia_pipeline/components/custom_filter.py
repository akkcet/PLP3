"""
Biovia Pipeline Pilot 'Custom Filter' Component
Implements the single unified function for the 'Custom Filter' component,
which takes a PLP script (PilotScript expression) as its primary argument.
"""
from typing import Any, Dict, Optional
from .pilotscript_parser import PilotScriptEngine, PilotScriptParser


def custom_filter(
    expression: str,
    record: Optional[Dict[str, Any]] = None,
    globals_dict: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Unified implementation of the Biovia Pipeline Pilot 'Custom Filter' component.

    In Pipeline Pilot, 'Custom Filter' is a single component configured with an
    'Expression' argument written in PilotScript (PLP script). This single function
    accepts that PLP script expression and evaluates whether an incoming data record
    passes the filter (True) or is filtered out (False).

    Parameters:
        expression (str): The PLP script / PilotScript expression string.
            Examples:
              - "findsubstring(DocRelativepath, '.pdf')>1"
              - "findsubstring(DocRelativepath, '.xlsx')>1"
              - "@experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''"
              - "@xml is defined and @xml ne '' and @filelist is eq ''"
              - "@filelist is defined and @filelist is ne ''"
        record (dict, optional): Current data record attributes (e.g. {'DocRelativepath': 'test.pdf'})
        globals_dict (dict, optional): Global workflow variables (e.g. {'experiment_number': 'EXP-2026-01'})

    Returns:
        bool: True if the record/condition passes the filter, False otherwise.
    """
    if not expression or not expression.strip():
        # Pipeline Pilot default: empty expression passes through
        return True

    rec = record if record is not None else {}
    globs = globals_dict if globals_dict is not None else {}

    # Evaluate the PLP script expression using the safe PilotScriptEngine
    result = PilotScriptEngine.evaluate(
        expression=expression.strip(),
        globals_ctx=globs,
        record_ctx=rec
    )
    return bool(result)
