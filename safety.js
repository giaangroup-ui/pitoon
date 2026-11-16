/* PiToon – kiểm tra an toàn kịch bản cho bé 3–10 tuổi, chạy ngay trong trình duyệt (không gửi đi đâu).
   Theo tools/HUONG_DAN_NOI_DUNG.md: trẻ BẮT CHƯỚC mọi thứ nhân vật làm.
   So khớp theo ranh giới từ tiếng Việt (chữ có dấu), nên "đánh răng", "đồng hồ", "xe lửa", "ngã tư", "kéo co" không bị chặn.
   PiToonSafety.check(text) -> [{id, label, level:"block"|"note", found, tip}] */
(function(){
"use strict";
var L="[\\p{L}\\p{M}\\p{N}_]";                        // ký tự thuộc một từ (kể cả dấu tiếng Việt)
function W(src){return new RegExp("(?<!"+L+")(?:"+src+")(?!"+L+")","giu")}
var R=[
 {id:"cao",label:"Trèo lên chỗ cao",tip:"Cho nhân vật đứng dưới đất: nhờ người lớn lấy giúp, dùng cây sào hái quả ở cành thấp, hoặc kiễng chân nhìn.",
  re:W("trèo(?: lên)?|leo (?:lên|cây|trèo|tường|rào|cửa sổ|mái|thang|ghế|bàn|tủ)|đứng (?:lên|trên) (?:ghế|bàn|chum|vại|tủ|lan can|bậu cửa|thành giường|xô)|mái nhà|nóc nhà|lan can|bậu cửa sổ|nhảy (?:lên|từ|xuống từ) (?:ghế|bàn|chum|vại|giường|tủ|cây|tường|mái|chỗ cao)|đu (?:cây|cành|dây)|climb\\w*|on the roof|onto the (?:roof|table|chair|jar|ledge)|jumps? (?:off|from) (?:the )?(?:roof|table|chair|tree|bed)")},
 {id:"nga",label:"Ngã, đập đầu",tip:"Thay cú ngã bằng một cú trượt nhẹ lên gối êm, hoặc đồ mềm (bóng bay, lá chuối, khăn) rơi nhẹ lên đầu – không ai đau.",
  re:W("ngã(?! (?:ba|tư|năm|sáu|rẽ|giá|lòng|ngũ))|vấp ngã|té(?! ra)(?: ngã| nhào| xuống| sấp| ngửa)?|đập đầu|cụng đầu|u đầu|choáng(?: váng)?|sao (?:quay|bay|xoay) quanh đầu|rơi (?:từ|xuống từ) (?:trên )?(?:cao|cây|mái|ghế|bàn|tầng)|lộn cổ|falls?|falling|fell|tumbl\\w*|hits? (?:his|her|the|its) head|dizzy|knocked out|faceplant")},
 {id:"danh",label:"Đánh, đá, đẩy, cắn bạn",tip:"Cho nhân vật giải quyết bằng lời nói, ôm nhau làm lành, hoặc một trò đùa vui như rượt nhau chậm trên sân bằng.",
  re:W("đánh (?:nhau|bạn|em|anh|chị|người|vào|con|mèo|chó|cún|thỏ|rùa)|đấm|tát|đá (?:bạn|vào|em|anh|chị|người|con|mèo|chó|cún)|đẩy (?:ngã|bạn|em|anh|chị|người)|xô (?:ngã|bạn|em|anh|chị)|ném (?:đá|gạch|đồ|dép|cát|que)?\\s?(?:vào|trúng) (?:người|bạn|em|anh|chị|mặt|đầu|mèo|chó|cún|con)|cắn (?:bạn|em|anh|chị|người|tay|chân|tai)|giật tóc|bắt nạt|punch\\w*|kick\\w*|slap\\w*|shove\\w*|bit(?:e|es|ing) (?:him|her|someone)|beat (?:him|her|up)")},
 {id:"lua",label:"Lửa, diêm, nến, pháo",tip:"Thay bằng đèn pin, đèn lồng điện, bánh sinh nhật cắm nến điện tử, hoặc pháo giấy (tung giấy màu).",
  re:W("(?<!xe |tàu |hỏa )lửa|diêm|bật lửa|bếp lửa|đốt (?:lửa|nến|pháo|giấy|lá|rơm|củi|nhà|đồ)|châm (?:lửa|nến|pháo)|thắp nến|ngọn nến|cây nến|(?:đốt|châm|cầm|ném|bắn) pháo|pháo nổ|fire(?!fl)|flames?|matches|lighter|candles?|fireworks?")},
 {id:"dien",label:"Ổ cắm, dây điện",tip:"Nhân vật không chạm đồ điện. Nếu cần ánh sáng, người lớn bật đèn giúp.",
  re:W("ổ (?:cắm|điện)|dây điện|cột điện|cầu dao|điện giật|bị giật điện|chọc (?:vào )?(?:ổ|lỗ cắm)|electric(?:al)? (?:socket|outlet|wire)|power (?:line|outlet)|socket|electrocut\\w*")},
 {id:"nuoc",label:"Nước sâu (ao, hồ, sông, giếng)",tip:"Cho nhân vật chơi xa mép nước, có người lớn đi cùng; hoặc chơi té nước ở chậu nhỏ trong sân.",
  re:W("nhảy (?:xuống|ùm xuống) (?:ao|hồ|sông|suối|giếng|biển|nước)|bơi (?:một mình|ra xa|qua sông|ở sông|ở ao|ở hồ)|lặn (?:xuống|sâu)|tắm (?:sông|ao|hồ|suối)|cúi (?:xuống|nhìn) (?:giếng|ao|hồ)|rơi xuống (?:ao|hồ|sông|giếng|nước)|đuối nước|chết đuối|thả (?:mình )?xuống giếng|chum nước đầy|drown\\w*|swim\\w* alone|jumps? into (?:the )?(?:river|pond|lake|well)")},
 {id:"nhon",label:"Dao, kéo, kim, mảnh vỡ",tip:"Thay bằng đồ chơi mềm, kéo nhựa đầu tròn có người lớn giúp, hoặc xé giấy bằng tay.",
  re:W("con dao|dao(?! động)|cái kéo|cây kéo|chiếc kéo|lưỡi kéo|cầm kéo|dùng kéo|kéo cắt|cây kim|cái kim|kim (?:khâu|tiêm|băng|chỉ)|mảnh (?:vỡ|kính|chai|sành)|que nhọn|dao rựa|lưỡi lam|knife|knives|scissors|needles?|broken glass|shards?|sharp stick")},
 {id:"an",label:"Ăn, nuốt đồ lạ",tip:"Nhân vật chỉ ăn đồ ăn thật, người lớn đưa cho. Có thể đùa bằng cách NHÌN NHẦM (tưởng cục xà phòng là bánh) rồi người lớn nhắc kịp.",
  re:W("ăn (?:đất|cát|sỏi|lá lạ|nấm lạ|quả lạ|thuốc|xà phòng|phấn|bút|giấy|đồ chơi)|nuốt (?:hạt|đồ|viên|đồng xu|pin|bi|nút)|ngậm (?:đồ chơi|viên bi|đồng xu|pin|hạt|nút)|uống (?:thuốc|nước lạ)(?: (?:của|một mình))?|nấm lạ|quả lạ|eat\\w* (?:dirt|mushrooms?|pills?|berries|soap)|swallow\\w*")},
 {id:"tui",label:"Túi ni-lông trùm đầu",tip:"Không trùm gì lên mặt. Muốn hoá trang thì đội mũ giấy hoặc đeo mặt nạ hở mắt, mũi, miệng.",
  re:W("(?:trùm|chụp|đội) (?:túi|bao) (?:ni ?-?lông|nilon|nylon)|túi (?:ni ?-?lông|nilon|nylon) (?:lên|trùm|chụp) (?:đầu|mặt)|plastic bag over")},
 {id:"duong",label:"Chạy ra đường xe",tip:"Cho nhân vật nắm tay người lớn, đi trên vỉa hè, chờ đèn xanh.",
  re:W("chạy (?:ra|qua|sang|băng qua) (?:đường|lòng đường|đường cái)|băng qua đường một mình|đuổi theo (?:bóng|bạn|cún|mèo) ra đường|run\\w* into the (?:street|road)")},
 {id:"hon",label:"Hỗn với người lớn, nói lời xấu",tip:"Đổi thành câu lễ phép: \u201cDạ, con xin lỗi ạ\u201d, \u201cCon cảm ơn bà ạ\u201d. Cái hài nên đến từ hiểu lầm vui, không chê bai ai.",
  re:W("lè lưỡi|đồ ngốc|đồ ngu|ngu ngốc|\\bngu|im (?:đi|mồm|miệng)|câm (?:mồm|miệng)|cãi (?:lại )?(?:bà|ông|mẹ|bố|ba|cô|thầy|người lớn)|chế giễu|lừa (?:bà|ông|mẹ|bố|ba|cô|thầy|người lớn)|stupid|shut up|idiot|dumb")},
 {id:"so",label:"Cảnh làm bé sợ",tip:"Giữ không khí ấm áp: trời tối thì có đèn ngủ và người lớn bên cạnh; con vật to thì hiền lành, mỉm cười.",
  re:W("máu|quái vật|ma quỷ|con ma|hồn ma|la hét|thét lên|bắt cóc|bị bỏ rơi|bóng tối đáng sợ|chết|blood|monster|ghost|kidnap\\w*|scream\\w*")}
];
var NOTES=[
 {id:"nuoc_nhac",label:"Có cảnh gần nước",tip:"Ổn nếu nhân vật đứng xa mép nước và có người lớn. Không cho nhân vật cúi xuống, nhảy xuống hay bơi một mình.",
  re:W("ao|hồ(?! (?:sơ|dán|hởi|lô|chí minh))|sông|suối|giếng|biển|pond|river|lake|well(?! done)")},
 {id:"treu",label:"Trêu bạn",tip:"Trêu cho vui thì được, nhưng không chê bai, không làm bạn buồn. Cuối cảnh nên làm lành.",
  re:W("trêu(?: chọc)?|chọc ghẹo|tease\\w*")}
];
var EXCEPT=/(?:đồng hồ|mơ hồ|bác hồ|hồ dán|hồ sơ|hồ hởi|ao ước|ước ao)/giu;
function norm(t){return String(t||"").normalize("NFC").replace(/\s+/g," ")}
function scan(text,list,level){var t=norm(text),out=[];var plain=t.replace(EXCEPT,function(m){return " ".repeat(m.length)});
 list.forEach(function(r){r.re.lastIndex=0;var m=r.re.exec(plain);if(m)out.push({id:r.id,label:r.label,level:level,found:t.substr(m.index,m[0].length).trim(),tip:r.tip})});return out}
function check(text){var b=scan(text,R,"block");var seen={};b.forEach(function(x){seen[x.id]=1});
 var n=scan(text,NOTES,"note").filter(function(x){return !(x.id==="nuoc_nhac"&&seen.nuoc)});return b.concat(n)}
function scriptText(P){if(!P)return"";var a=[P.idea||""];if(P.script)a.push(P.script.title,P.script.summary,P.script.moral);
 (P.shots||[]).forEach(function(s){a.push(s.action||"",s.motion||"");(s.dialogue||[]).forEach(function(d){a.push(d.line||"")})});return a.join(" \n ")}
function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function html(issues,where){if(!issues.length)return"";var bl=issues.filter(function(i){return i.level==="block"}),nt=issues.filter(function(i){return i.level!=="block"});
 var h='<div class="pt-safe '+(bl.length?"blk":"nt")+'" role="status"><b>'+(bl.length?"🛡️ Ối! Chỗ này bé có thể bắt chước rồi bị đau. Mình sửa một chút nhé:":"💡 Nhắc nhỏ cho phim thật an toàn:")+'</b><ul>';
 issues.forEach(function(i){h+='<li><span class="pt-safe-w">“'+esc(i.found)+'”</span> – '+esc(i.label)+'.<br><span class="pt-safe-tip">👉 '+esc(i.tip)+'</span></li>'});
 return h+"</ul>"+(bl.length&&where==="script"?'<button class="btn" type="button" onclick="PiToonSafety.rewrite(P)">✨ Viết lại cho an toàn</button>':"")+"</div>"}
var css=".pt-safe{border-radius:16px;padding:10px 14px;margin:8px 0;font-size:14px;line-height:1.45}.pt-safe ul{margin:6px 0 4px;padding-left:20px}.pt-safe li{margin:4px 0}"+
 ".pt-safe.blk{background:#fff1ec;border:2px solid #ff9b7a}.pt-safe.nt{background:#fff8e1;border:1px solid #f5d27a}.pt-safe-w{font-weight:800;color:#c2410c}.pt-safe-tip{color:#2b3fa0;font-weight:700}";
function injectCss(){if(document.getElementById("pt-safe-css"))return;var s=document.createElement("style");s.id="pt-safe-css";s.textContent=css;document.head.appendChild(s)}
if(typeof document!=="undefined"){if(document.head)injectCss();else document.addEventListener("DOMContentLoaded",injectCss)}
var api={check:check,scriptText:scriptText,html:html,
 blocked:function(P){return check(scriptText(P)).some(function(i){return i.level==="block"})},
 show:function(id,text){var e=document.getElementById(id);if(e)e.innerHTML=html(check(text),"idea")},
 rewrite:function(P){if(typeof window.writeScript==="function"){window.PiToonSafety._fix=check(scriptText(P)).filter(function(i){return i.level==="block"});window.writeScript()}},
 rules:R,notes:NOTES};
if(typeof window!=="undefined")window.PiToonSafety=api;
if(typeof module!=="undefined")module.exports=api;
})();
