#!/usr/bin/env python3
"""PiToon free pipeline v3: GenerateVideo clip + character voices + SFX/ambience + mood music -> mp4.
Usage: python3 pitoon_pipeline.py scene.json      (needs ffmpeg, numpy, edge-tts; piper optional)
scene.json keys (times in seconds):
  video, out, bpm
  lines:    [{who, voice: child_boy|child_girl|woman|man|grandpa|grandma, emo, text, win:[t0,t1],
              src: native|edge|piper}]   native = keep the clip's own lip-synced speech (best sync)
  sfx:      [{t, name, gain}]   name = file in tools/sfx (bark, splash...) or synth:
            whoosh, boing, slide_down, slide_up, pop, twinkle, thud, zip
  ambience: [{name: birds|wind|rain|crickets|wind_synth|rain_synth, gain, from, to}]
  mood:     [{t, mood: playful|chase|surprise|sad|happy|tense|sneaky}]  (changes snap to the beat)
  native_gain: level of the clip's own audio outside dialogue (its own barks/splashes)."""
import json, subprocess as sp, sys, os, wave, tempfile, numpy as np
SR = 44100; HERE = os.path.dirname(os.path.abspath(__file__)); SFXDIR = os.path.join(HERE, "sfx")
rng = np.random.default_rng(7)

