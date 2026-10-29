"""
Biovia Pipeline Pilot Component: 'Subprotocol'
Component Path: Components\\Data Access and Manipulation\\Utilities\\Subprotocol Utilities\\Subprotocol
Component GUID: {17001C74-63CE-4B4B-B37C-F0EAA19CE4AA}

Architectural Role in Pipeline Pilot:
  - In Biovia PLP, a "Protocol" is the entire executable pipeline (macro application).
  - A "Component" is an atomic node (Custom Filter, Custom Manipulator, HTTP Connector, etc.).
  - A "Subprotocol" is a composite graphical & logical container that encapsulates a network
    of components to eliminate visual clutter and present a clean, modular abstraction.
  - Subprotocols expose promoted parameters (e.g. 'Section Title', 'PowerPoint File') that
    are passed down to the internal child components.
  - Subprotocols can be nested hierarchically.

Capabilities Implemented:
  1. Internal Component Graph & Port Routing (Pass / Fail / Filtered ports)
  2. Promoted Parameter Mappings (LinkSingleParentParameterType)
  3. Execution Semantics ('RunToCompletion'):
      * 'False': Streams records sequentially through the internal component network
      * 'True - For Each Data Record': Re-initializes subprotocol context per data record
      * 'True - For Each Category': Partitions data records into categories via 'RunToCompletion Categorize Using'
  4. Local Scope Management ('DeclareLocal') with PilotScript variable scoping
  5. Built-in Factory Subprotocols (e.g. Add PowerPoint Section, Add Word Section, Extract Sections)
  6. Topology Inspection (extracts inner component layout, local IDs, and connection wiring)
"""
import copy
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class SubprotocolContext:
    """Manages the scoped execution environment and declared properties for a Subprotocol."""

    def __init__(self, declare_local_expr: Optional[str] = None):
        self.locals: Dict[str, Any] = {}
        if declare_local_expr:
            self._parse_declare_local(declare_local_expr)

    def _parse_declare_local(self, expr: str):
        """
        Parses PilotScript DeclareLocal syntax:
        e.g. 'serial' or 'top,skip,recordCount,sectionfilter,iteration,error,recordFound'
        or 'SubP_Counter := 0, SubP_TitleText:="Sample 1"'
        """
        parts = [p.strip() for p in expr.split(",") if p.strip()]
        for part in parts:
            if ":=" in part:
                k, v = part.split(":=", 1)
                k = k.strip().lstrip("@")
                v = v.strip().strip("'\"")
                try:
                    if "." in v:
                        self.locals[k] = float(v)
                    else:
                        self.locals[k] = int(v)
                except ValueError:
                    if v.lower() == "true":
                        self.locals[k] = True
                    elif v.lower() == "false":
                        self.locals[k] = False
                    else:
                        self.locals[k] = v
            else:
                k = part.lstrip("@")
                self.locals[k] = None

    def clone(self) -> "SubprotocolContext":
        ctx = SubprotocolContext()
        ctx.locals = copy.deepcopy(self.locals)
        return ctx


class SubprotocolNode:
    """Represents a component node inside a subprotocol."""

    def __init__(
        self,
        local_id: str,
        name: str,
        component_type: str,
        func: Callable[[Dict[str, Any], SubprotocolContext, Dict[str, Any]], Tuple[Optional[Dict[str, Any]], bool]],
        parameters: Optional[Dict[str, Any]] = None,
    ):
        self.local_id = str(local_id)
        self.name = name
        self.component_type = component_type
        self.func = func
        self.parameters = parameters or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "local_id": self.local_id,
            "name": self.name,
            "component_type": self.component_type,
            "parameters": self.parameters,
        }


