// Cache theo phiên bản: sw.js?v=<commit>. Không bao giờ chạm vào API/bên thứ ba.
const V=new URL(self.location).searchParams.get("v")||"dev",C="pitoon-"+V,SHELL=["./","./index.html","./intro.js","./intro.css","./manifest.webmanifest","./favicon.ico","./icons/favicon.ico","./icons/favicon-16.png","./icons/favicon-32.png","./icons/favicon-48.png","./icons/icon-192.png","./icons/icon-512.png","./icons/maskable-192.png","./icons/maskable-512.png","./icons/apple-touch-icon.png","./assets/ant.webp","./assets/ant_head.webp","./assets/logo_sm.webp","./assets/logo_pit.webp","./assets/logo_n.webp","./assets/logo_eyes.webp","./assets/logo_antenna.webp","./assets/intro_audio.mp3","./assets/rig/rig.json","./assets/rig/abd.webp","./assets/rig/body.webp","./assets/rig/head.webp","./assets/rig/antL.webp","./assets/rig/antR.webp","./assets/rig/armL.webp","./assets/rig/armL_lo.webp","./assets/rig/armR.webp","./assets/rig/legHL.webp","./assets/rig/legHL_lo.webp","./assets/rig/legML.webp","./assets/rig/legML_lo.webp","./assets/rig/legHR.webp","./assets/rig/legHR_lo.webp","./assets/rig/legMR.webp","./assets/rig/legMR_lo.webp"];
self.addEventListener("install",e=>{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>Promise.all(SHELL.map(u=>fetch(u,{cache:"reload"}).then(r=>r.ok&&c.put(u,r)).catch(()=>{})))))});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x.startsWith("pitoon-")&&x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener("fetch",e=>{const r=e.request,u=new URL(r.url);
 if(r.method!=="GET"||u.origin!==location.origin)return;
 if(u.pathname.endsWith("version.json")){e.respondWith(fetch(new Request(r,{cache:"no-store"})));return}
 const dest=r.destination,fresh=r.mode==="navigate"||dest==="document"||dest==="script"||dest==="style"||dest==="manifest"||/\/$|\.(html|js|css|json|webmanifest)$/.test(u.pathname);
 if(fresh){e.respondWith(fetch(r,{cache:"no-store"}).then(res=>{if(res.ok){const cp=res.clone();caches.open(C).then(c=>c.put(r,cp))}return res})
  .catch(()=>caches.match(r,{ignoreSearch:true}).then(m=>m||caches.match("./"))));return}
 e.respondWith(caches.match(r).then(m=>m||fetch(r).then(res=>{if(res.ok){const cp=res.clone();caches.open(C).then(c=>c.put(r,cp))}return res})))});
self.addEventListener("message",e=>{if(e.data==="skipWaiting")self.skipWaiting()});
