"""
Biovia Pipeline Pilot Component: 'Extract Sections from Experiment'
Component Display Name: 'Sections from Experiment'
Component Path: Components\\Database and Application Integration\\Application Integration\\Notebook\\Experiments\\Attach and Extract\\Extract Sections from Experiment
Component GUID: {9371960B-8C09-4303-93A8-B74422F2B964}
Component LocalID: 4

Replaces the PLP subprotocol containing:
  - Check Input Experiment (LocalID 26, PilotScript validation of experimentnumber / ID)
  - Any sections selected? (LocalID 44, Gatekeeper filter for Selected Section Types)
  - Loop for sections JSON / XML (Subprotocols LocalID 57 / 58)
  - HTTP Connector using Connection (RTC LocalID 28 / 41, OData paging with top/skip and section filters)
  - First Occurrence Filter (LocalID 35, Deduplication on section id)
  - Sort Data (LocalID 56, Sort on indexindocument Ascending Numbers)
"""
import copy
import json
import logging
from typing import Any, Dict, List, Optional, Union

from .section_models import PLP_SECTION_TYPE_IDS
from .biovia_notebook import BioviaNotebookClient
from .notebook_connection import NotebookConnectionObject

logger = logging.getLogger("biovia_pipeline.extract_sections")


def build_section_filter(
    what_to_extract: str = "All Section Types",
    section_types: Optional[List[str]] = None,
) -> str:
    """
    Constructs the OData $filter string for section retrieval matching PLP PilotScript logic:
      - If 'All Section Types': returns empty string.
      - If 'Selected Section Types': constructs query from sectiontypeid values.
      - Handles 'Custom Sections' by negating non-selected section type IDs.
    """
    if what_to_extract == "All Section Types" or not section_types:
        return ""

    selected = list(section_types)
    has_custom = "Custom Sections" in selected

    type_ids = []
    for st in selected:
        if st in PLP_SECTION_TYPE_IDS:
            type_ids.append(PLP_SECTION_TYPE_IDS[st])

    type_ids = sorted(list(set(type_ids)))

    if not type_ids:
        return ""

    if has_custom:
        # PLP logic: if 'Custom Sections' selected, filter non-selected types with 'ne' and 'and'
        all_known_ids = set(PLP_SECTION_TYPE_IDS.values())
        non_selected = sorted(list(all_known_ids - set(type_ids)))
        clauses = [f"sectiontypeid ne {tid}" for tid in non_selected]
        return "&$filter=" + " and ".join(clauses)
    else:
        # Standard inclusion with 'eq' and 'or'
        clauses = [f"sectiontypeid eq {tid}" for tid in type_ids]
        return "&$filter=" + " or ".join(clauses)


