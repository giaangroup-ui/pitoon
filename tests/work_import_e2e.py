#!/usr/bin/env python3
"""E2E: cổng Nạp nguyên tác phẩm — dán chữ, file .docx, pipeline các khâu AI."""
from __future__ import annotations

import http.server
import json
import os
import socketserver
import sys
import threading
import base64
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
STORY = (ROOT / "tests/sample_story.txt").read_text(encoding="utf-8")
DOCX = ROOT / "tests/sample_story.docx"
ADS = Path(os.environ.get("ADS_DIR", "/workspace/ref/pitoon_free/ads"))
PORT = int(os.environ.get("PORT", "8765"))
BASE = f"http://127.0.0.1:{PORT}/pitoon/"
TINY = Path("/tmp/pitoon-work/tiny.mp4")

MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json",
    ".webmanifest": "application/manifest+json",
    ".png": "image/png",
    ".webp": "image/webp",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".ico": "image/x-icon",
    ".mp3": "audio/mpeg",
    ".mp4": "video/mp4",
    ".wasm": "application/wasm",
    ".svg": "image/svg+xml",
    ".woff2": "font/woff2",
}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        raw = self.path.split("?", 1)[0]
        if raw.startswith("/pitoon"):
            self.path = raw[len("/pitoon"):] or "/"
        return super().do_GET()

    def guess_type(self, path):
        ext = Path(path).suffix.lower()
        if ext in MIME:
            return MIME[ext]
        return super().guess_type(path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def start_server(port=0):
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def boot(page):
    page.add_init_script(
        """
        try { sessionStorage.setItem("pt_intro_skip", "1"); } catch (e) {}
        try {
          localStorage.setItem("pt_llm", "pollinations");
          localStorage.setItem("pt_imgp", "demo");
          localStorage.setItem("pt_vprov", "kenburns");
          localStorage.setItem("pt_ttsp", "mms");
          localStorage.setItem("pt_res", "854");
          localStorage.setItem("pt_lang", "vi");
        } catch (e) {}
        """
    )
    page.goto(BASE, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_selector("#workGate", timeout=20000)
    page.evaluate(
        """() => {
          const b = document.getElementById("installBanner");
          if (b) b.hidden = true;
          const intro = document.getElementById("pt-intro");
          if (intro) { intro.style.display = "none"; intro.setAttribute("hidden", ""); }
          window.llm = async () => { throw new Error("test-heuristic"); };
          try {
            localStorage.setItem("pt_imgp", "demo");
            localStorage.setItem("pt_vprov", "kenburns");
            localStorage.setItem("pt_ttsp", "mms");
          } catch (e) {}
        }"""
    )
    img_p = page.evaluate("() => (typeof IMGP==='function'?IMGP():'?') + ' v=' + (localStorage.pt_vprov||'') + ' llm=' + (typeof llm)")
    print("providers", img_p)


def stub_heavy(page):
    """Install stubs in a page <script> so they can see `let P` (not on window)."""
    b64 = base64.b64encode(TINY.read_bytes()).decode("ascii")
    page.evaluate(
        """(b64) => {
          const s = document.createElement("script");
          s.textContent = `
            (function (b64) {
              const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
              const filmBlob = new Blob([bin], { type: "video/mp4" });
              window.assemble = async function (opts) {
                opts = opts || {};
                if (typeof opts.onStatus === "function") opts.onStatus("ffmpeg… test stub");
                await setB("film_" + P.id, filmBlob);
                P.film = "film_" + P.id;
                save();
                if (typeof opts.onStatus === "function") opts.onStatus("Xong");
              };
              window.genVoice = async function (sh) {
                const d = Math.max(1, sh.dur || 6);
                const sr = 22050, n = Math.max(1, Math.floor(sr * Math.min(d, 2)));
                const ctx = new OfflineAudioContext(1, n, sr);
                const buf = await ctx.startRendering();
                const wavBlob = wav(buf);
                await setB("a_" + sh.id, wavBlob);
                sh.aud = "a_" + sh.id;
                sh.adur = d;
                save();
              };
            })(${JSON.stringify(b64)});
          `;
          document.documentElement.appendChild(s);
          s.remove();
        }""",
        b64,
    )


def analyze_paste(page):
    page.locator("#workRaw").fill(STORY)
    page.locator("#bAnalyze").click()
    page.wait_for_selector("#workReview", timeout=20000)


def must(cond, msg):
    if not cond:
        raise AssertionError(msg)


results = []


def passed(name, detail=""):
    results.append((name, True, detail))
    print("PASS", name, detail)


def failed(name, err):
    results.append((name, False, str(err)))
    print("FAIL", name, err, file=sys.stderr)


def main():
    ADS.mkdir(parents=True, exist_ok=True)
    httpd = start_server()
    global BASE
    host, port = httpd.server_address
    BASE = f"http://127.0.0.1:{port}/pitoon/"
    print("serving", BASE)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                # Phone paste + review
                phone = browser.new_context(
                    viewport={"width": 390, "height": 844},
                    device_scale_factor=2,
                    is_mobile=True,
                    has_touch=True,
                    locale="vi-VN",
                )
                p = phone.new_page()
                p.set_default_timeout(30000)
                boot(p)
                gate = p.locator("#workGate h2").inner_text()
                must("Nạp nguyên tác phẩm" in gate, f"missing gate: {gate}")
                must(p.locator("#importGate").count() == 1, "existing import gate missing")
                must(p.locator("#installBtn").count() == 1, "install button missing")
                analyze_paste(p)
                title = p.locator("#workReview input").first.input_value()
                must("hộp màu của bạn Mây" in title, f"title not extracted: {title}")
                agents = p.locator("#workReview h3").all_inner_texts()
                need = [
                    "AI Biên kịch",
                    "AI Nhân vật",
                    "AI Bối cảnh",
                    "AI Phân cảnh",
                    "AI Lồng tiếng",
                    "AI Âm thanh",
                    "AI Dựng",
                    "AI Kiểm duyệt",
                    "Xuất phim",
                ]
                joined = " | ".join(agents)
                for a in need:
                    must(any(a in t for t in agents), f"missing agent section: {a} in {joined}")
                scene_heads = p.locator("#workReview b").evaluate_all(
                    "els => els.filter(e => /^Cảnh \\d/.test(e.textContent||'')).length"
                )
                must(scene_heads == 5, f"expected 5 scenes, got {scene_heads}")
                body = p.locator("#workReview").inner_text()
                must("Bạn Mây" in body and "Bạn Tí" in body and "Bà Năm" in body, "characters missing")
                must("Giao cho các AI làm phim" in body, "run button missing")
                must("Gửi lên xưởng phim chuẩn" in body, "studio button missing")
                must("Phim hoạt hình thật" in body, "honesty note missing")
                p.locator("#workReview").scroll_into_view_if_needed()
                p.screenshot(path=str(ADS / "work_review_phone.png"), full_page=False)
                p.locator("#workFlow").scroll_into_view_if_needed()
                p.locator("#workReview").screenshot(path=str(ADS / "work_review_phone_card.png"))
                passed("phone-paste-review", f"{title} · {scene_heads} scenes")

                # Pipeline
                stub_heavy(p)
                print("busy/imgp", p.evaluate("() => ({BUSY, img: typeof IMGP==='function'?IMGP():null, film: !!(P&&P.film), shots: (P&&P.shots||[]).length, chars: (P&&P.chars||[]).length})"))
                btn = p.locator("#bRunWork")
                print("run btn", btn.count(), btn.is_enabled() if btn.count() else None, btn.get_attribute("disabled") if btn.count() else None)
                p.locator("#bRunWork").click()
                try:
                    p.wait_for_selector("#workDone", timeout=60000)
                except Exception:
                    print("PIPE ST", p.locator("#workPipeSt").inner_text() if p.locator("#workPipeSt").count() else "no")
                    print("LOG", p.locator("#log").inner_text() if p.locator("#log").count() else "no")
                    print("PILLS", p.locator(".work-st").evaluate_all("""els => els.map(el => el.getAttribute('data-stage')+' '+el.className+' | '+(el.querySelector('[data-st]')||{}).textContent+' | '+(el.querySelector('[data-nt]')||{}).textContent)"""))
                    print("BUSY", p.evaluate("() => ({BUSY, film: P&&P.film, running: P&&P.work&&P.work.running, err: window.__pipeErr || null})"))
                    p.screenshot(path=str(ADS / "work_pipeline_fail_phone.png"), full_page=False)
                    raise
                done_text = p.locator("#workDone").inner_text()
                must("xong bản nháp" in done_text.lower() or "Các AI đã xong bản nháp" in done_text, f"done banner: {done_text}")
                pills = p.locator(".work-st").evaluate_all(
                    """els => els.map(el => ({
                      id: el.getAttribute("data-stage"),
                      cls: el.className,
                      st: (el.querySelector("[data-st]")||{}).textContent,
                      note: (el.querySelector("[data-nt]")||{}).textContent
                    }))"""
                )
                not_done = [x for x in pills if x["id"] != "tong_qc" and "xong" not in (x["cls"] or "")]
                must(len(not_done) == 0, "stages not xong: " + json.dumps(not_done, ensure_ascii=False))
                qc = next((x for x in pills if x["id"] == "tong_qc"), None)
                must(qc and "xong" in (qc["cls"] or ""), "QC not passed: " + json.dumps(qc, ensure_ascii=False))
                p.locator("#workDone").scroll_into_view_if_needed()
                p.screenshot(path=str(ADS / "work_pipeline_done_phone.png"), full_page=False)
                flow = p.locator("#workFlow").bounding_box()
                done = p.locator("#workDone").bounding_box()
                if flow and done:
                    y = max(0, flow["y"] - 8)
                    h = min(844, done["y"] + done["height"] - y + 16)
                    p.screenshot(
                        path=str(ADS / "work_pipeline_done_phone_card.png"),
                        clip={"x": 0, "y": y, "width": 390, "height": h},
                    )
                passed("phone-pipeline-done", json.dumps([{k: x[k] for k in ("id", "st")} for x in pills], ensure_ascii=False))
                phone.close()

                # Desktop paste
                desk = browser.new_context(viewport={"width": 1280, "height": 800}, locale="vi-VN")
                d = desk.new_page()
                d.set_default_timeout(30000)
                boot(d)
                analyze_paste(d)
                d_title = d.locator("#workReview input").first.input_value()
                must("hộp màu của bạn Mây" in d_title, f"desktop title: {d_title}")
                d.screenshot(path=str(ADS / "work_review_desktop.png"), full_page=False)
                passed("desktop-paste-review", d_title)
                desk.close()

                # Desktop docx
                desk2 = browser.new_context(viewport={"width": 1280, "height": 800}, locale="vi-VN")
                d2 = desk2.new_page()
                d2.set_default_timeout(60000)
                boot(d2)
                d2.locator('#workDrop input[type="file"]').set_input_files(str(DOCX))
                d2.wait_for_selector("#workReview", timeout=30000)
                x_title = d2.locator("#workReview input").first.input_value()
                must("hộp màu của bạn Mây" in x_title, f"docx title: {x_title}")
                x_scenes = d2.locator("#workReview b").evaluate_all(
                    "els => els.filter(e => /^Cảnh \\d/.test(e.textContent||'')).length"
                )
                must(x_scenes == 5, f"docx scenes: {x_scenes}")
                passed("desktop-docx", f"{x_title} · {x_scenes} scenes")
                desk2.close()

                # Phone docx
                phone2 = browser.new_context(
                    viewport={"width": 390, "height": 844},
                    device_scale_factor=2,
                    is_mobile=True,
                    has_touch=True,
                    locale="vi-VN",
                )
                p2 = phone2.new_page()
                boot(p2)
                p2.locator('#workDrop input[type="file"]').set_input_files(str(DOCX))
                p2.wait_for_selector("#workReview", timeout=30000)
                p2t = p2.locator("#workReview input").first.input_value()
                must("hộp màu" in p2t, f"phone docx title: {p2t}")
                passed("phone-docx", p2t)
                phone2.close()
            finally:
                browser.close()
    finally:
        httpd.shutdown()

    print("\n==== SUMMARY ====")
    for name, ok, detail in results:
        print(("✓" if ok else "✗"), name, detail)
    bad = [r for r in results if not r[1]]
    if bad:
        print(len(bad), "failed")
        sys.exit(1)
    print("All", len(results), "checks passed")
    print("Screenshots in", ADS)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        failed("fatal", e)
        raise
