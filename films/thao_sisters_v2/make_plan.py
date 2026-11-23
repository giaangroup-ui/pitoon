import json
STYLE="Cinematic high-quality 3D animated kids film, expressive cartoon acting like a feature animation, natural child proportions, keep exact faces, glasses, hair and outfits from the reference sheets, 16:9, no text."
SAY='{who} speaks this Vietnamese line clearly with visible lip-synced mouth movement and matching facial emotion: "{t}"'
# (id, scene, set, chars, camera, action/acting, line_who, line, emo, sfx, dur)
S=[
("A01","S01","cafe_rain","TN,TM","wide establishing, slow dolly-in through rainy window","Raindrops run down the cafe window; inside, warm light. Little bell over door swings.",None,None,"calm","rain_window,cafe_murmur,bell",3),
("A02","S01","cafe_rain","TM","medium close-up","Thao My reads a picture book, totally focused, tongue slightly out in concentration, turns a page.",None,None,"focused","page",2.5),
("A03","S01","cafe_rain","TN","close-up","Thao Nguyen leans in with a mischievous grin, wiggles eyebrows above her black glasses.","Thảo Nguyên","My ơi, đọc gì mà say thế?","cheeky","",3),
("A04","S01","cafe_rain","TM","close-up","Thao My puffs her cheeks, pushes up her pink glasses, then can't hold it and bursts into giggles.","Thảo My","Bí mật! Chị đừng phá em!","cheeky","giggle",3),
("A05","S01","cafe_rain","TN,TM","two-shot","Both sisters laugh together, Thao Nguyen ruffles My's bangs.",None,None,"happy","laugh_kids",2.5),
("A06","S02","cafe_porch","TM","over-shoulder through glass","Thao My stops laughing, notices something outside, her smile fades softly, head tilts.",None,None,"curious","rain_soft",2.5),
("A07","S02","cafe_porch","Khang","wide, respectful distance, eye level","Under the shop awning a boy (Khang) sits quietly hugging a small cloth bag, looking at the rain, hungry but calm and dignified.",None,None,"tender","rain_awning,stomach_soft",3.5),
("A08","S02","cafe_porch","TM","close-up","Thao My's eyes become soft and worried; she gently tugs her sister's sleeve.","Thảo My","Chị ơi, bạn ấy đói kìa.","sad","rain_soft",3),
("A09","S02","cafe_porch","TN","close-up","Thao Nguyen looks, nods thoughtfully, then looks back toward Mom.","Thảo Nguyên","Mình hỏi mẹ trước nhé!","kind","",3),
("A10","S03","cafe_porch","Me,TM","medium","Mom smiles warmly and nods yes; Thao My's face lights up with joy.",None,None,"warm","chime_soft",2.5),
("A11","S03","cafe_porch","TM,Khang","medium two-shot","Thao My crouches to Khang's eye level and offers a cleanly wrapped bun with both hands, smiling shyly.","Thảo My","Bạn ăn bánh nhé! Mình là My.","kind","paper_wrap",3.5),
("A12","S03","cafe_porch","Khang","close-up","Khang receives the bun with both hands, surprised, then a small grateful smile.","Khang","Cảm ơn bạn. Mình là Khang.","grateful","",3.5),
("A13","S03","cafe_porch","TN","close-up","Thao Nguyen waves friendly with a big smile.","Thảo Nguyên","Mình là Nguyên, chị của My!","happy","",3),
("A14","S04","cafe_porch","Khang,TN,TM","insert close-up on hands","Khang opens an old notebook showing a crayon drawing of a school with a flag; the sisters lean in.",None,None,"wonder","page,chime_soft",3),
("A15","S04","cafe_porch","TM","close-up","Thao My gasps with sparkling eyes, hands on cheeks.","Thảo My","Oa, tranh đẹp quá!","excited","sparkle",2.5),
("A16","S04","cafe_porch","Khang","close-up","Khang looks down at his drawing, a quiet hopeful longing, then up.","Khang","Mình mong được đi học lại.","sad_hope","",3.5),
("A17","S04","cafe_porch","TN","medium","Thao Nguyen puts a hand on her heart, determined and kind.","Thảo Nguyên","Tụi mình sẽ nhờ mẹ giúp!","determined","",3),
("A18","S05","home_living","Me,TN,TM","medium three-shot","At home on the sofa, the sisters tell Mom excitedly, hands moving; Mom listens and hugs them.",None,None,"warm","clock_tick,sofa",3),
("A19","S05","home_living","Me","close-up","Mom speaks gently with a proud warm smile.","Mẹ","Các con thương bạn, mẹ rất vui.","warm","",3.5),
("A20","S05","home_living","Me","close-up","Mom raises one finger softly, kind but serious.","Mẹ","Gặp bạn cần giúp, hãy báo người lớn nhé.","warm","",3.5),
("A21","S05","home_living","TN,TM","two-shot","Both sisters nod together, then Thao My raises her hand eagerly.","Thảo My","Con tặng bạn vở mới nha!","excited","pop",3),
("A22","S06","home_room","TN,TM","top-down insert","Small hands place a new notebook, colored pencils and folded clothes neatly into a gift bag.",None,None,"playful","paper,pencil_rattle",3),
("A23","S06","home_room","TN","medium","Thao Nguyen proudly holds up a box of colored pencils like a trophy; My claps.","Thảo Nguyên","Thêm hộp bút màu nữa!","playful","clap",3),
("A24","S07","park_day","Me,TN,TM,Khang","wide","In a bright public park, Mom walks with the sisters; Khang waits on a bench and stands up politely.",None,None,"hopeful","birds,kids_far",3),
("A25","S07","park_day","Khang","close-up","Khang holds the gift bag with both hands, eyes glistening with grateful tears but smiling, dignified.","Khang","Mình sẽ giữ thật cẩn thận.","moved","",3.5),
("A26","S07","park_day","TM,TN","two-shot","Thao My and Thao Nguyen smile and give a thumbs up.","Thảo My","Mong bạn sớm được đi học!","happy","",3),
("A27","S08","school_gate","Khang","wide, low angle","Morning at the school gate: Khang in a neat white uniform and backpack walks in with a kind adult relative, sunlight.",None,None,"bright","school_bell,kids_far",3),
("A28","S08","school_gate","TN,TM,Me","medium","The sisters wave both arms happily beside Mom.","Thảo Nguyên","Chúc bạn học vui nha!","happy","",3),
("A29","S08","school_gate","Khang","close-up","Khang turns back, waves, beaming.","Khang","Mình sẽ học thật giỏi!","proud","",2.5),
("A30","S09","cafe_sun","Khang,TN,TM","insert","Khang unrolls a drawing of three friends at a school gate (girl with black glasses, girl with pink glasses, boy with a book).",None,None,"tender","paper_unroll,sparkle",3),
("A31","S09","cafe_sun","Khang","close-up","Khang says shyly, rubbing the back of his head.","Khang","Tặng hai bạn: Những người bạn tốt!","shy","",3.5),
("A32","S09","cafe_sun","TM,TN","two-shot","Thao My hugs the drawing to her chest, Thao Nguyen dabs a happy tear.","Thảo My","Mình sẽ treo ở góc học tập!","moved","sparkle",3),
("A33","S10","school_art","Khang","medium","In a bright art classroom, Khang stands by his displayed drawing and speaks to classmates with a hopeful look.","Khang","Sau này mình sẽ giúp các bạn khác.","inspire","applause_small",3.5),
("A34","S11","cafe_sun","TN,TM,Khang","medium three-shot, slow push-in","Sunny cafe table: Thao My reads, Khang draws, Thao Nguyen smiles; they all laugh together.","Thảo Nguyên","Từ nay mình là bạn nhé!","joy","laugh_kids,cafe_murmur",3.5),
("A35","S12","path_trees","TN,TM,Khang","wide, crane up","The three friends walk down a tree-lined path near the school, leaves sway in golden light, space above for title.",None,None,"ending","wind_leaves,birds",4),
]
NARR=[("A01","Chiều mưa, hai chị em ghé quán quen."),("A18","Hai chị em kể hết cho mẹ nghe."),("A35","Quan tâm thật lòng, nhờ người lớn giúp đúng cách.")]
VOICE_FALLBACK={"Thảo Nguyên":{"engine":"vi-VN-HoaiMyNeural","pitch_hz":15,"rate":8,"formant":1.12},
 "Thảo My":{"engine":"vi-VN-HoaiMyNeural","pitch_hz":35,"rate":12,"formant":1.20},
 "Khang":{"engine":"vi-VN-NamMinhNeural","pitch_hz":40,"rate":4,"formant":1.24},
 "Mẹ":{"engine":"vi-VN-HoaiMyNeural","pitch_hz":-6,"rate":-6,"formant":1.0},
 "Người dẫn":{"engine":"vi-VN-HoaiMyNeural","pitch_hz":0,"rate":-4,"formant":1.0}}
