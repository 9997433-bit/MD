#!/usr/bin/env bash
# Quest sideload smoke test — install APK, launch app, pull verification report.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APK="${ROOT}/build/AetherboardVR.apk"
REPORT_DIR="${ROOT}/build/quest_reports"
REPORT_FILE="${REPORT_DIR}/quest_verification.txt"
PACKAGE="com.aetherboard.vr"
ACTIVITY="com.unity3d.player.UnityPlayerActivity"
REMOTE_REPORT="/sdcard/Download/quest_verification.txt"
BOOT_WAIT="${BOOT_WAIT:-12}"

find_adb() {
  if command -v adb >/dev/null 2>&1; then
    command -v adb
    return 0
  fi
  for sdk in "${ANDROID_HOME:-}" "${ANDROID_SDK_ROOT:-}"; do
    if [[ -n "$sdk" && -x "${sdk}/platform-tools/adb" ]]; then
      echo "${sdk}/platform-tools/adb"
      return 0
    fi
  done
  return 1
}

ADB="$(find_adb || true)"
if [[ -z "${ADB}" ]]; then
  echo "ERROR: adb not found. Set ANDROID_HOME or install platform-tools." >&2
  exit 1
fi

if ! "${ADB}" devices | grep -q "device$"; then
  echo "ERROR: No authorized Quest/device connected." >&2
  "${ADB}" devices -l
  exit 1
fi

if [[ ! -f "${APK}" ]]; then
  echo "ERROR: APK not found at ${APK}" >&2
  echo "Build in Unity: Aetherboard → Build Quest APK to build/" >&2
  exit 1
fi

echo "==> Installing ${APK}"
"${ADB}" install -r "${APK}"

echo "==> Clearing logcat"
"${ADB}" logcat -c

echo "==> Launching ${PACKAGE}/${ACTIVITY}"
"${ADB}" shell am start -n "${PACKAGE}/${ACTIVITY}"

echo "==> Waiting ${BOOT_WAIT}s for runtime diagnostics"
sleep "${BOOT_WAIT}"

mkdir -p "${REPORT_DIR}"
echo "==> Pulling verification report"
if "${ADB}" pull "${REMOTE_REPORT}" "${REPORT_FILE}" 2>/dev/null; then
  echo "Report saved: ${REPORT_FILE}"
  echo "---"
  cat "${REPORT_FILE}"
  echo "---"
  FAILS="$(grep -c '\[FAIL\]' "${REPORT_FILE}" || true)"
  echo "Automated FAIL count: ${FAILS}"
  if [[ "${FAILS}" -gt 0 ]]; then
    exit 2
  fi
else
  echo "WARN: Report file missing. Recent Aetherboard logcat lines:"
  "${ADB}" logcat -d -s Unity | grep Aetherboard | tail -n 40 || true
  exit 3
fi

echo "Quest smoke test passed (automated checks only). Complete manual checklist in QUEST_VERIFICATION.md."
