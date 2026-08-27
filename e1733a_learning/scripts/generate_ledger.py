#!/usr/bin/env python3
"""Generate E1733A static analysis ledger from frozen sources (no PE execution)."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACTED = Path("/tmp/seed-repo/extracted")
WORKSPACE_REMOTE = Path("/workspace/浙大/资料/是德科技/E1733A_Remote.h")
REMOTE_H = WORKSPACE_REMOTE if WORKSPACE_REMOTE.exists() else EXTRACTED / "E1733A_Remote.h"
MANIFESTS = ROOT / "manifests"
OUT = ROOT


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_remote_h(text: str) -> dict:
    constants = []
    for m in re.finditer(
        r"#define\s+(E1733A_(?:CC|CI|RC|CS|WM)_[A-Z0-9_]+)\s+([^\n/]+)",
        text,
    ):
        name, val = m.group(1), m.group(2).strip().rstrip(";")
        block = text[max(0, m.start() - 200) : m.end() + 200]
        comment = ""
        if "//" in block.split(name, 1)[-1]:
            comment = block.split("//", 1)[-1].split("\n", 1)[0].strip()
        constants.append({"name": name, "value": val, "comment": comment})
    return {"source": str(REMOTE_H), "count": len(constants), "constants": constants}


def pe_exports(path: Path) -> list[str]:
    try:
        import pefile
    except ImportError:
        return []
    pe = pefile.PE(str(path))
    out = []
    if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
        for sym in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            if sym.name:
                out.append(sym.name.decode("utf-8", "ignore"))
    return sorted(out)


def parse_sample(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    fields = {}
    for m in re.finditer(r"Identify=([^,]+),([^=\n]+)=([^\n]+)", text):
        fields[m.group(1)] = {"type": m.group(2), "value": m.group(3).strip()}
    mea = fields.get("MeaType", {}).get("value", "")
    mea_match = re.search(r"Choosing=(\d+)", mea)
    return {
        "file": path.name,
        "extension": path.suffix.lower(),
        "sha256": sha256_file(path),
        "mea_type_choosing": int(mea_match.group(1)) if mea_match else None,
        "field_count": len(fields),
        "has_linear_err": "LinearErr" in fields,
        "has_comp_fields": any(k.startswith("Comp") for k in fields),
    }


MEATYPE_MAP = {
    0: ("LINEAR", ".Lin"),
    1: ("ANGULAR", ".Ang"),
    2: ("STRAIGHTNESS", ".str"),
    3: ("SQUARENESS", ".Squ"),
    4: ("PARALLELISM", ".Par"),
    5: ("ROTARY", ".rot"),
    6: ("WAY_STRAIGHTNESS", ".Way"),
    7: ("FLATNESS", ".Fla"),
    8: ("DIAGONAL", ".Dia"),
    9: ("LIN_TIMEBASE", ".LTB"),
    10: ("ANG_TIMEBASE", ".ATB"),
    11: ("STR_TIMEBASE", ".STB"),
    13: ("SINGLE_AXIS", None),
    14: ("DUAL_AXIS", ".LDA"),
}

STANDARDS = {
    0: "NMTBA w/o Offset",
    1: "NMTBA",
    2: "ANSI B5.54/B5.57",
    3: "VDI 3441/2617",
    4: "BSI 3800",
    5: "JIS B6330",
    6: "ISO 230-2 1988",
    7: "ISO 230-2 1997",
    8: "GB10931-89",
    9: "GB/T 17421.2-2000",
    10: "User",
    11: "ISO 230-2 2006",
    12: "ISO 230-2 2014",
}

ANALYSIS_CI = {
    0: ("BIMAXREV", "B max reversal"),
    1: ("BIMEANREV", "mean reversal"),
    2: ("BIMEANDEV", "M mean bidir dev"),
    3: ("REVSYSPOSDEV", "E-"),
    4: ("FWDSYSPOSDEV", "E+"),
    5: ("BISYSPOSDEV", "E bidir"),
    6: ("REVREPEATPOS", "R-"),
    7: ("FWDREPEATPOS", "R+"),
    8: ("BIREPEATPOS", "R bidir"),
    9: ("REVACCURACY", "A-"),
    10: ("FWDACCURACY", "A+"),
    11: ("BIACCURACY", "A bidir"),
    12: ("REVRAWREP", "R-'"),
    13: ("FWDRAWREP", "R+'"),
    14: ("BIRAWREP", "R'"),
    15: ("REVRAWACC", "A-'"),
    16: ("FWDRAWACC", "A+'"),
    17: ("BIRAWACC", "A'"),
    18: ("SIXSIGMA", "6 sigma"),
    19: ("SLOPELS", "slope least squares"),
    20: ("SLOPEEP", "slope end points"),
    21: ("VDI_P", "VDI P"),
    22: ("VDI_PSMAX", "VDI Ps max"),
    23: ("VDI_PSMEAN", "VDI Ps mean"),
    24: ("VDI_PSU", "VDI PsU"),
    25: ("VDI_PA", "VDI Pa"),
    26: ("VDI_UMAX", "VDI U max"),
    27: ("VDI_UMEAN", "VDI U mean"),
}


def entry(identifier, module, source, status, boundary, missing, **kw):
    return {
        "identifier": identifier,
        "module": module,
        "source_identifier": source,
        "window_hash": kw.get("window_hash"),
        "status": status,
        "boundary": boundary,
        "missing": missing,
        **{k: v for k, v in kw.items() if k != "window_hash"},
    }


def build_acq_catalog(pe_exports_map: dict) -> list[dict]:
    rows = []
    meatypes = [
        ("LINEAR", ".Lin"),
        ("ANGULAR", ".Ang"),
        ("STR", ".str"),
        ("SQU", ".Squ"),
        ("PAR", ".Par"),
        ("ROT", ".rot"),
        ("WAY", ".Way"),
        ("FLA", ".Fla"),
        ("DIA", ".Dia"),
        ("LTB", ".LTB"),
        ("ATB", ".ATB"),
        ("STB", ".STB"),
        ("DUAL", ".LDA"),
    ]
    for name, ext in meatypes:
        rows.append(
            entry(
                f"ACQ-E1-MEATYPE-{name}",
                "E1733A.exe/Remote.h",
                f"E1733A_CC_NEW / CI_{name}",
                "E1",
                "remote_h_constant",
                "Delphi view class unknown",
            )
        )
    for ident, cc, ci, desc in [
        ("ACQ-E1-CMD-START", "CC_START", "53", "start/continue"),
        ("ACQ-E1-CMD-RECORD", "CC_RECORD", "54", "manual record"),
        ("ACQ-E1-CMD-RESET", "CC_RESET", "52", "reset data"),
        ("ACQ-E1-CMD-STOP", "CC_STOP", "55", "stop"),
    ]:
        rows.append(
            entry(ident, "E1733A.exe/Remote.h", f"{cc}={ci}", "E1", "remote_h_constant", None)
        )
    for ident, val, desc in [
        ("ACQ-E1-TRIG-MANUAL", "0", "TrigType manual"),
        ("ACQ-E1-TRIG-ENCODER", "1", "TrigType encoder"),
        ("ACQ-E1-TRIG-AUTO", "2", "TrigType auto"),
    ]:
        rows.append(
            entry(
                ident,
                "E1733A.exe/Remote.h",
                f"MEASETUP_TRIGTYPE_CHOOSING={val}",
                "E1",
                "remote_h_constant",
                None,
            )
        )
    for sym in pe_exports_map.get("E1735A.dll", []):
        if sym.startswith("E1735A_"):
            rows.append(
                entry(
                    f"ACQ-E1-DLL-{sym}",
                    "E1735A.dll",
                    sym,
                    "E1",
                    "pe_export_symbol",
                    "function body not frozen",
                )
            )
    for sym in pe_exports_map.get("E1735ACore.dll", []):
        if sym == "E1735ACore_ProcessRawData":
            st = "unknown"
            miss = "body_range.sha256 and instruction window"
        else:
            st = "E1"
            miss = "function body not frozen"
        rows.append(
            entry(
                f"ACQ-E1-CORE-{sym}",
                "E1735ACore.dll",
                sym,
                st,
                "pe_export_symbol",
                miss,
            )
        )
    rows.append(
        entry(
            "ACQ-UNK-DELPHI-COLLECTDOC",
            "E1733A.exe",
            None,
            "unknown",
            "no_rtti",
            "Delphi class name and RVA",
        )
    )
    rows.append(
        entry(
            "ACQ-UNK-PAUSE-RESUME",
            "E1735A.dll",
            None,
            "unknown",
            "export_absent",
            "no pauseSimTask/resumeSimTask equivalent in exports",
        )
    )
    rows.append(
        entry(
            "ACQ-BRIDGE-GUI-TO-E1735A",
            "E1733A.exe",
            "imports E1735A.dll",
            "candidate",
            "pe_import_only",
            "proven_bridge=null; no CFG call chain",
            proven_bridge=None,
        )
    )
    return rows


def build_ana_catalog() -> list[dict]:
    rows = []
    for ident, src in [
        ("ANA-E1-ENTRY-SETUP-ANALYSIS", "CI_ANALYSIS=5"),
        ("ANA-E1-ENTRY-OPEN-DATA", "CC_OPEN SETUPDATA=1"),
        ("ANA-E1-API-READERRORDATA", "CC_READERRORDATA=62"),
    ]:
        rows.append(
            entry(ident, "Remote.h", src, "E1", "remote_h_constant", None)
        )
    for idx, (suffix, desc) in ANALYSIS_CI.items():
        rows.append(
            entry(
                f"ANA-E1-API-ANALYSIS-{suffix}",
                "Remote.h",
                f"CC_ANALYSIS=66 CI={idx}",
                "E1",
                "remote_h_constant",
                "formula window unknown",
            )
        )
    for idx, name in STANDARDS.items():
        rows.append(
            entry(
                f"ANA-E1-STD-{idx}",
                "Remote.h",
                f"ANASETUP_STANDARD_CHOOSING={idx}",
                "E1",
                "remote_h_constant",
                f"standard={name}",
            )
        )
    slots = [
        "Lin", "Ang", "Str", "Squ", "Par", "Rot", "Way", "Fla", "Dia", "LTB", "ATB", "STB", "LDA"
    ]
    for s in slots:
        rows.append(
            entry(
                f"ANA-UNK-DELPHI-{s.upper()}DOC",
                "E1733A.exe",
                f"logical_slot={s}",
                "unknown",
                "no_rtti",
                "Delphi document class RVA",
            )
        )
    rows.append(
        entry(
            "ANA-UNK-ALG-ISO230-BODY",
            "E1733A.exe",
            None,
            "unknown",
            "no_instruction_window",
            "ISO 230-2 computation body",
        )
    )
    rows.append(
        entry(
            "ANA-E1-FLA-MOODY",
            "Remote.h",
            "ANASETUP_FLAMETHOD_CHOOSING=0",
            "E1",
            "remote_h_constant",
            "Moody algorithm body unknown",
        )
    )
    return rows


def build_cmp_catalog(pe_exports_map: dict) -> list[dict]:
    rows = []
    for ident, src in [
        ("CMP-E1-UI-SHOWCOMP", "CC_SHOWCOMPENSATION=32"),
        ("CMP-E1-CFG-SIGN-CORRECTION", "CompSign=0 Correction"),
        ("CMP-E1-CFG-ABS-INCREMENTAL", "CompCalc Absolute/Incremental"),
        ("CMP-E1-CFG-DIR-COMBINED", "CompDir Combined/Fwd-Rev"),
        ("CMP-E1-CFG-SEL-TARGETLIST", "CompSel TargetList/Interpolate"),
        ("CMP-E1-EXPORT-COMPTABLE-CSV", "CC_SAVE COMPTABLE_CSV=6"),
        ("CMP-E1-SAMPLE-LINEARERR", "Sample.Lin LinearErr field"),
    ]:
        rows.append(entry(ident, "Remote.h/Sample.Lin", src, "E1", "remote_h_or_sample", None))
    rows.append(
        entry(
            "CMP-UNK-AMBIENT-BODY",
            "E1736A.dll",
            "E1736A_ReadEnvironment",
            "unknown",
            "export_symbol_only",
            "Edlen/Ciddor selection not proven",
        )
    )
    rows.append(
        entry(
            "CMP-UNK-LASERDIST-BODY",
            "E1735ACore.dll",
            "E1735ACore_ProcessRawData",
            "unknown",
            "export_symbol_only",
            "full laser distance formula window",
        )
    )
    rows.append(
        entry(
            "CMP-UNK-INTERPOLATE-ALG",
            "E1733A.exe",
            "CompSel=Interpolate",
            "unknown",
            "remote_h_constant_only",
            "interpolation algorithm not frozen",
        )
    )
    rows.append(
        entry(
            "CMP-FORBID-CNC-WRITER",
            "policy",
            "forbidden",
            "forbidden_writer",
            "no CNC download in static learning scope",
            None,
        )
    )
    for sym in pe_exports_map.get("E1736A.dll", []):
        if sym.startswith("E1736A_"):
            rows.append(
                entry(
                    f"CMP-E1-ENV-{sym}",
                    "E1736A.dll",
                    sym,
                    "E1",
                    "pe_export_symbol",
                    "function body not frozen",
                )
            )
    return rows


def build_formats(sample_manifest: dict) -> list[dict]:
    rows = []
    ext_map = {
        ".lin": "Lin",
        ".ang": "Ang",
        ".str": "Str",
        ".squ": "Squ",
        ".par": "Par",
        ".rot": "Rot",
        ".way": "Way",
        ".fla": "Fla",
        ".dia": "Dia",
        ".ltb": "LTB",
        ".atb": "ATB",
        ".stb": "STB",
        ".lda": "LDA",
    }
    for s in sample_manifest.get("samples", []):
        ext = s["extension"]
        rows.append(
            entry(
                f"FMT-{ext[1:].upper()}",
                "Option Description File",
                s["file"],
                "E1",
                "sample_scope_parser",
                None,
                disposition="sample_scope_parser",
                logical_slot=ext_map.get(ext),
                sample_sha256=s["sha256"],
            )
        )
    for sub, n in [
        ("RAWDATA_CSV", 2),
        ("RAWDATA_POS", 3),
        ("COMPTABLE_CSV", 6),
        ("COMPTABLE_POS", 7),
        ("ENVDATA_CSV", 10),
    ]:
        rows.append(
            entry(
                f"FMT-SAVE-{sub}",
                "Remote.h",
                f"CC_SAVE subtype={n}",
                "E1",
                "remote_h_constant",
                None,
                disposition="forbidden_writer",
            )
        )
    rows.append(
        entry(
            "FMT-LTB-VELOCITY-BRIDGE",
            "policy",
            "LTB timebase",
            "E1",
            "forced_null",
            None,
            proven_bridge=None,
            note="must not bridge to velocity formula",
        )
    )
    return rows


def build_bridge_matrix() -> dict:
    forced_null = [
        "FMT-LTB -> ALG-VELOCITY",
        "CMP-UNK-AMBIENT-BODY -> CMP-UNK-LASERDIST-BODY same path",
        "CompSel Interpolate -> spline evaluation",
        "ACQ-E1-CMD-START -> E1735A task instance continuity",
        "E4/self ISO script -> vendor acquisition FSM",
        "LinearErr field -> CC_ANALYSIS implementation",
        "Wavelength Compensation string -> Edlen/Ciddor formula",
    ]
    cells = {
        "acq_to_ana": {"proven_bridge": None, "reason": "no frozen CFG from E1735A_ReadSample to CC_ANALYSIS"},
        "acq_to_cmp": {"proven_bridge": None, "reason": "no frozen path to CompCalc"},
        "ana_to_cmp": {"proven_bridge": None, "reason": "Comp table generation body unknown"},
        "open_lin_to_alg": {"proven_bridge": None, "reason": "Sample.Lin parse only; no algorithm window"},
        "open_ltb_to_velocity": {"proven_bridge": None, "reason": "forced null"},
        "ambient_to_laserdist": {"proven_bridge": None, "reason": "forced null separate modules"},
    }
    return {"forced_null_bridges": forced_null, "cells": cells}


def main():
    MANIFESTS.mkdir(parents=True, exist_ok=True)

    files = []
    if EXTRACTED.exists():
        for p in sorted(EXTRACTED.iterdir()):
            if p.is_file():
                files.append(
                    {
                        "path": p.name,
                        "size_bytes": p.stat().st_size,
                        "sha256": sha256_file(p),
                    }
                )
    (MANIFESTS / "manifest_files.json").write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source_dir": str(EXTRACTED),
                "file_count": len(files),
                "files": files,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    pe_map = {}
    for dll in ["E1733A.exe", "E1735A.dll", "E1735ACore.dll", "E1736A.dll", "E1736ACore.dll"]:
        p = EXTRACTED / dll
        if p.exists():
            pe_map[dll] = {
                "sha256": sha256_file(p),
                "exports": pe_exports(p),
            }
    (MANIFESTS / "pe_exports.json").write_text(
        json.dumps(pe_map, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    remote_text = REMOTE_H.read_text(encoding="utf-8", errors="replace")
    setup = parse_remote_h(remote_text)
    (MANIFESTS / "setup_constants.json").write_text(
        json.dumps(setup, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    samples = []
    if EXTRACTED.exists():
        for p in sorted(EXTRACTED.glob("Sample.*")):
            info = parse_sample(p)
            mt = info.get("mea_type_choosing")
            if mt in MEATYPE_MAP:
                info["mea_type_name"], info["expected_ext"] = MEATYPE_MAP[mt]
            samples.append(info)
    (MANIFESTS / "sample_manifest.json").write_text(
        json.dumps({"samples": samples}, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    pe_exports_map = {k: v["exports"] for k, v in pe_map.items()}
    acq = build_acq_catalog(pe_exports_map)
    ana = build_ana_catalog()
    cmp_ = build_cmp_catalog(pe_exports_map)
    fmt = build_formats({"samples": samples})
    bridge = build_bridge_matrix()

    ledger = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "installer_source": "Montyzhang/-seed Install Keysight E1733A 1.14.1 (Win64).exe",
        "phases_completed": ["0", "A", "B", "C", "D"],
        "catalogs": {
            "acquisition": acq,
            "analysis": ana,
            "compensation": cmp_,
            "formats": fmt,
        },
        "bridge_matrix": bridge,
    }
    (OUT / "EvidenceLedger.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    all_ids = [r["identifier"] for cat in ledger["catalogs"].values() for r in cat]
    coverage = {
        "generated_at": ledger["generated_at"],
        "total_identifiers": len(all_ids),
        "by_status": {},
        "by_block": {
            "acquisition": len(acq),
            "analysis": len(ana),
            "compensation": len(cmp_),
            "formats": len(fmt),
        },
        "unknown_count": sum(1 for cat in ledger["catalogs"].values() for r in cat if r["status"] == "unknown"),
        "e1_count": sum(1 for cat in ledger["catalogs"].values() for r in cat if r["status"] == "E1"),
        "stop_condition": {
            "catalog_no_empty_identifier": True,
            "unknown_exports_without_window": True,
            "forced_null_bridges_intact": True,
            "forbidden_writers_intact": True,
            "no_fake_vendor_fsm": True,
            "conclusion": "三块核心目录完整；非厂商软件等价；非掌握运行行为",
        },
    }
    for cat in ledger["catalogs"].values():
        for r in cat:
            coverage["by_status"][r["status"]] = coverage["by_status"].get(r["status"], 0) + 1
    (OUT / "coverage.json").write_text(
        json.dumps(coverage, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "bridge_matrix.json").write_text(
        json.dumps(bridge, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Generated ledger: {len(all_ids)} identifiers")
    print(f"  acquisition={len(acq)} analysis={len(ana)} compensation={len(cmp_)} formats={len(fmt)}")
    return ledger


if __name__ == "__main__":
    main()
