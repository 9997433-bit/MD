#!/usr/bin/env bash
# Pre-merge / pre-release checks for Aetherboard VR milestone.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

echo "Aetherboard VR release preflight"
echo "================================"
echo "Version: $(cat VERSION 2>/dev/null || echo unknown)"
echo ""

"${ROOT}/scripts/run_all_tests.sh"

echo ""
echo "Manual checklist (post-merge):"
echo "  [ ] Unity: Aetherboard → First Time Setup (Recommended) → Play"
echo "  [ ] Quest: Build APK → ./scripts/quest_verify.sh"
echo "  [ ] Quest: Complete 10 manual items in docs/QUEST_VERIFICATION.md"
echo "  [x] GitHub: PR #5 merged to main (2026-08-27)"
echo ""
echo "Preflight automated checks passed."
