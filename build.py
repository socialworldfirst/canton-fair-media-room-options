# -*- coding: utf-8 -*-
import json,math,html,os
exec(open('venues.py',encoding='utf-8').read())
IMG=json.load(open('images.json',encoding='utf-8'))
def km(ll):
    dy=(ll[0]-REF[0])*111320; dx=(ll[1]-REF[1])*102400
    return round(math.hypot(dx,dy)/1000,1)
ZONES=["Inside the halls","Attached to the complex","Across the street","Across the footbridge","Next door","Pazhou island","Canton Tower corridor","Zhujiang New Town"]
e=html.escape
order=sorted(V,key=lambda v:(km(v['ll']),v['rank']))

cards=[]
for i,v in enumerate(order,1):
    shots=IMG.get(v['id'],[])
    slides="".join(
      '<figure class="slide%s"><img src="%s" alt="%s" loading="lazy" decoding="async">'
      '<figcaption>%s · %s · %s</figcaption></figure>'%(
        ' on' if j==0 else '', e(s['file']), e(v['name']),
        e((s.get('title') or 'Photo')[:64]), e((s.get('credit') or 'Unknown')[:36]), e((s.get('lic') or '').strip() or 'see source'))
      for j,s in enumerate(shots)) or '<figure class="slide on ph"><figcaption>No open-licence photo found</figcaption></figure>'
    dots="".join('<button class="dot%s" data-i="%d" aria-label="Photo %d"></button>'%(' on' if j==0 else '',j,j+1) for j in range(len(shots))) if len(shots)>1 else ''
    tags="".join('<li>%s</li>'%e(t) for t in v['tags'])
    links=" · ".join('<a href="%s" target="_blank" rel="noopener">photo %d</a>'%(e(s.get('page') or '#'),j+1) for j,s in enumerate(shots))
    cards.append(f"""
<article class="card" data-zone="{e(v['zone'])}" data-km="{km(v['ll'])}" data-rank="{v['rank']}" id="{e(v['id'])}">
  <div class="shot">
    <span class="num">{i:02d}</span>
    <div class="slides">{slides}</div>
    {'<button class="nav prev" aria-label="Previous photo">‹</button><button class="nav next" aria-label="Next photo">›</button>' if len(shots)>1 else ''}
    <div class="dots">{dots}</div>
  </div>
  <div class="body">
    <div class="meta"><span class="zone">{e(v['zone'])}</span><span class="dist">{km(v['ll'])} km from the halls</span></div>
    <h3>{e(v['name'])}</h3>
    <p class="cn">{e(v['cn'])}</p>
    <dl class="facts">
      <dt>Address</dt><dd>{e(v['addr'])}</dd>
      <dt>Getting there</dt><dd>{e(v['walk'])}</dd>
      <dt>Backdrop</dt><dd>{e(v['backdrop'])}</dd>
    </dl>
    <p class="why"><b>Why it works.</b> {e(v['why'])}</p>
    <p class="watch"><b>Watch out.</b> {e(v['watch'])}</p>
    <ul class="tags">{tags}</ul>
    <p class="credit">Photo sources: {links or 'none'}</p>
  </div>
</article>""")

pins=json.dumps([{"id":v['id'],"n":v['name'],"lat":v['ll'][0],"lng":v['ll'][1],"km":km(v['ll']),"z":v['zone']} for v in order],ensure_ascii=False)
chips="".join('<button class="chip" data-z="%s">%s</button>'%(e(z),e(z)) for z in ZONES if any(v['zone']==z for v in V))

