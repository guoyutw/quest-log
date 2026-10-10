/*
Sanitized reference of the current private Quest Log HUD Worker.

Privacy boundary:
- No private endpoint URL, account id, KV namespace id, access key, Sheet id,
  or live Quest instance data is stored in this file.
- Runtime bindings are supplied outside the repository:
    QUEST_HUD_ENDPOINT
    QUEST_HUD_ACCESS_KEY
    QUEST_CACHE
- The deployed private runtime/config remains private.

Durable behavior captured here:
- exact projection freshness validation;
- fail-closed fallback to last-good player state;
- candidate statuses PARKED_CANDIDATE and ACTIVE_CANDIDATE are both
  non-promoted candidate identities;
- unknown statuses fail closed.
*/

const BASE_HTML="<!doctype html>\n<html lang=\"zh-Hant\">\n<head>\n<meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n<title>Quest Log</title>\n<style>\n:root{--bg:#090d11;--panel:#101820;--line:#25313b;--text:#eef3f6;--muted:#95a2ad;--gold:#e1b85b;--green:#55c5a5;--park:#758ca0;--purple:#9a82e8;--shadow:0 18px 45px rgba(0,0,0,.34);--serif:Georgia,\"Noto Serif TC\",\"Times New Roman\",serif;--sans:Inter,system-ui,-apple-system,BlinkMacSystemFont,\"Segoe UI\",\"Noto Sans TC\",\"PingFang TC\",\"Microsoft JhengHei\",sans-serif}\n*{box-sizing:border-box}html,body{margin:0;min-height:100%}body{background:radial-gradient(circle at 10% 0%,rgba(39,61,78,.2),transparent 28%),radial-gradient(circle at 100% 100%,rgba(31,69,59,.12),transparent 26%),linear-gradient(180deg,#0d1319,var(--bg) 70%);color:var(--text);font-family:var(--sans)}\nbutton{font:inherit}.app{max-width:1180px;margin:auto;padding:12px 12px 90px}.brand,.panel{border:1px solid var(--line);background:linear-gradient(180deg,rgba(16,24,32,.98),rgba(12,18,24,.99));border-radius:16px;box-shadow:var(--shadow)}\n.brand{padding:15px 17px;margin-bottom:12px}.brand h1{margin:0;font:700 26px var(--serif)}.brand h1 span{color:var(--gold)}.head{display:flex;justify-content:space-between;align-items:center;padding:11px 13px;border-bottom:1px solid var(--line);background:#0f171e}.head h2{margin:0;font:700 15px var(--serif)}.head .eng{color:var(--gold);font-size:12px;letter-spacing:.8px;margin-left:4px}.head small{font-size:10px;color:var(--muted)}\n.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:10px}.stat{border:1px solid var(--line);background:#0d141b;border-radius:11px;padding:9px;text-align:center}.stat strong{display:block;font-size:18px}.stat span{font-size:10px;color:var(--muted)}.stat.a strong{color:var(--gold)}.stat.r strong{color:var(--green)}.stat.f strong{color:var(--purple)}\n.layout{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(310px,.75fr);gap:12px}.map{position:relative;min-height:600px;overflow:hidden;background:radial-gradient(circle at 18% 23%,rgba(62,102,78,.22),transparent 19%),radial-gradient(circle at 78% 22%,rgba(107,78,50,.18),transparent 20%),radial-gradient(circle at 52% 72%,rgba(47,75,101,.2),transparent 23%),linear-gradient(135deg,#111a20,#0c1217)}\n.routes{position:absolute;inset:0;width:100%;height:100%;opacity:.55;pointer-events:none}.zone{position:absolute;width:190px;min-height:106px;padding:11px;border:1px solid #34424e;border-radius:15px;background:rgba(13,20,27,.96);box-shadow:0 12px 25px rgba(0,0,0,.26);cursor:pointer}.zone.active{border-color:#5a5037}.zone.ready{border-color:#355c53}.zone.park{border-color:#3f4d59}.zone.cand{border-color:#554672}.zt{display:flex;align-items:center;gap:8px;font:700 14px var(--serif)}.pin{width:26px;height:26px;border-radius:50%;display:grid;place-items:center;border:1px solid #34424e;background:#0d141b;font-weight:800}.active .pin{color:var(--gold);border-color:#6b5933}.ready .pin{color:var(--green);border-color:#3d6f63}.park .pin{color:var(--park);border-color:#536879}.cand .pin{color:var(--purple);border-color:#67558b}.zm{margin-top:7px;color:var(--muted);font-size:11px;line-height:1.42}.zn{margin-top:9px;font-size:12px;line-height:1.45}.zn b{color:var(--gold)}.z0{left:8%;top:8%}.z1{left:40%;top:6%}.z2{right:7%;top:27%}.z3{left:10%;bottom:14%}.z4{left:43%;bottom:8%}.z5{right:6%;bottom:13%}\n.tracker{padding:10px}.kicker{font-size:10px;letter-spacing:1.1px;color:var(--muted);margin:8px 2px 6px}.quest{padding:10px 11px 10px 12px;margin-bottom:8px;border-left:3px solid var(--line);border-radius:0 10px 10px 0;background:rgba(255,255,255,.018);cursor:pointer}.quest.active{border-left-color:var(--gold)}.quest.ready{border-left-color:var(--green)}.quest.park{border-left-color:var(--park)}.quest.cand{border-left-color:var(--purple)}.qt{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:13px}.qt b{font-family:var(--serif)}.badge{font-size:9px;border:1px solid #34424e;border-radius:999px;padding:3px 6px;color:var(--muted)}.meta{font-size:11px;color:var(--muted);margin-top:4px}.now{font-size:12px;margin-top:6px;line-height:1.45}.now b{color:var(--gold)}\n.mobile{display:none}.bottom{display:none;position:fixed;left:8px;right:8px;bottom:8px;z-index:30;border:1px solid var(--line);background:rgba(12,18,24,.94);backdrop-filter:blur(12px);border-radius:16px;padding:6px;box-shadow:0 16px 40px rgba(0,0,0,.5)}.bottom button{flex:1;border:0;background:transparent;color:var(--muted);padding:8px 4px;border-radius:10px;font-size:10px}.bottom button b{display:block;font-size:18px;color:#d8e0e5}.bottom button.active{background:rgba(225,184,91,.12);color:var(--gold)}.bottom button.active b{color:var(--gold)}\n.drawer{position:fixed;inset:0;display:none;align-items:flex-end;justify-content:center;z-index:40;background:rgba(0,0,0,.67)}.drawer.open{display:flex}.sheet{width:min(760px,100%);max-height:92vh;overflow:auto;background:linear-gradient(180deg,#121c24,#0b1117);border:1px solid #485764;border-radius:22px 22px 0 0;padding:18px}.close{float:right;border:1px solid #34424e;background:#17212a;color:var(--text);border-radius:9px;padding:6px 10px}.sheet h2{margin:0;font:700 21px var(--serif)}.flavor{margin:10px 0 14px;color:#b5c0c7;font-size:12px;line-height:1.55}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.detail,.reward{border:1px solid var(--line);background:#0d151c;border-radius:10px;padding:10px}.detail label{display:block;color:var(--muted);font-size:10px;margin-bottom:5px}.detail div,.reward{font-size:13px;line-height:1.55}.reward{margin-top:10px}.reward b{font-family:var(--serif);font-size:12px;color:var(--gold)}\n@media(max-width:900px){.app{padding:8px 8px 86px}.brand{padding:14px 15px}.brand h1{font-size:23px}.layout{display:none}.mobile{display:block}.bottom{display:flex}.mobile .map{min-height:650px}.zone{width:45%;min-height:102px;padding:9px}.z0{left:2%;top:5%}.z1{left:52%;top:5%}.z2{right:2%;top:31%}.z3{left:2%;bottom:22%}.z4{left:52%;bottom:22%}.z5{left:27%;bottom:3%}.grid{grid-template-columns:1fr}}\n</style>\n</head>\n<body>\n<div class=\"app\">\n<div class=\"brand\"><h1>Quest Log <span>·</span> 冒險地圖</h1></div>\n<div class=\"layout\"><section class=\"panel\"><div class=\"head\"><h2>世界地圖 <span class=\"eng\">MAP</span></h2><small>點區域看 Quest</small></div><div class=\"map\" id=\"desktopMap\"></div></section><aside class=\"panel\"><div class=\"head\"><h2>任務追蹤 <span class=\"eng\">QUEST</span></h2><small>只看下一步</small></div><div class=\"tracker\" id=\"desktopTracker\"></div></aside></div>\n<div class=\"mobile\">\n<section class=\"panel\" id=\"mQuest\"><div class=\"head\"><h2>任務 <span class=\"eng\">QUEST</span></h2><small>現在做什麼</small></div><div class=\"stats\" id=\"mStats\"></div><div class=\"tracker\" id=\"mobileTracker\"></div></section>\n<section class=\"panel\" id=\"mMap\" style=\"display:none\"><div class=\"head\"><h2>世界地圖 <span class=\"eng\">MAP</span></h2><small>點任務點</small></div><div class=\"map\" id=\"mobileMap\"></div></section>\n<section class=\"panel\" id=\"mProfile\" style=\"display:none\"><div class=\"head\"><h2>狀態 <span class=\"eng\">狀態</span></h2><small>目前世界</small></div><div class=\"stats\" id=\"pStats\"></div></section>\n</div></div>\n<nav class=\"bottom\" id=\"nav\"><button class=\"active\" data-tab=\"quest\"><b>⚔</b>任務</button><button data-tab=\"map\"><b>🗺</b>地圖</button><button data-tab=\"profile\"><b>🛡</b>角色</button></nav>\n<div class=\"drawer\" id=\"drawer\"><div class=\"sheet\"><button class=\"close\" id=\"closeBtn\">關閉</button><h2 id=\"dTitle\"></h2><div class=\"flavor\" id=\"dFlavor\"></div><div class=\"grid\"><div class=\"detail\"><label>📍 目前階段</label><div id=\"dState\"></div></div><div class=\"detail\"><label>🎯 NOW</label><div id=\"dNow\"></div></div><div class=\"detail\"><label>✅ 完成／切換條件</label><div id=\"dDone\"></div></div><div class=\"detail\"><label>🔒 卡住原因</label><div id=\"dBlocker\"></div></div></div><div class=\"reward\"><b>🔮 NEXT</b><div id=\"dNext\"></div></div><div class=\"reward\"><b>✨ 任務意義</b><div id=\"dWhy\"></div></div></div></div>\n<script>\nconst DATA={quests:[],candidate_count:0};\nfunction escapeHtml(x){return String(x==null?\"\":x).replace(/&/g,\"&amp;\").replace(/</g,\"&lt;\").replace(/>/g,\"&gt;\").replace(/\"/g,\"&quot;\");}\nfunction statsHTML(){const a=DATA.quests.filter(q=>q.status===\"active\").length,r=DATA.quests.filter(q=>q.status===\"ready\"||q.status===\"park\").length,f=DATA.candidate_count;return '<div class=\"stat a\"><strong>⚔ '+a+'</strong><span>進行中</span></div><div class=\"stat r\"><strong>✦ '+r+'</strong><span>可繼續</span></div><div class=\"stat f\"><strong>? '+f+'</strong><span>未探索</span></div>'}\nfunction questRow(q){return '<div class=\"quest '+q.status+'\" data-id=\"'+escapeHtml(q.id)+'\"><div class=\"qt\"><b>'+escapeHtml(q.title)+'</b><span class=\"badge\">'+(q.status===\"active\"?\"進行中\":q.status===\"ready\"?\"可繼續\":q.status===\"park\"?\"暫停\":\"?\")+'</span></div><div class=\"meta\">'+escapeHtml(q.stage)+'</div><div class=\"now\"><b>NOW</b> '+escapeHtml(q.now)+'</div></div>'}\nfunction trackerHTML(){let o='<div class=\"kicker\">NOW</div>';DATA.quests.filter(q=>q.status===\"active\").forEach(q=>o+=questRow(q));o+='<div class=\"kicker\">稍後</div>';DATA.quests.filter(q=>q.status===\"ready\"||q.status===\"park\").forEach(q=>o+=questRow(q));o+='<div class=\"kicker\">迷霧</div>';DATA.quests.filter(q=>q.status===\"cand\").forEach(q=>o+=questRow(q));return o}\nfunction mapHTML(){let o='<svg class=\"routes\" viewBox=\"0 0 1000 620\" preserveAspectRatio=\"none\"><path d=\"M150 110 C300 70 390 90 520 110\" fill=\"none\" stroke=\"#71808a\" stroke-width=\"2.4\" stroke-dasharray=\"7 9\"/><path d=\"M540 115 C700 145 790 170 865 245\" fill=\"none\" stroke=\"#71808a\" stroke-width=\"2.4\" stroke-dasharray=\"7 9\"/><path d=\"M160 490 C330 455 430 480 550 525\" fill=\"none\" stroke=\"#71808a\" stroke-width=\"2.4\" stroke-dasharray=\"7 9\"/></svg>';DATA.quests.forEach((q,i)=>o+='<div class=\"zone '+q.status+' z'+i+'\" data-id=\"'+escapeHtml(q.id)+'\"><div class=\"zt\"><span class=\"pin\">'+(q.status===\"active\"?\"!\":q.status===\"cand\"?\"?\":\"•\")+'</span>'+escapeHtml(q.title)+'</div><div class=\"zm\">'+escapeHtml(q.stage)+'</div><div class=\"zn\"><b>NOW</b> → '+escapeHtml(q.now)+'</div></div>');return o}\nfunction openQ(id){const q=DATA.quests.find(x=>x.id===id);if(!q)return;dTitle.textContent=q.title;dFlavor.textContent=q.flavor;dState.textContent=q.stage;dNow.textContent=q.now;dDone.textContent=q.done;dBlocker.textContent=q.blocker;dNext.textContent=q.next;dWhy.textContent=q.why;drawer.classList.add(\"open\")}\nfunction bind(){document.querySelectorAll(\"[data-id]\").forEach(el=>el.onclick=()=>openQ(el.dataset.id))}\ndesktopMap.innerHTML=mapHTML();mobileMap.innerHTML=mapHTML();desktopTracker.innerHTML=trackerHTML();mobileTracker.innerHTML=trackerHTML();mStats.innerHTML=statsHTML();pStats.innerHTML=statsHTML();bind();\ncloseBtn.onclick=e=>{e.preventDefault();e.stopPropagation();drawer.classList.remove(\"open\")};drawer.onclick=e=>{if(e.target===drawer)drawer.classList.remove(\"open\")};\ndocument.querySelectorAll(\"#nav button\").forEach(b=>b.onclick=()=>{document.querySelectorAll(\"#nav button\").forEach(x=>x.classList.toggle(\"active\",x===b));mQuest.style.display=b.dataset.tab===\"quest\"?\"block\":\"none\";mMap.style.display=b.dataset.tab===\"map\"?\"block\":\"none\";mProfile.style.display=b.dataset.tab===\"profile\"?\"block\":\"none\"})\n</script></body></html>";

