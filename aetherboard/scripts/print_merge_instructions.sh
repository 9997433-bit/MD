#!/usr/bin/env bash
# Print post-merge status for Aetherboard VR milestone.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(cat "${ROOT}/VERSION" 2>/dev/null || echo unknown)"

cat <<EOF
Aetherboard VR milestone status (${VERSION})
==========================================

PR #5: MERGED to main (2026-08-27)
https://github.com/9997433-bit/MD/pull/5

Verify locally:
  cd aetherboard && ./scripts/release_preflight.sh

Quest sideload (hardware required):
  Unity: First Time Setup → Build Quest APK
  ./scripts/quest_verify.sh
  docs/QUEST_VERIFICATION.md (10 manual items)

Optional:
  Replace FBX in Resources/Aetherboard/Art/Models/

EOF
