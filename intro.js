/* PiToon landing intro v3 — official 3D art, cut-out walk-cycle rig, spring physics, cartoon jingle + SFX.
   Story: the ant peeks in, sneaks and looks around, drags "PiToon" to the centre, the two O's roll away
   along one straight track, the ant gets an idea, runs into the gap and its glasses become the logo eyes,
   the logo comes alive, thumbs up, then BOOM — a fairy-tale portal into the app. */
(function (global) {
  const DUR = 10.0;
  const STORE = "pt_intro_seen";
  const SNDK = "pt_intro_sound";
  const BASE = (function () { try { const s = document.currentScript && document.currentScript.src; return s ? s.replace(/[^/]*$/, "") : ""; } catch (e) { return ""; } })();
  const A = BASE + "assets/";
  /* measured from the art (see assets/art.json) */
  const ART = {
    ant: { ar: 877 / 800, lmx: (0.48816 + 0.81345) / 2, lmy: (0.33905 + 0.30018) / 2, ldx: 0.81345 - 0.48816, tilt: 7.5,
           lensL: [0.48816, 0.33905, 0.155], lensR: [0.81345, 0.30018, 0.163] },
    logo: { ar: 425 / 1200,
      pit: [0.0, 0.03239, 0.46906, 0.96761], eyes: [0.39870, 0.27183, 0.36976, 0.63521],
      antenna: [0.40719, 0.0, 0.38972, 0.35775], n: [0.71657, 0.18451, 0.28343, 0.76761],
      ringL: [0.49800, 0.55070], ringR: [0.66866, 0.55352], ringR_vis: 0.0888 }
  };
  ART.rig = {"w":800,"h":877,"parts":{"antL":{"file":"assets/rig/antL.webp","x":165,"y":26,"w":213,"h":101,"px":362.40934065934067,"py":96.34615384615384,"ox":197.40934065934067,"oy":70.34615384615384},"antR":{"file":"assets/rig/antR.webp","x":521,"y":0,"w":190,"h":144,"px":535.4479768786127,"py":128.14739884393063,"ox":14.447976878612735,"oy":128.14739884393063},"head":{"file":"assets/rig/head.webp","x":234,"y":100,"w":566,"h":403,"px":500.0,"py":475.0,"ox":266.0,"oy":375.0},"armR":{"file":"assets/rig/armR.webp","x":509,"y":451,"w":240,"h":154,"px":555.0,"py":515.0,"ox":46.0,"oy":64.0},"armL":{"file":"assets/rig/armL.webp","x":281,"y":537,"w":118,"h":182,"px":370.0,"py":560.0,"ox":89.0,"oy":23.0},"armL_lo":{"file":"assets/rig/armL_lo.webp","x":272,"y":700,"w":82,"h":75,"px":300.0,"py":700.0,"ox":28.0,"oy":0.0},"legMR":{"file":"assets/rig/legMR.webp","x":473,"y":542,"w":82,"h":143,"px":535.0,"py":555.0,"ox":62.0,"oy":13.0},"legMR_lo":{"file":"assets/rig/legMR_lo.webp","x":510,"y":654,"w":128,"h":163,"px":520.0,"py":665.0,"ox":10.0,"oy":11.0},"legHR":{"file":"assets/rig/legHR.webp","x":377,"y":572,"w":111,"h":135,"px":445.0,"py":590.0,"ox":68.0,"oy":18.0},"legHR_lo":{"file":"assets/rig/legHR_lo.webp","x":391,"y":681,"w":93,"h":196,"px":412.0,"py":690.0,"ox":21.0,"oy":9.0},"legML":{"file":"assets/rig/legML.webp","x":203,"y":565,"w":118,"h":114,"px":300.0,"py":565.0,"ox":97.0,"oy":0.0},"legML_lo":{"file":"assets/rig/legML_lo.webp","x":185,"y":656,"w":99,"h":171,"px":250.0,"py":655.0,"ox":65.0,"oy":-1.0},"legHL":{"file":"assets/rig/legHL.webp","x":126,"y":467,"w":217,"h":146,"px":310.0,"py":535.0,"ox":184.0,"oy":68.0},"legHL_lo":{"file":"assets/rig/legHL_lo.webp","x":0,"y":536,"w":204,"h":302,"px":155.0,"py":568.0,"ox":155.0,"oy":32.0},"abd":{"file":"assets/rig/abd.webp","x":23,"y":408,"w":334,"h":273,"px":315.0,"py":530.0,"ox":292.0,"oy":122.0},"body":{"file":"assets/rig/body.webp","x":320,"y":465,"w":237,"h":175,"px":450.0,"py":530.0,"ox":130.0,"oy":65.0}},"children":{"legHL":"legHL_lo","legML":"legML_lo","armL":"armL_lo","legHR":"legHR_lo","legMR":"legMR_lo"},"order":["abd","legHL","legML","body","legHR","legMR","armL","armR","head"],"headChildren":["antL","antR"],"pivots":{"antL":[362.40934065934067,96.34615384615384],"antR":[535.4479768786127,128.14739884393063],"head":[500.0,475.0],"abd":[315.0,530.0],"body":[450.0,530.0],"armR":[555.0,515.0],"armR_lo":[610.0,575.0],"armL":[370.0,560.0],"armL_lo":[300.0,700.0],"legHL":[310.0,535.0],"legHL_lo":[155.0,568.0],"legML":[300.0,565.0],"legML_lo":[250.0,655.0],"legHR":[445.0,590.0],"legHR_lo":[412.0,690.0],"legMR":[535.0,555.0],"legMR_lo":[520.0,665.0]}};
  function rng(seed) { let s = seed >>> 0; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }

  /* ---------- Web Audio ---------- */
  let actx, master, muted = false, lastCue = {};
  function ctx() {
    if (!actx) {
      const ua = global.navigator && navigator.userActivation;
      if (ua && !ua.hasBeenActive) return null; /* wait for a tap: no autoplay warnings */
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
    if (usingFile && bgAudio && !bgAudio.paused && !muted) return;
    if (SFX[name]) SFX[name]();
  }
  SFX.ding = function () {
    const c = ctx(); if (!c || muted) return;
    const t = c.currentTime;
    [1318, 1976].forEach((f, i) => {
      const o = c.createOscillator(); o.type = "sine"; o.frequency.value = f;
      const g = envGain(t + i * 0.07, 0.004, 0.5, 0.18); if (!g) return;
      o.connect(g); o.start(t + i * 0.07); o.stop(t + i * 0.07 + 0.55);
    });
  };
  SFX.boing = function () {
    const c = ctx(); if (!c || muted) return;
    const t = c.currentTime, o = c.createOscillator(); o.type = "triangle";
    o.frequency.setValueAtTime(220, t); o.frequency.exponentialRampToValueAtTime(520, t + 0.12);
    o.frequency.exponentialRampToValueAtTime(260, t + 0.32);
    const g = envGain(t, 0.004, 0.36, 0.28); if (!g) return;
    o.connect(g); o.start(t); o.stop(t + 0.4);
  };
  SFX.sparkle = function () {
    const c = ctx(); if (!c || muted) return;
    const t = c.currentTime;
    [1568, 2093, 2637, 3136].forEach((f, i) => {
      const o = c.createOscillator(); o.type = "sine"; o.frequency.value = f;
      const g = envGain(t + i * 0.05, 0.003, 0.25, 0.09); if (!g) return;
      o.connect(g); o.start(t + i * 0.05); o.stop(t + i * 0.05 + 0.3);
    });
  };

  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function smooth(t0, t1, t) { const x = clamp((t - t0) / Math.max(0.0001, t1 - t0), 0, 1); return x * x * (3 - 2 * x); }
  function lin(t0, t1, t) { return clamp((t - t0) / Math.max(0.0001, t1 - t0), 0, 1); }
  /* closed-form under-damped spring 0→1 (overshoot), deterministic for video export */
  function spring(t0, t, k, z) {
    if (t <= t0) return 0;
    const x = t - t0, w = k || 14, d = z || 0.45;
    const wd = w * Math.sqrt(1 - d * d);
    return 1 - Math.exp(-d * w * x) * (Math.cos(wd * x) + (d * w / wd) * Math.sin(wd * x));
  }
  function wob(t0, t, f, decay) { if (t < t0) return 0; const x = t - t0; return Math.sin(x * (f || 18)) * Math.exp(-x * (decay || 4)); }


  /* ---------- rig DOM (cut-out parts of official ant.webp) ---------- */
  function pct(n, d) { return (n / d * 100).toFixed(3) + "%"; }
  function rigHTML() {
    const R = ART.rig, P = R.parts;
    const img = (name) => {
      const p = P[name];
      return `<img src="${A}rig/${name}.webp" alt="" draggable="false" style="left:${pct(p.x,R.w)};top:${pct(p.y,R.h)};width:${pct(p.w,R.w)}">`;
    };
    const origin = (name) => { const p = P[name]; return pct(p.px, R.w) + " " + pct(p.py, R.h); };
    const wrap = (name, inner, cls) => `<div class="pr ${cls || name}" data-part="${name}" style="transform-origin:${origin(name)}">${img(name)}${inner || ""}</div>`;
    const limb = (name) => {
      const lo = R.children && R.children[name];
      return wrap(name, lo && P[lo] ? wrap(lo, "", "lo") : "", "hi " + name);
    };
    let h = '<div class="pti-rig">';
    ["abd", "legHL", "legML", "body", "legHR", "legMR", "armL", "armR"].forEach(n => { h += limb(n); });
    h += `<div class="pr head" data-part="head" style="transform-origin:${origin("head")}">${img("head")}${wrap("antL","","ant-l")}${wrap("antR","","ant-r")}<i class="pti-glint g0"></i><i class="pti-glint g1"></i></div></div>`;
    h += `<img class="pti-ant-full" src="${A}ant.webp" alt="" draggable="false">`;
    return h;
  }

  /* ---------- cartoon walk cycle (cut-out, overlapping action) ---------- */
  function gait(phase, kind, ah) {
    const cfg = {
      tiptoe: { amp: 11, bob: 0.014, sq: 0.04,  headLag: 0.16, antAmp: 10, lift: 0.014, arm: 12, hang: 16 },
      walk:   { amp: 16, bob: 0.024, sq: 0.055, headLag: 0.2,  antAmp: 12, lift: 0.02,  arm: 16, hang: 24 },
      run:    { amp: 22, bob: 0.034, sq: 0.08,  headLag: 0.24, antAmp: 16, lift: 0.032, arm: 24, hang: 30 },
      idle:   { amp: 3,  bob: 0.01,  sq: 0.02,  headLag: 0.12, antAmp: 7,  lift: 0.004, arm: 4,  hang: 6  },
      still:  { amp: 0,  bob: 0,     sq: 0,     headLag: 0,    antAmp: 0,  lift: 0,     arm: 0,  hang: 0  }
    }[kind] || { amp: 0, bob: 0, sq: 0, headLag: 0, antAmp: 0, lift: 0, arm: 0, hang: 0 };
    const p = phase * Math.PI * 2;
    const bobUp = (1 - Math.abs(Math.cos(p))) * cfg.bob * ah;
    const contact = Math.abs(Math.cos(p));
    const sy = 1 - contact * cfg.sq + (1 - contact) * cfg.sq * 0.35;
    const sx = 1 + (1 - sy) * 0.85;
    /* right-facing: negative rotate swings a hanging leg forward */
    const midR = -Math.cos(p) * cfg.amp, midL = Math.cos(p) * cfg.amp;
    /* hind left is a long limb — smaller hip swing so it does not can-can */
    const hindR = Math.cos(p) * cfg.amp * 0.65, hindL = -Math.cos(p) * cfg.amp * 0.45;
    function knee(off) {
      const ph = ((phase + off) % 1 + 1) % 1;
      if (ph < 0.5) return 6 + 4 * Math.sin(ph * Math.PI * 2);
      return 8 + 14 * Math.sin((ph - 0.5) * Math.PI);
    }
    function lift(off) {
      const ph = ((phase + off) % 1 + 1) % 1;
      if (ph < 0.5) return 0;
      return Math.sin((ph - 0.5) * Math.PI) * cfg.lift * ah;
    }
    const pHead = p - cfg.headLag * 2 * Math.PI;
    const pAnt = p - cfg.headLag * 3.4 * Math.PI;
    return {
      bobUp, sx, sy,
      midR, midL, hindR, hindL,
      kneeMR: knee(0), kneeML: knee(0.5), kneeHR: knee(0.5), kneeHL: knee(0),
      liftMR: lift(0), liftML: lift(0.5), liftHR: lift(0.5), liftHL: lift(0), liftAL: lift(0),
      armR: cfg.hang - Math.cos(p) * cfg.arm, armL: -cfg.hang + Math.cos(p) * cfg.arm,
      armL_el: 10 + Math.abs(Math.sin(p + Math.PI)) * 14,
      headRot: Math.sin(pHead) * (cfg.amp * 0.16), headY: Math.sin(pHead) * cfg.bob * 0.45 * ah,
      antL: Math.sin(pAnt) * cfg.antAmp + Math.sin(p * 2.15) * cfg.antAmp * 0.28,
      antR: Math.sin(pAnt + 0.45) * cfg.antAmp * 0.85 + Math.sin(p * 2.15 + 1.1) * cfg.antAmp * 0.28,
      abdRot: -Math.sin(p - 0.55) * cfg.amp * 0.08,
      bodyRot: Math.sin(p) * 2.6,
      hang: cfg.hang
    };
  }
  function setPartRot(name, rot, tx, ty) {
    const el = els.parts && els.parts[name];
    if (!el) return;
    el.style.transform = "translate(" + (tx || 0).toFixed(2) + "px," + (ty || 0).toFixed(2) + "px) rotate(" + (rot || 0).toFixed(2) + "deg)";
  }
  function applyGait(g) {
    if (!g) {
      if (els.parts) Object.keys(els.parts).forEach(n => setPartRot(n, 0, 0, 0));
      return;
    }
    setPartRot("body", g.bodyRot, 0, 0);
    setPartRot("abd", g.abdRot, 0, 0);
    setPartRot("head", g.headRot, 0, g.headY);
    setPartRot("antL", g.antL, 0, 0);
    setPartRot("antR", g.antR, 0, 0);
    setPartRot("legMR", g.midR, 0, -g.liftMR);
    setPartRot("legMR_lo", g.kneeMR, 0, 0);
    setPartRot("legML", g.midL, 0, -g.liftML);
    setPartRot("legML_lo", g.kneeML, 0, 0);
    setPartRot("legHR", g.hindR, 0, -g.liftHR);
    setPartRot("legHR_lo", g.kneeHR, 0, 0);
    setPartRot("legHL", g.hindL, 0, -g.liftHL);
    setPartRot("legHL_lo", g.kneeHL, 0, 0);
    setPartRot("armR", g.armR, 0, 0);
    setPartRot("armL", g.armL, 0, -g.liftAL);
    setPartRot("armL_lo", g.armL_el, 0, 0);
  }

  /* ---------- intro jingle (pre-rendered, synced) ---------- */
  let bgAudio = null, usingFile = false, audioBlocked = false;
  function loadBgAudio() {
    if (bgAudio) return bgAudio;
    bgAudio = new Audio(A + "intro_audio.mp3");
    bgAudio.preload = "auto";
    bgAudio.loop = false;
    return bgAudio;
  }
  function nowT() {
    if (!playing || startT < 0) return 0;
    return Math.max(0, ((typeof performance !== "undefined" ? performance.now() : Date.now()) - startT) / 1000);
  }
  function showUnmute(on) {
    if (!els || !els.unmute) return;
    if (isAds || muted) on = false;
    els.unmute.classList.toggle("on", !!on);
  }
  function tryPlayAudio(offset) {
    if (muted) { showUnmute(false); usingFile = false; return Promise.resolve(false); }
    const a = loadBgAudio();
    const start = () => {
      try { a.currentTime = Math.max(0, Math.min(DUR - 0.05, offset || 0)); } catch (e) {}
      const p = a.play();
      if (p && p.then) {
        return p.then(() => { audioBlocked = false; usingFile = true; showUnmute(false); return true; })
          .catch(() => { audioBlocked = true; usingFile = false; showUnmute(true); return false; });
      }
      audioBlocked = false; usingFile = true; showUnmute(false); return Promise.resolve(true);
    };
    if (a.readyState >= 2) return start();
    return new Promise((res) => {
      let done = false;
      const go = () => { if (done) return; done = true; Promise.resolve(start()).then(res); };
      a.addEventListener("canplay", go, { once: true });
      a.addEventListener("error", () => { if (!done) { done = true; res(false); } }, { once: true });
      setTimeout(go, 700);
    });
  }
  function stopAudio() {
    if (bgAudio) { try { bgAudio.pause(); bgAudio.currentTime = 0; } catch (e) {} }
    usingFile = false;
  }
  function syncAudio(t) {
    if (!usingFile || !bgAudio || muted || bgAudio.paused) return;
    if (Math.abs(bgAudio.currentTime - t) > 0.18) {
      try { bgAudio.currentTime = Math.max(0, t); } catch (e) {}
    }
  }

  function build(root) {
    root.innerHTML = "";
    root.className = "pti";
    root.setAttribute("role", "dialog");
    root.setAttribute("aria-label", "Hoạt ảnh mở đầu PiToon");
    root.innerHTML =
      `<div class="pti-bg" aria-hidden="true"><i class="pti-sun"></i><i class="pti-cloud c1"></i><i class="pti-cloud c2"></i><i class="pti-hill h1"></i><i class="pti-hill h2"></i></div>
       <div class="pti-track" aria-hidden="true"></div>
       <svg class="pti-rope" aria-hidden="true"><path d=""/></svg>
       <div class="pti-ant" aria-hidden="true">${rigHTML()}</div>
       <div class="pti-logo" aria-hidden="true">
         <img class="pc pit" src="${A}logo_pit.webp" alt="" draggable="false">
         <img class="pc n" src="${A}logo_n.webp" alt="" draggable="false">
         <img class="pc eyes" src="${A}logo_eyes.webp" alt="" draggable="false">
         <img class="pc antenna" src="${A}logo_antenna.webp" alt="" draggable="false">
       </div>
       <div class="pti-o o0" aria-hidden="true"></div><div class="pti-o o1" aria-hidden="true"></div>
       <div class="pti-bulb" aria-hidden="true">💡</div>
       <div class="pti-thumb" aria-hidden="true"><img src="${A}ant.webp" alt="" draggable="false"><b>Vào xưởng phim thôi!</b></div>
       <canvas class="pti-fx" aria-hidden="true"></canvas>
       <div class="pti-flash" aria-hidden="true"></div>
       <button class="pti-unmute" type="button">🔊 Bật âm thanh</button>
       <button class="pti-skip" type="button">Bỏ qua</button>
       <button class="pti-snd" type="button" aria-label="Bật/tắt âm thanh"></button>`;
    const q = s => root.querySelector(s);
    const parts = {};
    root.querySelectorAll(".pti-rig [data-part]").forEach(el => { parts[el.dataset.part] = el; });
    return {
      root, track: q(".pti-track"), rope: q(".pti-rope"), ropeP: q(".pti-rope path"), logo: q(".pti-logo"),
      pit: q(".pc.pit"), n: q(".pc.n"), eyes: q(".pc.eyes"), antenna: q(".pc.antenna"),
      o0: q(".o0"), o1: q(".o1"), ant: q(".pti-ant"), g0: q(".g0"), g1: q(".g1"), bulb: q(".pti-bulb"),
      thumb: q(".pti-thumb"), fx: q(".pti-fx"), flash: q(".pti-flash"), skip: q(".pti-skip"), snd: q(".pti-snd"),
      unmute: q(".pti-unmute"), antFull: q(".pti-ant-full"), parts
    };
  }

  let playing = false, startT = 0, raf = 0, els = null, host = null, onDone = null, isAds = false;

  function setMuted(m) {
    muted = m; try { localStorage.setItem(SNDK, m ? "0" : "1"); } catch (e) {}
    if (master) master.gain.value = m ? 0 : 0.7;
    if (bgAudio) {
      if (m) { try { bgAudio.pause(); } catch (e) {} usingFile = false; showUnmute(false); }
      else if (playing) tryPlayAudio(nowT());
    }
    if (els && els.snd) els.snd.textContent = m ? "🔇" : "🔊";
    if (m) showUnmute(false);
  }

  function place(el, x, y, w, h, tf, origin) {
    el.style.width = w + "px"; el.style.height = h + "px";
    el.style.transform = "translate(" + x.toFixed(2) + "px," + y.toFixed(2) + "px)" + (tf || "");
    if (origin) el.style.transformOrigin = origin;
  }

  /* geometry for the current viewport */
  function layout() {
    const W = host.clientWidth || innerWidth, H = host.clientHeight || innerHeight;
    const portrait = H > W * 1.15;
    const logoW = Math.min(W * (portrait ? 0.9 : 0.66), H * 1.25, 860);
    const logoH = logoW * ART.logo.ar;
    const lx = (W - logoW) / 2, ly = H * (portrait ? 0.36 : 0.3) - logoH / 2;
    const antH0 = Math.min(H * (portrait ? 0.34 : 0.44), W * (portrait ? 0.62 : 0.34));
    const antW0 = antH0 / ART.ant.ar;
    const ground = H * (portrait ? 0.84 : 0.93);
    const antW1 = logoW * (ART.logo.ringR[0] - ART.logo.ringL[0]) / ART.ant.ldx;
    const mid = { x: lx + logoW * (ART.logo.ringL[0] + ART.logo.ringR[0]) / 2, y: ly + logoH * (ART.logo.ringL[1] + ART.logo.ringR[1]) / 2 };
    const trackY = ly + logoH * 1.04;
    return { W, H, portrait, logoW, logoH, lx, ly, antW0, antH0, ground, antW1, mid, trackY };
  }

  /* ant transform by its lens-midpoint P */
  function setAnt(L, P, aw, rot, flip, sx, sy, op) {
    const ah = aw * ART.ant.ar;
    const ox = ART.ant.lmx * aw, oy = ART.ant.lmy * ah;
    const e = els.ant;
    e.style.width = aw + "px"; e.style.height = ah + "px";
    e.style.transformOrigin = ox + "px " + oy + "px";
    e.style.transform = "translate(" + (P.x - ox).toFixed(2) + "px," + (P.y - oy).toFixed(2) + "px) rotate(" + rot.toFixed(2) + "deg) scale(" + (flip * sx).toFixed(3) + "," + sy.toFixed(3) + ")";
    e.style.opacity = op;
  }
  function groundP(L, x, aw, lift) { const ah = aw * ART.ant.ar; return { x: x, y: L.ground - (1 - ART.ant.lmy) * ah - (lift || 0) }; }

  /* ---------- canvas fx: sparkles + fairy portal ---------- */
  let sparks = [], streaks = [];
  function spawnSparks(x, y, n, seed, spread) {
    const r = rng(seed);
    for (let i = 0; i < n; i++) {
      const a = r() * Math.PI * 2, sp = (spread || 260) * (0.3 + r());
      sparks.push({ x, y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp - 60, t0: null, life: 0.6 + r() * 0.6,
        col: ["#fff6a8", "#ffd21f", "#ff9ad5", "#b8e8ff", "#ffffff", "#c9b8ff"][i % 6], s: 3 + r() * 6 });
    }
  }
  function star(g, x, y, s, rot) {
    g.save(); g.translate(x, y); g.rotate(rot || 0); g.beginPath();
    for (let i = 0; i < 8; i++) { const rr = i % 2 ? s * 0.38 : s; const a = i * Math.PI / 4; g.lineTo(Math.cos(a) * rr, Math.sin(a) * rr); }
    g.closePath(); g.fill(); g.restore();
  }
  function fairyWorld(g, cx, cy, R, t, W, H) {
    g.save();
    g.beginPath(); g.arc(cx, cy, R, 0, Math.PI * 2); g.clip();
    const S = Math.max(W, H);
    const gr = g.createLinearGradient(0, cy - S * 0.6, 0, cy + S * 0.6);
    gr.addColorStop(0, "#ffc9e8"); gr.addColorStop(0.45, "#d8c6ff"); gr.addColorStop(1, "#b6f0de");
    g.fillStyle = gr; g.fillRect(cx - R, cy - R, R * 2, R * 2);
    /* rainbow */
    const rc = ["#ff9aa8", "#ffc98a", "#fff09a", "#aef0b0", "#9fd8ff", "#c8a8ff"];
    g.lineWidth = S * 0.022;
    rc.forEach((c, i) => { g.strokeStyle = c; g.globalAlpha = 0.55; g.beginPath(); g.arc(cx, cy + S * 0.32, S * (0.42 - i * 0.022), Math.PI, 0); g.stroke(); });
    g.globalAlpha = 1;
    /* pastel castle */
    const bx = cx, by = cy + S * 0.3, u = S * 0.05;
    g.fillStyle = "#f7e9ff";
    g.fillRect(bx - u * 2.2, by - u * 3, u * 4.4, u * 3);
    g.fillRect(bx - u * 3.4, by - u * 4.2, u * 1.2, u * 4.2); g.fillRect(bx + u * 2.2, by - u * 4.2, u * 1.2, u * 4.2);
    g.fillRect(bx - u * 0.7, by - u * 5.2, u * 1.4, u * 2.4);
    g.fillStyle = "#ff9ad5";
    [[bx - u * 2.8, by - u * 4.2, u * 0.9], [bx + u * 2.8, by - u * 4.2, u * 0.9], [bx, by - u * 5.2, u * 1.0]].forEach(([x, y, w]) => {
      g.beginPath(); g.moveTo(x - w, y); g.lineTo(x, y - w * 2); g.lineTo(x + w, y); g.closePath(); g.fill();
    });
    g.fillStyle = "#c9a6ff"; g.beginPath(); g.arc(bx, by - u * 0.9, u * 0.8, Math.PI, 0); g.fill(); g.fillRect(bx - u * 0.8, by - u * 0.9, u * 1.6, u * 0.9);
    /* hills */
    g.fillStyle = "#9fe3b8"; g.beginPath(); g.ellipse(cx - S * 0.25, cy + S * 0.42, S * 0.5, S * 0.14, 0, 0, Math.PI * 2); g.fill();
    g.fillStyle = "#86d6a6"; g.beginPath(); g.ellipse(cx + S * 0.3, cy + S * 0.45, S * 0.5, S * 0.14, 0, 0, Math.PI * 2); g.fill();
    /* clouds */
    g.fillStyle = "#ffffffdd";
    [[-0.28, -0.22, 1], [0.26, -0.3, 0.8], [0.05, -0.12, 0.6]].forEach(([dx, dy, k], i) => {
      const x = cx + S * dx + Math.sin(t * 0.8 + i) * S * 0.02, y = cy + S * dy, s = S * 0.04 * k;
      g.beginPath(); g.arc(x, y, s, 0, 7); g.arc(x + s * 1.1, y - s * 0.4, s * 1.2, 0, 7); g.arc(x + s * 2.3, y, s, 0, 7); g.fill();
    });
    /* twinkles */
    const r = rng(77);
    for (let i = 0; i < 40; i++) {
      const x = cx + (r() - 0.5) * S, y = cy + (r() - 0.5) * S * 0.8, ph = r() * 6;
      g.globalAlpha = 0.4 + 0.6 * Math.abs(Math.sin(t * 4 + ph)); g.fillStyle = "#fff";
      star(g, x, y, 3 + r() * 6, t + ph);
    }
    g.restore(); g.globalAlpha = 1;
  }
  function drawFx(L, t) {
    const c = els.fx, g = c.getContext("2d");
    const dpr = Math.min(2, global.devicePixelRatio || 1);
    const W = L.W, H = L.H;
    if (c.width !== Math.round(W * dpr) || c.height !== Math.round(H * dpr)) { c.width = Math.round(W * dpr); c.height = Math.round(H * dpr); }
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, W, H);
    /* sparkles (time-based, deterministic) */
    for (const p of sparks) {
      const a = t - p.t0; if (a < 0 || a > p.life) continue;
      const x = p.x + p.vx * a, y = p.y + p.vy * a + 220 * a * a;
      g.globalAlpha = clamp(1 - a / p.life, 0, 1); g.fillStyle = p.col;
      star(g, x, y, p.s * (1 - a / p.life * 0.5), a * 6);
    }
    g.globalAlpha = 1;
    /* fairy portal */
    if (t >= 8.25) {
      const cx = L.W / 2, cy = L.H * 0.5, S = Math.hypot(L.W, L.H) / 2;
      const u = smooth(8.25, 9.35, t);
      const R = lerp(S * 0.1, S * 1.1, Math.sqrt(u));
      /* dim + glow rim */
      g.fillStyle = "rgba(60,30,110," + (0.12 * (1 - u)).toFixed(3) + ")"; g.fillRect(0, 0, W, H);
      /* swirling light tunnel (outside rim) */
      for (let k = 0; k < 6; k++) {
        const rr = R * (1.05 + k * 0.09);
        g.lineWidth = Math.max(3, R * 0.05 * (1 - k * 0.12));
        g.strokeStyle = ["#ff9ad5", "#c9b8ff", "#9fd8ff", "#fff09a", "#aef0b0", "#ffffff"][k];
        g.globalAlpha = 0.75 - k * 0.1;
        const a0 = t * (3.2 + k * 0.6) * (k % 2 ? -1 : 1) + k;
        for (let s = 0; s < 3; s++) { g.beginPath(); g.arc(cx, cy, rr, a0 + s * 2.094, a0 + s * 2.094 + 1.3); g.stroke(); }
      }
      g.globalAlpha = 1;
      /* inner tunnel rings rushing inward before world appears */
      fairyWorld(g, cx, cy, R, t, W, H);
      const tun = 1 - smooth(8.3, 8.9, t);
      if (tun > 0) {
        g.save(); g.beginPath(); g.arc(cx, cy, R, 0, 7); g.clip();
        for (let i = 0; i < 7; i++) {
          const f = ((t * 1.6 + i / 7) % 1);
          g.strokeStyle = ["#ffffff", "#ffd1ec", "#c9b8ff", "#9fd8ff"][i % 4]; g.globalAlpha = tun * (1 - f);
          g.lineWidth = 2 + 10 * (1 - f); g.beginPath(); g.arc(cx, cy, R * (1 - f), 0, 7); g.stroke();
        }
        g.restore(); g.globalAlpha = 1;
      }
      /* warp streaks */
      const r = rng(1234);
      for (let i = 0; i < 70; i++) {
        const a = r() * Math.PI * 2, sp = 0.6 + r() * 1.4, ph = r();
        const f = ((t - 8.25) * sp + ph) % 1;
        const d0 = R * 0.2 + f * S * 1.2, d1 = d0 + 18 + f * 90;
        g.strokeStyle = ["#ffffff", "#fff09a", "#ff9ad5", "#9fd8ff"][i % 4];
        g.globalAlpha = clamp(f * 2, 0, 1) * 0.85; g.lineWidth = 1.5 + f * 3;
        g.beginPath(); g.moveTo(cx + Math.cos(a) * d0, cy + Math.sin(a) * d0); g.lineTo(cx + Math.cos(a) * d1, cy + Math.sin(a) * d1); g.stroke();
      }
      g.globalAlpha = 1;
    }
  }

  function frame(now) {
    if (!playing) return;
    if (startT < 0) startT = now;
    const t = (now - startT) / 1000;
    render(t);
    if (t >= DUR) { if (isAds) return; finish(false); return; }
    raf = requestAnimationFrame(frame);
  }

  function render(t) {
    const L = layout();
    els.root.style.setProperty("--pti-vh", L.H + "px");
    const lg = ART.logo;

    /* ---------- logo pieces ---------- */
    /* pull: letters trail in from the left behind the ant (2.5–4.0) */
    const startOff = -(L.lx + L.logoW + L.W * 0.15);
    const pulls = { n: spring(2.55, t, 9, 0.55), o: spring(2.62, t, 9, 0.55), pit: spring(2.7, t, 9, 0.55) };
    const offN = startOff * (1 - pulls.n), offO = startOff * (1 - pulls.o), offP = startOff * (1 - pulls.pit);
    const tiltOf = (t0) => t < t0 ? -12 : -12 * Math.exp(-(t - t0) * 3) * Math.cos((t - t0) * 9);
    const wave = (i) => t > 6.95 && t < 8.2 ? -Math.max(0, Math.sin((t - 6.95 - i * 0.09) * 9)) * L.logoH * 0.08 * Math.exp(-(t - 6.95) * 1.6) : 0;
    const pos = (box, off, extraY, tf) => {
      place(els[box], L.lx + off + lg[box][0] * L.logoW, L.ly + lg[box][1] * L.logoH + (extraY || 0), lg[box][2] * L.logoW, lg[box][3] * L.logoH, tf || "");
    };
    const vis = t >= 2.5 ? 1 : 0;
    els.pit.style.opacity = els.n.style.opacity = vis;
    pos("pit", offP, wave(0), " rotate(" + tiltOf(3.2).toFixed(2) + "deg)");
    pos("n", offN, wave(3), " rotate(" + tiltOf(3.0).toFixed(2) + "deg)");
    els.pit.style.transformOrigin = "50% 100%"; els.n.style.transformOrigin = "50% 100%";

    /* official eyes + antenna: appear when the ant's glasses settle in the gap (6.55) */
    const becomeT = 6.55;
    const eu = t < becomeT ? 0 : spring(becomeT, t, 16, 0.4);
    const eOp = clamp((t - becomeT) / 0.22, 0, 1);
    const blinkE = (t > 7.5 && t < 7.62) ? 1 - Math.sin((t - 7.5) / 0.12 * Math.PI) * 0.85 : 1;
    const wig = t > 6.9 && t < 8.3 ? Math.sin((t - 6.9) * 14) * L.logoW * 0.006 * Math.exp(-(t - 6.9) * 1.2) : 0;
    const eScale = lerp(1.25, 1, eu);
    pos("eyes", wig, wave(1.5), " scale(" + eScale.toFixed(3) + "," + (eScale * blinkE).toFixed(3) + ")");
    els.eyes.style.transformOrigin = "50% 45%"; els.eyes.style.opacity = eOp;
    const boing = wob(6.7, t, 17, 2.6) * 14 + wob(7.9, t, 17, 3) * 8;
    pos("antenna", wig * 0.5, wave(1.5) + (1 - eu) * L.logoH * 0.25, " rotate(" + boing.toFixed(2) + "deg) scaleY(" + (1 + wob(6.7, t, 20, 3) * 0.12).toFixed(3) + ")");
    els.antenna.style.transformOrigin = "50% 100%"; els.antenna.style.opacity = eOp;
    if (t >= 6.7) cue("boing", 6.7, "boing1");
    if (t >= 7.9) cue("boing", 7.9, "boing2");

    /* ---------- the two plain O's ---------- */
    const rv = lg.ringR_vis * L.logoW, d = rv * 2;
    const oc = [{ x: L.lx + lg.ringL[0] * L.logoW, y: L.ly + lg.ringL[1] * L.logoH }, { x: L.lx + lg.ringR[0] * L.logoW, y: L.ly + lg.ringR[1] * L.logoH }];
    const trackY = L.trackY + rv * 1.15;            /* O's centre height when sitting on the track */
    const tOn = smooth(3.9, 4.25, t);               /* track line draws in */
    els.track.style.top = (trackY + rv) + "px";
    els.track.style.opacity = t < 6.3 ? tOn : 1 - smooth(6.3, 6.7, t);
    els.track.style.transform = "scaleX(" + tOn.toFixed(3) + ")";
    [0, 1].forEach(i => {
      const el = els["o" + i];
      let x = oc[i].x + offO, y = oc[i].y, rot = 0, sq = 1;
      if (t >= 4.25) {
        /* hop down onto the track */
        const hd = 4.25 + i * 0.08;
        const fall = smooth(hd, hd + 0.28, t);
        y = lerp(oc[i].y, trackY, fall * fall) - Math.sin(fall * Math.PI) * rv * 0.5;
        if (t > hd + 0.28) sq = 1 - wob(hd + 0.28, t, 26, 9) * 0.18;
        /* roll left along the straight line and exit */
        const rs = 4.6 + i * 0.06;
        if (t > rs) {
          const a = t - rs, dist = 0.5 * 1500 * a * a + 120 * a;
          x -= dist; rot = -(dist / rv) * 57.3;
        }
      }
      el.style.opacity = vis && x > -d * 2 ? 1 : 0;
      place(el, x - rv, y - rv, d, d, " rotate(" + rot.toFixed(1) + "deg) scale(" + (2 - sq).toFixed(3) + "," + sq.toFixed(3) + ")", "50% 50%");
    });
    if (t >= 4.27) cue("pop", 4.27, "hop");
    if (t >= 4.6) cue("roll", 4.6, "roll");

    /* ---------- the ant (rigged walk cycle) ---------- */
    let P, aw = L.antW0, rot = 0, flip = 1, sx = 1, sy = 1, op = 1;
    let G = null, fullOp = 0;
    const peekX = L.antW0 * (ART.ant.lmx - 0.56);  /* only the head shows at the left edge */
    if (t < 2.3) {
      /* sneaky tiptoe peek, look left/right */
      const inU = spring(0.1, t, 10, 0.5) - smooth(2.0, 2.3, t) * 1.0;
      const x = lerp(-L.antW0 * 0.5, peekX + L.antW0 * 0.06, inU);
      const ph = t * 1.7; /* ~3.4 tiptoe steps / s, two steps per cycle */
      G = gait(ph, "tiptoe", L.antH0);
      P = groundP(L, x, aw, G.bobUp);
      rot = t > 0.6 ? Math.sin((t - 0.6) * 4.2) * 9 : 0;
      flip = (t > 1.3 && t < 1.68) ? -1 : 1;
      if (t > 1.28 && t < 1.32) cue("blink", 1.28, "lk1");
      const bl = (t > 1.05 && t < 1.17) || (t > 1.9 && t < 2.02);
      const eye = bl ? 0.92 : 1 - Math.abs(wob(0.25, t, 16, 5)) * 0.06;
      sy = G.sy * eye; sx = G.sx * (bl ? 2 - eye : 1);
      if (bl) cue("blink", t < 1.5 ? 1.05 : 1.9, t < 1.5 ? "b1" : "b2");
      if (t > 0.35 && Math.floor(t * 5) !== render._s) { render._s = Math.floor(t * 5); cue("tiptoe", t, "s" + render._s); }
    } else if (t < 4.1) {
      /* walks back in, dragging the word to the centre */
      const u = spring(2.45, t, 8, 0.6);
      const endX = L.portrait ? L.W * 0.66 : L.lx + L.logoW + L.antW0 * 0.15;
      const x = lerp(-L.antW0 * 0.6, endX, u);
      const fade = 1 - smooth(3.6, 4.0, t);
      const ph = (t - 2.45) * 1.35;
      G = gait(ph, "walk", L.antH0);
      /* ease the cycle out as it arrives */
      if (fade < 1) {
        const k = fade;
        ["midR","midL","hindR","hindL","armR","armL","headRot","abdRot","bodyRot","antL","antR",
         "kneeMR","kneeML","kneeHR","kneeHL","armL_el","bobUp","liftMR","liftML","liftHR","liftHL","liftAL","headY"].forEach(key => {
          if (key[0] === "k") G[key] = G[key] * k;
          else if (key.indexOf("lift") === 0 || key === "bobUp" || key === "headY") G[key] *= k;
          else if (key === "armR") G[key] = G.hang * k + (G[key] - G.hang) * k;
          else G[key] = G[key] * k;
        });
        G.sy = lerp(1, G.sy, k); G.sx = lerp(1, G.sx, k);
      }
      P = groundP(L, x, aw, G.bobUp);
      rot = 3 * fade + G.bodyRot * 0.4;
      sx *= G.sx; sy *= G.sy;
      if (t > 2.45 && Math.floor(t * 6) !== render._s) { render._s = Math.floor(t * 6); cue("tiptoe", t, "w" + render._s); }
    } else if (t < 5.75) {
      /* watches the O's roll away, then gets the idea, anticipates the run */
      const endX = L.portrait ? L.W * 0.66 : L.lx + L.logoW + L.antW0 * 0.15;
      const jump = t > 4.6 && t < 4.95 ? Math.sin((t - 4.6) / 0.35 * Math.PI) * L.antH0 * 0.12 : 0;
      G = gait(t * 0.7, "idle", L.antH0);
      if (jump > 0) { G.midR = G.hindR = -12; G.midL = G.hindL = 10; G.kneeMR = G.kneeML = 28; }
      /* anticipation: squash + lean back before the scurry */
      const antc = t > 5.42 ? smooth(5.42, 5.75, t) : 0;
      if (antc > 0) {
        G.sy = G.sy * (1 - antc * 0.16); G.sx = G.sx * (1 + antc * 0.14);
        rot = lerp(t > 5.2 ? wob(5.2, t, 12, 3) * 8 : -6, 14, antc);
      } else {
        rot = t > 5.2 ? wob(5.2, t, 12, 3) * 8 : -6;
      }
      P = groundP(L, endX, aw, jump + G.bobUp * (1 - antc) - antc * L.antH0 * 0.04);
      flip = t > 4.7 && t < 5.15 ? -1 : 1;
      if (t <= 5.42) { sy = (1 - wob(5.2, t, 18, 6) * 0.1) * G.sy; sx = (2 - (1 - wob(5.2, t, 18, 6) * 0.1)) * G.sx * 0.5 + G.sx * 0.5; }
      else { sx = G.sx; sy = G.sy; }
    } else {
      /* scurry into the gap: lens midpoint → ring midpoint, glasses become the logo eyes */
      const endX = L.portrait ? L.W * 0.66 : L.lx + L.logoW + L.antW0 * 0.15;
      const P0 = groundP(L, endX, L.antW0, 0);
      const u = smooth(5.75, 6.5, t);
      const arc = Math.sin(u * Math.PI) * L.logoH * 0.6;
      P = { x: lerp(P0.x, L.mid.x, u), y: lerp(P0.y, L.mid.y, u) - arc };
      aw = lerp(L.antW0, L.antW1, smooth(5.85, 6.5, t));
      const runFade = 1 - smooth(6.25, 6.5, t);
      G = gait((t - 5.75) * 2.6, "run", lerp(L.antH0, aw * ART.ant.ar, u));
      rot = lerp(-10, ART.ant.tilt, smooth(5.8, 6.5, t)) + Math.sin(t * 30) * 4 * (1 - u) * 0.5 + (u < 0.7 ? -8 : 0);
      const land = wob(6.5, t, 22, 7);
      sy = (1 - land * 0.12) * lerp(G.sy, 1, 1 - runFade);
      sx = (1 + land * 0.12) * lerp(G.sx, 1, 1 - runFade);
      op = 1 - smooth(6.6, 6.95, t);
      /* crossfade to the official full art so the glasses snap cleanly */
      fullOp = smooth(6.28, 6.52, t) * (1 - smooth(6.6, 6.95, t));
      if (t >= 5.78) cue("whoosh", 5.78, "run");
      if (t >= 6.5) { cue("pop", 6.5, "land"); }
      if (t >= 6.55 && !render._spk) {
        render._spk = 1;
        const lr = [ART.logo.ringL, ART.logo.ringR];
        lr.forEach((c, i) => spawnSparks(L.lx + c[0] * L.logoW, L.ly + c[1] * L.logoH, 16, 9 + i, L.logoW * 0.5));
        sparks.forEach(s => { if (s.t0 === null) s.t0 = 6.55; });
        cue("sparkle", 6.55, "spk");
      }
    }
    setAnt(L, P, aw, rot, flip, sx, sy, op);
    applyGait(G);
    if (els.antFull) els.antFull.style.opacity = fullOp;
    if (els.root && els.root.querySelector) {
      const rigEl = els.ant && els.ant.querySelector(".pti-rig");
      if (rigEl) rigEl.style.opacity = String(1 - fullOp);
    }
    syncAudio(t);
    /* glasses glint sweeps */
    const glint = (t0) => clamp((t - t0) / 0.35, 0, 1);
    const gl = t < 1.6 ? glint(0.9) : t < 3 ? glint(1.95) : glint(5.3);
    [els.g0, els.g1].forEach(gg => { gg.style.setProperty("--g", (gl * 220 - 60).toFixed(1) + "%"); gg.style.opacity = gl > 0 && gl < 1 ? 1 : 0; });

    /* rope from the ant to the word while dragging */
    if (t > 2.5 && t < 4.05) {
      const ah = aw * ART.ant.ar, ax = P.x - ART.ant.lmx * aw + aw * 0.12, ay = P.y - ART.ant.lmy * ah + ah * 0.52;
      const nx = L.lx + offN + lg.n[0] * L.logoW + lg.n[2] * L.logoW * 0.45, ny = L.ly + (lg.n[1] + lg.n[3] * 0.95) * L.logoH;
      const sag = 30 + 30 * Math.sin(t * 6);
      els.ropeP.setAttribute("d", "M" + ax.toFixed(1) + " " + ay.toFixed(1) + " Q" + ((ax + nx) / 2).toFixed(1) + " " + (Math.max(ay, ny) + sag).toFixed(1) + " " + nx.toFixed(1) + " " + ny.toFixed(1));
      els.rope.style.opacity = 1 - smooth(3.85, 4.05, t);
    } else els.rope.style.opacity = 0;

    /* lightbulb idea */
    const bu = t > 5.2 && t < 6.0 ? spring(5.2, t, 18, 0.35) : 0;
    if (bu > 0) {
      const ah = L.antW0 * ART.ant.ar, bx = P.x - L.antW0 * 0.05, by = P.y - ART.ant.lmy * ah - L.antH0 * 0.18;
      const bs = Math.max(34, L.antH0 * 0.22);
      els.bulb.style.fontSize = bs + "px";
      els.bulb.style.transform = "translate(" + (bx - bs / 2) + "px," + (by - bs) + "px) scale(" + bu.toFixed(3) + ")";
      els.bulb.style.opacity = 1 - smooth(5.8, 6.0, t);
      cue("ding", 5.2, "ding");
    } else els.bulb.style.opacity = 0;

    /* thumbs up */
    const tu = spring(7.45, t, 13, 0.45);
    if (t > 7.45 && t < 8.6) {
      const th = Math.min(L.H * (L.portrait ? 0.3 : 0.36), L.W * (L.portrait ? 0.55 : 0.28));
      const tw = th / ART.ant.ar;
      const tx = L.portrait ? (L.W - tw) / 2 : L.W * 0.5 - tw / 2;
      const ty = L.portrait ? L.H * 0.5 : L.ly + L.logoH * 1.02;
      els.thumb.style.width = tw + "px";
      els.thumb.style.transform = "translate(" + tx + "px," + (ty + (1 - tu) * th * 0.6) + "px) scale(" + (0.4 + 0.6 * tu).toFixed(3) + ") rotate(" + (wob(7.6, t, 10, 3) * 6).toFixed(2) + "deg)";
      els.thumb.style.opacity = clamp((t - 7.45) / 0.15, 0, 1) * (1 - smooth(8.3, 8.6, t));
      if (t >= 7.5) cue("pop", 7.5, "thumb");
    } else els.thumb.style.opacity = 0;

    /* BOOM + fairy portal */
    if (t >= 8.25 && !render._boom) {
      render._boom = 1; cue("boom", 8.25, "boom");
      spawnSparks(L.W / 2, L.H * 0.5, 50, 4242, Math.max(L.W, L.H) * 0.6);
      sparks.forEach(s => { if (s.t0 === null) s.t0 = 8.25; });
    }
    if (t >= 8.4) cue("whoosh", 8.4, "portal");
    if (t >= 8.6) cue("sparkle", 8.6, "fairy");
    els.flash.style.opacity = t >= 8.25 && t < 8.6 ? (1 - (t - 8.25) / 0.35) * 0.9 : 0;
    const zoom = t > 8.25 ? 1 + smooth(8.25, 9.4, t) * 0.5 : 1;
    els.root.style.setProperty("--pti-zoom", zoom.toFixed(3));
    els.logo.style.opacity = 1 - smooth(8.6, 9.2, t);
    drawFx(L, t);
    if (!isAds && t > 9.55) host.style.opacity = String(1 - smooth(9.55, DUR, t));
  }

  function finish(skipped) {
    playing = false;
    stopAudio();
    if (raf) cancelAnimationFrame(raf);
    try { localStorage.setItem(STORE, "1"); } catch (e) {}
    if (host) { host.classList.add("is-out"); host.style.opacity = "0"; }
    setTimeout(() => { if (host && !playing) host.style.display = "none"; }, 480);
    if (typeof onDone === "function") onDone({ skipped: !!skipped });
  }

  function play() {
    if (!host) return;
    lastCue = {}; render._s = -1; render._spk = 0; render._boom = 0; sparks = [];
    host.style.display = "block"; host.classList.remove("is-out");
    host.style.opacity = "1";
    playing = true; startT = -1;
    try { ctx(); } catch (e) {}
    showUnmute(false);
    tryPlayAudio(0);
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
    if (els.unmute) els.unmute.onclick = (ev) => { ev.stopPropagation(); try { ctx(); } catch (e) {} setMuted(false); tryPlayAudio(nowT()); };
    const armAudio = () => { try { ctx(); } catch (e) {} if (!muted) tryPlayAudio(nowT()); };
    host.addEventListener("pointerdown", armAudio, { once: true });

    const reduce = opts.ignoreReduce ? false : (opts.forceMotion ? false : !!(global.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches));
    const seen = (() => { try { return localStorage.getItem(STORE) === "1"; } catch (e) { return false; } })();

    isAds = !!opts.ads;
    if (isAds) {
      els.skip.style.display = "none"; els.snd.style.display = "none";
      const imgs = Array.from(host.querySelectorAll("img"));
      Promise.all(imgs.map(i => i.complete ? 1 : new Promise(r => { i.onload = i.onerror = r; }))).then(() => {
        global.__DURATION = DUR; global.__READY = true; play();
      });
      return;
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
    skip, isPlaying: function () { return !!playing; }, duration: DUR, render: function (t) { render(t); }
  };
  global.playPiToonIntro = function () { global.PiToonIntro.play(); };
})(typeof window !== "undefined" ? window : this);
