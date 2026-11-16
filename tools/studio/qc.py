#!/usr/bin/env python3
"""PiToon QC director – automated measurable checks. Exit 0 = PASS, 1 = REJECT.
Usage: python3 qc.py scene.json film.mp4 [--report qc.md] [--grid-dir DIR]
Checks: safety + continuity rules (scene.json), resolution/length, black & frozen frames, cut smoothness,
Whisper transcript vs script per line (similarity), unexpected speech outside script windows,
lip timing (detected speech starts inside each line window), loudness (EBU R128), music ducking
and SFX presence (from pipeline stems _stem_*.wav). Writes frame grids for visual review.
Studio v2 (10 khâu): motion score (film + từng cảnh), % giây gần như đứng yên, đứng hình ≤ 1s (không nới),
độ dài từng cảnh, thoại do nhân vật nói trong video (khớp môi thật), Whisper ≥ 80%, câu ≤ 10 từ, ≤ 3 câu dẫn,
mỗi nhân vật một giọng, cảm xúc từng câu, mật độ tiếng động. Mỗi hạng mục ghi khâu chịu trách nhiệm (stages.py).
--json out.json ghi kết quả máy đọc cho line/studio_runner.py."""
import json, os, re, sys, subprocess as sp, difflib, unicodedata, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from safety_check import check as safety_check
import continuity
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stages import T, NARRATOR
SR = 16000
def sh(*a): return sp.run(a, capture_output=True, text=True)
def norm(t): t = unicodedata.normalize("NFC", t.lower()); return re.sub(r"[^\w\s]", "", t).split()
def notone(t): return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn").replace("đ", "d").replace("Đ", "D")
def sim(a, b):
    """Khớp lời: lấy điểm cao hơn giữa so có dấu và so bỏ dấu (Whisper hay nghe sai dấu ở tiếng cười, thán từ: 'hì hì' -> 'hi hi')."""
    s1 = difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()
    s2 = difflib.SequenceMatcher(None, norm(notone(a)), norm(notone(b))).ratio()
    return max(s1, s2)
