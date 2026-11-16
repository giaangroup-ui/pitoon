#!/usr/bin/env python3
"""PiToon Studio runner – 10 khâu + Tổng kiểm duyệt có vòng trả về. KHÔNG BAO GIỜ tự đăng.
Usage:
  studio_runner.py check FILM_DIR [--film F] [--publish]   QC phim (qc.py) -> trả về đúng khâu / đóng gói (export.py) -> Chờ chủ duyệt
  studio_runner.py script FILM_DIR [--publish]             chỉ khâu 1–2 (safety_check) cho kịch bản mới
  studio_runner.py set FILM_DIR STAGE STATE [ghi chú]       trợ lý cập nhật khâu 3–5 (tạo hình/video) – STATE: cho|dang_lam|dat|tra_ve
  studio_runner.py approve FILM_DIR                         chủ đã duyệt (chỉ đổi trạng thái, KHÔNG đăng)
  studio_runner.py publish                                  đẩy studio/status.json lên web (chỉ file này)
FILM_DIR chứa scene.json (+ studio.json do runner ghi: số vòng từng khâu, lịch sử).
Trạng thái khâu: cho (chờ), dang_lam, dat, tra_ve (kèm vòng n/4), can_chu_xem (quá 4 vòng)."""
import json, os, subprocess as sp, sys, time
H = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(H); REPO = os.path.dirname(TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "studio")); sys.path.insert(0, TOOLS); sys.path.insert(0, H)
from stages import STAGES, NAME, MAX_ROUNDS
STATUS = os.environ.get("PITOON_STATUS", os.path.join(REPO, "studio", "status.json"))
now = lambda: time.strftime("%Y-%m-%dT%H:%M:%S+07:00")
def load_state(d):
    p = os.path.join(d, "studio.json")
    if os.path.exists(p): return json.load(open(p))
    return {"rounds": {str(n): 0 for n, *_ in STAGES}, "stages": {str(n): {"state": "cho", "note": ""} for n, *_ in STAGES}, "history": []}
def save_state(d, st, cfg):
    st["updated"] = now(); json.dump(st, open(os.path.join(d, "studio.json"), "w"), ensure_ascii=False, indent=1); board_update(d, st, cfg)
def setst(st, n, state, note=""):
    st["stages"][str(n)] = {"state": state, "note": note[:180], "round": st["rounds"][str(n)]}
    st["history"].append([now(), n, state, note[:180]])
def reject(st, n, note):
    """Tổng kiểm duyệt trả về khâu n. Quá MAX_ROUNDS -> cần chủ xem."""
    st["rounds"][str(n)] += 1; r = st["rounds"][str(n)]
    setst(st, n, "can_chu_xem" if r > MAX_ROUNDS else "tra_ve", f"Lần {min(r, MAX_ROUNDS)}/{MAX_ROUNDS}: {note}" if r <= MAX_ROUNDS else f"Đã trả về {MAX_ROUNDS} lần – cần chủ xem: {note}")
    return r > MAX_ROUNDS
def summary(st):
    s = [st["stages"][str(n)]["state"] for n, *_ in STAGES]
    if "can_chu_xem" in s: return "can_chu_xem"
    if st.get("approved"): return "chu_da_duyet"
    if s[9] == "dat": return "cho_chu_duyet"
    if "tra_ve" in s: return "tra_ve"
    if "dang_lam" in s or "dat" in s: return "dang_lam"
    return "cho"
def board_update(d, st, cfg):
    """Ghi bảng công khai studio/status.json – chỉ tên phim, khâu, trạng thái, ghi chú kỹ thuật. Không key, không đường dẫn máy, không thông tin bé."""
    B = json.load(open(STATUS)) if os.path.exists(STATUS) else {"films": []}
    fid = st.get("id") or os.path.basename(os.path.abspath(d)); st["id"] = fid
    f = {"id": fid, "title": cfg.get("title", fid), "lesson": cfg.get("lesson", ""), "updated": st["updated"], "overall": summary(st),
         "qc": st.get("qc", {}), "outputs": st.get("outputs", []),
         "stages": [{"n": n, "name": name, **st["stages"][str(n)], "round": st["rounds"][str(n)]} for n, _, name, _ in STAGES]}
    B["films"] = [x for x in B["films"] if x["id"] != fid] + [f]; B["films"].sort(key=lambda x: x["updated"], reverse=True)
    B.update(updated=now(), max_rounds=MAX_ROUNDS, note="Không bao giờ tự đăng: bản đạt chờ chủ duyệt.")
    os.makedirs(os.path.dirname(STATUS), exist_ok=True); json.dump(B, open(STATUS, "w"), ensure_ascii=False, indent=1)
def script_fails(cfg):
    from safety_check import check as safety
    iss = safety(cfg); s1 = [x for x in iss if x.startswith(("[lời thoại dài]", "[bài học]"))]; s2 = [x for x in iss if x not in s1]
    f = {}
    if s1: f[1] = ["Kịch bản: " + "; ".join(s1[:2])]
    if s2: f[2] = ["Luật cấm: " + "; ".join(s2[:2])]
    return f
def stage_script(d, st, cfg):
    f = script_fails(cfg)
    for n, ok_note in ((1, f'{len(cfg.get("lines", []))} câu, có bài học'), (2, "0 lỗi luật cấm (máy) – AI đọc lại theo brief 02")):
        reject(st, n, "; ".join(f[n])) if n in f else setst(st, n, "dat", ok_note)
    return not f
