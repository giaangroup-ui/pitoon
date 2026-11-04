#!/usr/bin/env python3
"""PiToon pipeline (free): clip from GenerateVideo + edge-tts expressive voices aligned to
mouth movement + generated music + native SFX -> final mp4.
Usage: python3 pitoon_pipeline.py scene.json
scene.json: {"video":"raw.mp4","out":"out.mp4","music":true,
  "lines":[{"who":"Tí","voice":"child_boy","emo":"cheeky","text":"...","win":[0,4]}]}
'win' = time window (s) where the character's mouth moves in the clip (from the video prompt);
the script finds the exact speech span inside the window from the clip's own audio and
time-fits the edge-tts line onto it so lips and voice match."""
import json, subprocess as sp, sys, os, wave, numpy as np, tempfile
SR = 44100
# Vietnamese edge-tts has 2 voices; character + emotion are made with pitch/rate/volume.
VOICE = {"child_boy": ("vi-VN-NamMinhNeural", 35), "child_girl": ("vi-VN-HoaiMyNeural", 25),
         "woman": ("vi-VN-HoaiMyNeural", 0), "man": ("vi-VN-NamMinhNeural", 0),
         "grandpa": ("vi-VN-NamMinhNeural", -12), "grandma": ("vi-VN-HoaiMyNeural", -8)}
EMO = {"neutral": (0, 0, 0), "happy": (10, 8, 5), "cheeky": (12, 10, 5), "excited": (20, 15, 10),
       "surprised": (8, 20, 10), "scared": (25, 12, 0), "sad": (-15, -8, -10), "angry": (8, -5, 15),
       "laugh": (15, 18, 10)}  # rate %, pitch Hz offset, volume %

def run(*a): sp.run(a, check=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
def read_wav(p, sr=SR):
    raw = sp.run(["ffmpeg", "-v", "error", "-i", p, "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
def write_wav(p, x):
    x = np.clip(x, -1, 1); w = wave.open(p, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()

def tts(line, path):
    v, base = VOICE.get(line.get("voice", "man"), VOICE["man"])
    r, p, vol = EMO.get(line.get("emo", "neutral"), EMO["neutral"])
    run("edge-tts", "--voice", v, f"--rate={r:+d}%", f"--pitch={base + p:+d}Hz", f"--volume={vol:+d}%", "--text", line["text"], "--write-media", path)
    x = read_wav(path); nz = np.where(np.abs(x) > 0.02)[0]
    return x[nz[0]:nz[-1]] if len(nz) else x

def speech_span(a, w0, w1):
    """Voice-band energy in the clip's own audio inside the window -> (start, end) of speech."""
    seg = a[int(w0 * SR):int(w1 * SR)]; hop = SR // 50
    f = np.fft.rfftfreq(hop * 2, 1 / SR); band = (f > 250) & (f < 3500)
    e = np.array([np.sum(np.abs(np.fft.rfft(seg[i:i + hop * 2] * np.hanning(hop * 2)))[band]) for i in range(0, len(seg) - hop * 2, hop)])
    if not len(e): return w0, w1
    th = np.percentile(e, 30) + 0.35 * (e.max() - np.percentile(e, 30)); on = np.where(e > th)[0]
    if not len(on): return w0, w1
    return w0 + on[0] * hop / SR, w0 + (on[-1] + 2) * hop / SR

def fit(x, dur):
    """Time-stretch (pitch kept) with ffmpeg atempo to last `dur` seconds (limited 0.75–1.35x)."""
    t = max(0.75, min(1.35, len(x) / SR / dur)); fd, a = tempfile.mkstemp(suffix=".wav"); write_wav(a, x)
    b = a + ".o.wav"; run("ffmpeg", "-y", "-i", a, "-af", f"atempo={t:.4f}", b); y = read_wav(b); os.remove(a); os.remove(b); return y

def music(dur, bpm=128):
    """Bouncy cartoon tune: pizzicato-like plucks over I–vi–IV–V, bass + light shaker."""
    t8 = 60 / bpm / 2; n = int(dur * SR); out = np.zeros(n)
    prog = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
    mel = [72, 76, 79, 76, 74, 72, 74, 76, 69, 72, 76, 72, 71, 74, 79, 74]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    def pluck(m, L, amp):
        tt = np.arange(int(L * SR)) / SR; return amp * np.exp(-tt * 9) * (np.sin(2 * np.pi * hz(m) * tt) + .3 * np.sin(4 * np.pi * hz(m) * tt))
    i = 0; k = 0
    while i * t8 < dur:
        s = int(i * t8 * SR); ch = prog[(i // 8) % 4]
        parts = []
        if i % 2 == 0: parts.append(pluck(mel[k % 16], t8 * 1.5, .22)); k += 1
        if i % 4 == 0: parts.append(pluck(ch[0] - 24, t8 * 2, .35))
        if i % 2 == 1: parts += [pluck(c, t8 * .8, .07) for c in ch]
        sh = np.random.randn(int(.03 * SR)) * np.exp(-np.arange(int(.03 * SR)) / 300) * .04; parts.append(sh)
        for p in parts:
            e = min(n, s + len(p)); out[s:e] += p[:e - s]
        i += 1
    fade = np.minimum(1, np.minimum(np.arange(n) / (SR * .5), (n - np.arange(n)) / (SR * 1.2)))
    return out * fade / max(1e-6, np.abs(out).max()) * .5

def main(cfg_path):
    cfg = json.load(open(cfg_path)); d = os.path.dirname(os.path.abspath(cfg_path)); P = lambda f: os.path.join(d, f)
    native = read_wav(P(cfg["video"])); n = len(native); dur = n / SR
    voice = np.zeros(n); duck = np.ones(n); spans = []
    for j, ln in enumerate(cfg["lines"]):
        x = tts(ln, P(f"_l{j}.mp3")); s0, s1 = speech_span(native, *ln["win"])
        x = fit(x, max(.4, s1 - s0)); a = int(s0 * SR); b = min(n, a + len(x)); voice[a:b] += x[:b - a]
        lo, hi = max(0, a - SR // 10), min(n, b + SR // 10); duck[lo:hi] = 0.0; spans.append((round(s0, 2), round(s0 + len(x) / SR, 2)))
        print(f"line {j}: {ln['text']!r} mouth {s0:.2f}-{s1:.2f}s -> voice {spans[-1]}")
    duck = np.convolve(duck, np.ones(2205) / 2205, "same")  # smooth 50 ms
    sfx = native * duck * cfg.get("sfx_gain", 0.8)       # keep the clip's own splashes/barks, mute its speech
    mus = music(dur) * cfg.get("music_gain", 0.6) if cfg.get("music", True) else 0
    mus = mus * (1 - 0.55 * (np.convolve((voice != 0).astype(float), np.ones(SR // 4) / (SR // 4), "same") > 0.01))  # duck music under dialogue
    mix = voice / max(1e-6, np.abs(voice).max()) * .9 + sfx + mus
    write_wav(P("_mix.wav"), mix / max(1, np.abs(mix).max()))
    run("ffmpeg", "-y", "-i", P(cfg["video"]), "-i", P("_mix.wav"), "-map", "0:v:0", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-af", "loudnorm=I=-16:TP=-1.5", "-shortest", P(cfg["out"]))
    print("OK", P(cfg["out"]))

if __name__ == "__main__": main(sys.argv[1])
