/* PiToon – cổng nạp nguyên tác phẩm (ChatGPT / AI khác), phân tích và giao cho các khâu AI. */
(function (global) {
  "use strict";

  var STAGES = [
    {id:"bien_kich", n:1, name:"Kịch bản", agent:"AI Biên kịch", icon:"✍️"},
    {id:"nhan_vat", n:2, name:"Nhân vật", agent:"AI Nhân vật", icon:"🧸"},
    {id:"boi_canh", n:3, name:"Bối cảnh", agent:"AI Bối cảnh", icon:"🏡"},
    {id:"phan_canh", n:4, name:"Phân cảnh", agent:"AI Phân cảnh", icon:"🗂"},
    {id:"long_tieng", n:5, name:"Lồng tiếng", agent:"AI Lồng tiếng", icon:"🎙"},
    {id:"am_thanh", n:6, name:"Âm thanh", agent:"AI Âm thanh", icon:"🎵"},
    {id:"dung_phim", n:7, name:"Dựng phim", agent:"AI Dựng", icon:"🎥"},
    {id:"kiem_duyet", n:8, name:"Kiểm duyệt", agent:"AI Kiểm duyệt", icon:"🛡️"},
    {id:"xuat_phim", n:9, name:"Xuất phim", agent:"Xuất phim", icon:"📦"},
    {id:"tong_qc", n:10, name:"Kiểm duyệt cuối", agent:"AI Kiểm duyệt cuối", icon:"✅"}
  ];
  var ST_LB = {cho:"chờ", dang_lam:"đang làm", xong:"xong", can_sua:"cần sửa"};
  var ST_IC = {cho:"⏳", dang_lam:"🔧", xong:"✅", can_sua:"↩️"};

  function t(s) { return (typeof tr === "function") ? tr(s) : s; }
  function e(s) { return (typeof esc === "function") ? esc(s) : String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"})[c]; }); }
  function work() { return (P && P.work) || null; }

  function blankStages() {
    var o = {};
    STAGES.forEach(function (s) { o[s.id] = {state:"cho", note:""}; });
    return o;
  }

  function guessVoice(name, role) {
    var s = ((name || "") + " " + (role || "")).toLowerCase();
    if (/dẫn chuyện|người dẫn|narrator|mặt trời|ông mặt trời/.test(s)) return "narrator";
    if (/bà\b|cô giáo|mẹ\b|má\b|old.?wom|woman/.test(s) && /bà|già|old/.test(s)) return "old_woman";
    if (/ông\b|old.?man/.test(s) && !/mặt trời/.test(s)) return "old_man";
    if (/mẹ\b|má\b|cô\b|chị\b|woman|girl|bé gái|cô bé/.test(s)) return /cô bé|bé gái|girl|child/.test(s) ? "child_girl" : "woman";
    if (/bố\b|ba\b|chú\b|cậu\b|anh\b|man|boy|bé trai|cậu bé/.test(s)) return /cậu bé|bé trai|boy|child/.test(s) ? "child_boy" : "man";
    if (/bé\b|bạn\b/.test(s)) return /gái/.test(s) ? "child_girl" : "child_boy";
    return "narrator";
  }

  function wordCount(s) {
    return String(s || "").trim().split(/\s+/).filter(Boolean).length;
  }

  function cleanLines(s) {
    return String(s || "").replace(/\r\n/g, "\n").replace(/[ \t]+\n/g, "\n").replace(/\n{3,}/g, "\n\n").trim();
  }

  function isWorkLike(text) {
    var s = String(text || "");
    if (s.length < 80) return false;
    return /nhân vật|nhan vat|characters?/i.test(s) && /(?:cảnh|canh|scene)\s*\d+/i.test(s);
  }

  /* ---------- heuristic parser for common ChatGPT / screenplay layouts ---------- */
  function sectionBody(text, titles) {
    var re = new RegExp("(?:^|\\n)\\s*(?:" + titles.join("|") + ")\\s*[:：]?\\s*\\n?", "i");
    var m = re.exec(text);
    if (!m) return "";
    var rest = text.slice(m.index + m[0].length);
    var next = /\n\s*(?:nhân vật|nhan vat|characters?|bối cảnh|boi canh|settings?|cảnh\s*\d|canh\s*\d|scene\s*\d|bài học|bai hoc|moral|tóm tắt|tom tat|int\.|ext\.)\b/i.exec(rest);
    return (next ? rest.slice(0, next.index) : rest).trim();
  }

  function parseNameLine(line) {
    var s = line.replace(/^[\s\-–—*•]+/, "").replace(/\s+/g, " ").trim();
    if (!s) return null;
    var m = s.match(/^([^:：\-–—|]{1,40})\s*[:：\-–—|]\s*(.+)$/);
    if (m) return {name: m[1].replace(/\*\*/g, "").trim(), rest: m[2].trim()};
    if (s.length <= 40 && !/[.!?]$/.test(s)) return {name: s, rest: ""};
    return null;
  }

  function parseChars(block) {
    var out = [], cur = null;
    block.split(/\n/).forEach(function (line) {
      var raw = line.trim();
      if (!raw) return;
      var p = parseNameLine(raw);
      if (p && (raw.match(/^[\-–—*•]/) || /[:：\-–—|]/.test(raw) || raw.length < 50)) {
        cur = {name: p.name, role: p.rest, look: p.rest, voice: guessVoice(p.name, p.rest)};
        var gv = p.rest.match(/giọng\s*[:：]?\s*([a-z_]+)/i);
        if (gv) cur.voice = guessVoice(p.name, gv[1]);
        out.push(cur);
      } else if (cur) {
        cur.role = (cur.role ? cur.role + " " : "") + raw;
        cur.look = cur.role;
      }
    });
    return out;
  }

  function parseSets(block) {
    var out = [];
    block.split(/\n/).forEach(function (line) {
      var raw = line.trim();
      if (!raw) return;
      var p = parseNameLine(raw);
      if (p) out.push({name: p.name, look: p.rest || p.name});
      else out.push({name: raw.slice(0, 40), look: raw});
    });
    return out;
  }

  function isSceneHead(line) {
    return /^(?:cảnh|canh|scene|shot|phân cảnh|phan canh)\s*\d+\b/i.test(line) ||
      /^(?:INT|EXT|int|ext)\s*[\.]/.test(line);
  }

  function parseDialogueLine(line, known) {
    var s = line.replace(/^[\s\-–—*•]+/, "").trim();
    var m = s.match(/^([^:：]{1,40})\s*[:：]\s*(.+)$/);
    if (!m) return null;
    var who = m[1].replace(/^\(|\)$/g, "").trim();
    var lineText = m[2].replace(/^["“]|["”]$/g, "").trim();
    if (!lineText) return null;
    if (/^(bối cảnh|boi canh|nhân vật|nhan vat|hành động|hanh dong|sfx|âm thanh|am thanh|nhạc|nhac|thời lượng|thoi luong|camera|góc máy|goc may|cảm xúc|cam xuc|emotion|mood|setting|action)$/i.test(who)) return null;
    if (known && known.length && !known.some(function (n) { return n.toLowerCase() === who.toLowerCase(); })) {
      if (who.length > 24) return null;
    }
    return {who: who, line: lineText, emo: "happy"};
  }

  function fieldFrom(block, names) {
    var re = new RegExp("(?:^|\\n)\\s*(?:" + names.join("|") + ")\\s*[:：]\\s*(.+)", "i");
    var m = block.match(re);
    return m ? m[1].trim() : "";
  }

  function parseScenes(text, chars) {
    var known = (chars || []).map(function (c) { return c.name; });
    var lines = text.split(/\n/);
    var starts = [];
    lines.forEach(function (ln, i) {
      if (isSceneHead(ln.trim())) starts.push(i);
    });
    if (!starts.length) {
      var parts = text.split(/\n(?=(?:cảnh|canh|scene)\s*\d+)/i);
      if (parts.length > 1) {
        return parts.map(function (p, i) { return parseOneScene(p, i + 1, known); }).filter(function (s) { return s && (s.action || (s.dialogue && s.dialogue.length)); });
      }
      return [];
    }
    var scenes = [];
    for (var i = 0; i < starts.length; i++) {
      var chunk = lines.slice(starts[i], i + 1 < starts.length ? starts[i + 1] : lines.length).join("\n");
      scenes.push(parseOneScene(chunk, i + 1, known));
    }
    return scenes.filter(function (s) { return s && (s.action || (s.dialogue && s.dialogue.length)); });
  }

  function parseOneScene(chunk, idx, known) {
    var lines = chunk.split(/\n/).map(function (l) { return l.trim(); }).filter(Boolean);
    var head = lines[0] || ("Cảnh " + idx);
    var set = "", action = [], dialogue = [], chars = [], sfx = [], music = "", camera = "", emo = "", dur = 8;
    var intm = chunk.match(/\b(INT|EXT)\s*\.\s*([^\n\-–—]+)/i);
    if (intm) set = intm[2].replace(/\s*[-–—].*$/, "").trim();
    var setF = fieldFrom(chunk, ["bối cảnh", "boi canh", "setting", "set", "nơi", "noi"]);
    if (setF) set = setF;
    var actF = fieldFrom(chunk, ["hành động", "hanh dong", "action", "mô tả", "mo ta"]);
    if (actF) action.push(actF);
    var camF = fieldFrom(chunk, ["camera", "góc máy", "goc may"]);
    if (camF) camera = camF;
    var sfxF = fieldFrom(chunk, ["sfx", "tiếng động", "tieng dong", "âm thanh", "am thanh", "hiệu ứng"]);
    if (sfxF) sfx = sfxF.split(/[,;/]| và /).map(function (x) { return x.trim(); }).filter(Boolean);
    var musF = fieldFrom(chunk, ["nhạc", "nhac", "music", "mood", "không khí", "khong khi"]);
    if (musF) music = musF;
    var durF = fieldFrom(chunk, ["thời lượng", "thoi luong", "duration", "giây", "giay"]);
    if (durF) {
      var n = parseFloat(durF.replace(",", "."));
      if (n >= 2 && n <= 20) dur = n;
    }
    var chF = fieldFrom(chunk, ["nhân vật", "nhan vat", "characters?"]);
    if (chF) chars = chF.split(/[,;/]| và /).map(function (x) { return x.trim(); }).filter(Boolean);
    var emoF = fieldFrom(chunk, ["cảm xúc", "cam xuc", "emotion", "emo"]);
    if (emoF) emo = emoF.split(/[,/]/)[0].trim();

    lines.slice(1).forEach(function (ln) {
      if (/^(bối cảnh|boi canh|nhân vật|hành động|sfx|âm thanh|nhạc|thời lượng|camera|góc máy|cảm xúc|setting|action|music|duration)\s*[:：]/i.test(ln)) return;
      if (/^(INT|EXT)\s*\./i.test(ln)) return;
      var d = parseDialogueLine(ln, known);
      if (d) {
        if (emo) d.emo = normalizeEmo(emo);
        dialogue.push(d);
        if (chars.indexOf(d.who) < 0) chars.push(d.who);
        return;
      }
      if (!/^(cảnh|canh|scene|shot)\s*\d+/i.test(ln)) action.push(ln);
    });
    var act = action.join(" ").replace(/\s+/g, " ").trim() || (dialogue[0] ? dialogue[0].who + " nói: " + dialogue[0].line : "Các bạn xuất hiện, vui vẻ.");
    if (!set) set = "Bối cảnh " + idx;
    if (!chars.length && known.length) chars = known.slice(0, 2);
    return {
      set: set,
      chars: chars,
      action: act,
      camera: camera || (idx === 1 ? "wide shot" : "medium shot"),
      motion: act,
      dialogue: dialogue,
      sfx: sfx,
      music: music,
      ambient: sfx[0] || "",
      dur: Math.max(5, Math.min(10, Math.round(dur)))
    };
  }

  function normalizeEmo(s) {
    s = (s || "").toLowerCase();
    if (/vui|happy|cười|cuoi/.test(s)) return "happy";
    if (/háo|hao|excited|hào hứng/.test(s)) return "excited";
    if (/nghịch|nghich|cheeky|tinh nghịch/.test(s)) return "cheeky";
    if (/ngạc|ngac|surprised|bất ngờ/.test(s)) return "surprised";
    if (/sợ|so|scared|hoảng/.test(s)) return "scared";
    if (/buồn|buon|sad/.test(s)) return "sad";
    if (/giận|gian|angry/.test(s)) return "angry";
    if (/cười|cuoi|laugh|hì/.test(s)) return "laugh";
    return "neutral";
  }

  function firstLineMatch(text, names) {
    var re = new RegExp("(?:^|\\n)\\s*(?:" + names.join("|") + ")\\s*[:：]\\s*(.+)", "i");
    var m = text.match(re);
    return m ? m[1].trim() : "";
  }

  function parseHeuristic(text) {
    text = cleanLines(text);
    var title = firstLineMatch(text, ["tên phim", "ten phim", "tiêu đề", "tieu de", "title", "tên chuyện", "ten chuyen"]);
    if (!title) {
      var fl = text.split(/\n/).map(function (l) { return l.replace(/^#+\s*/, "").trim(); }).filter(Boolean)[0] || "";
      if (fl && fl.length <= 80 && !/^nhân vật|bối cảnh|cảnh 1/i.test(fl)) title = fl.replace(/^["“]|["”]$/g, "");
    }
    var moral = firstLineMatch(text, ["bài học", "bai hoc", "ý nghĩa", "y nghia", "moral", "bài học rút ra"]);
    var logline = firstLineMatch(text, ["tóm tắt", "tom tat", "logline", "nội dung", "noi dung", "summary", "tổng quan"]);
    if (!logline) {
      var paras = text.split(/\n\s*\n/).map(function (p) { return p.trim(); }).filter(function (p) { return p.length > 40 && !/^nhân vật|bối cảnh|cảnh/i.test(p); });
      logline = (paras[0] || text).slice(0, 280);
    }
    var chars = parseChars(sectionBody(text, ["nhân vật", "nhan vat", "characters?", "danh sách nhân vật", "các nhân vật"]));
    var sets = parseSets(sectionBody(text, ["bối cảnh", "boi canh", "settings?", "địa điểm", "dia diem", "nơi chốn"]));
    var shots = parseScenes(text, chars);
    if (!sets.length) {
      var seen = {};
      shots.forEach(function (s) {
        if (s.set && !seen[s.set]) { seen[s.set] = 1; sets.push({name: s.set, look: s.set + ", warm 3D children's film setting, Vietnamese, sunny and safe"}); }
      });
    }
    if (!chars.length) {
      var names = {};
      shots.forEach(function (s) { (s.dialogue || []).forEach(function (d) { names[d.who] = 1; }); });
      chars = Object.keys(names).map(function (n) { return {name: n, role: "", look: n, voice: guessVoice(n, "")}; });
    }
    return {
      title: title || "Phim mới",
      logline: logline,
      moral: moral || "",
      characters: chars,
      sets: sets,
      shots: shots,
      notes: "",
      via: "heuristic"
    };
  }

  function analysisPrompt(text) {
    return "You extract a children's cartoon film package from a complete work (possibly written by ChatGPT or another AI). Return ONLY valid JSON.\n" +
      "Schema: {\"title\",\"logline\",\"moral\",\"characters\":[{\"name\",\"look\" (English visual description),\"role\" (personality in the work's language),\"voice\" (narrator|man|woman|old_man|old_woman|child_boy|child_girl)}],\"sets\":[{\"name\",\"look\" (English visual)}],\"shots\":[{\"set\" (exact set name),\"characters\":[exact names],\"action\",\"camera\" (English),\"motion\" (English animation prompt),\"dialogue\":[{\"who\",\"line\",\"emo\" (neutral|happy|cheeky|excited|surprised|scared|sad|angry|laugh)}],\"sfx\":[short English or Vietnamese sound names],\"ambient\",\"music\",\"duration\" (5-10)}],\"notes\"}\n" +
      "Keep dialogue short (max 12 simple words). Kid-safe: no climbing high, hitting, fire, deep water, sharp objects, or rudeness. 4-8 shots if the work has scenes; do not invent a different story. Use exact character names from the work.\n---WORK---\n" + text.slice(0, 12000);
  }

  function withTimeout(p, ms) {
    return new Promise(function (ok, er) {
      var t = setTimeout(function () { er(new Error("timeout")); }, ms);
      Promise.resolve(p).then(function (v) { clearTimeout(t); ok(v); }, function (e) { clearTimeout(t); er(e); });
    });
  }

  function normalizeParsed(j) {
    var chars = (j.characters || j.chars || []).map(function (c) {
      return {
        name: String(c.name || "").trim(),
        role: c.role || c.personality || "",
        look: c.look || c.role || c.personality || c.name || "",
        voice: c.voice || guessVoice(c.name, c.role || "")
      };
    }).filter(function (c) { return c.name; });
    var sets = (j.sets || j.settings || []).map(function (s) {
      if (typeof s === "string") return {name: s, look: s};
      return {name: s.name || "Bối cảnh", look: s.look || s.name || ""};
    });
    var shots = (j.shots || j.scenes || []).map(function (s) {
      var dlg = (s.dialogue || s.lines || []).map(function (d) {
        if (typeof d === "string") {
          var p = parseDialogueLine(d, chars.map(function (c) { return c.name; }));
          return p || {who: "Người dẫn", line: d, emo: "neutral"};
        }
        return {who: d.who || d.name || "Người dẫn", line: d.line || d.text || "", emo: normalizeEmo(d.emo || d.emotion || "neutral")};
      }).filter(function (d) { return d.line; });
      return {
        set: s.set || s.setting || (sets[0] && sets[0].name) || "Bối cảnh",
        chars: s.characters || s.chars || dlg.map(function (d) { return d.who; }),
        action: s.action || s.acting || "",
        camera: s.camera || "medium shot",
        motion: s.motion || s.action || "",
        dialogue: dlg,
        sfx: Array.isArray(s.sfx) ? s.sfx : String(s.sfx || "").split(/[,;/]/).map(function (x) { return x.trim(); }).filter(Boolean),
        music: s.music || s.mood || "",
        ambient: s.ambient || "",
        dur: Math.max(5, Math.min(10, Math.round(+s.duration || +s.dur || 8)))
      };
    });
    return {
      title: j.title || "Phim mới",
      logline: j.logline || j.summary || "",
      moral: j.moral || j.lesson || "",
      characters: chars,
      sets: sets,
      shots: shots,
      notes: j.notes || "",
      via: j.via || "llm"
    };
  }

  function safetyOf(parsed, raw) {
    if (!global.PiToonSafety) return [];
    var parts = [raw || "", parsed && parsed.title, parsed && parsed.logline, parsed && parsed.moral];
    (parsed && parsed.shots || []).forEach(function (s) {
      parts.push(s.action || "");
      (s.dialogue || []).forEach(function (d) { parts.push(d.line || ""); });
    });
    return PiToonSafety.check(parts.filter(Boolean).join(" \n "));
  }

  function applyParsed(parsed, raw) {
    parsed = normalizeParsed(parsed);
    var custom = (P.chars || []).filter(function (c) { return c.custom; });
    var chars = custom.slice();
    parsed.characters.forEach(function (c) {
      var hit = chars.find(function (k) { return k.name.toLowerCase() === c.name.toLowerCase(); });
      if (hit) {
        if (!hit.role) hit.role = c.role;
        if (!hit.look || hit.look === hit.name) hit.look = c.look || hit.look;
        if (!hit.voice) hit.voice = c.voice;
      } else {
        chars.push({id: uid(), name: c.name, role: c.role, look: c.look, voice: c.voice || "narrator"});
      }
    });
    var sets = (parsed.sets || []).map(function (s) { return {id: uid(), name: s.name, look: s.look}; });
    var shots = (parsed.shots || []).map(function (s) {
      return {id: uid(), set: s.set, chars: s.chars || [], action: s.action, camera: s.camera, motion: s.motion || s.action, dialogue: s.dialogue || [], sfx: s.sfx || [], music: s.music || "", ambient: s.ambient || "", dur: s.dur || 8};
    });
    P.script = {title: parsed.title, moral: parsed.moral, summary: parsed.logline};
    P.name = parsed.title || P.name;
    P.chars = chars;
    P.sets = sets;
    P.shots = shots;
    if (!P.idea) P.idea = parsed.logline || "";
    var st = (P.work && P.work.stages) || blankStages();
    st.bien_kich = {state:"xong", note: parsed.shots.length + " cảnh, " + chars.length + " nhân vật"};
    var issues = safetyOf(parsed, raw);
    var blocks = issues.filter(function (i) { return i.level === "block"; });
    st.kiem_duyet = blocks.length
      ? {state:"can_sua", note: "Có chỗ bé có thể bắt chước mà bị đau – hãy sửa trước khi làm phim."}
      : {state:"xong", note: issues.length ? "Có nhắc nhỏ, xem thẻ an toàn." : "Không thấy chỗ nguy hiểm."};
    P.work = {
      raw: raw || (P.work && P.work.raw) || "",
      parsed: parsed,
      stages: st,
      safety: issues,
      loop: 0,
      maxLoops: 2,
      running: false,
      source: (P.work && P.work.source) || "paste",
      analyzedAt: Date.now()
    };
    save();
    try { global.PiToonStats && PiToonStats.event("script_created"); } catch (err) {}
  }

  async function analyzeWork(text, source) {
    text = cleanLines(text);
    if (!text || text.length < 20) { log(t("Dán hoặc nạp cả tác phẩm đã viết sẵn nhé!"), 5000); return; }
    if (BUSY) return;
    BUSY = 1;
    P.work = P.work || {};
    P.work.raw = text;
    P.work.source = source || P.work.source || "paste";
    save();
    log(t("Đang phân tích tác phẩm…"), 0);
    var parsed = null, via = "heuristic";
    try {
      if (typeof llm === "function") {
        var sys = "You are a children's animation script supervisor. Return ONLY valid JSON. No markdown.";
        var rawOut = await withTimeout(llm(sys, analysisPrompt(text)), 20000);
        parsed = normalizeParsed(pj(rawOut));
        parsed.via = "llm";
        via = "llm";
        if (!parsed.shots || parsed.shots.length < 2) throw new Error("too few shots");
      }
    } catch (err) {
      parsed = null;
    }
    if (!parsed) {
      parsed = parseHeuristic(text);
      via = "heuristic";
    }
    if (!parsed.shots || !parsed.shots.length) {
      BUSY = 0;
      log(t("Chưa tách được phân cảnh. Hãy ghi rõ “Cảnh 1”, “Cảnh 2” và lời thoại “Tên: câu nói” nhé."), 8000);
      render();
      return;
    }
    applyParsed(parsed, text);
    BUSY = 0;
    log(t("Đã phân tích xong") + " · " + (via === "llm" ? t("AI Biên kịch") : t("đọc dàn ý")) + " · " + P.shots.length + " " + t("Cảnh quay"));
    render();
    var ev = $("workReview");
    if (ev) ev.scrollIntoView({behavior: "smooth", block: "start"});
  }

  async function importWorkFile(inp) {
    var files = inp && inp.files ? [].slice.call(inp.files) : [];
    if (inp) inp.value = "";
    if (!files.length) return;
    log(t("Đang nạp…"), 0);
    var text = "", name = files[0].name || "";
    try {
      for (var i = 0; i < files.length; i++) {
        var f = files[i], k = fileKind(f);
        if (k === "docx") text += (text ? "\n\n" : "") + await readDocx(f);
        else if (k === "pdf") text += (text ? "\n\n" : "") + await readPdf(f);
        else if (k === "txt") text += (text ? "\n\n" : "") + await readPlain(f);
        else if (k === "doc") { log(t("File .doc cũ chưa đọc được. Bé lưu lại thành .docx hoặc PDF nhé."), 7000); return; }
        else { log(t("Chưa đọc được loại file này. Hãy dùng Word, PDF, TXT hoặc ảnh."), 7000); return; }
      }
      P.work = P.work || {};
      P.work.raw = text;
      P.work.source = name;
      save();
      await analyzeWork(text, name);
    } catch (err) {
      log(t("Lỗi") + ": " + err.message, 8000);
    }
  }

  function workDrop(ev) {
    ev.preventDefault();
    ev.currentTarget.classList.remove("over");
    var files = ev.dataTransfer && ev.dataTransfer.files;
    if (files && files.length) importWorkFile({files: files});
  }

  function startAnalyze() {
    var box = $("workRaw");
    var text = (box && box.value) || (P.work && P.work.raw) || P.idea || "";
    analyzeWork(text, "paste");
  }

  /* ---------- review + pipeline UI ---------- */
  function stagePill(id) {
    var st = (P.work && P.work.stages && P.work.stages[id]) || {state:"cho", note:""};
    return ST_IC[st.state] + " " + t(ST_LB[st.state] || st.state);
  }

  function workGateHtml() {
    var raw = (P.work && P.work.raw) || "";
    return '<div class="card work-gate" id="workGate">' +
      "<h2>📥 " + t("Nạp nguyên tác phẩm") + "</h2>" +
      '<p class="mut">' + t("Dán hoặc nạp cả câu chuyện đã viết từ ChatGPT hay AI khác — có tên phim, nhân vật, bối cảnh, phân cảnh và lời thoại. PiToon sẽ phân tích rồi giao cho từng AI agent theo từng khâu, đến khi xuất phim.") + "</p>" +
      '<textarea id="workRaw" placeholder="' + e(t("Dán cả tác phẩm vào đây…")) + '" oninput="P.work=P.work||{};P.work.raw=this.value;save()">' + e(raw) + "</textarea>" +
      '<div class="dropgate work-drop" id="workDrop" tabindex="0" ondragenter="event.preventDefault();this.classList.add(\'over\')" ondragover="event.preventDefault();this.classList.add(\'over\')" ondragleave="this.classList.remove(\'over\')" ondrop="workDrop(event)">' +
      '<p class="mut" style="margin:0 0 8px">' + t("Hoặc kéo thả / chọn file Word, PDF, TXT.") + "</p>" +
      '<label class="b2" style="margin:0;color:var(--t);display:inline-flex">📄 ' + t("Chọn file tác phẩm") +
      '<input type="file" hidden accept=".docx,.pdf,.txt,.md,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onchange="importWorkFile(this)"></label>' +
      "</div>" +
      '<div class="row" style="margin-top:12px"><button class="btn" id="bAnalyze" ' + (BUSY ? "disabled" : "") + ' onclick="startAnalyze()">🔎 ' + t("Phân tích tác phẩm") + "</button></div>" +
      "</div>";
  }

  function safetyHtml() {
    var issues = (P.work && P.work.safety) || [];
    if (global.PiToonSafety) return PiToonSafety.html(issues, "script");
    return "";
  }

  function voiceOpts(cur) {
    var keys = (typeof VOICES === "object" && VOICES) ? Object.keys(VOICES) : ["narrator","man","woman","old_man","old_woman","child_boy","child_girl"];
    return keys.map(function (v) {
      return "<option" + (cur === v ? " selected" : "") + ">" + e(v) + "</option>";
    }).join("");
  }

  function reviewChars() {
    return '<div class="g2">' + (P.chars || []).map(function (c, i) {
      return '<div class="card">' +
        (c.custom ? '<span class="badge-kid">' + t("Nhân vật của bé") + "</span>" : "") +
        '<img class="thumb sq" data-b="' + e(c.img || "") + '" alt="">' +
        "<label>" + t("Tên nhân vật") + "</label>" +
        '<input value="' + e(c.name) + '" onchange="P.chars[' + i + '].name=this.value;save()">' +
        "<label>" + t("Tính cách / mô tả") + "</label>" +
        "<textarea oninput=\"upd(P.chars[" + i + "],'role',this.value)\">" + e(c.role || "") + "</textarea>" +
        "<label>" + t("Mô tả ngoại hình") + "</label>" +
        "<textarea oninput=\"upd(P.chars[" + i + "],'look',this.value)\">" + e(c.look || "") + "</textarea>" +
        "<label>" + t("Giọng") + "</label>" +
        '<select onchange="upd(P.chars[' + i + '],\'voice\',this.value)">' + voiceOpts(c.voice) + "</select>" +
        '<div class="row" style="margin-top:8px"><label class="b2" style="margin:0;color:var(--t)">📷 ' + t("Chọn ảnh") +
        '<input type="file" accept="image/*" hidden onchange="upImg(this,P.chars[' + i + '],\'c_\')"></label></div></div>';
    }).join("") + "</div>";
  }

  function reviewSets() {
    return '<div class="g2">' + (P.sets || []).map(function (s, i) {
      return '<div class="card"><b>' + e(s.name) + "</b><textarea oninput=\"upd(P.sets[" + i + "],'look',this.value)\">" + e(s.look || "") + "</textarea></div>";
    }).join("") + "</div>";
  }

  var EMOS = ["neutral","happy","cheeky","excited","surprised","scared","sad","angry","laugh"];

  function reviewShots() {
    return (P.shots || []).map(function (s, i) {
      var dlg = (s.dialogue || []).map(function (d, k) {
        var emo = '<select style="width:auto" onchange="upd(P.shots[' + i + '].dialogue[' + k + '],\'emo\',this.value)">' +
          EMOS.map(function (em) { return "<option" + ((d.emo || "happy") === em ? " selected" : "") + ">" + em + "</option>"; }).join("") +
          "</select>";
        return '<div class="row"><b style="min-width:90px">' + e(d.who) + '</b><input style="flex:1;width:auto" value="' + e(d.line) +
          "\" oninput=\"upd(P.shots[" + i + "].dialogue[" + k + "],'line',this.value)\">" + emo + "</div>";
      }).join("");
      return '<div class="card"><b>Cảnh ' + (i + 1) + '</b> <span class="tag">' + e(s.set) + "</span> " +
        (s.chars || []).map(function (c) { return '<span class="tag">' + e(c) + "</span>"; }).join("") +
        "<label>" + t("Hành động") + "</label><textarea oninput=\"upd(P.shots[" + i + "],'action',this.value)\">" + e(s.action || "") + "</textarea>" +
        '<div class="row"><div style="flex:2"><label>' + t("Góc máy") + "</label>" +
        '<input value="' + e(s.camera || "") + "\" oninput=\"upd(P.shots[" + i + "],'camera',this.value)\"></div>" +
        '<div style="flex:1"><label>' + t("giây") + "</label>" +
        '<input type="number" min="4" max="10" value="' + (s.dur || 8) + "\" oninput=\"upd(P.shots[" + i + "],'dur',+this.value)\"></div></div>" +
        "<label>" + t("Lời thoại") + "</label>" + (dlg || '<p class="mut">—</p>') +
        "<label>SFX</label><input value=\"" + e((s.sfx || []).join(", ")) + "\" oninput=\"P.shots[" + i + "].sfx=this.value.split(/[,;]/).map(function(x){return x.trim()}).filter(Boolean);save()\">" +
        "<label>" + t("Nhạc") + " / mood</label><input value=\"" + e(s.music || "") + "\" oninput=\"upd(P.shots[" + i + "],'music',this.value)\"></div>";
    }).join("");
  }

  function reviewVoices() {
    var rows = [];
    (P.shots || []).forEach(function (s, i) {
      (s.dialogue || []).forEach(function (d) {
        rows.push("<div class=\"row\"><span class=\"tag\">Cảnh " + (i + 1) + "</span><b style=\"min-width:90px\">" + e(d.who) + "</b><span>" + e(d.line) + "</span><span class=\"mut\">" + e(d.emo || "") + "</span>" + (s.aud ? " ✓" : "") + "</div>");
      });
    });
    return rows.length ? rows.join("") : '<p class="mut">' + t("Chưa có lời thoại.") + "</p>";
  }

  function reviewAudio() {
    var n = 0;
    (P.shots || []).forEach(function (s) { n += (s.sfx || []).length; });
    return '<p class="mut">' + t("Nhạc nền") + ": " + (P.music ? "✓" : t("sẽ tạo nhạc vui khi làm phim")) +
      " · " + n + " SFX · " + t("Âm lượng nhạc") + ": " + (P.mvol || 15) + "%</p>";
  }

  function pipeHtml() {
    var stages = STAGES.map(function (s) {
      var st = (P.work && P.work.stages && P.work.stages[s.id]) || {state:"cho", note:""};
      return '<div class="work-st ' + st.state + '" data-stage="' + s.id + '">' +
        '<div class="n">Khâu ' + s.n + " · " + e(s.agent) + "</div>" +
        '<div class="nm">' + s.icon + " " + e(t(s.name)) + "</div>" +
        '<div class="s" data-st>' + ST_IC[st.state] + " " + t(ST_LB[st.state]) + "</div>" +
        (st.note ? '<div class="nt" data-nt>' + e(st.note) + "</div>" : '<div class="nt" data-nt></div>') +
        "</div>";
    }).join("");
    return '<div class="work-flow" id="workFlow">' + stages + "</div>";
  }

  function blocked() {
    return ((P.work && P.work.safety) || []).some(function (i) { return i.level === "block"; });
  }

  function pipelineDone() {
    var st = P.work && P.work.stages;
    return !!(st && st.xuat_phim && st.xuat_phim.state === "xong");
  }

  function workReviewHtml() {
    if (!(P.work && P.work.parsed && P.script)) return "";
    var p = P.work.parsed;
    var dis = BUSY || blocked() ? "disabled" : "";
    var warn = blocked() ? '<p class="mut">🛡️ ' + t("Hãy sửa các chỗ chưa an toàn ở trên rồi mới giao cho các AI làm phim.") + "</p>" : "";
    var done = pipelineDone()
      ? '<div class="work-done" id="workDone"><b>✅ ' + t("Các AI đã xong bản nháp.") + "</b> " +
        t("Trong app đây là bản nháp (ảnh, lia máy, lời và nhạc). Phim hoạt hình thật do xưởng phim làm từ file “Gửi lên xưởng phim chuẩn”.") +
        (P.film ? '<div style="margin-top:8px"><video id="film" class="thumb" controls data-b="' + e(P.film) + '"></video></div>' : "") +
        "</div>"
      : "";
    return '<div class="card work-review" id="workReview">' +
      "<h2>🔎 " + t("Phân tích tác phẩm") + "</h2>" +
      '<p class="mut">' + t("Mỗi thẻ là một khâu. Bé có thể sửa rồi bấm giao cho các AI.") +
      (p.via === "llm" ? " · " + t("AI Biên kịch đã đọc tác phẩm.") : " · " + t("Đã đọc dàn ý (Cảnh 1, Nhân vật…).") ) + "</p>" +
      pipeHtml() +
      '<p id="workPipeSt" class="mut" style="margin-top:8px"></p>' +
      done +
      '<div class="work-block"><h3>✍️ ' + t("Kịch bản") + " · " + t("AI Biên kịch") + "</h3>" +
      "<label>" + t("Tên phim") + '</label><input value="' + e(P.script.title || "") + "\" oninput=\"upd(P.script,'title',this.value);upd(P,'name',this.value)\">" +
      "<label>" + t("Tóm tắt") + "</label><textarea oninput=\"upd(P.script,'summary',this.value)\">" + e(P.script.summary || "") + "</textarea>" +
      "<label>" + t("Bài học") + '</label><input value="' + e(P.script.moral || "") + "\" oninput=\"upd(P.script,'moral',this.value)\"></div>" +
      '<div class="work-block"><h3>🧸 ' + t("Nhân vật") + " · " + t("AI Nhân vật") + "</h3>" +
      '<p class="mut">' + t("Trùng tên với “Nhân vật của bé” thì giữ ảnh bé đã chọn.") + "</p>" + reviewChars() + "</div>" +
      '<div class="work-block"><h3>🏡 ' + t("Bối cảnh") + " · " + t("AI Bối cảnh") + "</h3>" + reviewSets() + "</div>" +
      '<div class="work-block"><h3>🗂 ' + t("Phân cảnh") + " · " + t("AI Phân cảnh") + "</h3>" + reviewShots() + "</div>" +
      '<div class="work-block"><h3>🎙 ' + t("Lồng tiếng") + " · " + t("AI Lồng tiếng") + "</h3>" + reviewVoices() + "</div>" +
      '<div class="work-block"><h3>🎵 ' + t("Âm thanh") + " · " + t("AI Âm thanh") + "</h3>" + reviewAudio() + "</div>" +
      '<div class="work-block"><h3>🎥 ' + t("Dựng phim") + " · " + t("AI Dựng") + "</h3>" +
      '<p class="mut">' + t("Khi bấm giao việc, AI Dựng sẽ ghép ảnh, lời và nhạc thành bản nháp MP4 trong app.") + "</p></div>" +
      '<div class="work-block"><h3>🛡️ ' + t("Kiểm duyệt") + " · " + t("AI Kiểm duyệt") + "</h3>" + safetyHtml() +
      (blocked() ? "" : '<p class="ok">🛡️ ' + t("Kịch bản an toàn cho bé") + "</p>") + "</div>" +
      '<div class="work-block"><h3>📦 ' + t("Xuất phim") + "</h3>" +
      '<p class="warn">' + t("Trong app, các AI làm bản nháp: ảnh tĩnh, lia máy Ken Burns, lời và nhạc. Phim hoạt hình thật (nhân vật cử động, khớp miệng) do xưởng phim làm từ file “Gửi lên xưởng phim chuẩn”.") + "</p>" +
      (P.film ? '<button class="b2" type="button" onclick="getB(P.film).then(function(b){dl(b,(P.name||\'phim\')+\'.mp4\')})">⬇ ' + t("Tải phim") + "</button>" : "") +
      "</div>" +
      warn +
      '<div class="row" style="margin-top:12px">' +
      '<button class="btn" id="bRunWork" ' + dis + ' onclick="runWorkPipeline()">▶️ ' + t("Giao cho các AI làm phim") + "</button>" +
      '<button class="b2" type="button" onclick="downloadStudioJob()">📤 ' + t("Gửi lên xưởng phim chuẩn") + "</button>" +
      "</div></div>";
  }

  function paintStage(id, state, note) {
    if (!P.work) return;
    P.work.stages = P.work.stages || blankStages();
    P.work.stages[id] = {state: state, note: note || "", at: Date.now()};
    save();
    var el = document.querySelector('[data-stage="' + id + '"]');
    if (el) {
      el.className = "work-st " + state;
      var s = el.querySelector("[data-st]");
      var n = el.querySelector("[data-nt]");
      if (s) s.textContent = ST_IC[state] + " " + t(ST_LB[state]);
      if (n) n.textContent = note || "";
    }
    var st = $("workPipeSt");
    if (st) st.textContent = note || "";
  }

  function allDoneExceptQc() {
    return STAGES.every(function (s) {
      if (s.id === "tong_qc") return true;
      var st = P.work.stages[s.id];
      return st && (st.state === "xong" || st.state === "can_sua");
    });
  }

  /* ---------- QC + pipeline ---------- */
  function qcWork() {
    var issues = [];
    if (!P.script || !P.script.title) issues.push({stage:"bien_kich", msg:"Thiếu tên phim."});
    if (!P.script || !P.script.moral) issues.push({stage:"bien_kich", msg:"Thiếu bài học cuối phim."});
    if (!(P.shots && P.shots.length >= 2)) issues.push({stage:"phan_canh", msg:"Cần ít nhất 2 cảnh."});
    if (!(P.chars && P.chars.length)) issues.push({stage:"nhan_vat", msg:"Chưa có nhân vật."});
    var names = (P.chars || []).map(function (c) { return c.name; });
    var lower = names.map(function (n) { return n.toLowerCase(); });
    var used = {};
    (P.shots || []).forEach(function (s, i) {
      (s.chars || []).forEach(function (n) {
        if (n && lower.indexOf(String(n).toLowerCase()) < 0 && !/dẫn|narrator/i.test(n)) {
          issues.push({stage:"phan_canh", msg:"Cảnh " + (i + 1) + " có nhân vật chưa có trong danh sách: " + n});
        }
        used[String(n).toLowerCase()] = 1;
      });
      (s.dialogue || []).forEach(function (d) {
        if (wordCount(d.line) > 20) issues.push({stage:"bien_kich", msg:"Câu thoại của " + d.who + " dài quá 20 từ."});
        if (d.who && lower.indexOf(d.who.toLowerCase()) < 0 && !/dẫn|narrator/i.test(d.who)) {
          issues.push({stage:"phan_canh", msg:"Lời thoại của nhân vật chưa có: " + d.who});
        }
        if (d.who) used[d.who.toLowerCase()] = 1;
      });
    });
    (P.chars || []).forEach(function (c) {
      if (/dẫn|narrator/i.test(c.name) || /dẫn chuyện/.test(c.role || "")) return;
      if (!used[c.name.toLowerCase()]) issues.push({stage:"phan_canh", msg:"Nhân vật “" + c.name + "” chưa xuất hiện ở cảnh nào."});
    });
    var safe = safetyOf({title: P.script && P.script.title, logline: P.script && P.script.summary, moral: P.script && P.script.moral, shots: P.shots}, P.work && P.work.raw);
    P.work.safety = safe;
    safe.filter(function (i) { return i.level === "block"; }).forEach(function (i) {
      issues.push({stage:"kiem_duyet", msg: "An toàn: “" + i.found + "” – " + i.label});
    });
    return issues;
  }

  function autoFix(issues) {
    var did = 0;
    issues.forEach(function (it) {
      if (/dài quá 20 từ/.test(it.msg)) {
        (P.shots || []).forEach(function (s) {
          (s.dialogue || []).forEach(function (d) {
            var w = d.line.split(/\s+/);
            if (w.length > 20) { d.line = w.slice(0, 18).join(" "); did++; }
          });
        });
      }
      var m = it.msg.match(/nhân vật chưa có trong danh sách:\s*(.+)$/i) || it.msg.match(/Lời thoại của nhân vật chưa có:\s*(.+)$/i);
      if (m) {
        var name = m[1].trim();
        if (name && !(P.chars || []).some(function (c) { return c.name.toLowerCase() === name.toLowerCase(); })) {
          P.chars.push({id: uid(), name: name, role: "", look: name, voice: guessVoice(name, "")});
          did++;
        }
      }
    });
    if (did) save();
    return did;
  }

  async function runStage(id, fn, note) {
    paintStage(id, "dang_lam", note || t("Đang xử lý…"));
    try {
      await fn();
      paintStage(id, "xong", note || t("Xong"));
    } catch (err) {
      paintStage(id, "can_sua", (t("Lỗi") + ": " + err.message).slice(0, 180));
      throw err;
    }
  }

  async function silentWav(sec) {
    var sr = 22050, n = Math.max(1, Math.floor(sr * (sec || 0.6)));
    var ctx = new OfflineAudioContext(1, n, sr);
    return wav(await ctx.startRendering());
  }

  async function voiceSafe(sh) {
    try {
      await genVoice(sh);
    } catch (err) {
      var d = Math.max(1, sh.dur || 6);
      await setB("a_" + sh.id, await silentWav(d));
      sh.aud = "a_" + sh.id;
      sh.adur = d;
      save();
      return err.message || "fallback";
    }
    return "";
  }

  async function runWorkPipeline() {
    if (BUSY) return;
    if (!P.shots || !P.shots.length) return log(t("Chưa có kịch bản – hãy viết ở bước 1"), 5000);
    if (blocked()) { log(t("Hãy sửa các chỗ chưa an toàn ở trên rồi mới giao cho các AI làm phim."), 7000); return; }
    BUSY = 1;
    P.work.running = true;
    P.work.loop = 0;
    save();
    log(t("Các AI đang làm phim…"), 0);
    var ev = $("workFlow");
    if (ev) ev.scrollIntoView({behavior: "smooth", block: "start"});
    try {
      await runStage("bien_kich", async function () {
        if (!P.script.moral) P.script.moral = "Hãy quan tâm bạn bè và lắng nghe người lớn đáng tin.";
        save();
      }, (P.shots.length + " cảnh · " + P.chars.length + " nhân vật"));

      await runStage("nhan_vat", async function () {
        for (var i = 0; i < P.chars.length; i++) {
          var c = P.chars[i];
          if (!c.img) {
            log(t("AI Nhân vật") + " · " + c.name + "…", 0);
            await genChar(c);
            renderKeepPipe();
          }
        }
      }, t("Đã có ảnh nhân vật"));

      await runStage("boi_canh", async function () {
        for (var i = 0; i < P.sets.length; i++) {
          var s = P.sets[i];
          if (!s.img) {
            log(t("AI Bối cảnh") + " · " + s.name + "…", 0);
            await genSet(s);
            renderKeepPipe();
          }
        }
      }, t("Đã có ảnh bối cảnh"));

      await runStage("phan_canh", async function () {
        if (P.shots.length < 2) throw new Error("Cần ít nhất 2 cảnh.");
        for (var i = 0; i < P.shots.length; i++) {
          var sh = P.shots[i];
          log(t("AI Phân cảnh") + " · " + t("Cảnh quay") + " " + (i + 1) + "/" + P.shots.length + "…", 0);
          if (!sh.img) await genKey(sh);
          if (typeof genVideo === "function") await genVideo(sh);
          renderKeepPipe();
        }
      }, t("Đã có khung hình bản nháp"));

      var voiceNote = t("Xong");
      var voiceWarn = "";
      await runStage("long_tieng", async function () {
        for (var i = 0; i < P.shots.length; i++) {
          log(t("AI Lồng tiếng") + " · " + (i + 1) + "/" + P.shots.length + "…", 0);
          var w = await voiceSafe(P.shots[i]);
          if (w) voiceWarn = w;
          renderKeepPipe();
        }
      }, voiceWarn ? (t("Giọng tạm thời") + " — " + voiceWarn).slice(0, 160) : t("Xong"));
      if (voiceWarn) paintStage("long_tieng", "xong", (t("Giọng tạm thời") + " — " + voiceWarn).slice(0, 160));

      await runStage("am_thanh", async function () {
        if (!P.music) {
          var sec = Math.max(16, Math.round(P.shots.reduce(function (a, s) { return a + (s.dur || 8); }, 0)));
          await setB("m_" + P.id, await genMusic(Math.min(48, sec)));
          P.music = "m_" + P.id;
          P.mvol = P.mvol || 15;
          save();
        }
      }, t("Đã có nhạc nền vui"));

      await runStage("dung_phim", async function () {
        log(t("AI Dựng") + "…", 0);
        await assemble({force: true, quiet: true, keepBusy: true, onStatus: function (m) { var el = $("workPipeSt"); if (el) el.textContent = m; }});
        if (!P.film) throw new Error("Chưa dựng được file phim.");
      }, t("Đã dựng bản nháp MP4"));

      await runStage("kiem_duyet", async function () {
        var issues = safetyOf({title: P.script.title, logline: P.script.summary, moral: P.script.moral, shots: P.shots}, P.work.raw);
        P.work.safety = issues;
        if (issues.some(function (i) { return i.level === "block"; })) throw new Error("Còn chỗ chưa an toàn cho bé.");
      }, t("Kịch bản an toàn cho bé"));

      await finishQcLoops();
      if (P.film) paintStage("xuat_phim", "xong", t("Có thể tải phim nháp và file xưởng phim"));
      log(t("Xong") + " — " + t("Bản nháp đã sẵn. Muốn phim hoạt hình thật, gửi lên xưởng phim chuẩn."));
    } catch (err) {
      log(t("Lỗi") + ": " + err.message, 8000);
    }
    P.work.running = false;
    BUSY = 0;
    save();
    render();
    var ev2 = $("workDone") || $("workFlow");
    if (ev2) ev2.scrollIntoView({behavior: "smooth", block: "start"});
  }

  async function finishQcLoops() {
    var loop = 0;
    while (loop <= (P.work.maxLoops || 2)) {
      paintStage("tong_qc", "dang_lam", loop ? (t("Vòng sửa") + " " + loop) : t("Đang kiểm duyệt…"));
      var issues = qcWork();
      if (!issues.length) {
        paintStage("tong_qc", "xong", t("Đạt — bản nháp sẵn sàng. Phim hoạt hình thật do xưởng phim làm."));
        return;
      }
      if (loop >= (P.work.maxLoops || 2)) {
        paintStage("tong_qc", "can_sua", issues[0].msg + (issues.length > 1 ? " (+" + (issues.length - 1) + ")" : ""));
        var stg = issues[0].stage;
        if (stg) paintStage(stg, "can_sua", issues[0].msg);
        return;
      }
      var did = autoFix(issues);
      P.work.loop = ++loop;
      var back = issues[0].stage || "bien_kich";
      paintStage(back, "can_sua", issues[0].msg);
      paintStage("tong_qc", "can_sua", t("Trả về") + " " + t((STAGES.find(function (s) { return s.id === back; }) || {}).name || back));
      if (!did) {
        paintStage("tong_qc", "can_sua", issues[0].msg);
        return;
      }
    }
  }

  function renderKeepPipe() {
    var y = window.scrollY;
    render();
    window.scrollTo(0, y);
  }

  function downloadStudioJob() {
    if (!P || !P.shots || !P.shots.length) return log(t("Chưa có kịch bản – hãy viết ở bước 1"), 5000);
    var t0 = 0;
    var shots = P.shots.map(function (s, i) {
      var from = t0, to = t0 + (s.dur || 8);
      t0 = to;
      var line = (s.dialogue && s.dialogue[0]) ? s.dialogue[0].line : null;
      var emo = (s.dialogue && s.dialogue[0] && s.dialogue[0].emo) || "neutral";
      return {
        id: "S" + String(i + 1).padStart(2, "0"),
        scene: "S" + String(i + 1).padStart(2, "0"),
        set: s.set,
        chars: s.chars || [],
        from: from,
        to: to,
        camera: s.camera || "medium shot",
        acting: s.action || "",
        action: s.action || "",
        emo: emo,
        line: line,
        sfx: s.sfx || [],
        refs: [],
        video_prompt_en: (s.motion || s.action || "") + ". " + (s.camera || "") + ". 3D animated kids film, expressive cartoon acting, 16:9, no text, safe and gentle.",
        gen: {duration: Math.max(6, s.dur || 8), use_s: s.dur || 8}
      };
    });
    var lines = [];
    P.shots.forEach(function (s, i) {
      (s.dialogue || []).forEach(function (d) {
        var c = (P.chars || []).find(function (x) { return x.name === d.who; });
        lines.push({who: d.who, voice: (c && c.voice) || "narrator", emo: d.emo || "neutral", text: d.line, shot: "S" + String(i + 1).padStart(2, "0")});
      });
    });
    var sfx = [];
    var clock = 0;
    P.shots.forEach(function (s) {
      var d = s.dur || 8;
      (s.sfx || []).forEach(function (name, k) {
        sfx.push({t: Math.round((clock + d * (k + 1) / ((s.sfx.length) + 1)) * 10) / 10, name: name});
      });
      clock += d;
    });
    var job = {
      format: "pitoon-studio-job",
      version: 2,
      title: (P.script && P.script.title) || P.name,
      lesson: (P.script && P.script.moral) || "",
      logline: (P.script && P.script.summary) || "",
      out: ((P.name || "phim").replace(/[^\p{L}\p{N}]+/gu, "_") || "phim") + "_16x9.mp4",
      body_s: clock,
      characters: (P.chars || []).map(function (c) { return {name: c.name, role: c.role, look: c.look, voice: c.voice, custom: !!c.custom}; }),
      sets: (P.sets || []).map(function (s) { return {name: s.name, look: s.look}; }),
      shots: shots,
      lines: lines,
      sfx: sfx,
      qc: {line_words: 10, sfx_per_s: 0.3, shot_len: [2.5, 10]},
      note: "Phim hoạt hình thật (cử động, khớp miệng, edge-tts, nhạc + tiếng động) chạy trên máy xưởng: tools/pitoon_pipeline.py và tools/line/studio_runner.py. File này tương thích SHOT_PLAN / scene.json.",
      source: (P.work && P.work.source) || "",
      created: new Date().toISOString()
    };
    dl(new Blob([JSON.stringify(job, null, 2)], {type: "application/json"}), (P.name || "phim") + ".pitoon-studio.json");
    log(t("Đã tải file xưởng phim chuẩn"));
  }

  global.STAGES_WORK = STAGES;
  global.workGateHtml = workGateHtml;
  global.workReviewHtml = workReviewHtml;
  global.startAnalyze = startAnalyze;
  global.analyzeWork = analyzeWork;
  global.importWorkFile = importWorkFile;
  global.workDrop = workDrop;
  global.runWorkPipeline = runWorkPipeline;
  global.downloadStudioJob = downloadStudioJob;
  global.parseHeuristic = parseHeuristic;
  global.isWorkLike = isWorkLike;
})(typeof window !== "undefined" ? window : this);

if (typeof render === "function" && typeof P !== "undefined" && P && typeof document !== "undefined" && document.getElementById("main")) {
  try { render(); } catch (err) {}
}