function json(payload,status=200){
  return new Response(JSON.stringify(payload),{status,headers:{
    "content-type":"application/json; charset=UTF-8",
    "cache-control":"private, no-store",
    "x-content-type-options":"nosniff",
    "referrer-policy":"no-referrer"
  }});
}

function makePlayerState(canonical,projection){
  if(!projection || projection.contract!=="quest-hud-projection-v1" || !Array.isArray(projection.rows)){
    throw new Error("PROJECTION_MISSING");
  }
  const quests=canonical.quests||[];
  const candidates=canonical.candidates||[];
  if(!Array.isArray(quests) || !Array.isArray(candidates)) throw new Error("CANONICAL_INVALID");
  const map=new Map();
  for(const row of projection.rows){
    if(!row.entity_type || !row.entity_id) throw new Error("PROJECTION_BAD_KEY");
    const key=row.entity_type+":"+row.entity_id;
    if(map.has(key)) throw new Error("PROJECTION_DUPLICATE");
    map.set(key,row);
  }
  if(map.size!==quests.length+candidates.length) throw new Error("PROJECTION_CARDINALITY");
  const result=[];
  for(const q of quests){
    const p=map.get("quest:"+q.id);
    if(!p || p.projection_quality!=="CURRENT") throw new Error("QUEST_PROJECTION_MISSING");
    const rt=q.route||{};
    if(p.source_state_updated_at!==String(q.updated_at||"") ||
       p.source_route_updated_at!==String(rt.updated_at||"")) throw new Error("QUEST_PROJECTION_STALE");
    const raw=String(q.status||"").toUpperCase();
    if(!["ACTIVE","READY","PARKED"].includes(raw)) throw new Error("UNKNOWN_QUEST_STATUS");
    const status=String(rt.status||"").toUpperCase()==="PARKED" || raw==="PARKED"?"park":
       raw==="ACTIVE"?"active":"ready";
    result.push({
      id:String(q.id),title:p.display_title,status,
      stage:p.display_stage,now:p.display_now,
      flavor:"",done:"",blocker:p.display_blocker || "",
      next:p.display_next || "",why:p.display_meaning || ""
    });
  }
  const candidateRows=[];
  for(const c of candidates){
    const p=map.get("candidate:"+c.id);
    if(!p || p.projection_quality!=="CURRENT" ||
       p.source_state_updated_at!==String(c.updated_at||"")){
       throw new Error("CANDIDATE_PROJECTION_STALE");
    }
    if(!["PARKED_CANDIDATE","ACTIVE_CANDIDATE"].includes(String(c.status||""))) throw new Error("UNKNOWN_CANDIDATE_STATUS");
    candidateRows.push(p);
  }
  if(candidateRows.length){
    result.push({
      id:"candidate-camp",title:"迷霧營地",status:"cand",
      stage:"尚未確認的路線 · "+candidateRows.length+" 條",
      now:"有新證據時，再決定是否要繼續探索。",
      flavor:candidateRows.map(x=>x.display_title).join(" · "),
      done:"",blocker:"",next:"保留候選，不自動升格成正式任務。",why:""
    });
  }
  result.sort((a,b)=>{
    const rank={active:0,park:1,ready:2,cand:3};
    return (rank[a.status]??4)-(rank[b.status]??4);
  });
  return {
    quests:result,
    candidate_count:candidateRows.length,
    state_updated_at:canonical.state_updated_at||"",
    projection_updated_at:projection.rows.map(x=>x.projection_updated_at).sort().pop()||""
  };
}

