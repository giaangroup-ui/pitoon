#!/usr/bin/env python3
"""PiToon QC director – automated measurable checks. Exit 0 = PASS, 1 = REJECT.
Usage: python3 qc.py scene.json film.mp4 [--report qc.md] [--grid-dir DIR]
Checks: safety + continuity rules (scene.json), resolution/length, black & frozen frames, cut smoothness,
Whisper transcript vs script per line (similarity), unexpected speech outside script windows,
lip timing (detected speech starts inside each line window), loudness (EBU R128), music ducking
and SFX presence (from pipeline stems _stem_*.wav). Writes frame grids for visual review."""
import json, os, re, sys, subprocess as sp, difflib, unicodedata, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from safety_check import check as safety_check
import continuity
SR = 16000
def sh(*a): return sp.run(a, capture_output=True, text=True)
def norm(t): t = unicodedata.normalize("NFC", t.lower()); return re.sub(r"[^\w\s]", "", t).split()
def sim(a, b): return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()
def load(p, sr=SR):
    r = sp.run(["ffmpeg", "-v", "error", "-i", p, "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"], capture_output=True).stdout
    return np.frombuffer(r, np.int16).astype(np.float32) / 32768
_M = None
def whisper(x):
    global _M
    from faster_whisper import WhisperModel
    _M = _M or WhisperModel("small", compute_type="int8")
    seg, _ = _M.transcribe(x, language="vi", word_timestamps=True, vad_filter=True)
    return [w for s in seg for w in (s.words or [])]

