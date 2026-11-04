#!/usr/bin/env python3
"""Child-safety check for PiToon scenes (ages 3-10). See HUONG_DAN_NOI_DUNG.md.
Usage: python3 safety_check.py scene.json  -> exit 1 if risky content is found."""
import json, re, sys, unicodedata
RULES = {
 "trèo chỗ cao": r"trèo|leo lên|đứng lên (ghế|chum|bàn)|mái nhà|lan can|nhảy lên (chum|vại|ghế|bàn)|climb|on(to)? (a |the )?(jar|roof|chair|table|ledge)|jump(s|ing)? onto|balanc\w+ on",
 "ngã / đập đầu": r"ngã|té|đập đầu|choáng|sao quay|rơi từ|\bfall(s|ing)?\b|falls? (flat|over)|tumbl|hit(s)? (his|her|the) head|stars? (spin|over|around)|dizzy|knocked out|faceplant",
 "đánh người": r"đánh|đá vào|đấm|đẩy ngã|ném vào|cắn|\bhit(s|ting)? \w+|punch|kick|slap|shove|bite",
 "lửa": r"lửa|diêm|bật lửa|nến|pháo|\bfire\b|flame|match(es)?\b|lighter|candle|firework",
 "điện": r"ổ cắm|dây điện|cột điện|electric|socket|power line|wire",
 "nước sâu": r"ao\b|hồ\b|sông|giếng|chum nước|lặn|đuối|\bpond|river|lake|\bwell\b|deep water|drown|swim",
 "vật sắc nhọn": r"dao|kéo|kim\b|mảnh vỡ|que nhọn|knife|scissors|needle|sharp|broken glass|shard",
 "ăn vật lạ": r"ăn (đất|lá lạ|nấm|thuốc|sỏi)|nuốt|ngậm (đồ|viên)|eat(s|ing)? (dirt|mushroom|pill|berr)|swallow",
 "hỗn với người lớn": r"lè lưỡi|đồ ngốc|ngu|im đi|cãi (bà|ông|mẹ|bố)|stupid|shut up|stick(s)? (out )?tongue",
}
def scan_text(t):
    return [(k, m.group(0)) for k, r in RULES.items() for m in [re.search(r, t, re.I)] if m]
def check(cfg):
    issues = []
    def walk(x, path):
        if isinstance(x, str):
            if path.split(".")[-1] in ("video", "out", "name", "src", "voice", "mood", "emo"): return
            for k, w in scan_text(unicodedata.normalize("NFC", x)): issues.append(f"[{k}] '{w}' trong {path}: {x[:80]}")
        elif isinstance(x, dict): [walk(v, f"{path}.{k}") for k, v in x.items()]
        elif isinstance(x, list): [walk(v, f"{path}[{i}]") for i, v in enumerate(x)]
    walk(cfg, "scene")
    if not cfg.get("lesson"): issues.append("[bài học] thiếu 'lesson' – mỗi tập phải kết bằng một bài học dễ hiểu")
    for i, l in enumerate(cfg.get("lines", [])):
        if len(l.get("text", "").split()) > 12: issues.append(f"[lời thoại dài] lines[{i}] > 12 từ – nói ngắn cho bé dễ hiểu")
    return issues
if __name__ == "__main__":
    iss = check(json.load(open(sys.argv[1])))
    print("\n".join(iss) if iss else "✅ An toàn: không phát hiện hành động nguy hiểm"); sys.exit(1 if iss else 0)