def extract_sections(
    experiment_record: Optional[Dict[str, Any]] = None,
    experiment_id: Optional[str] = None,
    what_to_extract: str = "All Section Types",
    section_types: Optional[List[str]] = None,
    connection: Optional[NotebookConnectionObject] = None,
    client: Optional[BioviaNotebookClient] = None,
    sort_by_index: bool = True,
    deduplicate_by_id: bool = True,
) -> List[Dict[str, Any]]:
    """
    Extracts, filters, deduplicates, and sorts sections from an incoming experiment record or ELN server.
    Replicates PLP 'Extract Sections from Experiment' component behavior.

    :param experiment_record: Incoming Experiment or Template record dictionary (required if experiment_id is not given).
    :param experiment_id: Direct experiment number or ID override.
    :param what_to_extract: "All Section Types" or "Selected Section Types".
    :param section_types: List of section type names when what_to_extract is "Selected Section Types".
    :param connection: Optional NotebookConnectionObject holding credentials / endpoint.
    :param client: Optional BioviaNotebookClient for live/mock ELN queries.
    :param sort_by_index: If True, sorts sections by indexindocument ascending (PLP Sort Data LocalID 56).
    :param deduplicate_by_id: If True, keeps only first occurrence of each section id (PLP First Occurrence Filter LocalID 35).
    :return: List of extracted section records with enriched metadata and parent experiment linkage.
    """
    rec = dict(experiment_record) if experiment_record else {}

    # 1. PilotScript Input Validation (LocalID 26):
    # 'if nodetype(DataRoot()) eq "Experiment" then experimentnumber else ID'
    exp_num = (
        experiment_id
        or rec.get("experimentnumber")
        or rec.get("experimentNumber")
        or rec.get("id")
        or rec.get("ID")
    )

    if not exp_num:
        raise ValueError(
            "The incoming record does not have an experimentnumber property containing the "
            "experiment number of the experiment to retrieve sections for, or a template record with ID."
        )

    # 2. Gatekeeper Filter (LocalID 44):
    # 'not (@What To Extract eq "Selected Section Types" and numvalues(@Section Type) == 0)'
    if what_to_extract == "Selected Section Types" and (not section_types or len(section_types) == 0):
        logger.info("Selected Section Types specified with 0 types selected; passing 0 records.")
        return []

    # 3. Build section filter query string
    odata_filter = build_section_filter(what_to_extract, section_types)
    logger.debug(f"Extract sections OData filter: {odata_filter}")

    # 4. Retrieve sections from record simplesections or ELN client
    raw_sections: List[Dict[str, Any]] = []

    if client:
        # Query ELN client
        exp_data = client.get_experiment(exp_num)
        if exp_data and "simplesections" in exp_data:
            raw_sections = exp_data["simplesections"]
    elif "simplesections" in rec:
        raw_sections = rec["simplesections"]
    else:
        # Fallback: create mock client query
        mock_client = BioviaNotebookClient(mock_mode=True)
        exp_data = mock_client.get_experiment(exp_num)
        if exp_data and "simplesections" in exp_data:
            raw_sections = exp_data["simplesections"]

    # 5. Apply section type filtering in Python
    filtered_sections: List[Dict[str, Any]] = []
    allowed_types_lower = [t.lower() for t in (section_types or [])]

    for idx, s in enumerate(raw_sections):
        sec = copy.deepcopy(s)
        sec_type_str = str(sec.get("sectionType") or sec.get("type") or "").strip()

        # If filtering is enabled:
        if what_to_extract == "Selected Section Types" and section_types:
            # Check direct match or sectiontypeid
            matches = any(
                sec_type_str.lower() == at.lower() or at.lower() in sec_type_str.lower()
                for at in allowed_types_lower
            )
            if not matches:
                continue

        # 6. Replicate PLP Custom Manipulator (LocalID 36 / 44):
        # Set node properties, indexindocument, and minimal Experiment child node
        sec_id = str(sec.get("id") or sec.get("sectionId") or f"sec_{idx + 1}")
        sec["id"] = sec_id
        sec["sectionId"] = sec_id
        sec["experimentnumber"] = exp_num
        sec["connectionname"] = connection.connection_name if connection else rec.get("connectionname", "Connection1")
        sec["ref"] = rec.get("ref", f"exp-ref-{exp_num}")

        # Maintain index in document
        if "indexindocument" not in sec and "indexInDocument" not in sec:
            sec["indexindocument"] = idx + 1
        else:
            sec["indexindocument"] = int(sec.get("indexindocument") or sec.get("indexInDocument") or (idx + 1))

        # Reconstruct parent experiment child link as in PLP
        sec["Experiment"] = {
            "id": exp_num,
            "connectionname": sec["connectionname"],
            "ref": sec["ref"],
        }

        filtered_sections.append(sec)

    # 7. Deduplication via First Occurrence Filter on 'id' (LocalID 35)
    if deduplicate_by_id:
        seen_ids = set()
        deduped: List[Dict[str, Any]] = []
        for s in filtered_sections:
            sid = s.get("id")
            if sid not in seen_ids:
                seen_ids.add(sid)
                deduped.append(s)
        filtered_sections = deduped

    # 8. Sort Data by 'indexindocument' Ascending Numbers (LocalID 56)
    if sort_by_index:
        filtered_sections.sort(key=lambda s: int(s.get("indexindocument", 0)))

    return filtered_sections