def check(d, film=None):
    d = os.path.abspath(d); film = os.path.abspath(film) if film else None
    sc = os.path.join(d, "scene.json"); cfg = json.load(open(sc)); st = load_state(d)
    film = film or os.path.join(d, cfg.get("out", "film.mp4"))
    setst(st, 10, "dang_lam", "Đang chấm phim…"); save_state(d, st, cfg)
    qj = os.path.join(d, "qc.json")
    sp.run([sys.executable, os.path.join(TOOLS, "studio", "qc.py"), sc, film, "--report", os.path.join(d, "qc.md"), "--json", qj, "--grid-dir", d], cwd=d)
    q = json.load(open(qj)); fails = script_fails(cfg)   # mỗi khâu tối đa 1 vòng trả về cho mỗi lần chấm
    for it in q["items"]:
        if not it["ok"]: fails.setdefault(it["stage"], []).append(it["name"] + (f" ({it['detail'][:70]})" if it["detail"] else ""))
    ok_items = sum(i["ok"] for i in q["items"])
    st["qc"] = {"passed": ok_items, "total": len(q["items"]), "motion": q["measured"].get("motion_film"), "static_pct": q["measured"].get("static_pct"), "sfx_per_s": q["measured"].get("sfx_per_s")}
    flagged = False
    for n, *_ in STAGES[:8]:
        if n in fails: flagged |= reject(st, n, "; ".join(fails[n]))
        elif st["stages"][str(n)]["state"] in ("cho", "dang_lam", "tra_ve"): setst(st, n, "dat", "Đạt các hạng mục QC của khâu")
    if fails:
        setst(st, 9, "cho", "Chờ phim đạt mới đóng gói")
        setst(st, 10, "can_chu_xem" if flagged else "tra_ve", f"{len(q['items']) - ok_items} hạng mục chưa đạt → trả về khâu " + ", ".join(map(str, sorted(fails))))
        save_state(d, st, cfg); return False
    # 9 – đóng gói (chỉ khi phim đạt)
    setst(st, 9, "dang_lam", "Đang xuất 9:16, 16:9, phụ đề, ảnh bìa"); save_state(d, st, cfg)
    out = os.path.join(d, "export_pkg"); sp.run([sys.executable, os.path.join(H, "export.py"), sc, film, out])
    pq = json.load(open(os.path.join(out, "package_qc.json")))
    if not pq["passed"]:
        bad = [i for i in pq["items"] if not i["ok"]]
        for n in sorted({i["stage"] for i in bad}): flagged |= reject(st, n, "; ".join(i["name"] for i in bad if i["stage"] == n))
        setst(st, 10, "can_chu_xem" if flagged else "tra_ve", "Gói đăng chưa đạt"); save_state(d, st, cfg); return False
    setst(st, 9, "dat", "9:16 + 16:9, −14 LUFS, phụ đề trong vùng an toàn, 2 ảnh bìa, chú thích 6 nền tảng")
    st["outputs"] = sorted(x for x in os.listdir(out) if not x.startswith("package_qc"))
    setst(st, 10, "dat", f"Đạt {ok_items}/{len(q['items'])} hạng mục máy + gói đăng. Chờ chủ duyệt – KHÔNG tự đăng")
    save_state(d, st, cfg); return True
def publish():
    """Chỉ commit studio/status.json rồi đẩy lên. Workflow tính phiên bản app không tính thư mục studio/, nên app của khách không bị tải lại."""
    rel = os.path.relpath(STATUS, REPO); g = lambda *a: sp.run(["git", "-C", REPO, *a], capture_output=True, text=True)
    g("add", rel)
    if g("diff", "--cached", "--quiet", "--", rel).returncode == 0: print("status.json không đổi"); return
    print(g("commit", "-m", "Xưởng phim: cập nhật bảng khâu", "--", rel).stdout)
    print(g("pull", "--rebase", "--autostash").stderr[-300:]); r = g("push"); print(r.stdout, r.stderr[-300:])
if __name__ == "__main__":
    a = sys.argv[1:]; pub = "--publish" in a; a = [x for x in a if x != "--publish"]
    film = a[a.index("--film") + 1] if "--film" in a else None
    if film: a.remove("--film"); a.remove(film)
    c = a[0]; ok = True
    if c == "check": ok = check(a[1], film); print("ĐẠT – chờ chủ duyệt" if ok else "TRẢ VỀ – xem qc.md / studio.json")
    elif c == "script":
        d = a[1]; cfg = json.load(open(os.path.join(d, "scene.json"))); st = load_state(d); ok = stage_script(d, st, cfg); save_state(d, st, cfg)
    elif c == "set":
        d, n, state = a[1], int(a[2]), a[3]; cfg = json.load(open(os.path.join(d, "scene.json"))); st = load_state(d)
        (reject(st, n, " ".join(a[4:])) if state == "tra_ve" else setst(st, n, state, " ".join(a[4:]))); save_state(d, st, cfg)
    elif c == "approve":
        d = a[1]; cfg = json.load(open(os.path.join(d, "scene.json"))); st = load_state(d); st["approved"] = now(); save_state(d, st, cfg)
    if pub or c == "publish": publish()
    sys.exit(0 if ok else 1)
