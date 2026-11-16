#!/usr/bin/env python3
"""Pad each scene to script length (subtle zoom hold, not a hard freeze),
mux prepared mix, burn Vietnamese subtitles, wrap intro/title/outro,
export 16:9 master + contact sheet, then run studio qc.py."""
import json, os, shutil, subprocess as sp, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / "scene.json").read_text())
EXPORT = ROOT / "export"
EXPORT.mkdir(exist_ok=True)
REF = Path("/workspace/ref/pitoon_free")
REF.mkdir(parents=True, exist_ok=True)
OUT = REF / "thao_sisters_16x9.mp4"
SHEET = REF / "thao_sisters_16x9_sheet.jpg"
FPS = 24
W, H = 1920, 1080
INTRO_D, TITLE_D, OUTRO_D = 3.6, 2.8, 4.0
PRE = INTRO_D + TITLE_D  # 6.4
FONT = "/usr/share/fonts/truetype/sand-box/google/Be Vietnam Pro/BeVietnamPro-Bold.ttf"
VF_NORM = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1,format=yuv420p"

def run(cmd, **kw):
    r = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, text=True, **kw)
    if r.returncode:
        sys.stderr.write(r.stderr[-4000:] + "\n")
        raise SystemExit(f"cmd failed: {cmd[:6]}...")
    return r

def dur_of(p):
    return float(sp.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(p)
    ]).decode().strip())

def pad_shot(src, dst, want):
    dst = Path(dst)
    tmp = dst.with_name(dst.stem + "_raw.mp4")
    have = dur_of(src)
    take = min(have, want)
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-map", "0:v:0",
         "-vf", VF_NORM, "-an", "-t", f"{take:.3f}",
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", str(tmp)])
    got = dur_of(tmp)
    if got >= want - 0.04:
        # trim exactly
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(tmp), "-t", f"{want:.3f}",
             "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an", str(dst)])
        tmp.unlink(missing_ok=True)
        return
    remain = want - got
    last = dst.with_name(dst.stem + "_last.png")
    run(["ffmpeg", "-loglevel", "error", "-y", "-sseof", "-0.2", "-i", str(tmp),
         "-map", "0:v:0", "-frames:v", "1", "-update", "1", str(last)])
    pad = dst.with_name(dst.stem + "_pad.mp4")
    # Slow breathing zoom + tiny pan so freezedetect does not trip, still feels like a hold.
    zf = (
        f"scale={W}:{H},zoompan=z='min(1.07,1+0.0007*on)':"
        f"x='iw/2-(iw/zoom/2)+6*sin(on/45)':y='ih/2-(ih/zoom/2)+4*sin(on/60)':"
        f"d=1:s={W}x{H}:fps={FPS},format=yuv420p"
    )
    run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-i", str(last),
         "-vf", zf, "-t", f"{remain:.3f}", "-an",
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", str(pad)])
    lst = dst.with_name(dst.stem + "_concat.txt")
    lst.write_text(f"file '{tmp.resolve()}'\nfile '{pad.resolve()}'\n")
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an", "-t", f"{want:.3f}",
         "-pix_fmt", "yuv420p", str(dst)])
    for p in (tmp, pad, last, lst):
        Path(p).unlink(missing_ok=True)

def write_ass(path, lines, offset=0.0):
    def ts(t):
        t = max(0, t)
        h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
        return f"{h:d}:{m:02d}:{s:05.2f}"
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Be Vietnam Pro,54,&H00FFFFFF,&H000000FF,&H802B1A00,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,80,80,64,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for l in lines:
        a, b = l["win"]
        text = l["text"].replace("\n", "\\N").replace("{", "\\{")
        who = l.get("who") or ""
        # slight color cue: narrator vs dialogue stays white; keep one style for kids
        ev.append(f"Dialogue: 0,{ts(a+offset)},{ts(b+offset)},Default,{who},0,0,0,,{text}")
    path.write_text(header + "\n".join(ev) + "\n", encoding="utf-8")

def normalize_card(src, dst, t):
    # keep card audio, normalize picture to 24fps 1920x1080
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-map", "0:v:0", "-map", "0:a:0?",
         "-vf", VF_NORM, "-t", f"{t:.3f}",
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "160k", str(dst)])