def run(*a): sp.run(a, check=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
def load(p, ss=None, t=None):
    a = ["ffmpeg", "-v", "error"] + (["-ss", str(ss)] if ss is not None else []) + (["-t", str(t)] if t else []) + ["-i", p, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"]
    return np.frombuffer(sp.run(a, capture_output=True, check=True).stdout, np.int16).astype(np.float32) / 32768
def save(p, x):
    x = np.clip(x, -1, 1); w = wave.open(p, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
def ff(x, af):
    fd, a = tempfile.mkstemp(suffix=".wav"); os.close(fd); save(a, x); b = a + ".o.wav"; run("ffmpeg", "-y", "-i", a, "-af", af, "-ar", str(SR), b); y = load(b); os.remove(a); os.remove(b); return y
def trim(x, th=.02):
    nz = np.where(np.abs(x) > th)[0]; return x[max(0, nz[0] - 200):nz[-1] + 2000] if len(nz) else x
def norm(x, peak=1.0): return x / max(1e-6, np.abs(x).max()) * peak
def env(n, a=.005, r=.2):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / r)
def add(buf, x, t, g=1.0):
    s = int(t * SR); e = min(len(buf), s + len(x))
    if 0 <= s < len(buf): buf[s:e] += g * x[:e - s]

# ---------------- voices ----------------
# character -> (engine voice, pitch Hz, rate %, formant shift). Formant shift (resample + atempo back)
# turns an adult voice into a convincing child (>1) or elder (<1) instead of just a "pitched" adult.
VOICE = {"child_boy": ("vi-VN-HoaiMyNeural", 10, 5, 1.13), "child_girl": ("vi-VN-HoaiMyNeural", 20, 5, 1.15),
         "woman": ("vi-VN-HoaiMyNeural", 0, 0, 1.0), "man": ("vi-VN-NamMinhNeural", 0, 0, 1.0),
         "grandpa": ("vi-VN-NamMinhNeural", -8, -12, .93), "grandma": ("vi-VN-HoaiMyNeural", -10, -12, .95)}
EMO = {"neutral": (0, 0, 0), "happy": (8, 8, 5), "cheeky": (10, 10, 5), "excited": (18, 15, 10), "surprised": (8, 20, 10),
       "scared": (22, 12, 0), "sad": (-15, -10, -10), "angry": (6, -6, 15), "laugh": (12, 18, 10)}
def voice(ln, tmp):
    v, p0, r0, fs = VOICE.get(ln.get("voice", "man"), VOICE["man"]); r, p, vol = EMO.get(ln.get("emo", "neutral"), EMO["neutral"])
    if ln.get("src") == "piper":
        m = os.path.join(HERE, "piper", "vi_VN-vais1000-medium.onnx")
        sp.run([sys.executable, "-m", "piper", "-m", m, "-f", tmp + ".wav"], input=ln["text"].encode(), check=True, capture_output=True); x = load(tmp + ".wav")
    else:
        run("edge-tts", "--voice", v, f"--rate={r0 + r:+d}%", f"--pitch={p0 + p:+d}Hz", f"--volume={vol:+d}%", "--text", ln["text"], "--write-media", tmp + ".mp3"); x = load(tmp + ".mp3")
    if fs != 1: x = ff(x, f"asetrate={int(SR * fs)},aresample={SR},atempo={1 / fs:.4f}")
    return trim(x)
def speech_span(a, w0, w1):
    seg = a[int(w0 * SR):int(w1 * SR)]; hop = SR // 50; f = np.fft.rfftfreq(hop * 2, 1 / SR); band = (f > 250) & (f < 3500)
    e = np.array([np.sum(np.abs(np.fft.rfft(seg[i:i + hop * 2] * np.hanning(hop * 2)))[band]) for i in range(0, len(seg) - hop * 2, hop)])
    if not len(e): return w0, w1
    b = np.percentile(e, 30); on = np.where(e > b + .35 * (e.max() - b))[0]
    return (w0 + on[0] * hop / SR, w0 + (on[-1] + 2) * hop / SR) if len(on) else (w0, w1)

# ---------------- synth sfx ----------------
def synth(name):
    n = lambda s: int(s * SR); t = lambda s: np.arange(n(s)) / SR
    if name == "whoosh":
        x = rng.standard_normal(n(.6)); x = ff(x, "bandpass=f=1200:w=900"); return x * np.sin(np.pi * t(.6) / .6) ** 2 * .8
    if name == "zip":
        x = rng.standard_normal(n(.25)); x = ff(x, "highpass=f=2500"); return x * np.linspace(0, 1, len(x)) * .6
    if name in ("slide_down", "slide_up"):
        tt = t(.9); f = np.linspace(1600, 300, len(tt)) if name == "slide_down" else np.linspace(300, 1600, len(tt))
        return np.sin(2 * np.pi * np.cumsum(f * (1 + .02 * np.sin(2 * np.pi * 6 * tt))) / SR) * np.minimum(1, (len(tt) - np.arange(len(tt))) / n(.1)) * .5
    if name == "boing":
        tt = t(.7); f = 180 + 120 * np.sin(2 * np.pi * 9 * tt) * np.exp(-tt * 4); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 4) * .8
    if name == "pop":
        tt = t(.12); return np.sin(2 * np.pi * np.cumsum(np.linspace(900, 200, len(tt))) / SR) * np.exp(-tt * 40)
    if name == "thud":
        tt = t(.4); return (np.sin(2 * np.pi * 70 * tt) + .4 * ff(rng.standard_normal(len(tt)), "lowpass=f=400")) * np.exp(-tt * 12)
    if name == "twinkle":
        out = np.zeros(n(1.2))
        for i, m in enumerate([88, 91, 95, 100, 95, 100]):
            tt = t(.35); add(out, np.sin(2 * np.pi * 440 * 2 ** ((m - 69) / 12) * tt) * np.exp(-tt * 10) * .3, i * .13)
        return out
    raise KeyError(name)
def sfx(name):
    p = os.path.join(SFXDIR, name + ".ogg")
    return norm(trim(load(p)), .9) if os.path.exists(p) else norm(synth(name), .9)
def ambience(name, dur):
    if name == "wind_synth":
        x = ff(rng.standard_normal(int(dur * SR)), "lowpass=f=500,highpass=f=80"); return norm(x * (0.6 + .4 * np.sin(2 * np.pi * np.arange(len(x)) / SR / 3.7)), .5)
    if name == "rain_synth":
        x = ff(rng.standard_normal(int(dur * SR)), "highpass=f=1500,lowpass=f=8000"); return norm(x, .4)
    x = load(os.path.join(SFXDIR, name + ".ogg"))
    x = np.tile(x, int(np.ceil(dur * SR / len(x))))[:int(dur * SR)]; return norm(x, .6)

# ---------------- mood music ----------------
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
def tone(m, L, amp, kind="pluck"):
    tt = np.arange(int(L * SR)) / SR; f = hz(m)
    if kind == "pluck": return amp * np.exp(-tt * 9) * (np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt))
    if kind == "stac": return amp * np.exp(-tt * 25) * np.sign(np.sin(2 * np.pi * f * tt)) * .5
    if kind == "pad": return amp * np.minimum(1, tt / .3) * np.exp(-tt * 1.2) * (np.sin(2 * np.pi * f * tt) + .5 * np.sin(2 * np.pi * f * 1.005 * tt))
    if kind == "bass": return amp * np.exp(-tt * 6) * np.sin(2 * np.pi * f * tt)
