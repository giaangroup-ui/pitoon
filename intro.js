/* PiToon landing intro — SVG ant, spring physics, Web Audio SFX. No external assets. */
(function (global) {
  const DUR = 9.7;
  const STORE = "pt_intro_seen";
  const SNDK = "pt_intro_sound";

  function Spring(x, k, c) {
    this.x = x || 0; this.v = 0; this.k = k || 180; this.c = c || 16; this.t = x || 0;
  }
  Spring.prototype.set = function (t) { this.t = t; };
  Spring.prototype.snap = function (v) { this.x = this.t = v; this.v = 0; };
  Spring.prototype.step = function (dt) {
    const a = -this.k * (this.x - this.t) - this.c * this.v;
    this.v += a * dt; this.x += this.v * dt; return this.x;
  };

  const ANT_SVG = `<svg class="pti-ant" id="ptiAnt" viewBox="0 0 160 140" aria-hidden="true">
    <g id="ptiAntRoot">
      <g id="ptiLegs" fill="none" stroke="#3a241c" stroke-width="5" stroke-linecap="round">
        <path id="L1" d="M70 88 C50 100 40 118 28 124"/>
        <path id="L2" d="M78 92 C62 108 58 122 48 130"/>
        <path id="L3" d="M86 90 C80 110 86 124 80 132"/>
        <path id="R1" d="M96 88 C116 100 126 118 138 124"/>
        <path id="R2" d="M88 92 C104 108 108 122 118 130"/>
        <path id="R3" d="M80 90 C86 110 80 124 86 132"/>
      </g>
      <ellipse cx="86" cy="96" rx="28" ry="22" fill="#4a2e24"/>
      <ellipse cx="86" cy="96" rx="18" ry="13" fill="#5b3a30"/>
      <ellipse id="ptiThorax" cx="72" cy="78" rx="16" ry="14" fill="#3a241c"/>
      <g id="ptiHead">
        <path d="M58 38 C52 18 62 8 70 16" fill="none" stroke="#3a241c" stroke-width="3.5" stroke-linecap="round"/>
        <path d="M78 36 C86 14 100 10 104 20" fill="none" stroke="#3a241c" stroke-width="3.5" stroke-linecap="round"/>
        <circle cx="58" cy="16" r="3.2" fill="#3a241c"/><circle cx="104" cy="18" r="3.2" fill="#3a241c"/>
        <ellipse cx="70" cy="52" rx="26" ry="24" fill="#4a2e24"/>
        <ellipse cx="62" cy="58" rx="6" ry="4" fill="#f4a89a" opacity=".85"/>
        <ellipse cx="82" cy="58" rx="6" ry="4" fill="#f4a89a" opacity=".85"/>
        <path d="M62 66 Q70 72 80 66" fill="none" stroke="#2a1814" stroke-width="2" stroke-linecap="round"/>
        <g id="ptiEyes">
          <ellipse class="eye" cx="60" cy="50" rx="6" ry="7" fill="#fff"/>
          <ellipse class="eye" cx="80" cy="50" rx="6" ry="7" fill="#fff"/>
          <circle class="pup" cx="61" cy="51" r="3" fill="#1a1a1a"/>
          <circle class="pup" cx="81" cy="51" r="3" fill="#1a1a1a"/>
        </g>
        <g id="ptiGlasses" transform="translate(0,0)">
          <circle cx="60" cy="51" r="14" fill="none" stroke="#1a1a1a" stroke-width="5"/>
          <circle cx="84" cy="51" r="14" fill="none" stroke="#1a1a1a" stroke-width="5"/>
          <path d="M74 51 H70" stroke="#1a1a1a" stroke-width="3.5" stroke-linecap="round"/>
          <path d="M46 50 L40 48" stroke="#1a1a1a" stroke-width="3" stroke-linecap="round"/>
          <path d="M98 50 L104 48" stroke="#1a1a1a" stroke-width="3" stroke-linecap="round"/>
          <circle cx="60" cy="51" r="10" fill="#cfe8ff" opacity=".35"/>
          <circle cx="84" cy="51" r="10" fill="#cfe8ff" opacity=".35"/>
        </g>
      </g>
    </g>
  </svg>`;

  const BULB = `<svg class="pti-bulb" viewBox="0 0 52 64" aria-hidden="true">
    <ellipse cx="26" cy="24" rx="18" ry="20" fill="#ffe566" stroke="#e8b84a" stroke-width="2"/>
    <rect x="18" y="42" width="16" height="8" rx="2" fill="#cfd4dc"/>
    <rect x="20" y="50" width="12" height="6" rx="2" fill="#aeb6c1"/>
    <path d="M20 28 L32 20" stroke="#fff6" stroke-width="2"/>
  </svg>`;

  /* ---------- Web Audio ---------- */
  let actx, master, muted = false, lastCue = {};
  function ctx() {
    if (!actx) {
      const AC = global.AudioContext || global.webkitAudioContext;
      if (!AC) return null;
      actx = new AC();
      master = actx.createGain();
      master.gain.value = muted ? 0 : 0.7;
      master.connect(actx.destination);
    }
    if (actx.state === "suspended") actx.resume();
    return actx;
  }
  function envGain(t, a, d, v) {
    const c = ctx(); if (!c || muted) return null;
    const g = c.createGain();
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(v, t + a);
    g.gain.exponentialRampToValueAtTime(0.0001, t + a + d);
    g.connect(master); return g;
  }
  function noise(c, dur) {
    const n = c.createBufferSource();
    const b = c.createBuffer(1, Math.max(1, dur * c.sampleRate), c.sampleRate);
    const d = b.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    n.buffer = b; return n;
  }
  const SFX = {
    tiptoe() {
      const c = ctx(); if (!c || muted) return;
      const t = c.currentTime;
      const o = c.createOscillator(); o.type = "sine"; o.frequency.setValueAtTime(180, t);
      o.frequency.exponentialRampToValueAtTime(90, t + 0.07);
      const g = envGain(t, 0.005, 0.08, 0.22); if (!g) return;
      o.connect(g); o.start(t); o.stop(t + 0.1);
      const n = noise(c, 0.06), f = c.createBiquadFilter(); f.type = "lowpass"; f.frequency.value = 600;
      const ng = envGain(t, 0.002, 0.05, 0.12); n.connect(f); f.connect(ng); n.start(t); n.stop(t + 0.06);
    },
    blink() {
      const c = ctx(); if (!c || muted) return;
      const t = c.currentTime, o = c.createOscillator(); o.type = "triangle";
      o.frequency.setValueAtTime(1400, t); o.frequency.exponentialRampToValueAtTime(900, t + 0.04);
      const g = envGain(t, 0.001, 0.04, 0.08); if (!g) return;
      o.connect(g); o.start(t); o.stop(t + 0.05);
    },
    roll() {
      const c = ctx(); if (!c || muted) return;
      const t = c.currentTime, n = noise(c, 0.9), f = c.createBiquadFilter();
      f.type = "bandpass"; f.frequency.setValueAtTime(400, t); f.frequency.linearRampToValueAtTime(180, t + 0.8);
      const g = envGain(t, 0.05, 0.85, 0.18); if (!g) return;
      n.connect(f); f.connect(g); n.start(t); n.stop(t + 0.9);
    },
    pop() {
      const c = ctx(); if (!c || muted) return;
      const t = c.currentTime, o = c.createOscillator(); o.type = "sine";
      o.frequency.setValueAtTime(720, t); o.frequency.exponentialRampToValueAtTime(240, t + 0.14);
      const g = envGain(t, 0.003, 0.16, 0.35); if (!g) return;
      o.connect(g); o.start(t); o.stop(t + 0.18);
    },
    boom() {
      const c = ctx(); if (!c || muted) return;
      const t = c.currentTime;
      const o = c.createOscillator(); o.type = "sine"; o.frequency.setValueAtTime(110, t);
      o.frequency.exponentialRampToValueAtTime(40, t + 0.5);
      const g = envGain(t, 0.005, 0.6, 0.7); if (!g) return;
      o.connect(g); o.start(t); o.stop(t + 0.65);
      const n = noise(c, 0.45), f = c.createBiquadFilter(); f.type = "lowpass"; f.frequency.value = 800;
      const ng = envGain(t, 0.004, 0.4, 0.45); n.connect(f); f.connect(ng); n.start(t); n.stop(t + 0.45);
    },
    whoosh() {
      const c = ctx(); if (!c || muted) return;
      const t = c.currentTime, n = noise(c, 1.2), f = c.createBiquadFilter();
      f.type = "bandpass"; f.Q.value = 0.8;
      f.frequency.setValueAtTime(300, t); f.frequency.exponentialRampToValueAtTime(1800, t + 0.9);
      const g = envGain(t, 0.08, 1.0, 0.4); if (!g) return;
      n.connect(f); f.connect(g); n.start(t); n.stop(t + 1.2);
    }
  };
  function cue(name, t, key) {
    const k = key || name + t.toFixed(2);
    if (lastCue[k]) return;
    lastCue[k] = 1;
    if (SFX[name]) SFX[name]();
  }

  function easeOutBack(x) { const c = 1.70158; const t = x - 1; return 1 + (c + 1) * t * t * t + c * t * t; }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function smooth(t0, t1, t) { const x = clamp((t - t0) / Math.max(0.0001, t1 - t0), 0, 1); return x * x * (3 - 2 * x); }

  function build(root) {
    root.innerHTML = "";
    root.className = "pti";
    root.setAttribute("role", "dialog");
    root.setAttribute("aria-label", "Hoạt ảnh mở đầu PiToon");
    const fx = document.createElement("canvas"); fx.className = "pti-fx"; fx.id = "ptiFx";
    const flash = document.createElement("div"); flash.className = "pti-flash";
    const portal = document.createElement("div"); portal.className = "pti-portal";
    const stage = document.createElement("div"); stage.className = "pti-stage";
    const world = document.createElement("div"); world.className = "pti-world";
    world.innerHTML = ANT_SVG + BULB +
      `<div class="pti-logo" id="ptiLogo" aria-hidden="true">
        <span class="ch" data-ch="P">P</span><span class="ch" data-ch="i">i</span><span class="ch" data-ch="T">T</span>
        <span class="pti-hole" id="hole0"></span><span class="pti-hole" id="hole1"></span>
        <span class="ch" data-ch="n">n</span>
      </div>
      <div class="pti-o" id="o0"></div><div class="pti-o" id="o1"></div>`;
    stage.appendChild(world);
    const skip = document.createElement("button"); skip.className = "pti-skip"; skip.type = "button"; skip.textContent = "Bỏ qua";
    const snd = document.createElement("button"); snd.className = "pti-snd"; snd.type = "button"; snd.setAttribute("aria-label", "Bật/tắt âm thanh");
    root.append(fx, portal, flash, stage, skip, snd);
    return { fx, flash, portal, world, skip, snd };
  }

  let playing = false, startT = 0, raf = 0, els = null, host = null, onDone = null, particles = [], isAds = false;
  const oPhys = [{ x: 0, y: 0, vx: 0, vy: 0, r: 0, vr: 0, mode: "slot" }, { x: 0, y: 0, vx: 0, vy: 0, r: 0, vr: 0, mode: "slot" }];

  function setMuted(m) {
    muted = m; try { localStorage.setItem(SNDK, m ? "0" : "1"); } catch (e) {}
    if (master) master.gain.value = m ? 0 : 0.7;
    if (els && els.snd) els.snd.textContent = m ? "🔇" : "🔊";
  }

  function holeCenter(id) {
    const h = document.getElementById(id), w = els.world.getBoundingClientRect();
    const r = h.getBoundingClientRect();
    return { x: r.left - w.left + r.width / 2, y: r.top - w.top + r.height / 2, s: r.width };
  }
  function placeO(el, p, rot, size) {
    el.style.width = size + "px"; el.style.height = size + "px";
    el.style.left = (p.x - size / 2) + "px"; el.style.top = (p.y - size / 2) + "px";
    el.style.transform = "rotate(" + rot + "deg)";
  }

  function blinkAmount(t) {
    const wins = [[0.72, 0.86], [1.22, 1.36], [1.95, 2.06]];
    let b = 0;
    for (const [a, c] of wins) {
      if (t >= a && t <= c) {
        const u = (t - a) / (c - a);
        b = Math.max(b, u < 0.5 ? u * 2 : (1 - u) * 2);
      }
    }
    return b;
  }

  function spawnBurst(n) {
    particles = [];
    for (let i = 0; i < n; i++) {
      const a = Math.random() * Math.PI * 2, sp = 80 + Math.random() * 420;
      particles.push({ x: 0.5, y: 0.48, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, life: 0.7 + Math.random() * 0.5,
        col: ["#ff6b3d", "#e8b84a", "#ff6b9a", "#7ec8e3", "#fff", "#2b3fa0"][i % 6], r: 2 + Math.random() * 5 });
    }
  }

  function drawFx(t) {
    const c = els.fx, g = c.getContext("2d");
    const w = c.width = c.clientWidth, h = c.height = c.clientHeight;
    g.clearRect(0, 0, w, h);
    if (t < 7.35) return;
    const dt = 1 / 60;
    for (const p of particles) {
      p.x += (p.vx / w) * dt; p.y += (p.vy / h) * dt; p.vy += 280 * dt; p.life -= dt;
      if (p.life <= 0) continue;
      g.globalAlpha = clamp(p.life * 1.6, 0, 1);
      g.fillStyle = p.col;
      g.beginPath(); g.arc(p.x * w, p.y * h, p.r, 0, 6.28); g.fill();
    }
    g.globalAlpha = 1;
  }

  function frame(now) {
    if (!playing) return;
    if (!startT) startT = now;
    const t = (now - startT) / 1000;
    const dt = Math.min(0.033, Math.max(0.008, (frame._p ? now - frame._p : 16) / 1000));
    frame._p = now;

    const ant = document.getElementById("ptiAnt");
    const head = document.getElementById("ptiHead");
    const eyes = document.getElementById("ptiEyes");
    const glasses = document.getElementById("ptiGlasses");
    const logo = document.getElementById("ptiLogo");
    const bulb = els.world.querySelector(".pti-bulb");
    const o0 = document.getElementById("o0"), o1 = document.getElementById("o1");

    /* --- ant position: peek, then walk dragging logo --- */
    let antX = -0.12, walk = 0; // fraction of world width, 0 = left edge
    if (t < 0.5) antX = lerp(-0.12, 0.0, smooth(0, 0.5, t)); // poke head first
    else if (t < 1.75) antX = lerp(-0.01, 0.06, smooth(0.45, 1.75, t));
    else if (t < 3.45) { walk = smooth(1.75, 3.45, t); antX = lerp(0.06, 0.16, walk); }
    else antX = 0.16;

    const bob = (t > 1.7 && t < 3.4) ? Math.sin((t - 1.7) * 10) * 6 : (t >= 0.35 && t < 1.7 ? Math.sin(t * 3) * 2 : 0);
    const look = t < 1.75
      ? Math.sin(t * 5.2) * 16 * (t > 0.5 ? 1 : 0)
      : (t > 5.0 && t < 5.8 ? -8 : 0);
    const blink = blinkAmount(t);
    if (eyes) eyes.style.transform = "scaleY(" + (1 - blink * 0.88) + ")";
    if (head) head.style.transform = "rotate(" + look + "deg)";

    /* walk legs */
    const lg = t > 1.7 && t < 3.4 ? Math.sin((t - 1.7) * 10) : 0;
    ["L1", "L2", "L3", "R1", "R2", "R3"].forEach((id, i) => {
      const el = document.getElementById(id); if (!el) return;
      const sgn = i < 3 ? 1 : -1;
      const ph = (i % 3) * 0.8;
      el.setAttribute("transform", "rotate(" + (lg * 12 * sgn * Math.sin(1 + ph)) + " 80 90)");
    });

    const worldW = els.world.clientWidth, worldH = els.world.clientHeight;
    ant.style.left = (antX * worldW) + "px";
    ant.style.top = (worldH * 0.62 + bob) + "px";
    ant.style.transform = "translate(-20%,-50%) scaleX(" + (t > 5.5 && t < 6.4 ? -1 : 1) + ")";

    /* ant drags the word from the left to centre */
    let logoLeft = 28, logoS = 0.55, logoOp = 0;
    if (t < 1.55) { logoOp = 0; logoS = 0.5; logoLeft = 22; }
    else if (t < 3.45) {
      const u = smooth(1.55, 3.45, t);
      logoOp = 1; logoS = lerp(0.7, 1, easeOutBack(u));
      logoLeft = lerp(26, 50, u);
    } else { logoOp = 1; logoS = 1; logoLeft = 50; }
    logo.style.opacity = logoOp;
    logo.style.left = logoLeft + "%";
    logo.style.transform = "translate(-50%,-50%) scale(" + logoS + ")";

    /* rolling O's */
    const c0 = holeCenter("hole0"), c1 = holeCenter("hole1");
    const sz = c0.s;
    if (t < 3.4) {
      oPhys[0].mode = oPhys[1].mode = "slot";
      o0.classList.remove("is-lens"); o1.classList.remove("is-lens");
      placeO(o0, c0, 0, sz); placeO(o1, c1, 0, sz);
      o0.style.opacity = o1.style.opacity = logoOp;
    } else if (t < 6.15) {
      if (oPhys[0].mode === "slot") {
        oPhys[0] = { x: c0.x, y: c0.y, vx: -460, vy: -640, r: 0, vr: -640, mode: "roll" };
        oPhys[1] = { x: c1.x, y: c1.y, vx: 520, vy: -680, r: 0, vr: 720, mode: "roll" };
        cue("roll", 3.4);
      }
      const floor = worldH * 0.9;
      for (const p of oPhys) {
        p.vy += 780 * dt; p.x += p.vx * dt; p.y += p.vy * dt; p.r += p.vr * dt;
        if (p.y > floor - sz / 2) { p.y = floor - sz / 2; p.vy *= -0.48; p.vx *= 0.96; p.vr *= 0.9; }
      }
      o0.style.opacity = o1.style.opacity = t < 5.2 ? 1 : clamp(1 - (t - 5.2) / 0.4, 0, 1);
      placeO(o0, oPhys[0], oPhys[0].r, sz);
      placeO(o1, oPhys[1], oPhys[1].r, sz);
    }

    /* idea bulb */
    if (t >= 5.05 && t < 7.4) {
      const u = smooth(5.05, 5.45, t);
      const ax = antX * worldW, ay = worldH * 0.62 + bob;
      bulb.style.opacity = u * (t < 6.9 ? 1 : clamp(1 - (t - 6.9) / 0.3, 0, 1));
      bulb.style.left = (ax + 36) + "px";
      bulb.style.top = (ay - 118 - (1 - u) * 20) + "px";
      bulb.style.transform = "scale(" + (0.4 + 0.7 * u) + ") rotate(" + ((1 - u) * -20) + "deg)";
      if (t >= 5.12) cue("pop", 5.12, "bulb");
    } else bulb.style.opacity = 0;

    /* glasses lift + lenses become O's */
    if (t >= 5.55 && glasses) {
      const lift = smooth(5.55, 6.15, t);
      glasses.style.transform = "translate(0," + (-lift * 28) + "px) rotate(" + (lift * -18) + "deg)";
      glasses.style.opacity = t < 6.2 ? 1 : clamp(1 - (t - 6.2) / 0.2, 0, 1);
    } else if (glasses) { glasses.style.transform = ""; glasses.style.opacity = 1; }

    if (t >= 6.2) {
      o0.classList.add("is-lens"); o1.classList.add("is-lens");
      o0.style.opacity = 1; o1.style.opacity = 1;
      const antR = ant.getBoundingClientRect(), wr = els.world.getBoundingClientRect();
      const hand0 = { x: antR.left - wr.left + antR.width * 0.35, y: antR.top - wr.top + antR.height * 0.25 };
      const hand1 = { x: antR.left - wr.left + antR.width * 0.55, y: antR.top - wr.top + antR.height * 0.25 };
      const u0 = easeOutBack(smooth(6.2, 7.05, t));
      const u1 = easeOutBack(smooth(6.38, 7.2, t));
      placeO(o0, { x: lerp(hand0.x, c0.x, u0), y: lerp(hand0.y, c0.y, u0) }, (1 - u0) * -80, sz);
      placeO(o1, { x: lerp(hand1.x, c1.x, u1), y: lerp(hand1.y, c1.y, u1) }, (1 - u1) * 80, sz);
      if (t >= 6.22) cue("pop", 6.22, "lens0");
      if (t >= 6.4) cue("pop", 6.4, "lens1");
    }

    /* logo bounce when complete */
    if (t >= 7.15 && t < 7.7) {
      const j = Math.sin((t - 7.15) * 16) * (1 - smooth(7.15, 7.7, t)) * 8;
      logo.style.transform = "translate(-50%,-50%) scale(" + (1.06 + j / 70) + ")";
    }

    /* boom + portal */
    if (t >= 7.45 && !frame._boom) { frame._boom = 1; spawnBurst(48); cue("boom", 7.45); }
    if (t >= 7.85) cue("whoosh", 7.85);
    const flashA = t >= 7.45 && t < 7.75 ? (1 - (t - 7.45) / 0.3) * 0.85 : 0;
    els.flash.style.opacity = flashA;

    if (t >= 7.7) {
      const u = smooth(7.7, 9.55, t);
      const sc = 0.2 + u * 4.2;
      els.portal.style.opacity = clamp(u * 1.8, 0, 1);
      els.portal.style.transform = "translate(-50%,-50%) scale(" + sc + ") rotate(" + (u * 320) + "deg)";
      const stage = host.querySelector(".pti-stage");
      if (stage) stage.style.transform = "scale(" + (1 + u * 0.35) + ")";
      if (!isAds && u > 0.92) host.style.opacity = String(1 - (u - 0.92) / 0.08);
    } else {
      const stage = host.querySelector(".pti-stage");
      if (stage) stage.style.transform = "";
      host.style.opacity = "1";
    }

    /* sfx walk / blink */
    if (t > 0.4 && t < 3.4 && Math.floor(t * 5) !== frame._step) { frame._step = Math.floor(t * 5); cue("tiptoe", t, "s" + frame._step); }
    if (blink > 0.7) cue("blink", t, "b" + t.toFixed(1));

    drawFx(t);

    if (t >= DUR) { if (isAds) return; finish(false); return; }
    raf = requestAnimationFrame(frame);
  }

  function finish(skipped) {
    playing = false;
    if (raf) cancelAnimationFrame(raf);
    try { localStorage.setItem(STORE, "1"); } catch (e) {}
    if (host) { host.classList.add("is-out"); host.style.opacity = "0"; }
    setTimeout(() => { if (host) host.style.display = "none"; }, 480);
    if (typeof onDone === "function") onDone({ skipped: !!skipped });
  }

  function play() {
    if (!host) return;
    lastCue = {}; frame._boom = 0; frame._p = 0; frame._step = -1; particles = [];
    oPhys[0].mode = oPhys[1].mode = "slot";
    host.style.display = "block"; host.classList.remove("is-out");
    host.style.opacity = "1"; host.style.transform = "none";
    const stg = host.querySelector(".pti-stage"); if (stg) stg.style.transform = "";
    playing = true; startT = 0;
    try { ctx(); } catch (e) {}
    raf = requestAnimationFrame(frame);
  }

  function skip() { cue("pop", 0, "skip"); finish(true); }

  function mount(opts) {
    opts = opts || {};
    onDone = opts.onDone || null;
    host = opts.root || document.getElementById("pt-intro") || document.createElement("div");
    if (!host.id) host.id = "pt-intro";
    if (!host.parentNode) document.body.appendChild(host);
    els = build(host);
    muted = false;
    try { if (localStorage.getItem(SNDK) === "0") muted = true; } catch (e) {}
    setMuted(muted);
    els.skip.onclick = () => { try { ctx(); } catch (e) {} skip(); };
    els.snd.onclick = () => { try { ctx(); } catch (e) {} setMuted(!muted); };
    host.addEventListener("pointerdown", () => { try { ctx(); } catch (e) {}; }, { once: true });

    const reduce = opts.ignoreReduce ? false : (opts.forceMotion ? false : !!(global.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches));
    const seen = (() => { try { return localStorage.getItem(STORE) === "1"; } catch (e) { return false; } })();

    isAds = !!opts.ads;
    if (isAds) {
      els.skip.style.display = "none"; els.snd.style.display = "none";
      global.__DURATION = DUR; global.__READY = true;
      play(); return;
    }
    if (reduce) {
      host.style.display = "none";
      try { localStorage.setItem(STORE, "1"); } catch (e) {}
      if (onDone) onDone({ skipped: true, reduced: true });
      return;
    }
    if (opts.auto !== false && (opts.once === false || !seen)) play();
    else host.style.display = "none";
  }

  global.PiToonIntro = {
    mount, play: function () { if (host) play(); else mount({ once: false, auto: true }); },
    skip, duration: DUR
  };
  global.playPiToonIntro = function () { global.PiToonIntro.play(); };
})(typeof window !== "undefined" ? window : this);
