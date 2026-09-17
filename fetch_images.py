# -*- coding: utf-8 -*-
import json,os,time,urllib.request,urllib.parse,re,sys
exec(open('venues.py',encoding='utf-8').read())
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36'}
WUA={'User-Agent':'CantonFairVenueBoard/1.0 (research build; steven) python-urllib'}
os.makedirs('img',exist_ok=True)
def get(u,h=UA,t=40):
    return urllib.request.urlopen(urllib.request.Request(u,headers=h),timeout=t).read()
def commons_info(title):
    for _ in range(4):
        try:
            u=("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|extmetadata"
               "&iiurlwidth=1600&format=json&titles="+urllib.parse.quote("File:"+title))
            d=json.loads(get(u,WUA,30))
            p=list(d['query']['pages'].values())[0]
            ii=p['imageinfo'][0]; em=ii.get('extmetadata',{})
            def g(k):
                v=em.get(k,{}).get('value','')
                return re.sub('<[^>]+>','',v).strip()
            return {'url':ii.get('thumburl') or ii['url'],'title':title.rsplit('.',1)[0].replace('_',' '),'credit':g('Artist') or 'Wikimedia Commons',
                    'lic':g('LicenseShortName') or 'see Commons','src':'Wikimedia Commons',
                    'page':'https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(title)}
        except Exception as e:
            time.sleep(4)
    return None
def openverse(q,n=3):
    out=[]
    try:
        u="https://api.openverse.org/v1/images/?q="+urllib.parse.quote(q)+"&page_size=%d&license_type=all"%(n*3)
        d=json.loads(get(u,UA,35))
        for r in d.get('results',[]):
            if not r.get('url'): continue
            out.append({'url':r['url'],'title':(r.get('title') or '').strip(),'credit':r.get('creator') or r.get('source','unknown'),
                        'lic':(r.get('license','') or '').upper()+' '+(r.get('license_version','') or ''),
                        'src':r.get('source','openverse'),'page':r.get('foreign_landing_url','')})
    except Exception as e:
        pass
    return out

manifest={}
for v in V:
    cands=[]
    for t in v.get('commons',[]):
        info=commons_info(t)
        if info: cands.append(info)
        time.sleep(1.2)
    for q in v.get('imgq',[]):
        cands+=openverse(q,3)
        time.sleep(1.0)
    saved=[]; seen=set()
    for c in cands:
        if len(saved)>=3: break
        if c['url'] in seen: continue
        seen.add(c['url'])
        ext='.jpg'
        fn='img/%s-%d%s'%(v['id'],len(saved)+1,ext)
        try:
            data=get(c['url'],UA,50)
            if len(data)<20000: continue
            open(fn,'wb').write(data)
            c2=dict(c); c2['file']=fn
            saved.append(c2)
        except Exception as e:
            continue
    manifest[v['id']]=saved
    print(v['id'],len(saved),flush=True)
json.dump(manifest,open('images.json','w'),ensure_ascii=False,indent=1)
