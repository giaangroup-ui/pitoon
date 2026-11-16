#!/usr/bin/env python3
"""Khâu 9 – Đóng gói đa nền tảng. Xuất NHÁP, không bao giờ tự đăng.
Usage: export.py scene.json film.mp4 out_dir      (chạy xong tự kiểm tra gói -> package_qc.json/.md; exit 1 nếu chưa đạt)
       export.py --check out_dir                    (chỉ kiểm tra lại gói)
Ra: vertical_9x16.mp4 (1080x1920), youtube_16x9.mp4 (1920x1080), subs.srt, thumb_16x9.jpg (1280x720),
    thumb_9x16.jpg (1080x1920), metadata.json. Âm lượng −14 LUFS, đỉnh thật ≤ −1 dBTP (loudnorm 2 lượt).
Phụ đề 9:16 nằm trong vùng an toàn chung TikTok/Reels/Shorts: cách trên 288, dưới 672, trái 65, phải 192 px."""
import json, os, re, shutil, subprocess as sp, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H); sys.path.insert(0, os.path.join(os.path.dirname(H), "studio"))
from stages import T
import metadata
FONT = "/usr/share/fonts/truetype/sand-box/google/Be Vietnam Pro/BeVietnamPro-Bold.ttf"
SAFE = {"top": 288, "bottom": 672, "left": 65, "right": 192}           # khung 1080x1920
FG_Y = 300                                                          # phim 16:9 đặt trong khung dọc, ngay dưới mép an toàn trên
SUB = {"v": dict(W=1080, H=1920, size=68, ml=SAFE["left"] + 20, mr=SAFE["right"] + 20, mv=SAFE["bottom"] + 8),
       "h": dict(W=1920, H=1080, size=52, ml=120, mr=120, mv=60)}
def run(*a): return sp.run(a, capture_output=True, text=True)
def ts(t, srt=False):
    h, r = divmod(max(t, 0), 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",") if srt else f"{int(h)}:{int(m):02d}:{s:05.2f}"
def clean(t): return re.sub(r"\s+", " ", t).strip()
def write_subs(lines, out, td):
    open(os.path.join(out, "subs.srt"), "w").write("\n".join(f"{i+1}\n{ts(l['win'][0], 1)} --> {ts(l['win'][1], 1)}\n{clean(l['text'])}\n" for i, l in enumerate(lines)))
    paths = {}
    for k, p in SUB.items():
        a = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {p['W']}\nPlayResY: {p['H']}\nWrapStyle: 0\n\n[V4+ Styles]\n"
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
             f"Style: Kid,Be Vietnam Pro,{p['size']},&H00FFFFFF,&H00FFFFFF,&H00402A1E,&H80000000,1,0,0,0,100,100,0,0,1,6,2,2,{p['ml']},{p['mr']},{p['mv']},1\n\n"
             "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        a += "".join(f"Dialogue: 0,{ts(l['win'][0])},{ts(l['win'][1])},Kid,,0,0,0,,{clean(l['text'])}\n" for l in lines)
        paths[k] = os.path.join(td, f"subs_{k}.ass"); open(paths[k], "w").write(a)
    return paths