def main():
    shots = CFG["shots"]
    parts = []
    XF = float(CFG.get("transition_s", 0.35))
    for idx, s in enumerate(shots):
        src = ROOT / s["video"]
        if not src.exists():
            raise SystemExit(f"missing {src}")
        want = float(s["to"]) - float(s["from"]) + (XF if idx < len(shots) - 1 else 0)
        n = EXPORT / f"{s['id']}_n.mp4"
        print(f"pad {s['id']} {want:.2f}s from {src}")
        pad_shot(src, n, want)
        print(f"  -> {dur_of(n):.2f}s")
        parts.append(n)

    body = EXPORT / "body.mp4"
    cmd = ["ffmpeg", "-loglevel", "error", "-y"]
    for p_ in parts: cmd += ["-i", str(p_)]
    fc = []; last = "0:v"; acc = 0.0
    for i in range(1, len(parts)):
        acc += float(shots[i-1]["to"]) - float(shots[i-1]["from"])
        fc.append(f"[{last}][{i}:v]xfade=transition=fade:duration={XF}:offset={acc:.3f}[x{i}]")
        last = f"x{i}"
    cmd += ["-filter_complex", ";".join(fc), "-map", f"[{last}]", "-r", str(FPS),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", str(body)]
    run(cmd)
    body_d = dur_of(body)
    print("body", body_d)

    mix = EXPORT / "_mix_v2.wav"
    if not mix.exists():
        mix = ROOT / "audio" / "_mix_preview.mp3"
    body_a = EXPORT / "body_a.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(body), "-i", str(mix),
         "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
         "-t", f"{body_d:.3f}", str(body_a)])
    print("body+audio", body_a, dur_of(body_a))

    ass = EXPORT / "body.ass"
    write_ass(ass, CFG["lines"], offset=0)
    # fontsdir so libass finds Be Vietnam Pro
    fontdir = str(Path(FONT).parent)
    body_s = EXPORT / "body_subs.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(body_a),
         "-vf", f"ass={ass}:fontsdir={fontdir}",
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "copy", str(body_s)])
    print("subs", body_s)

    intro_n = EXPORT / "intro_n.mp4"
    title_n = EXPORT / "title_n.mp4"
    outro_n = EXPORT / "outro_n.mp4"
    normalize_card(EXPORT / "intro_16x9.mp4", intro_n, INTRO_D)
    normalize_card(EXPORT / "title_16x9.mp4", title_n, TITLE_D)
    normalize_card(EXPORT / "outro_16x9.mp4", outro_n, OUTRO_D)

    flist = EXPORT / "final.txt"
    flist.write_text(
        f"file '{intro_n.resolve()}'\nfile '{title_n.resolve()}'\n"
        f"file '{body_s.resolve()}'\nfile '{outro_n.resolve()}'\n"
    )
    # re-encode concat to avoid timestamp issues across fps/audio
    tmpf = EXPORT / "final_tmp.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(flist),
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
         "-movflags", "+faststart", str(tmpf)])
    shutil.copy(tmpf, EXPORT / "thao_sisters_16x9.mp4")
    shutil.copy(tmpf, OUT)
    print("FINAL", OUT, dur_of(OUT))

    # contact sheet: 12 mid-scene frames (4x3) from the final film (offset by PRE)
    ins = []
    for s in shots:
        mid = PRE + (float(s["from"]) + float(s["to"])) / 2
        png = EXPORT / f"sheet_{s['id']}.png"
        run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{mid:.2f}", "-i", str(OUT),
             "-frames:v", "1", "-update", "1", str(png)])
        ins.append(png)
    cmd = ["ffmpeg", "-y"]
    for p in ins:
        cmd += ["-i", str(p)]
    filt = ";".join(f"[{i}:v]scale=480:270,setsar=1,drawtext=fontfile={FONT}:text='{shots[i]['id']}':"
                    f"x=16:y=16:fontsize=28:fontcolor=white:borderw=3:bordercolor=0x1e2a4a[s{i}]"
                    for i in range(12))
    for r in range(4):
        filt += ";" + "".join(f"[s{r*3+c}]" for c in range(3)) + f"hstack=3[r{r}]"
    filt += ";[r0][r1][r2][r3]vstack=4,format=yuv420p,pad=iw+16:ih+16:8:8:0x1e2a4a"
    cmd += ["-filter_complex", filt, "-frames:v", "1", "-update", "1", "-q:v", "3", str(SHEET)]
    run(cmd)
    print("sheet", SHEET, SHEET.stat().st_size)

    # qc config with timestamps shifted by intro+title, stems next to it
    qcfg = json.loads(json.dumps(CFG))
    qcfg["qc"] = dict(CFG.get("qc") or {})
    qcfg["qc"]["length"] = [188, 198]
    qcfg["qc"]["freeze_d"] = 3.0
    qcfg["qc"]["max_line_words"] = 32   # Vietnamese: 1 syllable = 1 "word"
    qcfg["qc"]["continuity"] = False    # film has its own bible/bible.json
    qcfg["qc"]["speech_film"] = str(body_a)
    qcfg["qc"]["speech_offset"] = PRE
    for s in qcfg["shots"]:
        s["from"] = float(s["from"]) + PRE
        s["to"] = float(s["to"]) + PRE
    for l in qcfg["lines"]:
        l["win"] = [l["win"][0] + PRE, l["win"][1] + PRE]
    qpath = EXPORT / "qc_scene.json"
    qpath.write_text(json.dumps(qcfg, ensure_ascii=False, indent=2))
    # stems expected beside scene.json — copy next to export qc? qc uses dirname(cfg)
    for name in ("_stem_music.wav", "_stem_fx.wav", "_stem_voice.wav"):
        src = ROOT / "audio" / name
        dst = EXPORT / name
        if src.exists() and not dst.exists():
            shutil.copy(src, dst)

    qc = Path("/workspace/pitoon/tools/studio/qc.py")
    report = REF / "thao_sisters_qc.md"
    cmd = ["python3", str(qc), str(qpath), str(OUT), "--report", str(report), "--grid-dir", str(EXPORT / "qc")]
    (EXPORT / "qc").mkdir(exist_ok=True)
    print("running qc...")
    r = sp.run(cmd, cwd=str(EXPORT))
    print("qc exit", r.returncode)
    return r.returncode

if __name__ == "__main__":
    sys.exit(main() or 0)
