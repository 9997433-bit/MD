"""Shared pytest fixtures for device_learning tests."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / "phase_b" / "captures"
GITKEEP = CAPTURES / ".gitkeep"
SYNTH = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"
EEPROM_CAPTURE = CAPTURES / "eeprom.bin"
SCRIPTS = ROOT / "scripts"
# Session stash so real device dumps survive pytest without breaking empty-capture tests.
_STASH = ROOT / "phase_b" / ".pytest_captures_stash"


def _refresh_phase_b_manifests() -> None:
    for script in ("ingest_phase_b.py", "sync_phase_b_checklist.py", "detect_phase_transition.py"):
        subprocess.run([sys.executable, str(SCRIPTS / script)], cwd=ROOT, check=False)


FW_OUT = ROOT / "phase_b" / "analysis" / "firmware.bin"


def restore_analysis_artifacts() -> None:
    analysis = ROOT / "phase_b" / "analysis"
    if analysis.exists():
        for path in analysis.iterdir():
            if path.is_file() and path.name != ".gitkeep":
                path.unlink()
        (analysis / ".gitkeep").touch(exist_ok=True)


def restore_captures_dir() -> None:
    """Empty captures/ for test isolation (real dumps live in session stash)."""
    CAPTURES.mkdir(parents=True, exist_ok=True)
    for path in CAPTURES.iterdir():
        if path.is_file() and path.name != ".gitkeep":
            path.unlink()
    GITKEEP.touch(exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def _stash_real_captures_for_session():
    """Move real captures aside for the whole pytest session, restore afterward."""
    _STASH.mkdir(parents=True, exist_ok=True)
    CAPTURES.mkdir(parents=True, exist_ok=True)
    for path in list(CAPTURES.iterdir()):
        if path.is_file() and path.name != ".gitkeep":
            dest = _STASH / path.name
            if dest.exists():
                dest.unlink()
            shutil.move(str(path), str(dest))
    GITKEEP.touch(exist_ok=True)
    yield
    CAPTURES.mkdir(parents=True, exist_ok=True)
    for path in list(CAPTURES.iterdir()):
        if path.is_file() and path.name != ".gitkeep":
            path.unlink()
    if _STASH.exists():
        for path in _STASH.iterdir():
            if path.is_file():
                shutil.move(str(path), str(CAPTURES / path.name))
        shutil.rmtree(_STASH, ignore_errors=True)
    # Prefer git-tracked copies when stash was empty but files exist in index.
    subprocess.run(
        ["git", "checkout", "--", "phase_b/captures"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    GITKEEP.touch(exist_ok=True)
    _refresh_phase_b_manifests()


@pytest.fixture(autouse=True)
def _phase_c_logs_hygiene():
    yield
    logs = ROOT / "phase_c" / "logs"
    if logs.exists():
        for path in logs.glob("_test*.json"):
            path.unlink()
    subprocess.run([sys.executable, str(SCRIPTS / "sync_phase_c_checklist.py")], cwd=ROOT, check=False)


@pytest.fixture(autouse=True)
def _captures_dir_hygiene():
    yield
    restore_captures_dir()
    restore_analysis_artifacts()
    _refresh_phase_b_manifests()


@pytest.fixture
def synthetic_eeprom_capture():
    """Place synthetic fixture in captures/ for pipeline tests (not device data)."""
    CAPTURES.mkdir(parents=True, exist_ok=True)
    shutil.copy(SYNTH, EEPROM_CAPTURE)
    yield
    restore_captures_dir()
    _refresh_phase_b_manifests()
