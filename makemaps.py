# -*- coding: utf-8 -*-
import json,math,os,time,urllib.request
from PIL import Image,ImageDraw,ImageFont
exec(open('venues.py',encoding='utf-8').read())
R=json.load(open('routes.json'))
UA={'User-Agent':'CantonFairVenueBoard/1.0 (internal venue scouting; contact steven) PIL'}
TS=256; W,H=800,460
def x2(lon,z): return (lon+180)/360*(2**z)
def y2(lat,z):
    s=math.sin(math.radians(lat)); return (0.5-math.log((1+s)/(1-s))/(4*math.pi))*(2**z)
def tile(z,x,y):
    n=2**z
    if x<0 or y<0 or x>=n or y>=n: return Image.new('RGB',(TS,TS),(242,242,242))
    p='.tilecache/%d_%d_%d.png'%(z,x,y)
    if not os.path.exists(p):
        for _ in range(4):
            try:
                d=urllib.request.urlopen(urllib.request.Request(
                  'https://tile.openstreetmap.org/%d/%d/%d.png'%(z,x,y),headers=UA),timeout=30).read()
                open(p,'wb').write(d); break
            except Exception: time.sleep(2)
        else: return Image.new('RGB',(TS,TS),(242,242,242))
    try: return Image.open(p).convert('RGB')
    except Exception: return Image.new('RGB',(TS,TS),(242,242,242))
def font(sz):
    for f in ['fonts/Poppins-SemiBold.ttf','fonts/Poppins-Medium.ttf']:
        try: return ImageFont.truetype(f,sz)
        except Exception: pass
    return ImageFont.load_default()
def render(vid,pts,venue,pad=72):
    lats=[p[1] for p in pts]+[venue[0],REF[0]]; lons=[p[0] for p in pts]+[venue[1],REF[1]]
    z=17
    while z>11:
        dx=(max(x2(l,z) for l in lons)-min(x2(l,z) for l in lons))*TS
        dy=(max(y2(l,z) for l in lats)-min(y2(l,z) for l in lats))*TS
        if dx<=W-pad*2 and dy<=H-pad*2: break
        z-=1
    cx=(max(x2(l,z) for l in lons)+min(x2(l,z) for l in lons))/2
    cy=(max(y2(l,z) for l in lats)+min(y2(l,z) for l in lats))/2
    ox,oy=cx*TS-W/2, cy*TS-H/2
    im=Image.new('RGB',(W,H),(238,238,238))
    for tx in range(int(ox//TS),int((ox+W)//TS)+1):
        for ty in range(int(oy//TS),int((oy+H)//TS)+1):
            im.paste(tile(z,tx,ty),(int(tx*TS-ox),int(ty*TS-oy)))
    im=Image.blend(im,Image.new('RGB',(W,H),(255,255,255)),0.14)
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    P=lambda lon,lat:(x2(lon,z)*TS-ox, y2(lat,z)*TS-oy)
    if len(pts)>1:
        xy=[P(p[0],p[1]) for p in pts]
        d.line(xy,fill=(255,255,255,235),width=10,joint='curve')
        d.line(xy,fill=(255,0,81,255),width=5,joint='curve')
    ax,ay=P(REF[1],REF[0]); bx,by=P(venue[1],venue[0])
    d.ellipse([ax-11,ay-11,ax+11,ay+11],fill=(19,0,45,255),outline=(255,255,255,255),width=3)
    d.ellipse([bx-15,by-15,bx+15,by+15],fill=(255,0,81,255),outline=(255,255,255,255),width=4)
    f=font(15); f2=font(12)
    def lab(x,y,t,bg,fg=(255,255,255,255),off=24):
        tb=d.textbbox((0,0),t,font=f2); w,h=tb[2]-tb[0],tb[3]-tb[1]
        lx,ly=min(max(x-w/2-8,6),W-w-20), y+off
        if ly+h+12>H-6: ly=y-off-h-12
        d.rounded_rectangle([lx,ly,lx+w+16,ly+h+11],7,fill=bg)
        d.text((lx+8,ly+4),t,font=f2,fill=fg)
    lab(ax,ay,'Canton Fair Complex',(19,0,45,238))
    lab(bx,by,'HERE',(255,0,81,242))
    d.rounded_rectangle([W-138,H-30,W-8,H-8],5,fill=(255,255,255,205))
    d.text((W-131,H-26),'© OpenStreetMap',font=f2,fill=(90,90,90,255))
    im=Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB')
    im.save('maps/%s.jpg'%vid,quality=80,optimize=True)
for v in V:
    r=R[v['id']]
    render(v['id'],r.get('geom') or [], v['ll'])
    print(v['id'],flush=True)
