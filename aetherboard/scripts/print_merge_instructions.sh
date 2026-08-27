#!/usr/bin/env bash
# Print merge instructions for Aetherboard VR milestone PR.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(cat "${ROOT}/VERSION" 2>/dev/null || echo unknown)"

cat <<EOF
Aetherboard VR merge instructions (${VERSION})
============================================

Branch:  cursor/vr-battle-board-e6ea → main
PR:      https://github.com/9997433-bit/MD/pull/5

1. Run automated preflight:
   cd aetherboard && ./scripts/release_preflight.sh

2. Update PR title to:
   feat(aetherboard): VR battle board milestone — Unity OpenXR, netcode, Quest toolchain (v0.2.0-vr)

3. Copy PR body from:
   aetherboard/docs/GITHUB_PR_BODY.md

4. Mark PR as "Ready for review" (undraft) and merge.

5. After merge (Quest hardware required):
   - Unity: First Time Setup → Build APK
   - ./scripts/quest_verify.sh
   - Complete docs/QUEST_VERIFICATION.md manual checklist

EOF
