# -*- coding: utf-8 -*-
import json,time,urllib.request
exec(open('venues.py',encoding='utf-8').read())
UA={'User-Agent':'CantonFairVenueBoard/1.0 (internal venue scouting; steven)'}
def osrm(base,a,b):
    u="%s/route/v1/driving/%f,%f;%f,%f?overview=false"%(base,a[1],a[0],b[1],b[0])
    for _ in range(4):
        try:
            d=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=35).read())
            if d.get('code')=='Ok':
                r=d['routes'][0]; return round(r['distance']),round(r['duration'])
        except Exception: time.sleep(3)
    return None,None
out={}
for v in V:
    dm,ds=osrm("https://router.project-osrm.org",REF,v['ll']); time.sleep(1.1)
    wm,ws=osrm("https://routing.openstreetmap.de/routed-foot",REF,v['ll']); time.sleep(1.1)
    out[v['id']]={'drive_m':dm,'drive_s':ds,'walk_m':wm,'walk_s':ws}
    print("%-16s drive %s m / %s s   walk %s m / %s s"%(v['id'],dm,ds,wm,ws),flush=True)
json.dump(out,open('routes.json','w'),indent=1)
