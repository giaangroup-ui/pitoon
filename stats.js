/* PiToon usage counters.
   Chỉ gửi tên sự kiện (mở app, nguồn, cài, kịch bản, phim).
   Không gửi tên, email, ảnh, cookie hay dữ liệu cá nhân. */
(function () {
  const TOPIC = "pitoon-giaangroup-ui-v1";
  const BASE = "https://tally.legible.sh/" + TOPIC + "/";
  const SOURCES = { tiktok: 1, facebook: 1, youtube: 1, zalo: 1, direct: 1 };
  const INSTALL_FLAG = "pt_installed";
  const SRC_KEY = "pt_src";
  const AU_KEY = "pt_au_reload";

  function hit(metric) {
    try {
      if (typeof navigator !== "undefined" && navigator.onLine === false) return;
      const name = String(metric || "").toLowerCase().replace(/[^a-z0-9_-]/g, "");
      if (!name) return;
      fetch(BASE + name, {
        method: "POST",
        body: "+1",
        mode: "cors",
        keepalive: true,
        cache: "no-store",
        credentials: "omit",
        referrerPolicy: "no-referrer"
      }).catch(function () {});
    } catch (e) {}
  }

  function normSource(raw) {
    const s = String(raw || "").toLowerCase().trim();
    if (!s) return "direct";
    if (s === "fb" || s === "meta" || s.indexOf("facebook") !== -1) return "facebook";
    if (s === "tt" || s.indexOf("tiktok") !== -1) return "tiktok";
    if (s === "yt" || s === "youtu" || s.indexOf("youtube") !== -1) return "youtube";
    if (s.indexOf("zalo") !== -1) return "zalo";
    if (SOURCES[s]) return s;
    return "direct";
  }

  function currentSource() {
    try {
      const u = new URL(location.href);
      const raw = u.searchParams.get("src") || u.searchParams.get("utm_source");
      if (raw) {
        const src = normSource(raw);
        try { sessionStorage.setItem(SRC_KEY, src); } catch (e) {}
        return src;
      }
      const saved = sessionStorage.getItem(SRC_KEY);
      if (saved) return normSource(saved);
    } catch (e) {}
    return "direct";
  }

  function isStandalone() {
    try {
      return (window.matchMedia && (
        window.matchMedia("(display-mode: standalone)").matches ||
        window.matchMedia("(display-mode: minimal-ui)").matches
      )) || navigator.standalone === true;
    } catch (e) { return false; }
  }

  function isUpdateReload() {
    try {
      if (sessionStorage.getItem(AU_KEY) === "1") {
        sessionStorage.removeItem(AU_KEY);
        return true;
      }
    } catch (e) {}
    return false;
  }

  function onInstalled() {
    try {
      if (!localStorage.getItem(INSTALL_FLAG)) {
        localStorage.setItem(INSTALL_FLAG, String(Date.now()));
        hit("install");
      }
    } catch (e) {}
  }

  function boot() {
    const updateReload = isUpdateReload();
    const src = currentSource();
    if (!updateReload) {
      hit("app_open");
      hit("src_" + src);
    }
    try {
      if (isStandalone() && !localStorage.getItem(INSTALL_FLAG)) {
        localStorage.setItem(INSTALL_FLAG, String(Date.now()));
        hit("install");
      }
    } catch (e) {}
  }

  window.PiToonStats = {
    event: function (name) {
      if (name === "script_created" || name === "film_created") hit(name);
    },
    source: currentSource,
    topic: TOPIC
  };

  addEventListener("appinstalled", onInstalled);
  addEventListener("pitoon-appinstalled", onInstalled);

  if (document.readyState === "loading") addEventListener("DOMContentLoaded", boot);
  else boot();
})();
