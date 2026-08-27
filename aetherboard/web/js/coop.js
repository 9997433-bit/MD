export const P1_UNITS = ["knight", "bard"];
export const P2_UNITS = ["white_mage", "black_mage"];

export function canControl(playerId, unitId, coopEnabled) {
  if (!coopEnabled || !playerId) return true;
  const allowed = playerId === 1 ? P1_UNITS : P2_UNITS;
  return allowed.includes(unitId);
}

export function ownerOf(unitId) {
  if (P1_UNITS.includes(unitId)) return 1;
  if (P2_UNITS.includes(unitId)) return 2;
  return 0;
}