class Subprotocol:
    """
    Python translation of Pipeline Pilot Subprotocol container (GUID: {17001C74-63CE-4B4B-B37C-F0EAA19CE4AA}).
    Encapsulates and executes a network of child components with parameter promotion, port connections, and scoping.
    """

    def __init__(
        self,
        name: str = "Subprotocol",
        guid: Optional[str] = None,
        run_to_completion: str = "False",
        categorize_using: Optional[str] = None,
        declare_local: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        description: str = "Subprotocol container encapsulating child components into a reusable block",
    ):
        self.name = name
        self.guid = guid or "{17001C74-63CE-4B4B-B37C-F0EAA19CE4AA}"
        self.run_to_completion = run_to_completion or "False"
        self.categorize_using = categorize_using
        self.declare_local = declare_local
        self.description = description

        # Subprotocol-level promoted parameters exposed on the container
        self.parameters: Dict[str, Any] = parameters or {}

        # Internal child nodes (LocalID -> SubprotocolNode)
        self.nodes: Dict[str, SubprotocolNode] = {}
        # Node sequence order for execution
        self.execution_order: List[str] = []
        # Connections: List of tuples (from_node_id, to_node_id, port_type: 'pass' | 'fail')
        self.connections: List[Dict[str, str]] = []
        # Parameter promotions: maps subprotocol parameter to child node parameter
        # List of {"subprotocol_param": "title", "target_node_id": "2", "target_param": "section_title"}
        self.promotions: List[Dict[str, str]] = []

        # Validate RunToCompletion
        if self.run_to_completion == "True - For Each Category" and not self.categorize_using:
            raise ValueError(
                "This parameter is required when RunToCompletion is set to True - For Each Category: 'RunToCompletion Categorize Using'"
            )

    def set_parameter(self, name: str, value: Any):
        """Sets a subprotocol-level promoted parameter value."""
        self.parameters[name] = value
        return self

    def add_node(
        self,
        local_id: Union[str, int],
        name: str,
        component_type: str,
        func: Callable[[Dict[str, Any], SubprotocolContext, Dict[str, Any]], Tuple[Optional[Dict[str, Any]], bool]],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> "Subprotocol":
        """Adds a child component node to this subprotocol."""
        lid = str(local_id)
        node = SubprotocolNode(
            local_id=lid,
            name=name,
            component_type=component_type,
            func=func,
            parameters=parameters or {},
        )
        self.nodes[lid] = node
        if lid not in self.execution_order:
            self.execution_order.append(lid)
        return self

    def connect(self, from_id: Union[str, int], to_id: Union[str, int], port_type: str = "pass") -> "Subprotocol":
        """Defines an internal port connection between two child nodes."""
        self.connections.append({
            "from": str(from_id),
            "to": str(to_id),
            "port": port_type,
        })
        return self

    def promote_parameter(
        self,
        subprotocol_param: str,
        target_node_id: Union[str, int],
        target_param: str,
        default_value: Any = None,
    ) -> "Subprotocol":
        """
        Promotes a child component's parameter to the subprotocol level.
        Corresponds to PLP's <sci:arg type="LinkSingleParentParameterType">.
        """
        if subprotocol_param not in self.parameters:
            self.parameters[subprotocol_param] = default_value
        self.promotions.append({
            "subprotocol_param": subprotocol_param,
            "target_node_id": str(target_node_id),
            "target_param": target_param,
        })
        return self

    def _resolve_child_parameters(self, node_id: str) -> Dict[str, Any]:
        """Resolves effective parameters for a child node by applying promoted subprotocol parameters."""
        node = self.nodes.get(node_id)
        if not node:
            return {}
        params = copy.deepcopy(node.parameters)
        for promo in self.promotions:
            if promo["target_node_id"] == node_id:
                sub_val = self.parameters.get(promo["subprotocol_param"])
                if sub_val is not None:
                    params[promo["target_param"]] = sub_val
        return params

    def _execute_pipeline_on_record(
        self, record: Dict[str, Any], context: SubprotocolContext
    ) -> Tuple[Optional[Dict[str, Any]], bool]:
        """Runs a record through the internal component network."""
        current_rec = copy.deepcopy(record)

        for node_id in self.execution_order:
            node = self.nodes[node_id]
            node_params = self._resolve_child_parameters(node_id)

            # Execute node func: (record, context, params) -> (new_record, is_pass)
            try:
                res, is_pass = node.func(current_rec, context, node_params)
            except Exception as e:
                # Capture failure on fail port
                if current_rec is not None:
                    current_rec["_subprotocol_error"] = str(e)
                    current_rec["_failed_node"] = node.name
                return current_rec, False

            if not is_pass:
                return res, False

            if res is None:
                # Filtered out (filtered port)
                return None, True

            current_rec = res

        return current_rec, True

    def execute(
        self, records: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Executes the subprotocol on incoming records according to RunToCompletion semantics."""
        input_list = [records] if isinstance(records, dict) else list(records)
        passed_records: List[Dict[str, Any]] = []
        failed_records: List[Dict[str, Any]] = []

        base_context = SubprotocolContext(self.declare_local)

        if self.run_to_completion == "False":
            # Stream execution
            ctx = base_context.clone()
            for r in input_list:
                res, is_pass = self._execute_pipeline_on_record(r, ctx)
                if is_pass:
                    if res is not None:
                        passed_records.append(res)
                else:
                    if res is not None:
                        failed_records.append(res)

        elif self.run_to_completion == "True - For Each Data Record":
            # Context isolated per record
            for r in input_list:
                ctx = base_context.clone()
                res, is_pass = self._execute_pipeline_on_record(r, ctx)
                if is_pass:
                    if res is not None:
                        passed_records.append(res)
                else:
                    if res is not None:
                        failed_records.append(res)

        elif self.run_to_completion == "True - For Each Category":
            # Batch partition by category
            cat_prop = self.categorize_using
            categories: Dict[str, List[Dict[str, Any]]] = {}
            for r in input_list:
                cat_val = str(r.get(cat_prop, "Uncategorized"))
                categories.setdefault(cat_val, []).append(r)

            for cat_name, cat_records in categories.items():
                ctx = base_context.clone()
                ctx.locals["_CurrentCategory"] = cat_name
                for r in cat_records:
                    res, is_pass = self._execute_pipeline_on_record(r, ctx)
                    if is_pass:
                        if res is not None:
                            passed_records.append(res)
                    else:
                        if res is not None:
                            failed_records.append(res)

        return {
            "subprotocol_name": self.name,
            "guid": self.guid,
            "run_to_completion": self.run_to_completion,
            "categorize_using": self.categorize_using,
            "parameters": self.parameters,
            "total_input": len(input_list),
            "passed_count": len(passed_records),
            "failed_count": len(failed_records),
            "passed_records": passed_records,
            "failed_records": failed_records,
            "topology": self.inspect_topology(),
        }

    def inspect_topology(self) -> Dict[str, Any]:
        """Returns the structural schematic of the encapsulated components inside this subprotocol."""
        return {
            "name": self.name,
            "guid": self.guid,
            "description": self.description,
            "promoted_parameters": self.parameters,
            "nodes": [self.nodes[nid].to_dict() for nid in self.execution_order if nid in self.nodes],
            "connections": self.connections,
            "parameter_promotions": self.promotions,
        }


# ============================================================================
# Pre-built Standard Subprotocols matching Biovia Pipeline Pilot Specifications
# ============================================================================

def create_add_powerpoint_subprotocol(
    section_title: str = "Synthesis Overview",
    powerpoint_file: str = "synthesis.pptx",
    preview_text: str = "Preview will be generated when the file is edited.",
    preview_width: int = 600,
    preview_height: int = 30,
) -> Subprotocol:
    """
    Builds the subprotocol corresponding to PLP 'Add PowerPoint Presentation Section'
    (GUID: {E5B6E23D-CC7F-4D04-878E-606E3B4B6E7E}).
    Encapsulates:
      - LocalID 9: Create Section
      - LocalID 2: Edit Section
      - LocalID 18: Custom Manipulator (Canvas preview format)
      - LocalID 16: Serialize Section XML Node
      - LocalID 17: Append to Experiment Record
    """
    from .section_models import SectionType

    subp = Subprotocol(
        name="Add PowerPoint Presentation Section",
        guid="{E5B6E23D-CC7F-4D04-878E-606E3B4B6E7E}",
        description="Encapsulates PowerPoint presentation attachment creation, preview canvas generation, and record serialization",
        parameters={
            "Section Title": section_title,
            "PowerPoint File": powerpoint_file,
            "Canvas Preview Text": preview_text,
            "Preview Width": preview_width,
            "Preview Height": preview_height,
        },
    )

    # Step 1: Create Section
    def step_create_section(rec, ctx, params):
        title = params.get("Section Title") or "PowerPoint Presentation"
        rec["_active_section"] = {
            "title": title,
            "sectionType": SectionType.POWERPOINT.value,
        }
        return rec, True

    # Step 2: Custom Manipulator (Canvas Preview Message)
    def step_format_preview(rec, ctx, params):
        p_text = params.get("Canvas Preview Text") or "Preview will be generated when the file is edited."
        w = params.get("Preview Width", 600)
        h = params.get("Preview Height", 30)
        p_file = params.get("PowerPoint File", "")

        sec = rec.get("_active_section", {})
        sec["files"] = [p_file] if p_file else []
        sec["metadata"] = {
            "previewText": p_text,
            "previewImageWidth": w,
            "previewImageHeight": h,
            "fileName": p_file,
        }
        rec["_active_section"] = sec
        return rec, True

    # Step 3: Append Section to Experiment
    def step_append_section(rec, ctx, params):
        import uuid
        from .section_models import ElnSectionRecord
        sec_dict = rec.pop("_active_section", {})
        sec_id = f"sec_{uuid.uuid4().hex[:8]}"
        sec_obj = ElnSectionRecord(
            section_id=sec_id,
            section_title=sec_dict.get("title", "PowerPoint Presentation"),
            section_type=SectionType.POWERPOINT,
            files=sec_dict.get("files", []),
            metadata=sec_dict.get("metadata", {}),
            connection_name=rec.get("connectionname", "Connection1"),
        )
        serialized = sec_obj.to_serialized_node()
        rec.setdefault("simplesections", []).append(serialized)
        rec["last_added_section"] = serialized
        return rec, True

    subp.add_node("9", "Create Section", "Add Section", step_create_section)
    subp.add_node("18", "Format Canvas Preview", "Custom Manipulator", step_format_preview)
    subp.add_node("17", "Append Section to Experiment", "Custom Manipulator", step_append_section)

    subp.connect("9", "18")
    subp.connect("18", "17")

    subp.promote_parameter("Section Title", "9", "Section Title")
    subp.promote_parameter("PowerPoint File", "18", "PowerPoint File")
    subp.promote_parameter("Canvas Preview Text", "18", "Canvas Preview Text")
    subp.promote_parameter("Preview Width", "18", "Preview Width")
    subp.promote_parameter("Preview Height", "18", "Preview Height")

    return subp


def create_extract_sections_subprotocol(
    experiment_id: str = "EXP-2026-XRF-01",
    what_to_extract: str = "All Section Types",
    section_types: Optional[List[str]] = None,
) -> Subprotocol:
    """
    Builds the subprotocol corresponding to PLP 'Extract Sections from Experiment'
    (GUID: {9371960B-8C09-4303-93A8-B74422F2B964}).
    Encapsulates:
      - LocalID 4: Validate Experiment Number (Gatekeeper)
      - LocalID 44: Section Type Filter Gatekeeper
      - LocalID 26: Query Experiment REST API
      - LocalID 28: Expand simplesections Array
      - LocalID 35: First Occurrence Filter (Deduplicate Section IDs)
      - LocalID 56: Sort Data (by indexindocument)
    """
    subp = Subprotocol(
        name="Extract Sections from Experiment",
        guid="{9371960B-8C09-4303-93A8-B74422F2B964}",
        description="Encapsulates experiment section extraction, OData filtering, ID deduplication, and index sorting",
        parameters={
            "Experiment ID": experiment_id,
            "What To Extract": what_to_extract,
            "Section Types": section_types or [],
        },
    )

    # Step 1: Gatekeeper check
    def step_gatekeeper(rec, ctx, params):
        what = params.get("What To Extract")
        types = params.get("Section Types") or []
        if what == "Selected Section Types" and len(types) == 0:
            return None, True  # Filtered out
        return rec, True

    # Step 2: Query & Expand sections
    def step_query_expand(rec, ctx, params):
        from .extract_sections import extract_sections
        exp_id = params.get("Experiment ID") or rec.get("experimentnumber") or "EXP-01"
        what = params.get("What To Extract", "All Section Types")
        types = params.get("Section Types", [])

        sections = extract_sections(
            experiment_record=rec,
            experiment_id=exp_id,
            what_to_extract=what,
            section_types=types,
        )
        rec["_extracted_sections"] = sections
        return rec, True

    subp.add_node("44", "Section Filter Gatekeeper", "Custom Filter", step_gatekeeper)
    subp.add_node("26", "Query & Expand Sections", "HTTP Connector", step_query_expand)

    subp.connect("44", "26")
    subp.promote_parameter("What To Extract", "44", "What To Extract")
    subp.promote_parameter("Section Types", "44", "Section Types")
    subp.promote_parameter("Experiment ID", "26", "Experiment ID")

    return subp


def run_subprotocol(
    name: str = "Subprotocol",
    run_to_completion: str = "False",
    categorize_using: Optional[str] = None,
    declare_local: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    records: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    """Convenience functional interface for executing a Subprotocol."""
    subp = Subprotocol(
        name=name,
        run_to_completion=run_to_completion,
        categorize_using=categorize_using,
        declare_local=declare_local,
        parameters=parameters,
    )
    return subp.execute(records or [])
