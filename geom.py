# -*- coding: utf-8 -*-
import json,time,urllib.request
exec(open('venues.py',encoding='utf-8').read())
R=json.load(open('routes.json'))
UA={'User-Agent':'CantonFairVenueBoard/1.0 (internal venue scouting; steven)'}
def osrm(base,a,b):
    u="%s/route/v1/driving/%f,%f;%f,%f?overview=full&geometries=geojson"%(base,a[1],a[0],b[1],b[0])
    for _ in range(4):
        try:
            d=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read())
            if d.get('code')=='Ok': return d['routes'][0]['geometry']['coordinates']
        except Exception: time.sleep(3)
    return []
for v in V:
    r=R[v['id']]
    if not r['walk_s']: r['geom']=[]; r['mode']='onsite'; continue
    walk = r['walk_s']<=1250
    r['mode']='walk' if walk else 'drive'
    base="https://routing.openstreetmap.de/routed-foot" if walk else "https://router.project-osrm.org"
    r['geom']=osrm(base,REF,v['ll']); time.sleep(1.2)
    print(v['id'],r['mode'],len(r['geom']),flush=True)
json.dump(R,open('routes.json','w'))
