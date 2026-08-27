#!/usr/bin/env bash
# Run the same checks as CI locally (Python + C# + script syntax).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

echo "==> Python tests"
PYTHONPATH=. python3 -m unittest discover -s tests -q

echo "==> C# tests"
(cd csharp/Aetherboard.Core.Tests && dotnet test -v q)

echo "==> Script syntax"
bash -n scripts/quest_verify.sh

echo ""
echo "All Aetherboard tests passed (Python + C# + scripts)."
