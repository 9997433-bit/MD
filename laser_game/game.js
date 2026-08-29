(() => {
  const SIZE = 8;
  const DIRS = {
    N: { x: 0, y: -1 },
    E: { x: 1, y: 0 },
    S: { x: 0, y: 1 },
    W: { x: -1, y: 0 },
  };
  // 角反射镜：仅两个入射方向有效（facing 表示开口朝向）
  const MIRROR_REFLECT = {
    NE: { N: "E", E: "N", S: null, W: null },
    NW: { N: "W", W: "N", S: null, E: null },
    SE: { S: "E", E: "S", N: null, W: null },
    SW: { S: "W", W: "S", N: null, E: null },
  };
  const MIRROR_CYCLE = ["NE", "SE", "SW", "NW"];

  // facing 为开局打乱态；通关解已用脚本校验
  const LEVELS = [
    {
      name: "对准",
      tip: "点击反射镜旋转，把红光送进探测器。",
      emitter: { x: 1, y: 3, dir: "E" },
      mirrors: [{ x: 4, y: 3, facing: "SW" }],
      walls: [],
      targets: [{ x: 4, y: 1 }],
    },
    {
      name: "拐角",
      tip: "需要两次反射才能进探测器。",
      emitter: { x: 1, y: 1, dir: "E" },
      mirrors: [
        { x: 5, y: 1, facing: "NW" },
        { x: 5, y: 5, facing: "NE" },
      ],
      walls: [{ x: 3, y: 3 }],
      targets: [{ x: 2, y: 5 }],
    },
    {
      name: "挡板",
      tip: "挡板会挡住光束，绕过去。",
      emitter: { x: 0, y: 4, dir: "E" },
      mirrors: [
        { x: 3, y: 4, facing: "SW" },
        { x: 3, y: 1, facing: "SW" },
        { x: 6, y: 1, facing: "NW" },
      ],
      walls: [
        { x: 5, y: 4 },
        { x: 5, y: 3 },
        { x: 5, y: 2 },
      ],
      targets: [{ x: 6, y: 4 }],
    },
    {
      name: "双探",
      tip: "同一束光要依次点亮两个探测器。",
      emitter: { x: 1, y: 6, dir: "N" },
      mirrors: [
        { x: 1, y: 2, facing: "SW" },
        { x: 5, y: 2, facing: "NW" },
        { x: 5, y: 5, facing: "NE" },
      ],
      walls: [{ x: 3, y: 4 }],
      targets: [
        { x: 1, y: 4 },
        { x: 3, y: 5 },
      ],
    },
    {
      name: "迷宫",
      tip: "多面镜子，慢慢排光路。",
      emitter: { x: 0, y: 0, dir: "E" },
      mirrors: [
        { x: 3, y: 0, facing: "NW" },
        { x: 3, y: 3, facing: "NW" },
        { x: 6, y: 3, facing: "NW" },
        { x: 6, y: 6, facing: "NE" },
        { x: 1, y: 6, facing: "SE" },
      ],
      walls: [
        { x: 2, y: 2 },
        { x: 4, y: 4 },
        { x: 5, y: 1 },
      ],
      targets: [{ x: 1, y: 3 }],
    },
    {
      name: "远端",
      tip: "最后一关：把光送到棋盘另一侧。",
      emitter: { x: 7, y: 0, dir: "S" },
      mirrors: [
        { x: 7, y: 2, facing: "NE" },
        { x: 4, y: 2, facing: "NE" },
        { x: 4, y: 5, facing: "NE" },
        { x: 1, y: 5, facing: "NE" },
        { x: 1, y: 7, facing: "NW" },
      ],
      walls: [
        { x: 5, y: 3 },
        { x: 3, y: 6 },
        { x: 2, y: 3 },
      ],
      targets: [{ x: 6, y: 7 }],
    },
  ];

  const els = {
    intro: document.getElementById("intro"),
    play: document.getElementById("play"),
    win: document.getElementById("win"),
    how: document.getElementById("how"),
    canvas: document.getElementById("board"),
    tip: document.getElementById("tip"),
    levelLabel: document.getElementById("levelLabel"),
    moveLabel: document.getElementById("moveLabel"),
    winText: document.getElementById("winText"),
  };
  const ctx = els.canvas.getContext("2d");

  let levelIndex = 0;
  let state = null;
  let beamPath = [];
  let lit = new Set();
  let moves = 0;
  let anim = null;
  let beamProgress = 0;

  function cloneLevel(level) {
    return {
      name: level.name,
      tip: level.tip,
      emitter: { ...level.emitter },
      mirrors: level.mirrors.map((m) => ({ ...m })),
      walls: level.walls.map((w) => ({ ...w })),
      targets: level.targets.map((t) => ({ ...t })),
    };
  }

  function cellAt(x, y) {
    if (x < 0 || y < 0 || x >= SIZE || y >= SIZE) return { type: "edge" };
    for (const w of state.walls) if (w.x === x && w.y === y) return { type: "wall" };
    for (const m of state.mirrors) if (m.x === x && m.y === y) return { type: "mirror", facing: m.facing };
    for (const t of state.targets) if (t.x === x && t.y === y) return { type: "target" };
    const e = state.emitter;
    if (e.x === x && e.y === y) return { type: "emitter", dir: e.dir };
    return { type: "empty" };
  }

  function simulate() {
    const path = [];
    const hit = new Set();
    let x = state.emitter.x;
    let y = state.emitter.y;
    let dir = state.emitter.dir;
    path.push({ x, y, dir });

    for (let step = 0; step < 64; step++) {
      const d = DIRS[dir];
      const nx = x + d.x;
      const ny = y + d.y;
      const cell = cellAt(nx, ny);
      if (cell.type === "edge" || cell.type === "wall") break;

      x = nx;
      y = ny;
      path.push({ x, y, dir });

      if (cell.type === "target") {
        hit.add(`${x},${y}`);
      }

      if (cell.type === "mirror") {
        const next = MIRROR_REFLECT[cell.facing][dir];
        if (!next) break; // hit back of mirror
        dir = next;
        path[path.length - 1].dir = dir;
        path[path.length - 1].bounce = true;
      }

      if (cell.type === "emitter" && step > 0) break;
    }
    return { path, hit };
  }

  function loadLevel(i) {
    levelIndex = Math.max(0, Math.min(i, LEVELS.length - 1));
    state = cloneLevel(LEVELS[levelIndex]);
    beamPath = [];
    lit = new Set();
    moves = 0;
    beamProgress = 0;
    if (anim) cancelAnimationFrame(anim);
    anim = null;
    els.levelLabel.textContent = `关卡 ${levelIndex + 1} · ${state.name}`;
    els.moveLabel.textContent = `操作 ${moves}`;
    els.tip.textContent = state.tip;
    draw();
  }

  function show(view) {
    for (const key of ["intro", "play", "win", "how"]) {
      els[key].classList.toggle("hidden", key !== view);
    }
  }

  function cellSize() {
    return els.canvas.width / SIZE;
  }

  function drawGrid() {
    const s = cellSize();
    ctx.clearRect(0, 0, els.canvas.width, els.canvas.height);

    // optical table holes
    ctx.fillStyle = "#eef3f7";
    ctx.fillRect(0, 0, els.canvas.width, els.canvas.height);
    ctx.fillStyle = "rgba(26,34,41,0.12)";
    for (let y = 0; y < SIZE; y++) {
      for (let x = 0; x < SIZE; x++) {
        const cx = (x + 0.5) * s;
        const cy = (y + 0.5) * s;
        ctx.beginPath();
        ctx.arc(cx, cy, 2.2, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    ctx.strokeStyle = "rgba(26,34,41,0.08)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= SIZE; i++) {
      ctx.beginPath();
      ctx.moveTo(i * s, 0);
      ctx.lineTo(i * s, els.canvas.width);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, i * s);
      ctx.lineTo(els.canvas.width, i * s);
      ctx.stroke();
    }
  }

  function drawWall(x, y, s) {
    ctx.fillStyle = "#3d4650";
    roundRect(x * s + s * 0.18, y * s + s * 0.18, s * 0.64, s * 0.64, 4);
    ctx.fill();
  }

  function drawEmitter(x, y, dir, s) {
    const cx = (x + 0.5) * s;
    const cy = (y + 0.5) * s;
    ctx.fillStyle = "#e6232a";
    ctx.beginPath();
    ctx.arc(cx, cy, s * 0.22, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "rgba(230,35,42,0.35)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(cx, cy, s * 0.32, 0, Math.PI * 2);
    ctx.stroke();

    const d = DIRS[dir];
    ctx.strokeStyle = "#e6232a";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + d.x * s * 0.38, cy + d.y * s * 0.38);
    ctx.stroke();
  }

  function drawMirror(x, y, facing, s) {
    const cx = (x + 0.5) * s;
    const cy = (y + 0.5) * s;
    const map = {
      NE: -Math.PI / 4,
      SE: Math.PI / 4,
      SW: (3 * Math.PI) / 4,
      NW: (-3 * Math.PI) / 4,
    };
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(map[facing]);
    ctx.fillStyle = "#2f6f8f";
    ctx.strokeStyle = "#1d4d66";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(-s * 0.28, s * 0.06);
    ctx.lineTo(s * 0.28, s * 0.06);
    ctx.lineTo(s * 0.28, -s * 0.06);
    ctx.lineTo(-s * 0.28, -s * 0.06);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    // reflective face highlight
    ctx.strokeStyle = "rgba(255,255,255,0.55)";
    ctx.beginPath();
    ctx.moveTo(-s * 0.22, -s * 0.02);
    ctx.lineTo(s * 0.22, -s * 0.02);
    ctx.stroke();
    ctx.restore();
  }

  function drawTarget(x, y, s, on) {
    const cx = (x + 0.5) * s;
    const cy = (y + 0.5) * s;
    ctx.fillStyle = on ? "#1fd9a0" : "#0f8f6b";
    ctx.beginPath();
    ctx.arc(cx, cy, s * 0.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = on ? "rgba(31,217,160,0.45)" : "rgba(15,143,107,0.35)";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(cx, cy, s * 0.3, 0, Math.PI * 2);
    ctx.stroke();
    if (on) {
      ctx.fillStyle = "rgba(31,217,160,0.2)";
      ctx.beginPath();
      ctx.arc(cx, cy, s * 0.42, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function drawBeam() {
    if (!beamPath.length) return;
    const s = cellSize();
    const maxPts = Math.max(1, Math.floor(beamProgress));
    const pts = beamPath.slice(0, maxPts);
    if (pts.length < 2) {
      // start glow
      const p = pts[0] || beamPath[0];
      glowAt((p.x + 0.5) * s, (p.y + 0.5) * s);
      return;
    }

    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = "rgba(230,35,42,0.25)";
    ctx.lineWidth = 10;
    ctx.beginPath();
    ctx.moveTo((pts[0].x + 0.5) * s, (pts[0].y + 0.5) * s);
    for (let i = 1; i < pts.length; i++) {
      ctx.lineTo((pts[i].x + 0.5) * s, (pts[i].y + 0.5) * s);
    }
    ctx.stroke();

    ctx.strokeStyle = "#e6232a";
    ctx.lineWidth = 3.5;
    ctx.beginPath();
    ctx.moveTo((pts[0].x + 0.5) * s, (pts[0].y + 0.5) * s);
    for (let i = 1; i < pts.length; i++) {
      ctx.lineTo((pts[i].x + 0.5) * s, (pts[i].y + 0.5) * s);
    }
    ctx.stroke();

    const last = pts[pts.length - 1];
    glowAt((last.x + 0.5) * s, (last.y + 0.5) * s);
  }

  function glowAt(x, y) {
    const g = ctx.createRadialGradient(x, y, 0, x, y, 18);
    g.addColorStop(0, "rgba(255,120,100,0.85)");
    g.addColorStop(1, "rgba(230,35,42,0)");
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, 18, 0, Math.PI * 2);
    ctx.fill();
  }

  function roundRect(x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  function draw() {
    drawGrid();
    const s = cellSize();
    for (const w of state.walls) drawWall(w.x, w.y, s);
    for (const m of state.mirrors) drawMirror(m.x, m.y, m.facing, s);
    for (const t of state.targets) drawTarget(t.x, t.y, s, lit.has(`${t.x},${t.y}`));
    drawEmitter(state.emitter.x, state.emitter.y, state.emitter.dir, s);
    drawBeam();
  }

  function fire() {
    const result = simulate();
    beamPath = result.path;
    lit = new Set();
    beamProgress = 1;

    const animate = () => {
      beamProgress += 0.35;
      const reached = Math.min(beamPath.length, Math.floor(beamProgress));
      for (let i = 0; i < reached; i++) {
        const p = beamPath[i];
        if (state.targets.some((t) => t.x === p.x && t.y === p.y)) {
          lit.add(`${p.x},${p.y}`);
        }
      }
      draw();
      if (beamProgress < beamPath.length) {
        anim = requestAnimationFrame(animate);
      } else {
        anim = null;
        const win = state.targets.every((t) => lit.has(`${t.x},${t.y}`));
        if (win) {
          setTimeout(() => {
            els.winText.textContent =
              levelIndex === LEVELS.length - 1
                ? `全部 ${LEVELS.length} 关完成。氦氖红光稳稳落在探测器上。`
                : `关卡「${state.name}」完成，用了 ${moves} 次旋转。`;
            show("win");
          }, 280);
        } else {
          els.tip.textContent = "没全中。再调镜子，然后发射。";
        }
      }
    };
    if (anim) cancelAnimationFrame(anim);
    anim = requestAnimationFrame(animate);
  }

  function rotateAt(gx, gy) {
    const m = state.mirrors.find((mm) => mm.x === gx && mm.y === gy);
    if (!m) return;
    const i = MIRROR_CYCLE.indexOf(m.facing);
    m.facing = MIRROR_CYCLE[(i + 1) % MIRROR_CYCLE.length];
    moves += 1;
    els.moveLabel.textContent = `操作 ${moves}`;
    beamPath = [];
    lit = new Set();
    els.tip.textContent = state.tip;
    draw();
  }

  function canvasCoords(evt) {
    const rect = els.canvas.getBoundingClientRect();
    const scaleX = els.canvas.width / rect.width;
    const scaleY = els.canvas.height / rect.height;
    const x = (evt.clientX - rect.left) * scaleX;
    const y = (evt.clientY - rect.top) * scaleY;
    return {
      gx: Math.floor(x / cellSize()),
      gy: Math.floor(y / cellSize()),
    };
  }

  els.canvas.addEventListener("click", (evt) => {
    const { gx, gy } = canvasCoords(evt);
    rotateAt(gx, gy);
  });

  document.getElementById("btnStart").addEventListener("click", () => {
    loadLevel(0);
    show("play");
  });
  document.getElementById("btnHow").addEventListener("click", () => show("how"));
  document.getElementById("btnHowClose").addEventListener("click", () => show("intro"));
  document.getElementById("btnFire").addEventListener("click", fire);
  document.getElementById("btnReset").addEventListener("click", () => loadLevel(levelIndex));
  document.getElementById("btnSkip").addEventListener("click", () => {
    if (levelIndex < LEVELS.length - 1) {
      loadLevel(levelIndex + 1);
      show("play");
    } else {
      els.winText.textContent = "已经是最后一关。";
      show("win");
    }
  });
  document.getElementById("btnNext").addEventListener("click", () => {
    if (levelIndex < LEVELS.length - 1) {
      loadLevel(levelIndex + 1);
      show("play");
    } else {
      loadLevel(0);
      show("play");
    }
  });
  document.getElementById("btnAgain").addEventListener("click", () => {
    loadLevel(levelIndex);
    show("play");
  });

  if (new URLSearchParams(location.search).get("play") === "1") {
    loadLevel(0);
    show("play");
    const m = state.mirrors[0];
    if (m) m.facing = "NE";
    draw();
    setTimeout(fire, 500);
  }
})();
