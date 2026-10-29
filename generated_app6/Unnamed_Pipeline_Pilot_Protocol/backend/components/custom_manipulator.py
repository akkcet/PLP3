"""
Biovia Pipeline Pilot 'Custom Manipulator (PilotScript)' Component
Accepts a PLP PilotScript expression (or list of expressions separated by semicolons),
parses and evaluates it against data records, local variables, and global properties.
"""
from typing import Any, Dict, Optional, Tuple
from .pilotscript_parser import PilotScriptParser, PilotScriptEngine


def custom_manipulator(
    expression: str,
    record: Optional[Dict[str, Any]] = None,
    globals_dict: Optional[Dict[str, Any]] = None,
    locals_dict: Optional[Dict[str, Any]] = None,
    initial_expression: Optional[str] = None,
    final_expression: Optional[str] = None,
    keep_calculated_properties: bool = True
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Unified implementation of the Biovia Pipeline Pilot 'Custom Manipulator (PilotScript)' component.

    In Pipeline Pilot, the Custom Manipulator evaluates PilotScript statements for each incoming record.
    It can query or alter properties on data records (%), access/mutate globals (@), and use local variables (#).

    Parameters:
        expression (str): Main PilotScript expression or script block.
        record (dict, optional): Incoming record attributes to manipulate.
        globals_dict (dict, optional): Global workflow state.
        locals_dict (dict, optional): Component-scoped local variables.
        initial_expression (str, optional): PilotScript executed once upon initialization.
        final_expression (str, optional): PilotScript executed upon completion.
        keep_calculated_properties (bool): If True, retains newly assigned record properties.

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
            (updated_record, updated_globals, updated_locals)
    """
    rec = dict(record) if record is not None else {}
    globs = dict(globals_dict) if globals_dict is not None else {}
    locs = dict(locals_dict) if locals_dict is not None else {}

    # 1. Evaluate Initial Expression if provided
    if initial_expression and initial_expression.strip():
        engine_init = PilotScriptEngine(globals_ctx=globs, record_ctx=rec, locals_ctx=locs)
        engine_init.execute(initial_expression.strip())
        globs = engine_init.globals_ctx
        rec = engine_init.record_ctx
        locs = engine_init.locals_ctx

    # 2. Evaluate Main Expression
    if expression and expression.strip():
        engine = PilotScriptEngine(globals_ctx=globs, record_ctx=rec, locals_ctx=locs)
        engine.execute(expression.strip())
        if keep_calculated_properties:
            rec = engine.record_ctx
        else:
            # Revert to original keys if not keeping calculated properties
            rec = {k: engine.record_ctx[k] for k in (record or {}).keys() if k in engine.record_ctx}
        globs = engine.globals_ctx
        locs = engine.locals_ctx

    # 3. Evaluate Final Expression if provided
    if final_expression and final_expression.strip():
        engine_final = PilotScriptEngine(globals_ctx=globs, record_ctx=rec, locals_ctx=locs)
        engine_final.execute(final_expression.strip())
        globs = engine_final.globals_ctx
        rec = engine_final.record_ctx
        locs = engine_final.locals_ctx

    return rec, globs, locs