HTML=f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Media room options · Canton Fair 2026 · Pazhou, Guangzhou</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
@font-face{{font-family:Poppins;src:url(fonts/Poppins-Regular.ttf) format('truetype');font-weight:400;font-display:swap}}
@font-face{{font-family:'Alibaba PuHuiTi';src:url(fonts/Alibaba-PuHuiTi-Regular.otf) format('opentype');font-weight:400;font-display:swap}}
@font-face{{font-family:'Alibaba PuHuiTi';src:url(fonts/Alibaba-PuHuiTi-Bold.otf) format('opentype');font-weight:700;font-display:swap}}
@font-face{{font-family:Poppins;src:url(fonts/Poppins-Medium.ttf) format('truetype');font-weight:500;font-display:swap}}
@font-face{{font-family:Poppins;src:url(fonts/Poppins-SemiBold.ttf) format('truetype');font-weight:600;font-display:swap}}
@font-face{{font-family:Poppins;src:url(fonts/Poppins-Bold.ttf) format('truetype');font-weight:700;font-display:swap}}
@font-face{{font-family:Poppins;src:url(fonts/Poppins-ExtraBold.ttf) format('truetype');font-weight:800;font-display:swap}}
:root{{--red:#FF0051;--dpurple:#13002D;--purple:#32006E;--grey:#484F56;--black:#1F2323;--lgrey:#ECEDEE;--n400:#DADCDD;--n500:#A8AEB5;--white:#fff;--orange:#FF882A}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:Poppins,system-ui,sans-serif;font-size:18px;line-height:1.55;color:var(--black);background:var(--white);-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1232px;margin:0 auto;padding:0 24px}}
h1,h2,h3{{font-weight:800;margin:0}}
h1{{font-size:clamp(38px,6vw,68px);line-height:1.02;letter-spacing:-1px}}
h2{{font-size:clamp(26px,3.4vw,40px);letter-spacing:-1.5px}}
h3{{font-size:23px;letter-spacing:-.5px;line-height:1.2}}

header.hero{{background:linear-gradient(135deg,var(--purple) 0%,var(--dpurple) 70%);color:#fff;position:relative;overflow:hidden}}
header.hero .belt{{position:absolute;right:-8%;bottom:-40%;width:70%;height:180%;background:linear-gradient(135deg,var(--red),var(--orange));border-radius:50% 50% 0 0/60% 60% 0 0;transform:rotate(-18deg);opacity:.9;filter:blur(0px)}}
header.hero .inner{{position:relative;z-index:2;padding:46px 0 60px}}
.brandbar{{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap;margin-bottom:56px}}
.brandbar img{{height:30px}}
.brandbar .tag{{font-size:13px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;opacity:.82}}
.kicker{{display:inline-block;background:var(--red);color:#fff;font-weight:600;font-size:13px;letter-spacing:.14em;text-transform:uppercase;padding:7px 14px;border-radius:999px;margin-bottom:22px}}
header.hero p.lede{{max-width:660px;font-size:20px;margin:22px 0 0;color:rgba(255,255,255,.9)}}
.stats{{display:flex;gap:44px;flex-wrap:wrap;margin-top:44px;padding-top:28px;border-top:1px solid rgba(255,255,255,.22)}}
.stats div b{{display:block;font-size:34px;font-weight:800;letter-spacing:-1px;line-height:1}}
.stats div span{{font-size:14px;color:rgba(255,255,255,.75)}}

section.note{{background:var(--lgrey);padding:34px 0}}
section.note p{{margin:0;font-size:16px;color:var(--grey);max-width:900px}}
section.note b{{color:var(--black)}}

.mapwrap{{padding:56px 0 8px}}
#map{{height:430px;border-radius:16px;overflow:hidden;border:1px solid var(--n400);margin-top:22px}}
.leaflet-container{{font-family:Poppins,sans-serif}}

.controls{{position:sticky;top:0;z-index:40;background:rgba(255,255,255,.95);backdrop-filter:blur(8px);border-bottom:1px solid var(--lgrey);padding:14px 0;margin-top:44px}}
.controls .wrap{{display:flex;gap:10px;flex-wrap:wrap;align-items:center}}
.chip{{font-family:inherit;font-size:14px;font-weight:500;border:1px solid var(--n400);background:#fff;color:var(--grey);padding:8px 15px;border-radius:999px;cursor:pointer;transition:.15s}}
.chip:hover{{border-color:var(--red);color:var(--red)}}
.chip.on{{background:var(--red);border-color:var(--red);color:#fff}}
.spacer{{flex:1}}
.sortsel{{font-family:inherit;font-size:14px;padding:8px 12px;border-radius:999px;border:1px solid var(--n400);background:#fff;color:var(--grey)}}

.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(372px,1fr));gap:26px;padding:40px 0 70px}}
.card{{border:1px solid var(--lgrey);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;background:#fff;transition:.18s}}
.card:hover{{border-color:var(--n400);box-shadow:0 14px 34px rgba(19,0,45,.10);transform:translateY(-2px)}}
.shot{{position:relative;aspect-ratio:16/10;background:var(--dpurple)}}
.slides{{position:absolute;inset:0}}
.slide{{position:absolute;inset:0;margin:0;opacity:0;transition:opacity .3s}}
.slide.on{{opacity:1}}
.slide img{{width:100%;height:100%;object-fit:cover;display:block}}
.slide figcaption{{position:absolute;left:0;right:0;bottom:0;font-size:10.5px;line-height:1.35;color:rgba(255,255,255,.88);background:linear-gradient(transparent,rgba(19,0,45,.82));padding:22px 12px 8px}}
.slide.ph{{display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,var(--purple),var(--dpurple));opacity:1}}
.slide.ph figcaption{{position:static;background:none;font-size:13px;padding:0}}
.num{{position:absolute;top:12px;left:12px;z-index:3;background:var(--red);color:#fff;font-weight:800;font-size:13px;padding:5px 10px;border-radius:8px;letter-spacing:.02em}}
.nav{{position:absolute;top:50%;transform:translateY(-50%);z-index:3;width:32px;height:32px;border:0;border-radius:50%;background:rgba(255,255,255,.88);color:var(--dpurple);font-size:19px;line-height:1;cursor:pointer;opacity:0;transition:.15s}}
.card:hover .nav{{opacity:1}}
.nav.prev{{left:10px}} .nav.next{{right:10px}}
.dots{{position:absolute;bottom:9px;right:11px;z-index:3;display:flex;gap:5px}}
.dot{{width:7px;height:7px;border-radius:50%;border:0;padding:0;background:rgba(255,255,255,.45);cursor:pointer}}
.dot.on{{background:var(--red)}}

.body{{padding:20px 22px 24px;display:flex;flex-direction:column;gap:11px;flex:1}}
.meta{{display:flex;justify-content:space-between;gap:10px;font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase}}
.zone{{color:var(--red)}} .dist{{color:var(--grey)}}
.cn{{margin:-6px 0 0;font-size:14px;color:var(--grey);font-family:'Alibaba PuHuiTi',Poppins,sans-serif;font-weight:400}}
.facts{{margin:4px 0 0;display:grid;grid-template-columns:96px 1fr;gap:5px 12px;font-size:14px}}
.facts dt{{color:var(--grey);font-weight:600}}
.facts dd{{margin:0;color:var(--black)}}
.why,.watch{{margin:0;font-size:15px;line-height:1.55}}
.why b{{color:var(--red)}}
.watch{{color:var(--grey)}} .watch b{{color:var(--black)}}
.tags{{list-style:none;margin:2px 0 0;padding:0;display:flex;gap:6px;flex-wrap:wrap}}
.tags li{{font-size:12px;font-weight:500;background:var(--lgrey);color:var(--grey);padding:4px 10px;border-radius:999px}}
.credit{{margin:auto 0 0;padding-top:8px;font-size:11px;color:var(--n500)}}
.credit a{{color:var(--n500)}}

footer{{background:var(--dpurple);color:rgba(255,255,255,.76);padding:54px 0 62px;font-size:15px}}
footer h2{{color:#fff;margin-bottom:18px}}
footer a{{color:#fff}}
footer .cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:34px;margin-top:26px}}
footer .cols h4{{color:#fff;font-size:14px;letter-spacing:.1em;text-transform:uppercase;margin:0 0 10px}}
footer ul{{margin:0;padding-left:18px}} footer li{{margin-bottom:7px}}
.rule{{height:4px;background:linear-gradient(90deg,var(--red),var(--orange));border:0;margin:0}}
@media(max-width:720px){{.grid{{grid-template-columns:1fr}}.facts{{grid-template-columns:86px 1fr}}}}
</style></head><body>

<header class="hero"><div class="belt"></div><div class="inner"><div class="wrap">
  <div class="brandbar"><img src="assets/wf_logo_en_hrz_rev.svg" alt="WorldFirst"><span class="tag">Internal · venue scouting</span></div>
  <span class="kicker">Canton Fair 2026 · 140th session</span>
  <h1>20 places to put<br>a media room.</h1>
  <p class="lede">Twenty shortlisted rooms, halls, decks and rooftops for interviews and filmed conversations around the Canton Fair Complex in Pazhou. Ranked by how close they sit to the halls, with what each one gives you on camera and what to check before you commit.</p>
  <div class="stats">
    <div><b>20</b><span>options scouted</span></div>
    <div><b>13</b><span>within 1.7 km of the halls</span></div>
    <div><b>15 Oct</b><span>Phase 1 opens</span></div>
    <div><b>4 Nov</b><span>Phase 3 closes</span></div>
  </div>
</div></div></header>
<hr class="rule">

<section class="note"><div class="wrap"><p><b>How to read this.</b> Distance is straight-line from the China Import and Export Fair Complex on Yuejiang Zhong Road, so treat it as a sort order rather than a walking time. Everything in the first four groups is on Pazhou island. The Canton Tower corridor and Zhujiang New Town options sit across the river: they buy you the landmark backdrop and cost you twenty minutes each way in fair-week traffic. Nothing here is booked. Photos are open-licence images of the venue or its immediate location, credited on each card.</p></div></section>

<div class="mapwrap"><div class="wrap">
  <h2>Where they sit</h2>
  <p style="color:var(--grey);font-size:16px;margin:10px 0 0">The red marker is the Canton Fair Complex. Click a pin to jump to its card.</p>
  <div id="map"></div>
</div></div>

<div class="controls"><div class="wrap">
  <button class="chip on" data-z="all">All 20</button>
  {chips}
  <span class="spacer"></span>
  <select class="sortsel" id="sort">
    <option value="km">Sort: nearest first</option>
    <option value="rank">Sort: our recommendation</option>
  </select>
</div></div>

<div class="wrap"><div class="grid" id="grid">{''.join(cards)}</div></div>

<footer><div class="wrap">
  <h2>Before you pick one</h2>
  <p>Three questions decide this list. Does the guest need the Canton Fair halls visibly behind them, or the Canton Tower skyline? Is the room a working media room running all day, or a one-hour evening set? And who is hosting the space, because the organiser, a hotel, a broadcaster and a public riverside each need a different conversation and a different lead time.</p>
  <div class="cols">
    <div><h4>If the story is the fair</h4><ul><li>Official Press Centre, Area A</li><li>Area D conference rooms</li><li>Nan Fung exhibition halls</li></ul></div>
    <div><h4>If the story is the skyline</h4><ul><li>Guangzhou International Media Port</li><li>Park Hyatt Roof Bar</li><li>Haixin Bridge riverfront</li></ul></div>
    <div><h4>Lowest risk, fastest yes</h4><ul><li>Shangri-La Hotel, Guangzhou</li><li>InterContinental Guangzhou Exhibition Center</li><li>Langham Place, Guangzhou</li></ul></div>
    <div><h4>Still to confirm</h4><ul><li>Fair-week availability at every hotel</li><li>Filming permits for public riverside sites</li><li>GRT studio access and a media partner</li></ul></div>
  </div>
  <p style="margin-top:34px;font-size:13px;color:rgba(255,255,255,.55)">Built for WorldFirst venue scouting · {os.popen("date +'%d %B %Y'").read().strip()} · Photography under Creative Commons and public-domain licences from Wikimedia Commons and Openverse, credited per image. Venue details are from public sources and are not confirmed bookings.</p>
</div></footer>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
var PINS={pins};
var map=L.map('map',{{scrollWheelZoom:false}}).setView([23.1055,113.3430],13);
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{maxZoom:19,attribution:'&copy; OpenStreetMap contributors'}}).addTo(map);
function dot(c,r){{return L.divIcon({{className:'',html:'<div style="width:'+r+'px;height:'+r+'px;border-radius:50%;background:'+c+';border:2.5px solid #fff;box-shadow:0 2px 7px rgba(0,0,0,.35)"></div>',iconSize:[r,r],iconAnchor:[r/2,r/2]}});}}
L.marker([23.10344,113.35412],{{icon:dot('#FF0051',22)}}).addTo(map).bindPopup('<b>Canton Fair Complex</b><br>380 Yuejiang Zhong Rd');
PINS.forEach(function(p,i){{
  L.marker([p.lat,p.lng],{{icon:dot('#32006E',14)}}).addTo(map)
   .bindPopup('<b>'+(i+1<10?'0':'')+(i+1)+'. '+p.n+'</b><br>'+p.km+' km · '+p.z+'<br><a href="#'+p.id+'">Open card</a>');
}});

document.querySelectorAll('.card').forEach(function(c){{
  var sl=c.querySelectorAll('.slide'), dt=c.querySelectorAll('.dot'); if(sl.length<2) return; var i=0;
  function go(n){{i=(n+sl.length)%sl.length;sl.forEach(function(s,j){{s.classList.toggle('on',j===i)}});dt.forEach(function(d,j){{d.classList.toggle('on',j===i)}});}}
  var p=c.querySelector('.prev'),n=c.querySelector('.next');
  if(p)p.onclick=function(){{go(i-1)}}; if(n)n.onclick=function(){{go(i+1)}};
  dt.forEach(function(d){{d.onclick=function(){{go(+d.dataset.i)}}}});
}});

var grid=document.getElementById('grid');
document.querySelectorAll('.chip').forEach(function(b){{
  b.onclick=function(){{
    document.querySelectorAll('.chip').forEach(function(x){{x.classList.remove('on')}});
    b.classList.add('on'); var z=b.dataset.z;
    document.querySelectorAll('.card').forEach(function(c){{
      c.style.display=(z==='all'||c.dataset.zone===z)?'':'none';
    }});
  }};
}});
document.getElementById('sort').onchange=function(){{
  var k=this.value, cs=Array.prototype.slice.call(grid.children);
  cs.sort(function(a,b){{return parseFloat(a.dataset[k])-parseFloat(b.dataset[k])}});
  cs.forEach(function(c){{grid.appendChild(c)}});
}};
</script></body></html>"""
open('index.html','w',encoding='utf-8').write(HTML)
print("wrote index.html", len(HTML), "bytes")
