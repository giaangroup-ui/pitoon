#!/usr/bin/env python3
"""Shot queue + stage QC (JSON file). Stages: script>design>shot>voice>sfx>edit>qc>export>draft.
Mỗi shot: pending -> generated -> qc_pass | qc_fail(retry<=4) -> rejected(cần người).
Usage: queue.py add EP.json | next | mark SHOT STATE [note] | status"""
import json, os, sys, time
Q = os.environ.get("PITOON_QUEUE", os.path.join(os.path.dirname(__file__), "queue.json")); MAXR = 4
def load(): return json.load(open(Q)) if os.path.exists(Q) else {"shots": []}
def save(q): json.dump(q, open(Q, "w"), ensure_ascii=False, indent=1)
def add(ep):
    e = json.load(open(ep)); q = load()
    for k in range(e.get("shots_5s", 60)):
        q["shots"].append({"id": f'{e["id"]}_s{k+1:03d}', "ep": e["id"], "state": "pending", "tries": 0, "log": []})
    save(q)
def nxt():
    for s in load()["shots"]:
        if s["state"] in ("pending", "qc_fail"): return s
def mark(sid, st, note=""):
    q = load()
    for s in q["shots"]:
        if s["id"] == sid:
            if st == "qc_fail": s["tries"] += 1; st = "rejected" if s["tries"] >= MAXR else st
            s["state"] = st; s["log"].append([time.strftime("%F %T"), st, note])
    save(q)
def status():
    from collections import Counter; return Counter(s["state"] for s in load()["shots"])
if __name__ == "__main__":
    c, *a = sys.argv[1:]
    print({"add": lambda: add(*a), "next": nxt, "mark": lambda: mark(*a), "status": status}[c]())