def run(cfg_path, film, report=None, grid_dir=None):
    cfg = json.load(open(cfg_path)); d = os.path.dirname(os.path.abspath(cfg_path)); R = []
    def item(name, ok, detail=""): R.append((name, bool(ok), detail))
    # 1 rules
    s = safety_check(cfg); item("An toàn trẻ em (luật cấm)", not s, "; ".join(s))
    if cfg.get("qc", {}).get("continuity", True):
        c = continuity.check(cfg); item("Liên tục / luật một đạo cụ (scene.json)", not c, "; ".join(c))
    else:
        item("Liên tục / luật một đạo cụ (scene.json)", True, "bỏ qua: phim dùng bible riêng, QC nhân vật bằng mắt")
    # 2 technical
    pr = json.loads(sh("ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration", "-of", "json", film).stdout)
    v = [x for x in pr["streams"] if x["codec_type"] == "video"][0]; dur = float(pr["format"]["duration"])
    want = cfg.get("qc", {}).get("length", [14, 16])
    item("Độ phân giải ≥ 1280x720", v["width"] >= 1280 and v["height"] >= 720, f'{v["width"]}x{v["height"]}')
    item("Độ dài", want[0] <= dur <= want[1], f"{dur:.2f}s (yêu cầu {want[0]}–{want[1]}s)")
    bd = sh("ffmpeg", "-i", film, "-vf", "blackdetect=d=0.2:pix_th=0.1", "-an", "-f", "null", "-").stderr
    item("Không có khung đen", "black_start" not in bd, ";".join(re.findall(r"black_start:\S+ black_end:\S+", bd)))
    fz = sh("ffmpeg", "-i", film, "-vf", "freezedetect=n=0.003:d=" + str(cfg.get("qc", {}).get("freeze_d", 1.0)) + "", "-an", "-f", "null", "-").stderr
    item("Không đứng hình > 1s", "freeze_start" not in fz, ";".join(re.findall(r"freeze_start: \S+", fz)))
    # cut smoothness: mean abs frame diff at shot boundaries vs typical
    cuts = [sh_["to"] for sh_ in cfg.get("shots", [])][:-1]; bad = []
    for t in cuts:
        # max frame-to-frame jump across the whole transition window (a hard cut = one big jump, a fade = many small)
        r = sp.run(["ffmpeg", "-v", "error", "-ss", f"{max(t - 0.25, 0):.3f}", "-t", "0.8", "-i", film, "-vf", "fps=24,scale=160:90,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
        fr = np.frombuffer(r, np.uint8).astype(float).reshape(-1, 160 * 90)
        if len(fr) > 1:
            dd = np.abs(np.diff(fr, axis=0)).mean(axis=1).max()
            if dd > 18: bad.append(f"{t}s Δ={dd:.1f}")
    item("Chuyển cảnh mượt (không giật tại điểm nối)", not bad, "; ".join(bad))
    # 3 audio – speech
    lines = cfg.get("lines", []); used = set(); det = []
    # optional speech_film: ASR a pre-MG body file (timestamps +offset); else speech_range slice; else whole film
    sf = cfg.get("qc", {}).get("speech_film"); sr = cfg.get("qc", {}).get("speech_range"); off = 0.0
    if sf and os.path.exists(sf):
        x = load(sf); words = whisper(x); off = float(cfg.get("qc", {}).get("speech_offset", 0))
        for w in words: w.start += off; w.end += off
    elif sr:
        x = load(film); a, b = int(sr[0] * SR), int(sr[1] * SR)
        words = whisper(x[a:b]); off = sr[0]
        for w in words: w.start += off; w.end += off
    else:
        words = whisper(load(film))
    ok_all = True; lip_ok = True
    for i, l in enumerate(lines):
        w0, w1 = l["win"]; ws = [w for w in words if w0 - .3 <= w.start < w1]
        for w in ws: used.add(id(w))
        heard = " ".join(w.word.strip() for w in ws); sc = sim(heard, l["text"])
        if sc < cfg.get("qc", {}).get("min_sim", .7): ok_all = False
        if not ws or ws[0].start < w0 - .3: lip_ok = False
        det.append(f'L{i+1} {sc:.0%} “{heard}” / kịch bản “{l["text"]}”' + (f" @ {ws[0].start:.2f}s" if ws else ""))
    item("Lời thoại nghe rõ & đúng kịch bản (Whisper ≥ 70%)", ok_all, " | ".join(det))
    item("Thời điểm nói nằm trong cửa sổ khớp môi", lip_ok, "")
    stray = [f"{w.start:.1f}s “{w.word.strip()}”" for w in words if id(w) not in used and w.probability > .3]
    item("Không có giọng lạ / lẩm bẩm ngoài kịch bản", not stray, ", ".join(stray))
    # 4 mix
    ln = sh("ffmpeg", "-i", film, "-af", "ebur128", "-f", "null", "-").stderr; I = re.findall(r"I:\s+(-?[\d.]+) LUFS", ln)
    I = float(I[-1]) if I else -99; item("Âm lượng tổng −18…−14 LUFS", -18 <= I <= -14, f"{I} LUFS")
    mus, fx = os.path.join(d, "_stem_music.wav"), os.path.join(d, "_stem_fx.wav")
    if os.path.exists(mus):
        m = load(mus); talk = np.zeros(len(m), bool)
        vp = os.path.join(d, "_stem_voice.wav")
        if os.path.exists(vp):   # talk = where the voice stem is actually speaking (50 ms frames), not the whole window
            v = load(vp)[:len(m)]; H = SR // 20
            for i in range(0, len(v) - H, H):
                if 20 * np.log10(np.sqrt((v[i:i + H] ** 2).mean()) + 1e-9) > -35: talk[i:i + H] = True
        else:
            for l in lines: talk[int(l["win"][0] * SR):int(l["win"][1] * SR)] = True
        rms = lambda a: 20 * np.log10(np.sqrt((a ** 2).mean()) + 1e-9); dk = rms(m[~talk]) - rms(m[talk])
        item("Nhạc tự hạ khi có thoại (≥ 4 dB)", dk >= 4, f"{dk:.1f} dB")
        f = load(fx); miss = [s["name"] for s in cfg.get("sfx", []) if rms(f[int(s["t"] * SR):int((s["t"] + .4) * SR)]) < -45]
        item("SFX có mặt đúng thời điểm", not miss and cfg.get("sfx"), ", ".join(miss) or f'{len(cfg.get("sfx", []))} SFX')
    else: item("Stem âm thanh để kiểm tra mix", False, "thiếu _stem_*.wav")
    # grids for visual review
    gd = grid_dir or d
    for s_ in cfg.get("shots", [{"id": "all", "from": 0, "to": dur}]):
        sp.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s_["from"]), "-t", str(s_["to"] - s_["from"]), "-i", film, "-vf", "fps=2,scale=320:-1,tile=5x2", "-frames:v", "1", os.path.join(gd, f"qc_grid_{s_['id']}.jpg")])
    passed = all(ok for _, ok, _ in R)
    md = [f"# QC – {os.path.basename(film)}", "", f"**KẾT QUẢ TỰ ĐỘNG: {'ĐẠT ✅' if passed else 'TRẢ VỀ ❌'}**", "", "| Hạng mục | KQ | Chi tiết |", "|---|---|---|"]
    md += [f"| {n} | {'✅' if ok else '❌'} | {dt} |" for n, ok, dt in R]
    txt = "\n".join(md); print(txt)
    if report: open(report, "w").write(txt + "\n")
    return passed, R
if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    rep = sys.argv[sys.argv.index("--report") + 1] if "--report" in sys.argv else None
    if rep in a: a.remove(rep)
    ok, _ = run(a[0], a[1], rep); sys.exit(0 if ok else 1)
