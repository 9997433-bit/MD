"""Catalog package for the E1733A learning project.

Re-exports the main public API of the catalog modules. Functions that share
a name across modules (``load_ledger``, ``get_entry``) are exported at the
top level from :mod:`static_catalog`; block-specific variants remain
accessible through the submodules, which are also re-exported here.
"""
from . import (
    catalog_e1733a_acq,
    catalog_e1733a_ana,
    catalog_e1733a_cmp,
    catalog_formats,
    static_catalog,
)
from .catalog_e1733a_acq import (
    ACQ_ENTRY_IDS,
    acquisition_entries,
    dll_export_ids,
    entries_by_status,
    meatype_ids,
)
from .catalog_e1733a_ana import (
    ANALYSIS_CI_MAP,
    STANDARDS_MAP,
    analysis_ci_constants,
    analysis_entries,
    analysis_entry_ids,
    load_setup_constants,
    setup_constant_value,
    standard_entries,
    unknown_delphi_slots,
    verify_analysis_ci_map,
)
from .catalog_e1733a_cmp import compensation_entries, window_audit
from .catalog_formats import (
    EXT_TO_SLOT,
    format_by_extension,
    format_disposition,
    format_entries,
)
from .static_catalog import (
    Block,
    all_entries,
    entries_by_block,
    forced_null_bridges,
    get_entry,
    identifiers,
    load_bridge_matrix,
    load_coverage,
    load_ledger,
    unknown_entries,
)

__all__ = [
    # Submodules
    "static_catalog",
    "catalog_e1733a_acq",
    "catalog_e1733a_ana",
    "catalog_e1733a_cmp",
    "catalog_formats",
    # static_catalog (unified API)
    "Block",
    "load_ledger",
    "load_coverage",
    "load_bridge_matrix",
    "entries_by_block",
    "all_entries",
    "get_entry",
    "identifiers",
    "unknown_entries",
    "forced_null_bridges",
    # catalog_e1733a_acq
    "ACQ_ENTRY_IDS",
    "acquisition_entries",
    "entries_by_status",
    "meatype_ids",
    "dll_export_ids",
    # catalog_e1733a_ana
    "STANDARDS_MAP",
    "ANALYSIS_CI_MAP",
    "analysis_entries",
    "analysis_entry_ids",
    "standard_entries",
    "unknown_delphi_slots",
    "load_setup_constants",
    "setup_constant_value",
    "analysis_ci_constants",
    "verify_analysis_ci_map",
    # catalog_e1733a_cmp
    "compensation_entries",
    "window_audit",
    # catalog_formats
    "EXT_TO_SLOT",
    "format_entries",
    "format_disposition",
    "format_by_extension",
]