async function readState(){
  try{
    const controller=new AbortController();
    const timer=setTimeout(()=>controller.abort(),8000);
    let r;
    try{
      r=await fetch(QUEST_HUD_ENDPOINT,{
        method:"POST",
        headers:{"content-type":"application/json"},
        body:JSON.stringify({key:QUEST_HUD_ACCESS_KEY}),
        redirect:"follow",
        signal:controller.signal
      });
    }finally{clearTimeout(timer)}
    if(!r.ok) throw new Error("UPSTREAM_HTTP");
    const p=await r.json();
    if(!p || p.ok!==true || !p.data) throw new Error("UPSTREAM_INVALID");
    const projection=p.data.player_projection_contract==="quest-hud-projection-v1" && Array.isArray(p.data.player_projection) ? {contract:"quest-hud-projection-v1",rows:p.data.player_projection} : await QUEST_CACHE.get("hud_projection_v1","json");
    const data=makePlayerState(p.data,projection);
    const saved={data,fetched_at:new Date().toISOString()};
    await QUEST_CACHE.put("last_good_player_v1",JSON.stringify(saved));
    return {ok:true,stale:false,source:"projection",...saved};
  }catch(e){
    let saved;
    try{saved=await QUEST_CACHE.get("last_good_player_v1","json")}catch(_){}
    if(saved && saved.data && Array.isArray(saved.data.quests)){
      return {ok:true,stale:true,source:"last_good_player",...saved};
    }
    return {ok:false,error:"PLAYER_PROJECTION_NOT_READY"};
  }
}