REFS={"TN":"bible/thao_nguyen_model_sheet.png","TM":"bible/thao_my_model_sheet.png","Khang":"bible/khang_master.png","Me":"bible/me_master.png","both":"bible/TWO_SISTERS_APPROVED_MASTER.png"}
shots=[];t=0
for (i,sc,st,ch,cam,act,who,line,emo,sfx,d) in S:
    p=f"{STYLE} Camera: {cam}. {act}"+(" "+SAY.format(who=who,t=line) if line else " No dialogue, natural ambient sound only.")+" Lively natural movement throughout, no frozen poses. Safe, gentle, respectful."
    shots.append({"id":i,"scene":sc,"set":st,"chars":ch.split(","),"from":round(t,2),"to":round(t+d,2),"camera":cam,"acting":act,"emo":emo,
      "line":{"who":who,"text":line,"src":"native","fallback":"edge"} if line else None,"sfx":[x for x in sfx.split(",") if x],
      "refs":["../thao_sisters/"+REFS[c] for c in ch.split(",") if c in REFS],"video_prompt_en":p,"gen":{"duration":6,"use_s":d,"chain_from_prev_last_frame":True}})
    t+=d
plan={"lesson":"Thấy bạn cần giúp, hãy quan tâm và báo người lớn đáng tin.","title":"Hai chị em Thảo Nguyên – Thảo My và người bạn ăn xin (v2)","method":"v7: short shots, native lip-synced speech, never stretch clips, cut more shots instead",
 "out":"/workspace/ref/pitoon_free/thao_sisters_v2_16x9.mp4","body_s":round(t,1),"intro_s":3.6,"outro_s":4.0,"transition_s":0.25,
 "narration":[{"at_shot":a,"text":x,"voice":"Người dẫn"} for a,x in NARR],"voice_fallback":VOICE_FALLBACK,
 "qc":{"visual_min":8,"max_regen":4,"no_freeze_over_s":0.8,"whisper_min":0.7,"motion_min_mean_diff":3.0,"usage_stop_pct":90},
 "shots":shots}
json.dump(plan,open("SHOT_PLAN_v2.json","w"),ensure_ascii=False,indent=1)
print(len(shots),"shots body",round(t,1),"s; total",round(t+7.6,1))