MOODS = {  # tempo multiplier, chords, melody, instrument
    "playful": (1.0, [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]], [72, 76, 79, 76, 74, 72, 74, 76], "pluck"),
    "happy": (1.0, [[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]], [79, 76, 79, 81, 79, 76, 74, 76], "pluck"),
    "chase": (1.5, [[57, 60, 64], [57, 60, 64], [53, 57, 60], [52, 56, 59]], [81, 80, 81, 76, 77, 76, 74, 72], "stac"),
    "sneaky": (.75, [[57, 60, 64], [56, 60, 63], [57, 60, 64], [52, 56, 59]], [69, 0, 72, 0, 71, 0, 68, 0], "stac"),
    "tense": (1.2, [[57, 60, 63], [57, 60, 63], [56, 59, 62], [56, 59, 62]], [69, 70, 69, 70, 69, 70, 69, 70], "stac"),
    "sad": (.6, [[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 55, 59]], [76, 74, 72, 71, 69, 0, 0, 0], "pad"),
}
def music(mood_list, dur, bpm):
    out = np.zeros(int(dur * SR)); beat = 60 / bpm
    ml = sorted(mood_list, key=lambda m: m["t"]); snapped = [dict(m, t=round(m["t"] / beat) * beat) for m in ml]
    for j, m in enumerate(snapped):
        t0, t1 = m["t"], (snapped[j + 1]["t"] if j + 1 < len(snapped) else dur); mood = m["mood"]
        if mood == "surprise":  # stinger: drum hit + rising slide + cymbal, then hold
            add(out, synth("thud") * 1.2, t0); add(out, synth("slide_up") * .5, t0)
            add(out, ff(rng.standard_normal(int(1.2 * SR)), "highpass=f=5000") * env(int(1.2 * SR), .001, .3) * .12, t0); continue
        sp_, ch, mel, kind = MOODS.get(mood, MOODS["playful"]); st = beat / 2 / sp_; i = 0; k = 0
        while t0 + i * st < t1 - .05:
            t = t0 + i * st; c = ch[(i // 8) % 4]
            if i % 2 == 0 and mel[k % 8]: add(out, tone(mel[k % 8], st * (4 if kind == "pad" else 1.5), .22, kind), t)
            if i % 2 == 0: k += 1
            if i % 4 == 0: add(out, tone(c[0] - 24, st * 2, .35, "bass"), t)
            if kind == "pad" and i % 8 == 0: [add(out, tone(x, st * 8, .08, "pad"), t) for x in c]
            elif i % 2 == 1: [add(out, tone(x, st * .8, .06, "pluck"), t) for x in c]
            if kind != "pad": add(out, rng.standard_normal(int(.03 * SR)) * np.exp(-np.arange(int(.03 * SR)) / 300) * (.06 if i % 2 else .03), t)
            i += 1
        # short fade at the boundary so mood changes land cleanly on the beat
        a, b = int(t1 * SR) - int(.06 * SR), int(t1 * SR); out[max(0, a):b] *= np.linspace(1, 0, len(out[max(0, a):b]))
    n = len(out); return norm(out * np.minimum(1, np.minimum(np.arange(n) / (SR * .3), (n - np.arange(n)) / (SR * 1.2))), .5)

def main(cfg_path):
    cfg = json.load(open(cfg_path)); d = os.path.dirname(os.path.abspath(cfg_path)); P = lambda f: os.path.join(d, f)
    nat = load(P(cfg["video"])); n = len(nat); dur = n / SR
    vo = np.zeros(n); keep = np.zeros(n); talk = np.zeros(n)
    for j, ln in enumerate(cfg.get("lines", [])):
        s0, s1 = speech_span(nat, *ln["win"]); a, b = int(s0 * SR), int(s1 * SR)
        if ln.get("src", "native") == "native":
            keep[max(0, a - 2205):b + 4410] = 1; talk[a:b] = 1; print(f"line {j} native voice {s0:.2f}-{s1:.2f}s"); continue
        x = voice(ln, P(f"_l{j}")); x = ff(x, f"atempo={max(.75, min(1.35, len(x) / SR / max(.4, s1 - s0))):.4f}")
        add(vo, norm(x, .9), s0); talk[a:a + len(x)] = 1; print(f"line {j} {ln.get('src','edge')} voice {s0:.2f}s +{len(x)/SR:.2f}s")
    sm = lambda x, w: np.convolve(x, np.ones(w) / w, "same")
    keep = np.clip(sm(keep, 2205), 0, 1); talkd = np.clip(sm(talk, SR // 3) * 3, 0, 1)
    # native track: full where we keep its lip-synced speech, else its own SFX at native_gain;
    # if a line is re-voiced, the native speech in that span is muted.
    ng = cfg.get("native_gain", .5); mute = np.clip(sm(((talk > 0) & (keep == 0)).astype(float), 2205) * 2, 0, 1)
    natl = nat * (keep + (1 - keep) * ng * (1 - mute))
    fx = np.zeros(n)
    for s in cfg.get("sfx", []):
        x = sfx(s["name"]); L = min(len(x), int(s.get("len", 2.0) * SR)); x = x[:L] * np.minimum(1, (L - np.arange(L)) / (SR * .25))
        add(fx, x, s["t"], s.get("gain", .7))
    amb = np.zeros(n)
    for a in cfg.get("ambience", []):
        f0, f1 = a.get("from", 0), a.get("to", dur); x = ambience(a["name"], f1 - f0); L = len(x); fade = np.minimum(1, np.minimum(np.arange(L), L - np.arange(L)) / (SR * .5))
        add(amb, x * fade, f0, a.get("gain", .15))
    mus = music(cfg.get("mood", [{"t": 0, "mood": "playful"}]), dur, cfg.get("bpm", 120)) * cfg.get("music_gain", .55)
    duck = 1 - .6 * talkd                      # music & ambience step back under every spoken line
    mix = natl + vo + fx * cfg.get("sfx_gain", 1) + amb * (1 - .4 * talkd) + mus * duck
    save(P("_mix.wav"), mix / max(1, np.abs(mix).max()))
    for k, v in {"_stem_voice.wav": natl * keep + vo, "_stem_fx.wav": fx + amb, "_stem_music.wav": mus * duck}.items(): save(P(k), v)
    run("ffmpeg", "-y", "-i", P(cfg["video"]), "-i", P("_mix.wav"), "-map", "0:v:0", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-af", "loudnorm=I=-16:TP=-1.5", "-shortest", P(cfg["out"]))
    print("OK", os.path.abspath(P(cfg["out"])))
if __name__ == "__main__": main(sys.argv[1])