def loud_params(film):
    e = run("ffmpeg", "-hide_banner", "-i", film, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-").stderr
    j = json.loads(e[e.rindex("{"):e.rindex("}") + 1])
    return f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000"
def enc(inp, vf, af, out):
    r = run("ffmpeg", "-loglevel", "error", "-y", "-i", inp, "-filter_complex", vf, "-map", "[v]", "-map", "0:a:0?", "-af", af,
            "-c:v", "libx264", "-profile:v", "high", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out)
    if r.returncode: raise SystemExit(r.stderr[-800:])
def thumbs(film, title, t, out, td):
    tf = os.path.join(td, "title.txt"); open(tf, "w").write(title)
    fd = os.path.join(td, "fonts"); os.makedirs(fd, exist_ok=True); shutil.copy(FONT, os.path.join(fd, "f.ttf")); ff = os.path.join(fd, "f.ttf")
    dt = lambda size, y: f"drawtext=fontfile={ff}:textfile={tf}:fontsize={size}:fontcolor=white:borderw=8:bordercolor=0x1e2a4a:x=(w-text_w)/2:y={y}"
    run("ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", film, "-frames:v", "1", "-vf", f"scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,{dt(64, 'h-text_h-48')}", "-q:v", "3", os.path.join(out, "thumb_16x9.jpg"))
    run("ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", film, "-frames:v", "1", "-filter_complex",
        f"split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=0:{FG_Y + 200},{dt(78, SAFE['top'] + 60)}",
        "-q:v", "3", os.path.join(out, "thumb_9x16.jpg"))
def export(scene, film, out):
    cfg = json.load(open(scene)); os.makedirs(out, exist_ok=True)
    dur = float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", film).stdout)
    with tempfile.TemporaryDirectory() as td:
        fd = os.path.join(td, "fonts"); os.makedirs(fd); shutil.copy(FONT, fd)
        ass = write_subs(cfg.get("lines", []), out, td); af = loud_params(film)
        enc(film, f"[0:v:0]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,ass={ass['h']}:fontsdir={fd}[v]", af, os.path.join(out, "youtube_16x9.mp4"))
        enc(film, f"[0:v:0]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=0:{FG_Y},setsar=1,ass={ass['v']}:fontsdir={fd}[v]", af, os.path.join(out, "vertical_9x16.mp4"))
        thumbs(film, cfg.get("title", "PiToon"), float(cfg.get("thumb_t", min(dur * .4, dur - .5))), out, td)
    json.dump(metadata.gen(cfg, dur=round(dur, 1)), open(os.path.join(out, "metadata.json"), "w"), ensure_ascii=False, indent=1)
    return check(out)
def check(out):
    """Kiểm tra gói (khâu 9). Trả (đạt?, items) và ghi package_qc.json/.md."""
    R = []
    def item(n, ok, dt="", st=9): R.append({"name": n, "ok": bool(ok), "detail": dt, "stage": st})
    want = {"vertical_9x16.mp4": (1080, 1920), "youtube_16x9.mp4": (1920, 1080)}; dur = 0
    for f, (w, h) in want.items():
        p = os.path.join(out, f)
        if not os.path.exists(p): item(f"{f} có trong gói", False, "thiếu"); continue
        pr = json.loads(run("ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,profile,width,height,sample_rate:format=duration", "-of", "json", p).stdout)
        v = next(s for s in pr["streams"] if s["codec_type"] == "video"); a = next((s for s in pr["streams"] if s["codec_type"] == "audio"), {})
        dur = float(pr["format"]["duration"])
        item(f"{f}: {w}×{h}, H.264 High, AAC 48 kHz", (v["width"], v["height"]) == (w, h) and v["codec_name"] == "h264" and v.get("profile") == "High" and a.get("codec_name") == "aac" and a.get("sample_rate") == "48000",
             f'{v["width"]}×{v["height"]} {v["codec_name"]}/{v.get("profile")} {a.get("codec_name")} {a.get("sample_rate")} Hz')
        e = run("ffmpeg", "-hide_banner", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-").stderr
        I = float((re.findall(r"I:\s+(-?[\d.]+) LUFS", e) or ["-99"])[-1]); tp = float((re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e) or ["99"])[-1])
        lo, hi = T["pkg_lufs"]
        item(f"{f}: âm lượng −14 LUFS ±1, đỉnh thật ≤ {T['pkg_tp']:g} dBTP", lo <= I <= hi and tp <= T["pkg_tp"], f"{I} LUFS, đỉnh {tp} dBTP")
    s = SUB["v"]; top_of_fg_sub = s["H"] - s["mv"]
    item("Phụ đề 9:16 trong vùng an toàn (trên 288, dưới 672, trái 65, phải 192 px)", s["ml"] >= SAFE["left"] and s["mr"] >= SAFE["right"] and s["mv"] >= SAFE["bottom"] and FG_Y >= SAFE["top"],
         f"lề trái {s['ml']}, phải {s['mr']}, đáy chữ cách đáy {s['mv']} px (y ≤ {top_of_fg_sub}); phim bắt đầu y={FG_Y}")
    item("Phụ đề rời subs.srt", os.path.exists(os.path.join(out, "subs.srt")) and os.path.getsize(os.path.join(out, "subs.srt")) > 0)
    for f, (w, h) in {"thumb_16x9.jpg": (1280, 720), "thumb_9x16.jpg": (1080, 1920)}.items():
        p = os.path.join(out, f); ok = os.path.exists(p)
        d = json.loads(run("ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "json", p).stdout)["streams"][0] if ok else {}
        item(f"Ảnh bìa {f} {w}×{h}", ok and (d.get("width"), d.get("height")) == (w, h), f'{d.get("width")}×{d.get("height")}' if ok else "thiếu")
    mp = os.path.join(out, "metadata.json"); md = json.load(open(mp)) if os.path.exists(mp) else {}
    item("Chú thích, hashtag 6 nền tảng; YouTube 'dành cho trẻ em' + nhãn AI; trạng thái NHÁP",
         all(k in md for k in ("tiktok", "instagram_reels", "facebook", "youtube_shorts", "youtube", "zalo")) and md.get("youtube", {}).get("madeForKids") and md.get("youtube", {}).get("privacyStatus") == "private" and md.get("tiktok", {}).get("ai_generated_label"),
         md.get("status", "thiếu metadata.json"))
    item(f"Bản 9:16 ≤ {T['short_max_s']} giây (đăng được Shorts, Reels tới người mới)", dur <= T["short_max_s"], f"{dur:.0f}s", 1)
    ok = all(r["ok"] for r in R)
    json.dump({"passed": ok, "items": R, "return_to": sorted({r["stage"] for r in R if not r["ok"]})}, open(os.path.join(out, "package_qc.json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(out, "package_qc.md"), "w").write(f"# Kiểm tra gói đăng – {'ĐẠT ✅' if ok else 'TRẢ VỀ ❌'}\n\n| Hạng mục | KQ | Khâu | Chi tiết |\n|---|---|---|---|\n" + "".join(f"| {r['name']} | {'✅' if r['ok'] else '❌'} | {r['stage']} | {r['detail']} |\n" for r in R))
    return ok, R
if __name__ == "__main__":
    if sys.argv[1] == "--check": ok, R = check(sys.argv[2])
    else: ok, R = export(*sys.argv[1:4])
    print(open(os.path.join(sys.argv[-1], "package_qc.md")).read()); sys.exit(0 if ok else 1)
