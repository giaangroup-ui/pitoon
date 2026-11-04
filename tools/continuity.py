#!/usr/bin/env python3
"""Consistency + continuity for PiToon (uses tools/bible/bible.json).
scene.json 'shots': [{id, from, to, set, chars:[...], action, lines_in_shot?,
   continuity: {start: {prop: holder}, end: {prop: holder}}}]   holder = character id | "stool" | "ground" ...
- check(cfg)         -> continuity problems (end of shot i must equal start of shot i+1; unique props held once)
- plan(cfg, dir)     -> per-shot GenerateImage/GenerateVideo calls with locked descriptions + reference images.
  Shot 1 starts from a keyframe built from the references; every next shot starts from the LAST FRAME of the
  previous clip (image-to-video), so characters/props/set carry over exactly.
CLI: python3 continuity.py scene.json [--plan] | python3 continuity.py scene.json --lastframe clip.mp4 out.png"""
import json, os, sys, subprocess as sp
HERE = os.path.dirname(os.path.abspath(__file__)); BIB = os.path.join(HERE, "bible")
def bible(): return json.load(open(os.path.join(BIB, "bible.json")))

def check(cfg):
    b = bible(); out = []; shots = cfg.get("shots", [])
    for i, s in enumerate(shots):
        c = s.get("continuity", {})
        for ph in ("start", "end"):
            st = c.get(ph, {})
            for prop, holder in st.items():
                if prop not in b["props"]: out.append(f"[{s['id']}] prop lạ '{prop}' – thêm vào bible.json")
                if holder in b["characters"] and holder not in s.get("chars", []): out.append(f"[{s['id']}] {ph}: {prop} ở {holder} nhưng {holder} không có trong shot")
        if i and shots[i - 1].get("continuity", {}).get("end") != c.get("start"):
            out.append(f"[{shots[i-1]['id']}→{s['id']}] trạng thái không nối: end={shots[i-1].get('continuity',{}).get('end')} start={c.get('start')}")
        for ch in s.get("chars", []):
            if ch not in b["characters"]: out.append(f"[{s['id']}] nhân vật '{ch}' chưa có trong bible.json")
        if s.get("set") not in b["sets"]: out.append(f"[{s['id']}] bối cảnh '{s.get('set')}' chưa có trong bible.json")
    return out

def _state_text(b, st):
    t = []
    for prop, holder in st.items():
        p = b["props"][prop]
        if holder in b["characters"]: t.append(f"{b['characters'][holder]['locked'].split(':')[0]} is wearing/holding {p['locked']}")
        else: t.append(f"{p['locked']} is on the {holder}")
        if p.get("unique"):
            for cid, ch in b["characters"].items():
                if cid != holder and "when_no_hat" in ch and p.get("wearable"): t.append(f"{ch['locked'].split(':')[0]} is {ch['when_no_hat']}")
    return "; ".join(t)

def plan(cfg, d, safe_suffix="", style_extra=""):
    b = bible(); calls = []
    for i, s in enumerate(cfg["shots"]):
        refs = [os.path.join(BIB, b["characters"][c]["ref"]) for c in s["chars"]] + [os.path.join(BIB, b["sets"][s["set"]]["ref"])]
        cast = " ".join(f"<IMAGE_{k+1}> is the model sheet of {b['characters'][c]['locked']}." for k, c in enumerate(s["chars"]))
        setd = f"<IMAGE_{len(s['chars'])+1}> is the set: {b['sets'][s['set']]['locked']}."
        c = s.get("continuity", {}); start, end = _state_text(b, c.get("start", {})), _state_text(b, c.get("end", {}))
        lines = " ".join(f'{l["who"]} says clearly with big mouth movements: "{l["text"]}".' for l in cfg.get("lines", []) if s["from"] <= l["win"][0] < s["to"])
        vp = (f"{b['style']}. {style_extra} <IMAGE_0> is the first frame. {cast} {setd} Keep every character EXACTLY as on its model sheet "
              f"(same face, colours, outfit) and the set exactly as the plate. START STATE: {start}. Action: {s['action']}. {lines} "
              f"END STATE (must be true in the last frame): {end}. There is only one of each unique prop. {safe_suffix}")
        call = {"shot": s["id"], "duration": round(s["to"] - s["from"]), "video_prompt": " ".join(vp.split()),
                "reference_image_paths": refs, "clip": os.path.join(d, f"shot_{s['id']}.mp4")}
        if i == 0:
            call["keyframe"] = {"description": " ".join(f"{b['style']}. Film still, 16:9, wide eye-level shot. Characters must match the model sheets exactly: "
                f"{'; '.join(b['characters'][c]['locked'] for c in s['chars'])}. Set exactly as the plate: {b['sets'][s['set']]['locked']}. STATE: {start}. {s.get('key_pose','')}".split()),
                "reference_image_paths": refs, "out": os.path.join(d, f"key_{s['id']}.png")}
            call["image_path"] = call["keyframe"]["out"]
        else:
            call["image_path"] = os.path.join(d, f"last_{cfg['shots'][i-1]['id']}.png")
        calls.append(call)
    return calls

def lastframe(clip, out):
    sp.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i", clip, "-frames:v", "1", "-update", "1", out], check=True)

if __name__ == "__main__":
    if "--lastframe" in sys.argv: i = sys.argv.index("--lastframe"); lastframe(sys.argv[i + 1], sys.argv[i + 2]); sys.exit()
    p = sys.argv[1]; cfg = json.load(open(p)); iss = check(cfg)
    print("\n".join(iss) if iss else "✅ Liên tục: trạng thái đạo cụ nối khớp giữa các shot")
    if "--plan" in sys.argv: print(json.dumps(plan(cfg, os.path.dirname(os.path.abspath(p))), ensure_ascii=False, indent=1))
    sys.exit(1 if iss else 0)