def motion_curve(film):
    """Chênh lệch điểm ảnh trung bình giữa 2 khung liên tiếp (24 fps, 160x90 xám) – cùng cách đo với bản chẩn đoán 16/11."""
    b = sp.run(["ffmpeg", "-v", "error", "-i", film, "-vf", "fps=24,scale=160:90,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    a = np.frombuffer(b, np.uint8).reshape(-1, 90, 160).astype(np.float32)
    return np.abs(np.diff(a, axis=0)).mean(axis=(1, 2)) if len(a) > 1 else np.zeros(1)
def load(p, sr=SR):
    r = sp.run(["ffmpeg", "-v", "error", "-i", p, "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"], capture_output=True).stdout
    return np.frombuffer(r, np.int16).astype(np.float32) / 32768
_M = None
def whisper(x):
    global _M
    from faster_whisper import WhisperModel
    import fcntl   # một Whisper mỗi lúc: 2 lần chạy song song làm kết quả nhận dạng sai (đã gặp 16/11)
    with open("/tmp/pitoon_whisper.lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        _M = _M or WhisperModel("small", compute_type="int8")
        seg, _ = _M.transcribe(x, language="vi", word_timestamps=True, vad_filter=True)
        return [w for s in seg for w in (s.words or [])]

def run(cfg_path, film, report=None, grid_dir=None, json_out=None):
    cfg = json.load(open(cfg_path)); d = os.path.dirname(os.path.abspath(cfg_path)); R = []
    M = {}
    def item(name, ok, detail="", stage=10): R.append((name, bool(ok), detail, stage))
    # 1 rules
    s = safety_check(cfg); s1 = [x for x in s if x.startswith(("[lời thoại dài]", "[bài học]"))]; s2 = [x for x in s if x not in s1]
    item("An toàn trẻ em (luật cấm)", not s2, "; ".join(s2), 2)
    item("Kịch bản có bài học, câu ≤ 12 từ (safety_check)", not s1, "; ".join(s1[:3]) + (f" … ({len(s1)} mục)" if len(s1) > 3 else ""), 1)
    if cfg.get("qc", {}).get("continuity", True):
        c = continuity.check(cfg); item("Liên tục / luật một đạo cụ (scene.json)", not c, "; ".join(c), 4)
    else:
        item("Liên tục / luật một đạo cụ (scene.json)", True, "bỏ qua: phim dùng bible riêng, QC nhân vật bằng mắt", 4)
    # 2 technical
    pr = json.loads(sh("ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration", "-of", "json", film).stdout)
    v = [x for x in pr["streams"] if x["codec_type"] == "video"][0]; dur = float(pr["format"]["duration"])
    want = cfg.get("qc", {}).get("length", [14, 16])
    item("Độ phân giải ≥ 1280x720", v["width"] >= 1280 and v["height"] >= 720, f'{v["width"]}x{v["height"]}', 8)
    item("Độ dài", want[0] <= dur <= want[1], f"{dur:.2f}s (yêu cầu {want[0]}–{want[1]}s)", 8)
    bd = sh("ffmpeg", "-i", film, "-vf", "blackdetect=d=0.2:pix_th=0.1", "-an", "-f", "null", "-").stderr
    item("Không có khung đen", "black_start" not in bd, ";".join(re.findall(r"black_start:\S+ black_end:\S+", bd)), 8)
    fz = sh("ffmpeg", "-i", film, "-vf", "freezedetect=n=0.003:d=" + str(min(float(cfg.get("qc", {}).get("freeze_d", T["freeze_s"])), T["freeze_s"])), "-an", "-f", "null", "-").stderr
    fzs = re.findall(r"freeze_duration: ([\d.]+)", fz); fzt = re.findall(r"freeze_start: ([\d.]+)", fz)
    item("Không đứng hình > 1s", "freeze_start" not in fz, f"{len(fzt)} đoạn, dài nhất {max(map(float, fzs or ['0'])):.1f}s (từ {', '.join(fzt[:5])}s)" if fzt else "", 8)
    # cut smoothness: mean abs frame diff at shot boundaries vs typical
    cuts = [sh_["to"] for sh_ in cfg.get("shots", [])][:-1]; bad = []
    for t in cuts:
        # max frame-to-frame jump across the whole transition window (a hard cut = one big jump, a fade = many small)
        r = sp.run(["ffmpeg", "-v", "error", "-ss", f"{max(t - 0.25, 0):.3f}", "-t", "0.8", "-i", film, "-vf", "fps=24,scale=160:90,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
        fr = np.frombuffer(r, np.uint8).astype(float).reshape(-1, 160 * 90)
        if len(fr) > 1:
            dd = np.abs(np.diff(fr, axis=0)).mean(axis=1).max()
            if dd > 18: bad.append(f"{t}s Δ={dd:.1f}")
    item("Chuyển cảnh mượt (không giật tại điểm nối)", not bad, "; ".join(bad), 8)
    # 2b motion (studio v2)
    mc = motion_curve(film); fps = 24; mfilm = float(mc.mean())
    secs = np.array([mc[i * fps:(i + 1) * fps].mean() for i in range(max(1, len(mc) // fps))])
    static_pct = float(100 * (secs < 0.6).mean())
    shots = cfg.get("shots", [])
    per = [(s_["id"], float(mc[int(s_["from"] * fps):max(int(s_["to"] * fps), int(s_["from"] * fps) + 1)].mean())) for s_ in shots] if shots else []
    low = [f"{i} {m:.2f}" for i, m in per if m < T["motion_shot"]]
    M.update(motion_film=round(mfilm, 2), static_pct=round(static_pct, 1), motion_shots={i: round(m, 2) for i, m in per})
    item(f"Điểm chuyển động cả phim ≥ {T['motion_film']}", mfilm >= T["motion_film"], f"{mfilm:.2f} (mẫu Tí & Cún 5,6)", 5)
    item(f"Cảnh nào cũng cử động (mỗi cảnh ≥ {T['motion_shot']})", not low, ("yếu: " + ", ".join(low)) if low else ", ".join(f"{i} {m:.1f}" for i, m in per), 5)
    item(f"Giây gần như đứng yên ≤ {T['static_pct']:.0f}%", static_pct <= T["static_pct"], f"{static_pct:.0f}% số giây", 8)
    # 2c per-shot: độ dài cảnh
    a0, a1 = T["shot_len"]; longs = [f'{s_["id"]} {s_["to"] - s_["from"]:.1f}s' for s_ in shots if not (a0 <= s_["to"] - s_["from"] <= a1)]
    item(f"Mỗi cảnh dài {a0:g}–{a1 - .2:g} giây", shots and not longs, ", ".join(longs[:8]) + (f" … ({len(longs)} cảnh)" if len(longs) > 8 else ""), 4)
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
        if sc < max(float(cfg.get("qc", {}).get("min_sim", T["whisper"])), T["whisper"]): ok_all = False
        if not ws or ws[0].start < w0 - .3: lip_ok = False
        det.append(f'L{i+1} {sc:.0%} “{heard}” / kịch bản “{l["text"]}”' + (f" @ {ws[0].start:.2f}s" if ws else ""))
    item(f"Lời thoại nghe rõ & đúng kịch bản (Whisper ≥ {T['whisper']:.0%})", ok_all, " | ".join(det), 6)
    item("Thời điểm nói nằm trong cửa sổ khớp môi", lip_ok, "", 6)
    # 3b script/voice rules (studio v2)
    isnar = lambda l: (l.get("who", "").strip().lower() in NARRATOR) or l.get("voice") == "narrator"
    dia = [l for l in lines if not isnar(l)]; nar = [l for l in lines if isnar(l)]
    nonnative = [f'{l.get("who")}: “{l["text"][:30]}”' for l in dia if l.get("src") != "native" and not l.get("offscreen")]
    item("Nhân vật tự nói trong video (khớp môi thật)", not nonnative, f"{len(nonnative)}/{len(dia)} câu lồng sau: " + "; ".join(nonnative[:3]) if nonnative else f"{len(dia)} câu", 5)
    longl = [f'“{l["text"][:40]}” ({len(l["text"].split())} từ)' for l in dia if len(l["text"].split()) > T["line_words"]]
    item(f"Câu thoại ≤ {T['line_words']} từ", not longl, "; ".join(longl[:3]) + (f" … ({len(longl)} câu)" if len(longl) > 3 else ""), 1)
    item(f"Lời dẫn tối đa {T['narration_max']} câu ngắn", len(nar) <= T["narration_max"], f"{len(nar)} câu dẫn, {sum(l['win'][1] - l['win'][0] for l in nar):.0f}s", 1)
    vo = {}
    for l in dia: vo.setdefault(l.get("tts") or l.get("voice", "?") , set()).add(l.get("who"))
    shared = [f"{v}: {', '.join(sorted(w))}" for v, w in vo.items() if len(w) > 1]
    item("Mỗi nhân vật một giọng riêng", not shared, "; ".join(shared) or ", ".join(sorted({f'{l.get("who")}={l.get("tts") or l.get("voice")}' for l in dia})), 3)
    emos = {l.get("emo") for l in dia if l.get("emo")}
    item("Cảm xúc ghi cho từng câu (≥ 2 loại)", dia and all(l.get("emo") for l in dia) and len(emos) >= min(2, len(dia)), ", ".join(sorted(emos)), 4)
    stray = [f"{w.start:.1f}s “{w.word.strip()}”" for w in words if id(w) not in used and w.probability > .3]
    item("Không có giọng lạ / lẩm bẩm ngoài kịch bản", not stray, ", ".join(stray), 6)
    # 4 mix
    ln = sh("ffmpeg", "-i", film, "-af", "ebur128", "-f", "null", "-").stderr; I = re.findall(r"I:\s+(-?[\d.]+) LUFS", ln)
    I = float(I[-1]) if I else -99; lo, hi = T["film_lufs"]; item(f"Âm lượng phim gốc {lo}…{hi} LUFS (bản đăng chuẩn hoá −14 ở khâu 9)", lo <= I <= hi, f"{I} LUFS", 7)
    nsfx = len(cfg.get("sfx", [])); dens = nsfx / max(dur, 1); M.update(sfx_per_s=round(dens, 2), lufs=I)
    item(f"Mật độ tiếng động ≥ {T['sfx_per_s']}/giây", dens >= T["sfx_per_s"], f"{nsfx} tiếng / {dur:.0f}s = {dens:.2f}/giây (mẫu 0,6)", 7)
    sd = next((x for x in (d, os.path.dirname(os.path.abspath(film)), os.path.join(d, "export")) if os.path.exists(os.path.join(x, "_stem_music.wav"))), d)
    mus, fx = os.path.join(sd, "_stem_music.wav"), os.path.join(sd, "_stem_fx.wav")
    if os.path.exists(mus):
        m = load(mus); talk = np.zeros(len(m), bool)
        vp = os.path.join(sd, "_stem_voice.wav")
        if os.path.exists(vp):   # talk = where the voice stem is actually speaking (50 ms frames), not the whole window
            v = load(vp)[:len(m)]; H = SR // 20
            for i in range(0, len(v) - H, H):
                if 20 * np.log10(np.sqrt((v[i:i + H] ** 2).mean()) + 1e-9) > -35: talk[i:i + H] = True
        else:
            for l in lines: talk[int(l["win"][0] * SR):int(l["win"][1] * SR)] = True
        rms = lambda a: 20 * np.log10(np.sqrt((a ** 2).mean()) + 1e-9); dk = rms(m[~talk]) - rms(m[talk])
        item("Nhạc tự hạ khi có thoại (≥ 4 dB)", dk >= T["duck_db"], f"{dk:.1f} dB", 7)
        f = load(fx); miss = [s["name"] for s in cfg.get("sfx", []) if rms(f[int(s["t"] * SR):int((s["t"] + .4) * SR)]) < -45]
        item("SFX có mặt đúng thời điểm", not miss and cfg.get("sfx"), ", ".join(miss) or f'{len(cfg.get("sfx", []))} SFX', 7)
    else: item("Stem âm thanh để kiểm tra mix", False, "thiếu _stem_*.wav", 7)
    # grids for visual review
    gd = grid_dir or d
    for s_ in cfg.get("shots", [{"id": "all", "from": 0, "to": dur}]):
        sp.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s_["from"]), "-t", str(s_["to"] - s_["from"]), "-i", film, "-vf", "fps=2,scale=320:-1,tile=5x2", "-frames:v", "1", os.path.join(gd, f"qc_grid_{s_['id']}.jpg")])
    passed = all(ok for _, ok, _, _ in R)
    from stages import NAME
    back = sorted({st for _, ok, _, st in R if not ok})
    md = [f"# QC – {os.path.basename(film)}", "", f"**KẾT QUẢ TỰ ĐỘNG: {'ĐẠT ✅' if passed else 'TRẢ VỀ ❌'}**", ""]
    if back: md += ["Trả về: " + ", ".join(f"khâu {s} {NAME[s]}" for s in back), ""]
    md += ["| Hạng mục | KQ | Khâu | Chi tiết |", "|---|---|---|---|"]
    md += [f"| {n} | {'✅' if ok else '❌'} | {st} | {dt.replace('|', '/')} |" for n, ok, dt, st in R]
    md += ["", "Cần Tổng kiểm duyệt xem bằng mắt (qc_grid_*.jpg): nhân vật đúng bible, nét mặt khớp cảm xúc từng câu, không hành động nguy hiểm trong hình."]
    txt = "\n".join(md); print(txt)
    if report: open(report, "w").write(txt + "\n")
    if json_out:
        json.dump({"film": os.path.basename(film), "passed": passed, "return_to": back, "measured": M,
                   "items": [{"name": n, "ok": ok, "detail": dt, "stage": st} for n, ok, dt, st in R]}, open(json_out, "w"), ensure_ascii=False, indent=1)
    return passed, R
if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
    rep, js, gd = opt("--report"), opt("--json"), opt("--grid-dir")
    a = [x for x in a if x not in (rep, js, gd)]
    ok, _ = run(a[0], a[1], rep, gd, js); sys.exit(0 if ok else 1)