function safeJson(value){
  return JSON.stringify(value).replace(/</g,"\\u003c").replace(/>/g,"\\u003e").replace(/&/g,"\\u0026");
}

function inject(base,state){
  let html=base;
  const start=html.indexOf("const DATA=");
  const marker="function escapeHtml(";
  const end=html.indexOf(marker,start);
  if(start<0 || end<0) return '<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>Quest Log</title><body>任務畫面暫時無法顯示</body></html>';
  const empty={quests:[],candidate_count:0};
  html=html.slice(0,start)+"const DATA="+safeJson(state.ok?state.data:empty)+";\n"+html.slice(end);
  let announcement;
  if(!state.ok){
    announcement="中文任務狀態暫時無法同步，請稍後再試。";
    html=html.replace('<div class="layout">','<div class="layout" style="display:none">');
  }else if(state.stale){
    announcement="待同步 · 顯示上一次成功核對的中文版本";
  }else{
    announcement="已同步 · "+(state.data.projection_updated_at||"中文任務狀態");
  }
  const safeAnnouncement=announcement.replace(/[&<>"]/g,"");
  html=html.replace(
    '<div class="layout">',
    '<div style="font-size:12px;color:#8db8a8;padding:0 0 12px">'+safeAnnouncement+'</div><div class="layout">'
  );
  if(!state.ok){
    html=html.replace(
      '<div class="layout" style="display:none">',
      '<div style="font-size:13px;color:#cfbc91;padding:12px">請稍後重新整理；不會把讀取失敗當成沒有任務。</div><div class="layout" style="display:none">'
    );
  }
  return html;
}

async function handle(req){
  const url=new URL(req.url);
  if(url.pathname==="/api/quests"){
    const data=await readState();
    return json(data,data.ok?200:503);
  }
  if(url.pathname==="/api/health"){
    const state=await readState();
    return json({ok:state.ok,stale:!!state.stale,source:state.source||null,
      fetched_at:state.fetched_at||null,error:state.error||null},state.ok?200:503);
  }
  if(req.method!=="GET" && req.method!=="HEAD") return new Response("Method Not Allowed",{status:405});
  const state=await readState();
  const html=inject(BASE_HTML,state);
  return new Response(req.method==="HEAD"?null:html,{headers:{
    "content-type":"text/html; charset=UTF-8",
    "cache-control":"private, no-store",
    "x-content-type-options":"nosniff",
    "referrer-policy":"no-referrer"
  }});
}
addEventListener("fetch",e=>e.respondWith(handle(e.request)));
