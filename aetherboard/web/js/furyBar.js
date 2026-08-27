/** Boss fury / cyclone cast bar — aligned with Unity FuryCastBarVFX. */

export function createFuryBarElements(root = document) {
  const container = root.getElementById("fury-cast");
  return {
    container,
    fill: root.getElementById("fury-bar-fill"),
    label: root.getElementById("fury-label"),
    burst: root.getElementById("fury-burst"),
  };
}

export function updateFuryBar(elements, boss, profile, lastFury = 0) {
  if (!elements?.container) return boss?.fury ?? 0;

  const fury = boss?.fury ?? 0;
  const wasCasting = lastFury > 0;
  const interrupted = wasCasting && fury < 0;
  const casting = fury > 0;

  elements.container.classList.toggle("hidden", !casting && !interrupted);
  elements.container.classList.toggle("earth", profile?.bossId !== "wind");
  elements.container.classList.toggle("wind", profile?.bossId === "wind");
  elements.container.classList.toggle("urgent", casting && fury === 1);
  elements.container.classList.toggle("casting", casting);

  if (interrupted) {
    flashInterrupt(elements);
    return fury;
  }

  if (!casting) return fury;

  const maxTurns = 2;
  const ratio = Math.max(0, Math.min(1, fury / maxTurns));
  if (elements.fill) elements.fill.style.width = `${ratio * 100}%`;
  if (elements.label) {
    elements.label.textContent = `${profile?.furyName ?? "读条"} · 剩余 ${fury} 回合`;
  }
  return fury;
}

function flashInterrupt(elements) {
  if (!elements.burst) return;
  elements.burst.classList.remove("hidden");
  elements.burst.classList.add("active");
  if (elements.label) elements.label.textContent = "读条已打断！";
  if (elements.fill) elements.fill.style.width = "0%";
  window.setTimeout(() => {
    elements.burst?.classList.remove("active");
    elements.burst?.classList.add("hidden");
    elements.container?.classList.add("hidden");
  }, 700);
}
